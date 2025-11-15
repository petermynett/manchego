"""Tests for database connection management."""

import logging
import sqlite3

import pytest

import manchego.database.connection as connection


def test_context_manager__opens_and_closes_connection(fresh_db, caplog):
    """Test basic context manager enter/exit."""
    caplog.set_level(logging.CRITICAL)

    conn = connection.DatabaseConnection()
    assert conn.conn is None

    with conn as db_conn:
        assert db_conn is not None
        assert isinstance(db_conn, sqlite3.Connection)
        assert conn.conn is not None

    # Connection should be closed after context exit
    assert conn.conn is None


def test_context_manager__sets_row_factory(fresh_db, caplog):
    """Test that Row factory is set for dict-like row access."""
    caplog.set_level(logging.CRITICAL)

    with connection.DatabaseConnection() as conn:
        assert conn.row_factory == sqlite3.Row

        # Insert a test row to verify dict-like access
        conn.execute(
            "INSERT INTO test_table (id, name) VALUES (?, ?)",
            ("row_factory_test", "Test"),
        )
        conn.commit()

        # Verify rows are accessible as dicts
        cursor = conn.execute(
            "SELECT * FROM test_table WHERE id = ?", ("row_factory_test",)
        )
        row = cursor.fetchone()
        assert row is not None
        # Row should support dict-like access
        assert hasattr(row, "keys")
        # sqlite3.Row requires .keys() for membership test (doesn't support 'in' operator)
        assert "id" in row.keys()
        assert row["id"] == "row_factory_test"
        # sqlite3.Row supports dict-like indexing and has keys() but not values()


def test_context_manager__enables_foreign_keys(fresh_db, caplog):
    """Test that foreign keys are enabled."""
    caplog.set_level(logging.CRITICAL)

    with connection.DatabaseConnection() as conn:
        cursor = conn.execute("PRAGMA foreign_keys")
        result = cursor.fetchone()
        assert result[0] == 1  # Foreign keys should be ON


def test_context_manager__commits_on_success(fresh_db, caplog):
    """Test that transaction is committed on successful exit."""
    caplog.set_level(logging.CRITICAL)

    with connection.DatabaseConnection() as conn:
        conn.execute(
            "INSERT INTO test_table (id, name) VALUES (?, ?)",
            ("commit_test", "Commit Test"),
        )
        # No explicit commit here - should happen on exit

    # Verify data persisted (committed)
    with connection.DatabaseConnection() as conn:
        cursor = conn.execute("SELECT * FROM test_table WHERE id = ?", ("commit_test",))
        row = cursor.fetchone()
        assert row is not None
        assert row[1] == "Commit Test"


def test_context_manager__rolls_back_on_exception(fresh_db, caplog):
    """Test that transaction is rolled back on exception."""
    caplog.set_level(logging.CRITICAL)

    try:
        with connection.DatabaseConnection() as conn:
            conn.execute(
                "INSERT INTO test_table (id, name) VALUES (?, ?)",
                ("rollback_test", "Rollback Test"),
            )
            # Raise exception to trigger rollback
            raise ValueError("Test exception")
    except ValueError:
        pass  # Expected

    # Verify data was NOT persisted (rolled back)
    with connection.DatabaseConnection() as conn:
        cursor = conn.execute(
            "SELECT * FROM test_table WHERE id = ?", ("rollback_test",)
        )
        row = cursor.fetchone()
        assert row is None  # Should not exist due to rollback


def test_context_manager__handles_custom_database_path(tmp_path, caplog):
    """Test that custom database path parameter works."""
    caplog.set_level(logging.CRITICAL)

    custom_db_path = tmp_path / "custom.db"

    # Create schema in custom database
    with connection.DatabaseConnection(custom_db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS test_table (
                id TEXT PRIMARY KEY,
                name TEXT
            )
            """
        )
        conn.commit()

    # Verify custom database exists and works
    assert custom_db_path.exists()

    with connection.DatabaseConnection(custom_db_path) as conn:
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        assert len([t for t in tables if t[0] == "test_table"]) == 1


def test_context_manager__handles_connection_error(tmp_path, caplog):
    """Test that connection errors are handled properly."""
    caplog.set_level(logging.CRITICAL)

    # Create a directory with the database name (should cause connection error)
    invalid_db_path = tmp_path / "invalid.db"
    invalid_db_path.mkdir(parents=True, exist_ok=True)

    # Try to connect to invalid path
    # SIM117: Use a single 'with' statement with multiple contexts
    with pytest.raises(sqlite3.Error), connection.DatabaseConnection(invalid_db_path):
        pass  # Should not reach here
