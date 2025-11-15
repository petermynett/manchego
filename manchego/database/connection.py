"""Database connection management with context manager support.

Provides DatabaseConnection context manager for automatic transaction handling
and foreign key enforcement.
"""

import logging
import sqlite3
from pathlib import Path
from typing import ContextManager

import manchego.global_config as g

logger = logging.getLogger(__name__)


class DatabaseConnection(ContextManager[sqlite3.Connection]):
    """Context manager for SQLite database connections.

    Automatically enables foreign keys, handles transactions (commit on success,
    rollback on exception), and uses Row factory for dict-like row access.

    Example:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM vendors WHERE name = ?", ("Walmart",))
            results = cursor.fetchall()
    """

    def __init__(self, database_path: Path | None = None) -> None:
        """Initialize database connection.

        Args:
            database_path: Path to database file. Defaults to global_config.DATABASE_PATH.
        """
        self.database_path = database_path or g.DATABASE_PATH
        self.conn: sqlite3.Connection | None = None

    def __enter__(self) -> sqlite3.Connection:
        """Open database connection and enable foreign keys.

        Returns:
            sqlite3.Connection: Database connection with Row factory.

        Raises:
            sqlite3.Error: If connection cannot be established.
        """
        self.conn = sqlite3.connect(str(self.database_path))
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        logger.debug(f"Connected to database: {self.database_path}")
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Close connection, committing on success or rolling back on exception.

        Args:
            exc_type: Exception type if exception occurred.
            exc_val: Exception value if exception occurred.
            exc_tb: Exception traceback if exception occurred.
        """
        if self.conn is None:
            return

        if exc_type is None:
            self.conn.commit()
            logger.debug("Transaction committed")
        else:
            self.conn.rollback()
            logger.error(f"Transaction rolled back due to: {exc_type.__name__}")

        self.conn.close()
        logger.debug("Connection closed")
