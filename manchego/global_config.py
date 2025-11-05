"""Global configuration for manchego paths and settings.

Defines root paths, database paths, environment detection, API keys,
and log path helpers. Module-specific paths are in respective module configs.
"""

import os
import warnings
from datetime import UTC
from pathlib import Path

# Project root (absolute path to project root directory)
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Export UTC for convenience (matches old global_config pattern)
__all__ = [
    "DATABASE_PATH",
    "DATASETS_ROOT",
    "DATA_ROOT",
    "DB_PATHS",
    "DB_ROOT",
    "DB_SNAPSHOT_DIR",
    "DB_SNAPSHOT_DIRS",
    "GOOGLE_CREDENTIALS_PATH",
    "LOGS_ROOT",
    "MANCHEGO_ENV",
    "OPENAI_API_KEY",
    "PROJECT_ROOT",
    "SCHEMA_PATH",
    "SQL_ROOT",
    "UTC",
    "get_log_path",
]

# Root paths (relative to project root where CLI runs)
DATA_ROOT = Path("data")
DB_ROOT = Path("db")
DATASETS_ROOT = DATA_ROOT / "datasets"
LOGS_ROOT = DATA_ROOT / "logs"
SQL_ROOT = Path("sql")

# Environment detection
_ENV = os.getenv("MANCHEGO_ENV", "dev")
VALID_ENVS = {"dev", "stage", "prod"}

if _ENV not in VALID_ENVS:
    warnings.warn(f"Invalid MANCHEGO_ENV={_ENV}, defaulting to 'dev'", stacklevel=2)
    _ENV = "dev"

MANCHEGO_ENV = _ENV

# Database paths for each environment
DB_PATHS = {
    "dev": DB_ROOT / "manchego_dev.db",
    "stage": DB_ROOT / "manchego_stage.db",
    "prod": DB_ROOT / "manchego_prod.db",
}

# Current database path based on environment
DATABASE_PATH = DB_PATHS[MANCHEGO_ENV]

# Database snapshot directories for each environment
DB_SNAPSHOT_DIRS = {
    "dev": DB_ROOT / "snapshots" / "dev",
    "stage": DB_ROOT / "snapshots" / "stage",
    "prod": DB_ROOT / "snapshots" / "prod",
}

# Current snapshot directory based on environment
DB_SNAPSHOT_DIR = DB_SNAPSHOT_DIRS[MANCHEGO_ENV]

# Schema file location (shared across all environments)
SCHEMA_PATH = SQL_ROOT / "schema.sql"

# API keys from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH")

if OPENAI_API_KEY is None:
    warnings.warn("OPENAI_API_KEY not set in environment", stacklevel=2)

if GOOGLE_CREDENTIALS_PATH is None:
    warnings.warn("GOOGLE_CREDENTIALS_PATH not set in environment", stacklevel=2)


def get_log_path(module_name: str) -> Path:
    """Get log file path for a module.

    Args:
        module_name: Module name (e.g., 'receipts.preprocess' or 'receipts').

    Returns:
        Path: Path to log file at data/logs/{domain}/{file}.log
    """
    # Split module name (e.g., 'receipts.preprocess' -> ['receipts', 'preprocess'])
    parts = module_name.split(".")
    domain = parts[0]  # First part is domain (receipts, ledger, time, etc.)
    filename = parts[-1] if len(parts) > 1 else domain  # Last part or domain name

    log_dir = LOGS_ROOT / domain
    return log_dir / f"{filename}.log"
