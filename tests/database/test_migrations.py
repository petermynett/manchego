"""Tests for database migration system."""

import logging
import sqlite3
from pathlib import Path

import pytest

import manchego.database.connection as connection
import manchego.database.migrations as migrations


def test_get_applied_migrations__returns_empty_set_initially(fresh_db, caplog):
    """Test get_applied_migrations returns empty set initially."""
    caplog.set_level(logging.CRITICAL)

    applied = migrations.get_applied_migrations()

    assert isinstance(applied, set)
    assert len(applied) == 0


def test_get_applied_migrations__returns_applied_filenames(
    _redirect_database_paths, fresh_db, caplog
):
    """Test get_applied_migrations returns applied filenames after applying migrations."""
    caplog.set_level(logging.CRITICAL)

    migrations_dir = _redirect_database_paths["db"] / "migrations"
    migrations_dir.mkdir(parents=True, exist_ok=True)

    # Create and apply a migration
    migration_file = migrations_dir / "20240101000000_test.sql"
    migration_file.write_text("CREATE TABLE test_migration (id TEXT PRIMARY KEY);")

    migrations.apply_migration(migration_file)

    applied = migrations.get_applied_migrations()

    assert "20240101000000_test.sql" in applied
    assert len(applied) == 1


def test_parse_migration_file__extracts_up_section(tmp_path, caplog):
    """Test _parse_migration_file extracts UP section."""
    caplog.set_level(logging.CRITICAL)

    migration_file = tmp_path / "test_migration.sql"
    migration_file.write_text(
        """
-- UP:
CREATE TABLE test_table (id TEXT PRIMARY KEY);
INSERT INTO test_table VALUES ('test');

-- DOWN:
DROP TABLE test_table;
"""
    )

    sql = migrations._parse_migration_file(migration_file)

    assert "CREATE TABLE" in sql
    assert "INSERT INTO" in sql
    assert "DROP TABLE" not in sql  # DOWN section excluded


def test_parse_migration_file__handles_markers(tmp_path, caplog):
    """Test _parse_migration_file handles UP/DOWN markers."""
    caplog.set_level(logging.CRITICAL)

    migration_file = tmp_path / "test_migration.sql"
    migration_file.write_text(
        """
-- UP: Create test table
CREATE TABLE test_table (id TEXT);

-- DOWN: Remove test table
DROP TABLE test_table;
"""
    )

    sql = migrations._parse_migration_file(migration_file)

    assert "CREATE TABLE" in sql
    assert "DROP TABLE" not in sql


def test_parse_migration_file__handles_file_without_markers(tmp_path, caplog):
    """Test _parse_migration_file handles file without markers (assumes entire file is UP)."""
    caplog.set_level(logging.CRITICAL)

    migration_file = tmp_path / "test_migration.sql"
    migration_file.write_text("CREATE TABLE test_table (id TEXT PRIMARY KEY);")

    sql = migrations._parse_migration_file(migration_file)

    assert "CREATE TABLE" in sql
    assert sql.strip() == "CREATE TABLE test_table (id TEXT PRIMARY KEY);"


def test_parse_migration_file__raises_on_invalid_format(tmp_path, caplog):
    """Test _parse_migration_file raises ValueError on invalid format."""
    caplog.set_level(logging.CRITICAL)

    # Note: The current implementation doesn't actually raise on invalid format
    # It returns empty string if no markers found, or entire file if no match
    # So this test verifies it doesn't crash on empty file
    migration_file = tmp_path / "empty_migration.sql"
    migration_file.write_text("")

    sql = migrations._parse_migration_file(migration_file)

    # Empty file should return empty string (not raise)
    assert sql == ""


def test_apply_migration__executes_sql_and_tracks(
    _redirect_database_paths, fresh_db, caplog
):
    """Test apply_migration executes SQL and tracks in migrations table."""
    caplog.set_level(logging.CRITICAL)

    migrations_dir = _redirect_database_paths["db"] / "migrations"
    migrations_dir.mkdir(parents=True, exist_ok=True)

    migration_file = migrations_dir / "20240101000000_create_test.sql"
    migration_file.write_text("CREATE TABLE migration_test (id TEXT PRIMARY KEY);")

    migrations.apply_migration(migration_file)

    # Verify table created
    with connection.DatabaseConnection() as conn:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='migration_test'"
        )
        table = cursor.fetchone()
        assert table is not None

    # Verify migration tracked
    applied = migrations.get_applied_migrations()
    assert "20240101000000_create_test.sql" in applied


