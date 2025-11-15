"""Tests for database CRUD operations."""

import logging
import sqlite3

import pytest

import manchego.database.connection as connection
import manchego.database.crud as crud


def test_insert__creates_record(fresh_db, caplog):
    """Test basic insert creates record."""
    caplog.set_level(logging.CRITICAL)

    with connection.DatabaseConnection() as conn:
        data = {"id": "test1", "name": "Test Record"}
        result = crud.insert(conn, "test_table", data)

        assert result["id"] == "test1"
        assert result["name"] == "Test Record"

        # Verify record exists
        cursor = conn.execute("SELECT * FROM test_table WHERE id = ?", ("test1",))
        row = cursor.fetchone()
        assert row is not None
        assert row[1] == "Test Record"


def test_insert__adds_timestamps(fresh_db, caplog):
    """Test insert automatically adds timestamps."""
    caplog.set_level(logging.CRITICAL)

    with connection.DatabaseConnection() as conn:
        data = {"id": "timestamp_test", "name": "Timestamp Test"}
        result = crud.insert(conn, "test_table", data)

        assert "created_at" in result
        assert "updated_at" in result
        assert result["created_at"] is not None
        assert result["updated_at"] is not None
        assert "T" in result["created_at"]  # ISO format
        assert result["created_at"] == result["updated_at"]  # Same on insert


def test_insert__preserves_existing_timestamps(fresh_db, caplog):
    """Test insert preserves user-provided timestamps."""
    caplog.set_level(logging.CRITICAL)

    with connection.DatabaseConnection() as conn:
        custom_timestamp = "2024-01-01T12:00:00+00:00"
        data = {
            "id": "custom_timestamp",
            "name": "Custom Timestamp",
            "created_at": custom_timestamp,
            "updated_at": custom_timestamp,
        }
        result = crud.insert(conn, "test_table", data)

        assert result["created_at"] == custom_timestamp
        assert result["updated_at"] == custom_timestamp


def test_insert__raises_on_constraint_violation(fresh_db, caplog):
    """Test insert raises IntegrityError on constraint violation."""
    caplog.set_level(logging.CRITICAL)

    with connection.DatabaseConnection() as conn:
        # Insert first record
        data1 = {"id": "duplicate", "name": "First"}
        crud.insert(conn, "test_table", data1)

        # Try to insert duplicate primary key
        data2 = {"id": "duplicate", "name": "Second"}
        with pytest.raises(sqlite3.IntegrityError):
            crud.insert(conn, "test_table", data2)


def test_get_by_id__returns_dict_when_found(sample_data, caplog):
    """Test get_by_id returns dict when record found."""
    caplog.set_level(logging.CRITICAL)

    with connection.DatabaseConnection() as conn:
        result = crud.get_by_id(conn, "test_table", "1")

        assert result is not None
        assert isinstance(result, dict)
        assert result["id"] == "1"
        assert result["name"] == "Test One"


def test_get_by_id__returns_none_when_not_found(sample_data, caplog):
    """Test get_by_id returns None when record not found."""
    caplog.set_level(logging.CRITICAL)

    with connection.DatabaseConnection() as conn:
        result = crud.get_by_id(conn, "test_table", "999")

        assert result is None


def test_get_by_id__with_custom_pk_column(fresh_db, caplog):
    """Test get_by_id with custom primary key column."""
    caplog.set_level(logging.CRITICAL)

    with connection.DatabaseConnection() as conn:
        # Insert into account_types (uses 'label' as PK)
        data = {"label": "CustomPK", "description": "Test"}
        crud.insert(conn, "account_types", data)

        # Get by custom PK column
        result = crud.get_by_id(conn, "account_types", "CustomPK", pk_column="label")

        assert result is not None
        assert result["label"] == "CustomPK"


@pytest.mark.parametrize(
    "table_name", ["test_table", "account_types"], ids=["test_table", "account_types"]
)
def test_get_by_id__works_with_different_tables(fresh_db, caplog, table_name):
    """Test get_by_id works with different table structures."""
    caplog.set_level(logging.CRITICAL)

    with connection.DatabaseConnection() as conn:
        if table_name == "test_table":
            data = {"id": "test_id", "name": "Test"}
            pk_col = "id"
            pk_val = "test_id"
        else:
            data = {"label": "test_label", "description": "Test"}
            pk_col = "label"
            pk_val = "test_label"

        crud.insert(conn, table_name, data)
        result = crud.get_by_id(conn, table_name, pk_val, pk_column=pk_col)

        assert result is not None
        assert result[pk_col] == pk_val


