"""Migration runner and tracking.

Provides functions to discover, apply, and track database migrations.
"""

import logging
import re
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import NamedTuple

import manchego.global_config as g
from manchego.database.connection import DatabaseConnection

logger = logging.getLogger(__name__)


class MigrationInfo(NamedTuple):
    """Information about a migration file."""

    filename: str
    path: Path
    applied: bool
    applied_at: str | None = None


def _ensure_migrations_table(conn: sqlite3.Connection) -> None:
    """Ensure migrations tracking table exists.

    Args:
        conn: Database connection.
    """
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS migrations (
            filename TEXT PRIMARY KEY,
            applied_at TEXT NOT NULL
        )
        """
    )


def get_applied_migrations() -> set[str]:
    """Get set of applied migration filenames.

    Returns:
        set[str]: Set of migration filenames that have been applied.
    """
    with DatabaseConnection() as conn:
        _ensure_migrations_table(conn)
        cursor = conn.execute("SELECT filename FROM migrations")
        return {row[0] for row in cursor.fetchall()}


def _parse_migration_file(migration_path: Path) -> str:
    """Parse migration file and extract UP section.

    Extracts SQL between "-- UP:" or "-- ============================================================================"
    and "-- DOWN:" markers.

    Args:
        migration_path: Path to migration file.

    Returns:
        str: SQL from UP section.

    Raises:
        ValueError: If migration file format is invalid.
    """
    with open(migration_path) as f:
        content = f.read()

    # Look for UP section marker
    up_pattern = r"--\s*UP:.*?\n(.*?)(?=--\s*DOWN:|--\s*={10,}|\Z)"
    match = re.search(up_pattern, content, re.DOTALL | re.IGNORECASE)

    if match:
        return match.group(1).strip()

    # If no markers found, assume entire file is UP section
    # (for simple migrations without DOWN section)
    return content.strip()


def apply_migration(migration_path: Path) -> None:
    """Apply a single migration file.

    Parses the migration file, extracts UP section, executes it, and records
    the migration in the tracking table.

    Args:
        migration_path: Path to migration file.

    Raises:
        FileNotFoundError: If migration file doesn't exist.
        sqlite3.Error: If migration execution fails.
        ValueError: If migration file format is invalid.
    """
    if not migration_path.exists():
        raise FileNotFoundError(f"Migration file not found: {migration_path}")

    filename = migration_path.name
    logger.info(f"Applying migration: {filename}")

    # Parse migration file
    try:
        sql = _parse_migration_file(migration_path)
    except Exception as e:
        raise ValueError(f"Failed to parse migration {filename}: {e}") from e

    if not sql:
        raise ValueError(f"Migration {filename} contains no SQL")

    # Apply migration
    with DatabaseConnection() as conn:
        _ensure_migrations_table(conn)

        try:
            conn.executescript(sql)
            applied_at = datetime.now(UTC).isoformat()
            conn.execute(
                "INSERT INTO migrations (filename, applied_at) VALUES (?, ?)",
                (filename, applied_at),
            )
            conn.commit()
            logger.info(f"Migration applied successfully: {filename}")
        except sqlite3.Error as e:
            logger.error(f"Migration failed: {filename} - {e}")
            raise


def list_migrations() -> list[MigrationInfo]:
    """List all migrations (both applied and pending).

    Scans db/migrations/ directory for migration files and checks which
    have been applied.

    Returns:
        list[MigrationInfo]: List of migration information, sorted by filename.
    """
    migrations_dir = g.DB_ROOT / "migrations"
    applied = get_applied_migrations()

    if not migrations_dir.exists():
        return []

    migrations: list[MigrationInfo] = []

    for path in migrations_dir.glob("*.sql"):
        filename = path.name
        is_applied = filename in applied

        # Get applied_at timestamp if applied
        applied_at = None
        if is_applied:
            with DatabaseConnection() as conn:
                cursor = conn.execute(
                    "SELECT applied_at FROM migrations WHERE filename = ?",
                    (filename,),
                )
                row = cursor.fetchone()
                if row:
                    applied_at = row[0]

        migrations.append(
            MigrationInfo(
                filename=filename,
                path=path,
                applied=is_applied,
                applied_at=applied_at,
            )
        )

    # Sort by filename (timestamp order)
    return sorted(migrations, key=lambda m: m.filename)


def apply_all_pending() -> list[str]:
    """Apply all pending migrations in order.

    Discovers all migration files, filters out already applied ones,
    and applies them in filename order (timestamp order).

    Returns:
        list[str]: List of applied migration filenames.

    Raises:
        sqlite3.Error: If any migration fails (stops at first failure).
    """
    migrations = list_migrations()
    pending = [m for m in migrations if not m.applied]

    if not pending:
        logger.info("No pending migrations")
        return []

    applied: list[str] = []

    for migration in pending:
        apply_migration(migration.path)
        applied.append(migration.filename)

    logger.info(f"Applied {len(applied)} migration(s)")
    return applied