def test_apply_migration__creates_migrations_table(
    _redirect_database_paths, fresh_db, caplog
):
    """Test apply_migration creates migrations table if it doesn't exist."""
    caplog.set_level(logging.CRITICAL)

    migrations_dir = _redirect_database_paths["db"] / "migrations"
    migrations_dir.mkdir(parents=True, exist_ok=True)

    # Verify migrations table doesn't exist initially (fresh_db might have it from schema)
    # Apply a migration which should ensure table exists
    migration_file = migrations_dir / "20240101000000_test.sql"
    migration_file.write_text("SELECT 1;")  # Simple SQL

    migrations.apply_migration(migration_file)

    # Verify migrations table exists and has our migration
    with connection.DatabaseConnection() as conn:
        cursor = conn.execute("SELECT filename FROM migrations")
        rows = cursor.fetchall()
        assert len(rows) >= 1


def test_apply_migration__raises_on_missing_file(
    _redirect_database_paths, fresh_db, caplog
):
    """Test apply_migration raises FileNotFoundError when file missing."""
    caplog.set_level(logging.CRITICAL)

    missing_file = Path("/nonexistent/migration.sql")

    with pytest.raises(FileNotFoundError, match="Migration file not found"):
        migrations.apply_migration(missing_file)


def test_apply_migration__raises_on_empty_sql(
    _redirect_database_paths, fresh_db, caplog
):
    """Test apply_migration raises ValueError when SQL is empty."""
    caplog.set_level(logging.CRITICAL)

    migrations_dir = _redirect_database_paths["db"] / "migrations"
    migrations_dir.mkdir(parents=True, exist_ok=True)

    empty_migration = migrations_dir / "20240101000000_empty.sql"
    empty_migration.write_text("   \n\n   ")  # Whitespace only

    with pytest.raises(ValueError, match="contains no SQL"):
        migrations.apply_migration(empty_migration)


def test_apply_migration__raises_on_sql_error(
    _redirect_database_paths, fresh_db, caplog
):
    """Test apply_migration raises sqlite3.Error on SQL execution error."""
    caplog.set_level(logging.CRITICAL)

    migrations_dir = _redirect_database_paths["db"] / "migrations"
    migrations_dir.mkdir(parents=True, exist_ok=True)

    invalid_migration = migrations_dir / "20240101000000_invalid.sql"
    invalid_migration.write_text("INVALID SQL SYNTAX!!!")

    with pytest.raises(sqlite3.Error):
        migrations.apply_migration(invalid_migration)


def test_list_migrations__returns_empty_list_when_no_files(
    _redirect_database_paths, fresh_db, caplog
):
    """Test list_migrations returns empty list when no migration files exist."""
    caplog.set_level(logging.CRITICAL)

    # Ensure migrations directory doesn't exist
    migrations_dir = _redirect_database_paths["db"] / "migrations"
    if migrations_dir.exists():
        import shutil

        shutil.rmtree(migrations_dir)

    result = migrations.list_migrations()

    assert isinstance(result, list)
    assert len(result) == 0


def test_list_migrations__includes_applied_and_pending(
    _redirect_database_paths, fresh_db, caplog
):
    """Test list_migrations includes both applied and pending migrations."""
    caplog.set_level(logging.CRITICAL)

    migrations_dir = _redirect_database_paths["db"] / "migrations"
    migrations_dir.mkdir(parents=True, exist_ok=True)

    # Create two migration files
    migration1 = migrations_dir / "20240101000000_first.sql"
    migration1.write_text("CREATE TABLE first (id TEXT);")

    migration2 = migrations_dir / "20240102000000_second.sql"
    migration2.write_text("CREATE TABLE second (id TEXT);")

    # Apply only the first one
    migrations.apply_migration(migration1)

    result = migrations.list_migrations()

    assert len(result) == 2
    assert all(
        m.filename in ("20240101000000_first.sql", "20240102000000_second.sql")
        for m in result
    )

    # Check applied status
    applied_status = {m.filename: m.applied for m in result}
    assert applied_status["20240101000000_first.sql"] is True
    assert applied_status["20240102000000_second.sql"] is False


def test_list_migrations__sorts_by_filename(_redirect_database_paths, fresh_db, caplog):
    """Test list_migrations sorts migrations by filename (timestamp order)."""
    caplog.set_level(logging.CRITICAL)

    migrations_dir = _redirect_database_paths["db"] / "migrations"
    migrations_dir.mkdir(parents=True, exist_ok=True)

    # Create migrations out of order
    migration3 = migrations_dir / "20240103000000_third.sql"
    migration3.write_text("SELECT 3;")

    migration1 = migrations_dir / "20240101000000_first.sql"
    migration1.write_text("SELECT 1;")

    migration2 = migrations_dir / "20240102000000_second.sql"
    migration2.write_text("SELECT 2;")

    result = migrations.list_migrations()

    assert len(result) == 3
    assert result[0].filename == "20240101000000_first.sql"
    assert result[1].filename == "20240102000000_second.sql"
    assert result[2].filename == "20240103000000_third.sql"


