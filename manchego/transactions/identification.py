"""Account identification logic for transaction files."""

import csv
import logging
from pathlib import Path
from typing import Literal

logger = logging.getLogger(__name__)

# Account label type
AccountLabel = Literal[
    "personal-visa", "business-visa", "personal-chequing", "business-savings"
]

# Account mapping to UUIDs (from seed_data.sql)
ACCOUNT_MAP: dict[AccountLabel, str] = {
    "personal-visa": "account-personal-visa-uuid",
    "business-visa": "account-business-visa-uuid",
    "personal-chequing": "account-checking-uuid",
    "business-savings": "account-savings-uuid",
}


def identify_account(file_path: Path) -> AccountLabel | None:
    """Identify account type for a transaction file.

    Uses multiple heuristics in priority order:
    1. Filename override check
    2. Card number check (for credit card files)
    3. Suzanne rent check (for personal chequing)
    4. SOCAN check (for business savings)

    Args:
        file_path: Path to transaction CSV file.

    Returns:
        AccountLabel | None: Account label if identified, None if unidentified.
    """
    filename_lower = file_path.name.lower()

    # 1. Filename override check
    if "personal-visa" in filename_lower or "visa-personal" in filename_lower:
        logger.debug(f"Identified {file_path.name} as personal-visa via filename")
        return "personal-visa"

    if "business-visa" in filename_lower or "visa-business" in filename_lower:
        logger.debug(f"Identified {file_path.name} as business-visa via filename")
        return "business-visa"

    if (
        "personal-chequing" in filename_lower or "chequing-personal" in filename_lower
    ) and "visa" not in filename_lower:
        logger.debug(f"Identified {file_path.name} as personal-chequing via filename")
        return "personal-chequing"

    if (
        "business-savings" in filename_lower or "savings-business" in filename_lower
    ) and "visa" not in filename_lower:
        logger.debug(f"Identified {file_path.name} as business-savings via filename")
        return "business-savings"

    # 2. Card number check (for 5-column credit card files)
    try:
        with open(file_path, encoding="utf-8") as f:
            reader = csv.reader(f)
            first_row = next(reader, None)
            if first_row is None:
                return None

            # Check if 5 columns (credit card format)
            if len(first_row) == 5:
                # Check last column for card number
                card_number = first_row[4].strip() if len(first_row) > 4 else ""
                if card_number.endswith("9256"):
                    logger.debug(
                        f"Identified {file_path.name} as personal-visa via card number"
                    )
                    return "personal-visa"
                if card_number.endswith("4128"):
                    logger.debug(
                        f"Identified {file_path.name} as business-visa via card number"
                    )
                    return "business-visa"
    except Exception as e:
        logger.warning(f"Error reading {file_path.name} for card number check: {e}")
        # Continue to other checks

    # 3. Suzanne rent check (for 4-column chequing files)
    try:
        with open(file_path, encoding="utf-8") as f:
            reader = csv.reader(f)
            has_suzanne = False
            for row in reader:
                if len(row) < 3:
                    continue
                description = row[1].lower() if len(row) > 1 else ""
                debit_str = row[2].strip() if len(row) > 2 else ""
                credit_str = row[3].strip() if len(row) > 3 else ""

                # Check for Suzanne in description
                if "suzanne" in description:
                    # Check amount (debit or credit)
                    amount = None
                    try:
                        if debit_str:
                            amount = float(debit_str)
                        elif credit_str:
                            amount = float(credit_str)
                    except ValueError:
                        continue

                    if amount and 1200 <= amount <= 1250:
                        # Check date (around 1st of month)
                        try:
                            date_str = row[0].strip() if len(row) > 0 else ""
                            if date_str:
                                day = int(date_str.split("-")[2])
                                if 1 <= day <= 3:  # Within first 3 days
                                    has_suzanne = True
                                    break
                        except (ValueError, IndexError):
                            continue

            if has_suzanne:
                logger.debug(
                    f"Identified {file_path.name} as personal-chequing via Suzanne rent payment"
                )
                return "personal-chequing"
    except Exception as e:
        logger.warning(f"Error reading {file_path.name} for Suzanne check: {e}")
        # Continue to other checks

    # 4. SOCAN check (for 4-column savings files)
    try:
        with open(file_path, encoding="utf-8") as f:
            reader = csv.reader(f)
            has_socan = False
            has_suzanne = False

            for row in reader:
                if len(row) < 2:
                    continue
                description = row[1].lower() if len(row) > 1 else ""

                if "socan" in description:
                    has_socan = True
                if "suzanne" in description:
                    has_suzanne = True

            if has_socan and not has_suzanne:
                logger.debug(
                    f"Identified {file_path.name} as business-savings via SOCAN payment"
                )
                return "business-savings"
    except Exception as e:
        logger.warning(f"Error reading {file_path.name} for SOCAN check: {e}")

    # Unidentified
    logger.warning(f"Could not identify account for {file_path.name}")
    return None


def get_account_id(account_label: AccountLabel) -> str:
    """Get account UUID for an account label.

    Args:
        account_label: Account label.

    Returns:
        str: Account UUID.

    Raises:
        ValueError: If account label is not in the map.
    """
    if account_label not in ACCOUNT_MAP:
        raise ValueError(f"Unknown account label: {account_label}")
    return ACCOUNT_MAP[account_label]
