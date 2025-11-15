"""Main import function for transaction files."""

import logging
import shutil
import time
from pathlib import Path
from typing import Any

from manchego.database.connection import DatabaseConnection
from manchego.transactions.config import (
    TRANSACTIONS_BACKUP_RAW_DIR,
    TRANSACTIONS_IMPORTED_DIR,
)
from manchego.transactions.discovery import get_raw_transaction_files
from manchego.transactions.identification import get_account_id, identify_account
from manchego.transactions.parsing import parse_transaction_file

logger = logging.getLogger(__name__)


def import_transactions(operation_id: str | None = None) -> dict[str, Any]:
    """Import all transaction files from raw directory.

    For each file:
    1. Identify account type
    2. Parse rows and collect errors
    3. Generate new filename with date range
    4. Move to backup_raw with new name
    5. Import to database
    6. Move to imported if successful

    Args:
        operation_id: Optional operation ID for logging.

    Returns:
        dict: Import results with success, total, succeeded, failed, failures.
    """
    if operation_id is None:
        operation_id = f"transactions_import_{int(time.time())}"

    logger.info("Starting transaction import", extra={"operation_id": operation_id})

    files = get_raw_transaction_files()
    logger.info(
        f"Found {len(files)} transaction files", extra={"operation_id": operation_id}
    )

    results = {"succeeded": [], "failed": []}
    start_time = time.time()

    for file_path in files:
        try:
            result = import_single_file(file_path, operation_id)
            if result["success"]:
                results["succeeded"].append(result)
            else:
                results["failed"].append(result)
        except Exception as e:
            logger.error(
                f"Unexpected error processing {file_path.name}: {e}",
                extra={"operation_id": operation_id},
            )
            results["failed"].append({"file": file_path.name, "reason": str(e)})

    elapsed_s = time.time() - start_time

    summary = {
        "success": len(results["failed"]) == 0,
        "total": len(files),
        "succeeded": len(results["succeeded"]),
        "failed": len(results["failed"]),
        "elapsed_s": elapsed_s,
        "failures": results["failed"] if results["failed"] else [],
    }

    logger.info(
        "Transaction import complete",
        extra={"operation_id": operation_id, "data": summary},
    )
    return summary


def import_single_file(file_path: Path, operation_id: str) -> dict[str, Any]:
    """Import a single transaction file.

    Args:
        file_path: Path to transaction CSV file.
        operation_id: Operation ID for logging.

    Returns:
        dict: Import result with success, file, rows_imported, errors.
    """
    logger.info(f"Processing {file_path.name}", extra={"operation_id": operation_id})

    # 1. Identify account
    account_label = identify_account(file_path)
    if account_label is None:
        logger.warning(
            f"Could not identify account for {file_path.name}, skipping",
            extra={"operation_id": operation_id},
        )
        return {
            "success": False,
            "file": file_path.name,
            "reason": "Account identification failed",
            "rows_imported": 0,
        }

    account_id = get_account_id(account_label)
    logger.debug(
        f"Identified {file_path.name} as {account_label}",
        extra={"operation_id": operation_id},
    )

    # 2. Parse rows
    parsed_rows, parse_errors, min_date, max_date = parse_transaction_file(file_path)

    if not parsed_rows and not parse_errors:
        logger.warning(
            f"No rows found in {file_path.name}", extra={"operation_id": operation_id}
        )
        return {
            "success": False,
            "file": file_path.name,
            "reason": "No rows found",
            "rows_imported": 0,
        }

    # 3. Generate new filename
    if min_date and max_date:
        new_filename = f"CIBC_{account_label}_{min_date}_to_{max_date}.csv"
    else:
        # Fallback if no dates found
        new_filename = f"CIBC_{account_label}_{file_path.stem}.csv"

    # 4. Move to backup_raw with new name
    backup_path = TRANSACTIONS_BACKUP_RAW_DIR / new_filename
    TRANSACTIONS_BACKUP_RAW_DIR.mkdir(parents=True, exist_ok=True)

    try:
        shutil.move(str(file_path), str(backup_path))
        logger.debug(
            f"Moved {file_path.name} to backup_raw/{new_filename}",
            extra={"operation_id": operation_id},
        )
    except Exception as e:
        logger.error(
            f"Failed to move {file_path.name} to backup: {e}",
            extra={"operation_id": operation_id},
        )
        return {
            "success": False,
            "file": file_path.name,
            "reason": f"Failed to move to backup: {e}",
            "rows_imported": 0,
        }

    # 5. Import to database
    rows_imported = 0
    db_errors: list[str] = []

    try:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()

            for row in parsed_rows:
                try:
                    # Add account_id and source_filename
                    row["account_id"] = account_id
                    row["source_filename"] = new_filename
                    row["vendor_id"] = None
                    row["location_id"] = None
                    row["category"] = None
                    row["internal_note"] = None

                    # Insert into ledger
                    columns = ", ".join(row.keys())
                    placeholders = ", ".join("?" * len(row))
                    sql = f"INSERT INTO ledger ({columns}) VALUES ({placeholders})"  # noqa: S608

                    cursor.execute(sql, tuple(row.values()))
                    rows_imported += 1
                except Exception as e:
                    db_errors.append(f"Row {row.get('id', 'unknown')}: {e!s}")
                    logger.warning(
                        f"Failed to insert row: {e}",
                        extra={"operation_id": operation_id},
                    )

            conn.commit()
            logger.info(
                f"Imported {rows_imported} rows from {new_filename}",
                extra={"operation_id": operation_id},
            )

    except Exception as e:
        logger.error(
            f"Database error importing {new_filename}: {e}",
            extra={"operation_id": operation_id},
        )
        return {
            "success": False,
            "file": file_path.name,
            "reason": f"Database error: {e}",
            "rows_imported": rows_imported,
            "parse_errors": [str(e) for e in parse_errors],
            "db_errors": db_errors,
        }

    # 6. Move to imported if successful (no parse errors and no db errors)
    if not parse_errors and not db_errors:
        imported_path = TRANSACTIONS_IMPORTED_DIR / new_filename
        TRANSACTIONS_IMPORTED_DIR.mkdir(parents=True, exist_ok=True)

        try:
            shutil.move(str(backup_path), str(imported_path))
            logger.debug(
                f"Moved {new_filename} to imported/",
                extra={"operation_id": operation_id},
            )
        except Exception as e:
            logger.warning(
                f"Failed to move {new_filename} to imported: {e}",
                extra={"operation_id": operation_id},
            )
            # Not a fatal error, file is still in backup_raw

    # Return result
    if parse_errors or db_errors:
        return {
            "success": False,
            "file": file_path.name,
            "reason": "Import completed with errors",
            "rows_imported": rows_imported,
            "parse_errors": [str(e) for e in parse_errors],
            "db_errors": db_errors,
        }

    return {
        "success": True,
        "file": file_path.name,
        "rows_imported": rows_imported,
    }
