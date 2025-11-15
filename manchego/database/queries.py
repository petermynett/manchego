"""Basic query execution helpers.

Provides simple functions for executing queries and fetching results.
"""

import logging
import sqlite3
from typing import Any

logger = logging.getLogger(__name__)


def execute_query(
    conn: sqlite3.Connection, sql: str, params: tuple | dict | None = None
) -> sqlite3.Cursor:
    """Execute a SQL query and return the cursor.

    Args:
        conn: Database connection.
        sql: SQL query string (parameterized).
        params: Query parameters (tuple, dict, or None).

    Returns:
        sqlite3.Cursor: Query result cursor.

    Raises:
        sqlite3.Error: If query execution fails.
    """
    try:
        cursor = conn.execute(sql, params or ())
        logger.debug(f"Executed query: {sql[:50]}...")
        return cursor
    except sqlite3.Error as e:
        logger.error(f"Query execution failed: {e}")
        raise


def fetch_one(
    conn: sqlite3.Connection, sql: str, params: tuple | dict | None = None
) -> dict[str, Any] | None:
    """Execute query and return single row as dict, or None if no results.

    Args:
        conn: Database connection.
        sql: SQL query string (parameterized).
        params: Query parameters (tuple, dict, or None).

    Returns:
        dict[str, Any] | None: Single row as dict, or None if no results.

    Raises:
        sqlite3.Error: If query execution fails.
    """
    cursor = execute_query(conn, sql, params)
    row = cursor.fetchone()
    if row is None:
        return None
    return dict(row)


def fetch_all(
    conn: sqlite3.Connection, sql: str, params: tuple | dict | None = None
) -> list[dict[str, Any]]:
    """Execute query and return all rows as list of dicts.

    Args:
        conn: Database connection.
        sql: SQL query string (parameterized).
        params: Query parameters (tuple, dict, or None).

    Returns:
        list[dict[str, Any]]: All rows as list of dicts (empty list if no results).

    Raises:
        sqlite3.Error: If query execution fails.
    """
    cursor = execute_query(conn, sql, params)
    rows = cursor.fetchall()
    return [dict(row) for row in rows]


def execute_update(
    conn: sqlite3.Connection, sql: str, params: tuple | dict | None = None
) -> int:
    """Execute INSERT/UPDATE/DELETE and return number of affected rows.

    Args:
        conn: Database connection.
        sql: SQL statement (parameterized).
        params: Query parameters (tuple, dict, or None).

    Returns:
        int: Number of affected rows.

    Raises:
        sqlite3.Error: If statement execution fails.
    """
    cursor = execute_query(conn, sql, params)
    rowcount = cursor.rowcount
    logger.debug(f"Update affected {rowcount} rows")
    return rowcount