def test_update__modifies_record(sample_data, caplog):
    """Test update modifies existing record."""
    caplog.set_level(logging.CRITICAL)

    with connection.DatabaseConnection() as conn:
        update_data = {"name": "Updated Name"}
        result = crud.update(conn, "test_table", "1", update_data)

        assert result is not None
        assert result["name"] == "Updated Name"
        assert result["id"] == "1"


def test_update__updates_timestamp(sample_data, caplog):
    """Test update automatically updates timestamp."""
    caplog.set_level(logging.CRITICAL)

    with connection.DatabaseConnection() as conn:
        # Get original record
        original = crud.get_by_id(conn, "test_table", "1")
        original_updated_at = original["updated_at"]

        # Wait a tiny bit and update
        import time

        time.sleep(0.01)

        update_data = {"name": "New Name"}
        result = crud.update(conn, "test_table", "1", update_data)

        assert result["updated_at"] != original_updated_at
        assert "updated_at" in result


def test_update__returns_none_when_not_found(sample_data, caplog):
    """Test update returns None when record not found."""
    caplog.set_level(logging.CRITICAL)

    with connection.DatabaseConnection() as conn:
        update_data = {"name": "Should Not Exist"}
        result = crud.update(conn, "test_table", "999", update_data)

        assert result is None


def test_delete__removes_record(sample_data, caplog):
    """Test delete removes record."""
    caplog.set_level(logging.CRITICAL)

    with connection.DatabaseConnection() as conn:
        result = crud.delete(conn, "test_table", "1")

        assert result is True

        # Verify deleted
        deleted = crud.get_by_id(conn, "test_table", "1")
        assert deleted is None


def test_delete__returns_false_when_not_found(sample_data, caplog):
    """Test delete returns False when record not found."""
    caplog.set_level(logging.CRITICAL)

    with connection.DatabaseConnection() as conn:
        result = crud.delete(conn, "test_table", "999")

        assert result is False


def test_delete__with_custom_pk_column(fresh_db, caplog):
    """Test delete with custom primary key column."""
    caplog.set_level(logging.CRITICAL)

    with connection.DatabaseConnection() as conn:
        # Insert into account_types (uses 'label' as PK)
        data = {"label": "DeleteTest", "description": "To Delete"}
        crud.insert(conn, "account_types", data)

        # Delete by custom PK column
        result = crud.delete(conn, "account_types", "DeleteTest", pk_column="label")

        assert result is True

        # Verify deleted
        deleted = crud.get_by_id(conn, "account_types", "DeleteTest", pk_column="label")
        assert deleted is None


def test_get_all__returns_all_records(sample_data, caplog):
    """Test get_all returns all records without filter."""
    caplog.set_level(logging.CRITICAL)

    with connection.DatabaseConnection() as conn:
        results = crud.get_all(conn, "test_table")

        assert isinstance(results, list)
        assert len(results) == 3
        assert all(isinstance(r, dict) for r in results)


def test_get_all__with_where_clause(sample_data, caplog):
    """Test get_all with WHERE clause filter."""
    caplog.set_level(logging.CRITICAL)

    with connection.DatabaseConnection() as conn:
        results = crud.get_all(
            conn, "test_table", where_clause="id IN (?, ?)", params=("1", "2")
        )

        assert len(results) == 2
        assert all(r["id"] in ("1", "2") for r in results)


def test_get_all__returns_empty_list_when_no_rows(fresh_db, caplog):
    """Test get_all returns empty list when no rows."""
    caplog.set_level(logging.CRITICAL)

    with connection.DatabaseConnection() as conn:
        results = crud.get_all(conn, "test_table")

        assert isinstance(results, list)
        assert len(results) == 0


def test_get_all__with_tuple_params(sample_data, caplog):
    """Test get_all with tuple parameters."""
    caplog.set_level(logging.CRITICAL)

    with connection.DatabaseConnection() as conn:
        results = crud.get_all(
            conn, "test_table", where_clause="name LIKE ?", params=("Test%",)
        )

        assert len(results) == 3


def test_get_all__with_dict_params(fresh_db, caplog):
    """Test get_all with dict parameters."""
    caplog.set_level(logging.CRITICAL)

    with connection.DatabaseConnection() as conn:
        # Insert test data
        crud.insert(conn, "test_table", {"id": "dict_param", "name": "Dict Param Test"})

        results = crud.get_all(
            conn,
            "test_table",
            where_clause="name = :name",
            params={"name": "Dict Param Test"},
        )

        assert len(results) == 1
        assert results[0]["name"] == "Dict Param Test"
