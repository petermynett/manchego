"""File discovery for transaction CSV files."""

import logging
from pathlib import Path

from manchego.transactions import config

logger = logging.getLogger(__name__)

# Import at function level to allow test patching
TRANSACTIONS_RAW_DIR = config.TRANSACTIONS_RAW_DIR


# ============================================================================
# FILE DISCOVERY
# ============================================================================


def get_raw_transaction_files() -> list[Path]:
    """Find transaction CSV files in raw directory.

    Returns:
        list[Path]: List of transaction CSV files.

    """
    # Use config module to allow test patching
    return list(config.TRANSACTIONS_RAW_DIR.glob("*.csv"))
