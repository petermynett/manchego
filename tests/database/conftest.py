"""Shared fixtures for database tests."""

import pytest

import manchego.global_config as g


@pytest.fixture(autouse=True)
def _redirect_database_paths(tmp_path, monkeypatch):
    """
    Redirect all database paths to tmp_path to prevent touching real data.
    This fixture runs automatically for all tests in this module.

    Redirects:
    - DATABASE_PATH (database file)
    - SCHEMA_PATH (schema SQL file)
    - SQL_ROOT (SQL directory)
    - DB_ROOT (database directory)
    """
    db_dir = tmp_path / "db"
    sql_dir = tmp_path / "sql"
    migrations_dir = db_dir / "migrations"

    db_dir.mkdir(parents=True, exist_ok=True)
    sql_dir.mkdir(parents=True, exist_ok=True)
    migrations_dir.mkdir(parents=True, exist_ok=True)

    db_path = db_dir / "test.db"
    schema_path = sql_dir / "schema.sql"

    monkeypatch.setattr(g, "DATABASE_PATH", db_path)
    monkeypatch.setattr(g, "SCHEMA_PATH", schema_path)
    monkeypatch.setattr(g, "SQL_ROOT", sql_dir)
    monkeypatch.setattr(g, "DB_ROOT", db_dir)

    return {
        "db": db_dir,
        "sql": sql_dir,
        "migrations": migrations_dir,
        "db_path": db_path,
        "schema_path": schema_path,
    }


@pytest.fixture
def test_schema(tmp_path, _redirect_database_paths):
    """Create test database schema file."""
    schema_path = _redirect_database_paths["schema_path"]

    schema_sql = """
-- Test schema
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS migrations (
    filename TEXT PRIMARY KEY,
    applied_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS test_table (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TEXT,
    updated_at TEXT
);

CREATE TABLE IF NOT EXISTS account_types (
    label TEXT PRIMARY KEY,
    description TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS payment_types (
    name TEXT PRIMARY KEY,
    description TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);
"""
    schema_path.write_text(schema_sql)
    return schema_path


@pytest.fixture
def fresh_db(test_schema, _redirect_database_paths):
    """Create fresh database with schema for each test."""
    from manchego.database.connection import DatabaseConnection

    db_path = _redirect_database_paths["db_path"]

    # Remove existing database if present
    if db_path.exists():
        db_path.unlink()

    # Create database with schema
    with open(test_schema) as f:
        schema_sql = f.read()

    with DatabaseConnection() as conn:
        conn.executescript(schema_sql)
        conn.commit()

    return db_path


@pytest.fixture
def sample_data(fresh_db):
    """Insert sample test data into database."""
    from manchego.database.connection import DatabaseConnection

    with DatabaseConnection() as conn:
        # Insert test records
        conn.execute(
            "INSERT INTO test_table (id, name, created_at, updated_at) VALUES (?, ?, ?, ?)",
            ("1", "Test One", "2024-01-01T00:00:00+00:00", "2024-01-01T00:00:00+00:00"),
        )
        conn.execute(
            "INSERT INTO test_table (id, name, created_at, updated_at) VALUES (?, ?, ?, ?)",
            ("2", "Test Two", "2024-01-02T00:00:00+00:00", "2024-01-02T00:00:00+00:00"),
        )
        conn.execute(
            "INSERT INTO test_table (id, name, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (
                "3",
                "Test Three",
                "2024-01-03T00:00:00+00:00",
                "2024-01-03T00:00:00+00:00",
            ),
        )
        conn.commit()

    return fresh_db
