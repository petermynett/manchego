"""Tests for database query helper functions."""

import logging
import sqlite3

import pytest

import manchego.database.connection as connection
import manchego.database.queries as queries


def test_execute_query__returns_cursor(fresh_db, caplog):
    """Test basic query execution returns cursor."""
    caplog.set_level(logging.CRITICAL)

    with connection.DatabaseConnection() as conn:
        cursor = queries.execute_query(conn, "SELECT * FROM test_table")
        assert cursor is not None
        assert isinstance(cursor, sqlite3.Cursor)


def test_execute_query__with_tuple_params(fresh_db, caplog):
    """Test parameterized query with tuple parameters."""
    caplog.set_level(logging.CRITICAL)

    with connection.DatabaseConnection() as conn:
        # Insert test data
        conn.execute(
            "INSERT INTO test_table (id, name) VALUES (?, ?)",
            ("param_test", "Param Test"),
        )
        conn.commit()

        # Query with parameters
        cursor = queries.execute_query(
            conn, "SELECT * FROM test_table WHERE id = ?", ("param_test",)
        )
        row = cursor.fetchone()
        assert row is not None
        assert row[1] == "Param Test"


def test_execute_query__with_dict_params(fresh_db, caplog):
    """Test parameterized query with dict parameters."""
    caplog.set_level(logging.CRITICAL)

    with connection.DatabaseConnection() as conn:
        # Insert test data
        conn.execute(
            "INSERT INTO test_table (id, name) VALUES (:id, :name)",
            {"id": "dict_test", "name": "Dict Test"},
        )
        conn.commit()

        # Query with dict parameters
        cursor = queries.execute_query(
            conn, "SELECT * FROM test_table WHERE id = :id", {"id": "dict_test"}
        )
        row = cursor.fetchone()
        assert row is not None
        assert row[1] == "Dict Test"


def test_execute_query__raises_on_sql_error(fresh_db, caplog):
    """Test that SQL errors raise exceptions."""
    caplog.set_level(logging.CRITICAL)

    with connection.DatabaseConnection() as conn, pytest.raises(sqlite3.Error):
        queries.execute_query(conn, "SELECT * FROM non_existent_table")


def test_fetch_one__returns_dict_when_found(sample_data, caplog):
    """Test fetch_one returns dict when row found."""
    caplog.set_level(logging.CRITICAL)

    with connection.DatabaseConnection() as conn:
        result = queries.fetch_one(
            conn, "SELECT * FROM test_table WHERE id = ?", ("1",)
        )

        assert result is not None
        assert isinstance(result, dict)
        assert result["id"] == "1"
        assert result["name"] == "Test One"


def test_fetch_one__returns_none_when_not_found(sample_data, caplog):
    """Test fetch_one returns None when no row found."""
    caplog.set_level(logging.CRITICAL)

    with connection.DatabaseConnection() as conn:
        result = queries.fetch_one(
            conn, "SELECT * FROM test_table WHERE id = ?", ("999",)
        )

        assert result is None


def test_fetch_one__with_params(sample_data, caplog):
    """Test fetch_one with parameterized query."""
    caplog.set_level(logging.CRITICAL)

    with connection.DatabaseConnection() as conn:
        result = queries.fetch_one(
            conn, "SELECT * FROM test_table WHERE name = ?", ("Test Two",)
        )

        assert result is not None
        assert result["name"] == "Test Two"


def test_fetch_all__returns_list_of_dicts(sample_data, caplog):
    """Test fetch_all returns list of dicts for multiple rows."""
    caplog.set_level(logging.CRITICAL)

    with connection.DatabaseConnection() as conn:
        results = queries.fetch_all(conn, "SELECT * FROM test_table ORDER BY id")

        assert isinstance(results, list)
        assert len(results) == 3
        assert all(isinstance(r, dict) for r in results)
        assert results[0]["id"] == "1"
        assert results[1]["id"] == "2"
        assert results[2]["id"] == "3"


def test_fetch_all__returns_empty_list_when_no_rows(fresh_db, caplog):
    """Test fetch_all returns empty list when no rows."""
    caplog.set_level(logging.CRITICAL)

    with connection.DatabaseConnection() as conn:
        results = queries.fetch_all(conn, "SELECT * FROM test_table")

        assert isinstance(results, list)
        assert len(results) == 0


def test_fetch_all__with_params(sample_data, caplog):
    """Test fetch_all with parameterized query."""
    caplog.set_level(logging.CRITICAL)

    with connection.DatabaseConnection() as conn:
        results = queries.fetch_all(
            conn, "SELECT * FROM test_table WHERE id IN (?, ?)", ("1", "2")
        )

        assert len(results) == 2
        assert all(r["id"] in ("1", "2") for r in results)


def test_execute_update__returns_rowcount(fresh_db, caplog):
    """Test execute_update returns number of affected rows."""
    caplog.set_level(logging.CRITICAL)

    with connection.DatabaseConnection() as conn:
        # Insert test data
        conn.execute(
            "INSERT INTO test_table (id, name) VALUES (?, ?)",
            ("update_test", "Original"),
        )
        conn.commit()

        # Update and check rowcount
        rowcount = queries.execute_update(
            conn,
            "UPDATE test_table SET name = ? WHERE id = ?",
            ("Updated", "update_test"),
        )

        assert rowcount == 1


def test_execute_update__handles_delete(fresh_db, caplog):
    """Test execute_update handles DELETE operations."""
    caplog.set_level(logging.CRITICAL)

    with connection.DatabaseConnection() as conn:
        # Insert test data
        conn.execute(
            "INSERT INTO test_table (id, name) VALUES (?, ?)",
            ("delete_test", "To Delete"),
        )
        conn.commit()

        # Delete and check rowcount
        rowcount = queries.execute_update(
            conn, "DELETE FROM test_table WHERE id = ?", ("delete_test",)
        )

        assert rowcount == 1

        # Verify deleted
        result = queries.fetch_one(
            conn, "SELECT * FROM test_table WHERE id = ?", ("delete_test",)
        )
        assert result is None
