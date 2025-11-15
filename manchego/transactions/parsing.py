"""CSV parsing and row transformation for transaction files."""

import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

logger = logging.getLogger(__name__)


class ParseError(Exception):
    """Error parsing a transaction row."""

    def __init__(self, row_num: int, message: str, row_data: list[str] | None = None):
        """Initialize parse error.

        Args:
            row_num: Row number (1-indexed).
            message: Error message.
            row_data: Optional row data for context.
        """
        self.row_num = row_num
        self.message = message
        self.row_data = row_data
        super().__init__(f"Row {row_num}: {message}")


def parse_transaction_file(
    file_path: Path,
) -> tuple[list[dict[str, Any]], list[ParseError], str | None, str | None]:
    """Parse transaction CSV file and transform rows.

    Args:
        file_path: Path to CSV file.

    Returns:
        tuple: (parsed_rows, errors, min_date, max_date)
            - parsed_rows: List of parsed transaction dicts
            - errors: List of parsing errors
            - min_date: Minimum transaction date (YYYY-MM-DD) or None
            - max_date: Maximum transaction date (YYYY-MM-DD) or None
    """
    parsed_rows: list[dict[str, Any]] = []
    errors: list[ParseError] = []
    dates: list[str] = []

    try:
        with open(file_path, encoding="utf-8") as f:
            reader = csv.reader(f)
            row_num = 0

            for row in reader:
                row_num += 1

                # Skip empty rows
                if not row or all(not cell.strip() for cell in row):
                    continue

                try:
                    parsed = parse_row(row, row_num)
                    if parsed:
                        parsed_rows.append(parsed)
                        if parsed.get("transaction_date"):
                            dates.append(parsed["transaction_date"])
                except ParseError as e:
                    errors.append(e)
                    logger.debug(
                        f"Parse error in {file_path.name} row {row_num}: {e.message}"
                    )

    except Exception as e:
        errors.append(ParseError(0, f"File read error: {e}"))
        logger.error(f"Error reading {file_path.name}: {e}")

    # Find min/max dates
    min_date = min(dates) if dates else None
    max_date = max(dates) if dates else None

    return parsed_rows, errors, min_date, max_date


def parse_row(row: list[str], row_num: int) -> dict[str, Any] | None:
    """Parse a single CSV row into a transaction dict.

    Args:
        row: CSV row as list of strings.
        row_num: Row number (1-indexed) for error reporting.

    Returns:
        dict: Parsed transaction with keys: id, transaction_date, description, amount, currency.

    Raises:
        ParseError: If row cannot be parsed.
    """
    # Determine format (4 or 5 columns)
    if len(row) < 4:
        raise ParseError(
            row_num, f"Row has {len(row)} columns, expected at least 4", row
        )

    # Extract fields
    date_str = row[0].strip()
    description = row[1].strip() if len(row) > 1 else ""
    debit_str = row[2].strip() if len(row) > 2 else ""
    credit_str = row[3].strip() if len(row) > 3 else ""

    # Validate date
    if not date_str:
        raise ParseError(row_num, "Missing transaction date", row)

    try:
        # Validate date format (YYYY-MM-DD)
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError as e:
        raise ParseError(row_num, f"Invalid date format: {date_str}", row) from e

    # Validate description
    if not description:
        raise ParseError(row_num, "Missing description", row)

    # Parse amount (debit = negative, credit = positive)
    amount: float | None = None
    try:
        if debit_str:
            amount = -float(debit_str)  # Debit is negative
        elif credit_str:
            amount = float(credit_str)  # Credit is positive
        else:
            raise ParseError(row_num, "Missing both debit and credit amounts", row)
    except ValueError as e:
        raise ParseError(
            row_num, f"Invalid amount: debit={debit_str}, credit={credit_str}", row
        ) from e

    # Generate UUID for transaction
    transaction_id = str(uuid4())

    return {
        "id": transaction_id,
        "transaction_date": date_str,
        "transaction_time": None,  # Not available in CSV
        "description": description,
        "amount": amount,
        "currency": "CAD",  # Always CAD per requirements
    }
