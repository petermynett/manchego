"""Database initialization functions.

Provides functions to create a fresh database from schema and seed data.
"""

import logging
import sqlite3

import manchego.global_config as g
from manchego.database.connection import DatabaseConnection

logger = logging.getLogger(__name__)


def initialize_database(load_seed: bool = True) -> None:
    """Initialize a fresh database from schema and optionally load seed data.

    Creates the database file if it doesn't exist, executes schema.sql to create
    tables, and optionally loads seed_data.sql.

    Args:
        load_seed: If True, load seed data after creating schema.

    Raises:
        FileNotFoundError: If schema.sql or seed_data.sql files don't exist.
        sqlite3.Error: If database operations fail.
        ValueError: If database already exists and has tables.
    """
    schema_path = g.SCHEMA_PATH
    seed_path = g.SQL_ROOT / "seed_data.sql"
    db_path = g.DATABASE_PATH

    # Validate SQL files exist
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    if load_seed and not seed_path.exists():
        raise FileNotFoundError(f"Seed data file not found: {seed_path}")

    # Check if database already exists and has tables
    if db_path.exists():
        try:
            with DatabaseConnection() as conn:
                cursor = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence'"
                )
                tables = cursor.fetchall()
                if tables:
                    raise ValueError(
                        f"Database {db_path} already exists and contains tables. "
                        "Use migrations to modify existing database."
                    )
        except sqlite3.Error:
            # If we can't read it, assume it's corrupted or empty, proceed
            pass

    # Create database directory if needed
    db_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Initializing database: {db_path}")

    # Execute schema
    with open(schema_path) as f:
        schema_sql = f.read()

    with DatabaseConnection() as conn:
        conn.executescript(schema_sql)
        logger.info("Schema created successfully")

    # Load seed data if requested
    if load_seed:
        with open(seed_path) as f:
            seed_sql = f.read()

        with DatabaseConnection() as conn:
            conn.executescript(seed_sql)
            logger.info("Seed data loaded successfully")

    logger.info("Database initialization complete")
