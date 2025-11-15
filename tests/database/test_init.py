"""Tests for database initialization."""

import logging

import pytest

import manchego.database.connection as connection
import manchego.database.init as init


def test_initialize_database__creates_fresh_database(
    _redirect_database_paths, test_schema, caplog
):
    """Test basic database initialization creates database."""
    caplog.set_level(logging.CRITICAL)

    db_path = _redirect_database_paths["db_path"]

    # Database should not exist initially
    if db_path.exists():
        db_path.unlink()

    init.initialize_database(load_seed=False)

    # Verify database created
    assert db_path.exists()


def test_initialize_database__loads_schema(
    _redirect_database_paths, test_schema, caplog
):
    """Test initialization loads and executes schema."""
    caplog.set_level(logging.CRITICAL)

    db_path = _redirect_database_paths["db_path"]

    if db_path.exists():
        db_path.unlink()

    init.initialize_database(load_seed=False)

    # Verify schema tables created
    with connection.DatabaseConnection() as conn:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence'"
        )
        tables = [row[0] for row in cursor.fetchall()]

        assert "test_table" in tables
        assert "account_types" in tables


def test_initialize_database__loads_seed_data_when_requested(
    _redirect_database_paths, test_schema, tmp_path, caplog
):
    """Test initialization loads seed data when requested."""
    caplog.set_level(logging.CRITICAL)

    db_path = _redirect_database_paths["db_path"]
    sql_dir = _redirect_database_paths["sql"]

    # Create seed data file
    seed_path = sql_dir / "seed_data.sql"
    seed_path.write_text(
        """
INSERT OR IGNORE INTO account_types (label, description) VALUES
    ('TestType', 'Test Description');
"""
    )

    # Update global_config to point to seed file
    import manchego.global_config as g

    g.SQL_ROOT = sql_dir

    if db_path.exists():
        db_path.unlink()

    init.initialize_database(load_seed=True)

    # Verify seed data loaded
    with connection.DatabaseConnection() as conn:
        cursor = conn.execute(
            "SELECT * FROM account_types WHERE label = ?", ("TestType",)
        )
        row = cursor.fetchone()
        assert row is not None
        assert row[1] == "Test Description"


@pytest.mark.parametrize("load_seed", [True, False], ids=["with_seed", "without_seed"])
def test_initialize_database__loads_seed_conditionally(
    _redirect_database_paths, test_schema, tmp_path, caplog, load_seed
):
    """Test initialization conditionally loads seed data."""
    caplog.set_level(logging.CRITICAL)

    db_path = _redirect_database_paths["db_path"]
    sql_dir = _redirect_database_paths["sql"]

    # Create seed data file
    seed_path = sql_dir / "seed_data.sql"
    seed_path.write_text(
        """
INSERT OR IGNORE INTO account_types (label, description) VALUES
    ('ConditionalTest', 'Conditional Description');
"""
    )

    import manchego.global_config as g

    g.SQL_ROOT = sql_dir

    if db_path.exists():
        db_path.unlink()

    init.initialize_database(load_seed=load_seed)

    # Verify seed data loaded or not based on parameter
    with connection.DatabaseConnection() as conn:
        cursor = conn.execute(
            "SELECT * FROM account_types WHERE label = ?", ("ConditionalTest",)
        )
        row = cursor.fetchone()

        if load_seed:
            assert row is not None
        else:
            assert row is None


def test_initialize_database__raises_on_missing_schema_file(
    _redirect_database_paths, caplog
):
    """Test initialization raises FileNotFoundError when schema missing."""
    caplog.set_level(logging.CRITICAL)

    schema_path = _redirect_database_paths["schema_path"]

    # Remove schema file if it exists
    if schema_path.exists():
        schema_path.unlink()

    with pytest.raises(FileNotFoundError, match="Schema file not found"):
        init.initialize_database(load_seed=False)


def test_initialize_database__raises_on_missing_seed_file(
    _redirect_database_paths, test_schema, tmp_path, caplog
):
    """Test initialization raises FileNotFoundError when seed file missing but requested."""
    caplog.set_level(logging.CRITICAL)

    sql_dir = _redirect_database_paths["sql"]
    seed_path = sql_dir / "seed_data.sql"

    # Ensure seed file doesn't exist
    if seed_path.exists():
        seed_path.unlink()

    import manchego.global_config as g

    g.SQL_ROOT = sql_dir

    with pytest.raises(FileNotFoundError, match="Seed data file not found"):
        init.initialize_database(load_seed=True)


def test_initialize_database__raises_when_database_exists_with_tables(
    _redirect_database_paths, test_schema, caplog
):
    """Test initialization raises ValueError when database exists with tables."""
    caplog.set_level(logging.CRITICAL)

    db_path = _redirect_database_paths["db_path"]

    # Create database with tables
    if db_path.exists():
        db_path.unlink()

    init.initialize_database(load_seed=False)

    # Try to initialize again (should fail)
    with pytest.raises(ValueError, match="already exists and contains tables"):
        init.initialize_database(load_seed=False)


def test_initialize_database__allows_existing_empty_database(
    _redirect_database_paths, test_schema, caplog
):
    """Test initialization allows existing empty database."""
    caplog.set_level(logging.CRITICAL)

    db_path = _redirect_database_paths["db_path"]

    # Create empty database file
    if db_path.exists():
        db_path.unlink()

    db_path.parent.mkdir(parents=True, exist_ok=True)
    db_path.touch()  # Create empty file

    # Should not raise error
    init.initialize_database(load_seed=False)

    # Verify schema loaded
    with connection.DatabaseConnection() as conn:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence'"
        )
        tables = [row[0] for row in cursor.fetchall()]
        assert len(tables) > 0


def test_initialize_database__creates_db_directory(
    _redirect_database_paths, test_schema, caplog
):
    """Test initialization creates database directory if it doesn't exist."""
    caplog.set_level(logging.CRITICAL)

    db_path = _redirect_database_paths["db_path"]
    db_dir = db_path.parent

    # Remove database and directory
    if db_path.exists():
        db_path.unlink()
    if db_dir.exists():
        import shutil

        shutil.rmtree(db_dir)

    init.initialize_database(load_seed=False)

    # Verify directory and database created
    assert db_dir.exists()
    assert db_path.exists()
