"""Generic CRUD operations for database tables.

Provides reusable functions for common database operations that work across
different tables.
"""

import logging
import sqlite3
from datetime import UTC, datetime
from typing import Any

from manchego.database.queries import execute_update, fetch_all, fetch_one

logger = logging.getLogger(__name__)


def insert(
    conn: sqlite3.Connection, table_name: str, data: dict[str, Any]
) -> dict[str, Any]:
    """Insert a single record into a table.

    Automatically adds created_at and updated_at timestamps if not present.

    Args:
        conn: Database connection.
        table_name: Name of the table.
        data: Dictionary of column names to values.

    Returns:
        dict[str, Any]: The inserted row as a dict.

    Raises:
        sqlite3.IntegrityError: If constraint violation occurs.
        sqlite3.Error: If insert fails.
    """
    now = datetime.now(UTC).isoformat()

    # Add timestamps if not present
    if "created_at" not in data:
        data["created_at"] = now
    if "updated_at" not in data:
        data["updated_at"] = now

    # Build INSERT statement
    columns = ", ".join(data.keys())
    placeholders = ", ".join("?" * len(data))
    # S608: table_name and columns come from function params, not user input
    sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"  # noqa: S608

    try:
        conn.execute(sql, tuple(data.values()))
        conn.commit()

        # Fetch and return inserted row
        # For tables with natural keys, use the key from data
        # For tables with UUID keys, we'd need to get lastrowid, but we're using TEXT PKs
        # So we'll query by the primary key value from data
        # This is a limitation - we assume the primary key is in the data
        # For now, return the data we inserted
        logger.debug(f"Inserted record into {table_name}")
        return data
    except sqlite3.Error as e:
        logger.error(f"Insert failed for {table_name}: {e}")
        raise


def get_by_id(
    conn: sqlite3.Connection,
    table_name: str,
    id_value: str,
    pk_column: str = "id",
) -> dict[str, Any] | None:
    """Get a single record by primary key.

    Args:
        conn: Database connection.
        table_name: Name of the table.
        id_value: Primary key value.
        pk_column: Primary key column name (defaults to "id").

    Returns:
        dict[str, Any] | None: The row as a dict, or None if not found.

    Raises:
        sqlite3.Error: If query fails.
    """
    # S608: table_name and pk_column come from function params, not user input
    sql = f"SELECT * FROM {table_name} WHERE {pk_column} = ?"  # noqa: S608
    return fetch_one(conn, sql, (id_value,))


def update(
    conn: sqlite3.Connection,
    table_name: str,
    id_value: str,
    data: dict[str, Any],
    pk_column: str = "id",
) -> dict[str, Any] | None:
    """Update a record by primary key.

    Automatically updates updated_at timestamp.

    Args:
        conn: Database connection.
        table_name: Name of the table.
        id_value: Primary key value.
        data: Dictionary of column names to new values.
        pk_column: Primary key column name (defaults to "id").

    Returns:
        dict[str, Any] | None: The updated row as a dict, or None if not found.

    Raises:
        sqlite3.Error: If update fails.
    """
    # Add updated_at timestamp
    data["updated_at"] = datetime.now(UTC).isoformat()

    # Build UPDATE statement
    set_clauses = ", ".join(f"{k} = ?" for k in data)
    # S608: table_name, columns, and pk_column come from function params, not user input
    sql = f"UPDATE {table_name} SET {set_clauses} WHERE {pk_column} = ?"  # noqa: S608

    try:
        params = (*tuple(data.values()), id_value)
        execute_update(conn, sql, params)
        conn.commit()

        # Return updated row
        return get_by_id(conn, table_name, id_value, pk_column)
    except sqlite3.Error as e:
        logger.error(f"Update failed for {table_name}: {e}")
        raise


def delete(
    conn: sqlite3.Connection,
    table_name: str,
    id_value: str,
    pk_column: str = "id",
) -> bool:
    """Delete a record by primary key.

    Args:
        conn: Database connection.
        table_name: Name of the table.
        id_value: Primary key value.
        pk_column: Primary key column name (defaults to "id").

    Returns:
        bool: True if record was deleted, False if not found.

    Raises:
        sqlite3.Error: If delete fails.
    """
    # S608: table_name and pk_column come from function params, not user input
    sql = f"DELETE FROM {table_name} WHERE {pk_column} = ?"  # noqa: S608
    rowcount = execute_update(conn, sql, (id_value,))
    conn.commit()
    return rowcount > 0


def get_all(
    conn: sqlite3.Connection,
    table_name: str,
    where_clause: str | None = None,
    params: tuple | dict | None = None,
) -> list[dict[str, Any]]:
    """Get all records from a table, optionally filtered by WHERE clause.

    Args:
        conn: Database connection.
        table_name: Name of the table.
        where_clause: Optional WHERE clause (without "WHERE" keyword).
        params: Parameters for WHERE clause.

    Returns:
        list[dict[str, Any]]: All matching rows as list of dicts.

    Raises:
        sqlite3.Error: If query fails.
    """
    # S608: table_name comes from function param, not user input
    # Note: where_clause is user-provided but caller is responsible for sanitization
    sql = f"SELECT * FROM {table_name}"  # noqa: S608
    if where_clause:
        sql += f" WHERE {where_clause}"
    return fetch_all(conn, sql, params)
