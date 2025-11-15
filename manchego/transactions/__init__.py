"""Transaction import and processing module.

Provides functions for importing bank transaction CSVs into the ledger table
with automatic account identification and file management.
"""

from manchego.transactions.loader import import_transactions

__all__ = ["import_transactions"]