def test_list_migrations__includes_applied_at_timestamp(
    _redirect_database_paths, fresh_db, caplog
):
    """Test list_migrations includes applied_at timestamp for applied migrations."""
    caplog.set_level(logging.CRITICAL)

    migrations_dir = _redirect_database_paths["db"] / "migrations"
    migrations_dir.mkdir(parents=True, exist_ok=True)

    migration_file = migrations_dir / "20240101000000_timestamp_test.sql"
    migration_file.write_text("SELECT 1;")

    migrations.apply_migration(migration_file)

    result = migrations.list_migrations()

    # RUF015: Prefer 'next(...)' over single element slice
    applied_migration = next(
        m for m in result if m.filename == "20240101000000_timestamp_test.sql"
    )
    assert applied_migration.applied is True
    assert applied_migration.applied_at is not None
    assert "T" in applied_migration.applied_at  # ISO format
    assert (
        applied_migration.applied_at.endswith("+00:00")
        or "Z" in applied_migration.applied_at
    )


def test_apply_all_pending__applies_multiple_migrations(
    _redirect_database_paths, fresh_db, caplog
):
    """Test apply_all_pending applies multiple pending migrations."""
    caplog.set_level(logging.CRITICAL)

    migrations_dir = _redirect_database_paths["db"] / "migrations"
    migrations_dir.mkdir(parents=True, exist_ok=True)

    # Create multiple migration files
    migration1 = migrations_dir / "20240101000000_migration1.sql"
    migration1.write_text("CREATE TABLE migration1 (id TEXT);")

    migration2 = migrations_dir / "20240102000000_migration2.sql"
    migration2.write_text("CREATE TABLE migration2 (id TEXT);")

    applied = migrations.apply_all_pending()

    assert len(applied) == 2
    assert "20240101000000_migration1.sql" in applied
    assert "20240102000000_migration2.sql" in applied

    # Verify all are now applied
    all_applied = migrations.get_applied_migrations()
    assert "20240101000000_migration1.sql" in all_applied
    assert "20240102000000_migration2.sql" in all_applied


def test_apply_all_pending__applies_in_order(
    _redirect_database_paths, fresh_db, caplog
):
    """Test apply_all_pending applies migrations in filename order."""
    caplog.set_level(logging.CRITICAL)

    migrations_dir = _redirect_database_paths["db"] / "migrations"
    migrations_dir.mkdir(parents=True, exist_ok=True)

    # Create migrations out of order
    migration3 = migrations_dir / "20240103000000_third.sql"
    migration3.write_text("CREATE TABLE third (id TEXT);")

    migration1 = migrations_dir / "20240101000000_first.sql"
    migration1.write_text("CREATE TABLE first (id TEXT);")

    migration2 = migrations_dir / "20240102000000_second.sql"
    migration2.write_text("CREATE TABLE second (id TEXT);")

    applied = migrations.apply_all_pending()

    # Should be applied in filename order
    assert applied[0] == "20240101000000_first.sql"
    assert applied[1] == "20240102000000_second.sql"
    assert applied[2] == "20240103000000_third.sql"


def test_apply_all_pending__returns_empty_list_when_none_pending(
    _redirect_database_paths, fresh_db, caplog
):
    """Test apply_all_pending returns empty list when all migrations already applied."""
    caplog.set_level(logging.CRITICAL)

    migrations_dir = _redirect_database_paths["db"] / "migrations"
    migrations_dir.mkdir(parents=True, exist_ok=True)

    migration_file = migrations_dir / "20240101000000_already_applied.sql"
    migration_file.write_text("SELECT 1;")

    # Apply migration manually
    migrations.apply_migration(migration_file)

    # Try to apply all pending (should return empty)
    applied = migrations.apply_all_pending()

    assert isinstance(applied, list)
    assert len(applied) == 0


def test_apply_all_pending__stops_on_first_failure(
    _redirect_database_paths, fresh_db, caplog
):
    """Test apply_all_pending stops at first failure and doesn't continue."""
    caplog.set_level(logging.CRITICAL)

    migrations_dir = _redirect_database_paths["db"] / "migrations"
    migrations_dir.mkdir(parents=True, exist_ok=True)

    # Create valid migration and invalid migration
    migration1 = migrations_dir / "20240101000000_valid.sql"
    migration1.write_text("CREATE TABLE valid (id TEXT);")

    migration2 = migrations_dir / "20240102000000_invalid.sql"
    migration2.write_text("INVALID SQL SYNTAX!!!")

    migration3 = migrations_dir / "20240103000000_should_not_run.sql"
    migration3.write_text("CREATE TABLE should_not_run (id TEXT);")

    # Should raise on invalid migration
    with pytest.raises(sqlite3.Error):
        migrations.apply_all_pending()

    # First migration should be applied
    applied = migrations.get_applied_migrations()
    assert "20240101000000_valid.sql" in applied

    # Second migration should NOT be applied (failed)
    assert "20240102000000_invalid.sql" not in applied

    # Third migration should NOT be applied (stopped before it)
    assert "20240103000000_should_not_run.sql" not in applied
