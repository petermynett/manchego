"""Database module for manchego.

Provides connection management, migrations, query helpers, and CRUD operations.
"""

from manchego.database.connection import DatabaseConnection
from manchego.database.crud import delete, get_all, get_by_id, insert, update
from manchego.database.init import initialize_database
from manchego.database.migrations import (
    apply_all_pending,
    get_applied_migrations,
    list_migrations,
)
from manchego.database.queries import (
    execute_query,
    execute_update,
    fetch_all,
    fetch_one,
)

__all__ = [
    "DatabaseConnection",
    "apply_all_pending",
    "delete",
    "execute_query",
    "execute_update",
    "fetch_all",
    "fetch_one",
    "get_all",
    "get_applied_migrations",
    "get_by_id",
    "initialize_database",
    "insert",
    "list_migrations",
    "update",
]
