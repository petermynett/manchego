# Manchego - Machine-Optimized Technical Reference

**Purpose**: Complete technical reference for AI agents and Cursor working on manchego. Optimized for machine parsing with structured sections, concrete code examples, and exhaustive cross-references.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Module Structure](#module-structure)
- [Key Patterns](#key-patterns)
- [Docstring Examples](#docstring-examples)
- [Configuration](#configuration)
- [Data Directory Structure](#data-directory-structure)
- [Development Workflow](#development-workflow)
- [Command Structure](#command-structure)
- [Rule References](#rule-references)

---

## Architecture Overview

### System Boundaries

**Manchego IS:**
- Personal finance and time tracking data management system
- CLI tool for data pipeline operations
- Data storage (SQLite)
- Modular, extensible architecture for 20-30 datasets

**Manchego IS NOT:**
- Web application
- API server
- Real-time system
- Multi-user system (single-user assumptions)

### Core Domains

#### Financial Data
- **Receipts**: Image receipt processing → parse → database
- **Transactions**: Bank statement processing → database
- **Ledger**: Matching receipts to transactions

#### Time Tracking
- **Rescuetime**: Activity tracking
- **Screentime**: Device usage
- **Geofency**: Location tracking

### Data Flow

```
Raw Sources → Processing Pipeline → Database → Google Sheets (optional review)
```

- Data flows from raw sources through processing stages into the database
- Google Sheets may be used for manual review and correction (not staging requirement)
- Database-first approach: schema drives implementation

### Module Organization Hierarchy

```
manchego/
├── cli/              # CLI commands (user interface layer)
├── database/         # Database connection, queries, loaders (data access layer)
├── receipts/         # Receipt processing module (planned)
├── transactions/     # Transaction processing module (planned)
├── ledger/           # Receipt-transaction matching (planned)
├── time/             # Time tracking modules (planned)
│   ├── rescuetime/
│   ├── screentime/
│   └── geofency/
├── google/           # Google API integration (Sheets only initially, planned)
├── utils/            # Shared utilities (logging, file ops, IDs)
└── global_config.py  # Configuration (paths, settings, API keys)
```

### Module Responsibilities

- **CLI modules**: User communication, command parsing, result formatting
- **Business modules**: Core logic, data processing, database operations
- **Utils**: Shared helpers (logging, file ops, IDs)
- **Database**: Data access layer, migrations, loaders

**Clear separation**: CLI formats output, modules do work. See [Rule 622: Module Responsibilities](.cursor/rules/622-module-responsibilities.mdc).

### Current Implementation Status

**Implemented:**
- `manchego/cli/main.py`: Basic CLI entry point with typer
- `manchego/global_config.py`: Configuration module (empty, ready for setup)
- `manchego/ledger/`: Module directory (empty, planned)
- `manchego/utils/`: Utilities directory (empty, planned)
- Project structure: `data/`, `db/`, `sql/`, `tests/` directories
- Environment setup: `env/environment.yml` with conda dependencies

**Planned:**
- Database module with connection management
- Receipts processing pipeline
- Transactions processing pipeline
- Time tracking modules (RescueTime, ScreenTime, Geofency)
- Google Sheets integration
- Comprehensive test suite

---

## Module Structure

### Complete Directory Tree

```
manchego/
├── __init__.py                    # Package initialization
├── global_config.py               # Global configuration (paths, settings)
├── cli/
│   ├── __init__.py
│   └── main.py                    # CLI entry point, command routing
├── database/                      # Database module (planned)
│   ├── __init__.py
│   ├── connection.py              # Database connection management
│   ├── queries.py                 # Query execution helpers
│   └── loaders/                   # Data loaders per dataset
├── receipts/                      # Receipt processing (planned)
│   ├── __init__.py
│   ├── intake.py                  # File discovery
│   ├── preprocess.py              # Image normalization
│   └── parse_gpt.py               # GPT-based parsing
├── transactions/                  # Transaction processing (planned)
│   └── __init__.py
├── ledger/                        # Receipt-transaction matching (planned)
│   └── __init__.py
├── time/                          # Time tracking modules (planned)
│   ├── __init__.py
│   ├── rescuetime/
│   ├── screentime/
│   └── geofency/
├── google/                        # Google API integration (planned)
│   ├── __init__.py
│   └── sheets.py
└── utils/                         # Shared utilities (planned)
    ├── __init__.py
    ├── logging_config.py          # Logger setup
    ├── logging_helpers.py         # Operation ID, log helpers
    ├── cli_audit.py               # CLI audit logging
    └── file_ops.py                # File operations
```

### Per-Module Breakdown

#### CLI Module (`manchego/cli/`)

**Purpose**: User interface layer for all commands.

**Key Files:**
- `main.py`: Entry point, command registration, global commands

**Responsibilities:**
- Parse command-line arguments
- Format user-friendly output (with emojis: 🔄, ✅, ❌)
- Catch exceptions and show user-friendly error messages
- Log command invocations for audit trail
- Call business logic from modules (never implement business logic)

**See Also:**
- [Rule 612: CLI Command Pattern](.cursor/rules/612-cli-command-pattern.mdc)
- [Rule 620: CLI Output Standards](.cursor/rules/620-cli-output-standards.mdc)
- [Rule 622: Module Responsibilities](.cursor/rules/622-module-responsibilities.mdc)
- [docs/rebuild/CLI-IMPLEMENTATION.md](docs/rebuild/CLI-IMPLEMENTATION.md)

#### Database Module (`manchego/database/`) - Planned

**Purpose**: Data access layer for database operations.

**Key Responsibilities:**
- Connection management with context managers
- Query execution with parameterized queries
- Migration runner integration
- Data loaders for each dataset
- NO CLI output (raise errors, return results)

**See Also:**
- [Rule 500: Database Patterns](.cursor/rules/500-database-patterns.mdc)
- [Rule 502: Schema Conventions](.cursor/rules/502-schema-conventions.mdc)

#### Utils Module (`manchego/utils/`) - Planned

**Purpose**: Shared utilities used across modules.

**Key Files:**
- `logging_config.py`: Logger setup with JSON formatting
- `logging_helpers.py`: Operation ID generation, log helpers
- `cli_audit.py`: CLI command audit logging
- `file_ops.py`: File operations helpers

**See Also:**
- [Rule 600: Logging Configuration](.cursor/rules/600-logging-configuration.mdc)
- [Rule 610: Operation ID Tracing](.cursor/rules/610-operation-id-tracing.mdc)

#### Global Config (`manchego/global_config.py`)

**Purpose**: Centralized configuration for paths, settings, API keys.

**Current Status**: Empty, ready for implementation.

**Expected Structure:**
- Dataset paths: `data/datasets/{dataset}/{stage}/`
- Database paths: `db/manchego_{env}.db`
- Log paths: `data/logs/{module}/`
- Google Sheets IDs and names
- API keys (from environment variables)

---

## Key Patterns

### CLI Command Pattern

Every CLI command must follow this exact pattern. See [Rule 612: CLI Command Pattern](.cursor/rules/612-cli-command-pattern.mdc) for complete details.

```python
import time
from typing import Annotated

import typer

from manchego.cli.base import format_result
from manchego.utils.cli_audit import log_command_end, log_command_start
from manchego.utils.logging_helpers import generate_operation_id

@app.command("operation")
def operation_cmd(
    arg1: Annotated[type, typer.Option(help="Description")] = default,
    dry_run: Annotated[bool, typer.Option(help="Preview without executing")] = False,
):
    """Description of what this command does."""
    # 1. Generate operation_id (ALWAYS at CLI entry point)
    operation_id = generate_operation_id("dataset_operation")
    t0 = time.time()
    
    # 2. Log command start (for audit trail)
    log_command_start("dataset:operation", {
        "arg1": arg1,
        "dry_run": dry_run
    }, operation_id)
    
    # 3. Handle dry-run mode if supported
    if dry_run:
        typer.echo("🔍 Dry-run: Previewing operation...")
        result = {"success": True, "dry_run": True}
        log_command_end("dataset:operation", operation_id, result, time.time() - t0)
        return
    
    # 4. User-friendly console output
    typer.echo("🔄 Starting operation...")
    
    try:
        # 5. Call business function with operation_id
        result = business_function(arg1, operation_id=operation_id)
        
        # 6. Log command end (success)
        log_command_end("dataset:operation", operation_id, result, time.time() - t0)
        
        # 7. Format and display result for user
        format_result(result, "Operation name")
        
    except Exception as e:
        # 8. Log command end (failure)
        log_command_end("dataset:operation", operation_id, {
            "success": False,
            "error": str(e)
        }, time.time() - t0)
        
        # 9. User-friendly error message
        typer.echo(f"❌ Operation failed: {e}", err=True)
        raise typer.Exit(1) from e
```

**Key Components:**
1. **Operation ID**: Always generate at CLI entry point
2. **Timing**: Capture start time, calculate elapsed at end
3. **Audit Logging**: Log command start/end for audit trail
4. **Error Handling**: Always log command end, even on error
5. **User Output**: Friendly console messages with emojis

### Logging Patterns

#### Logger Setup

All modules must use `setup_logger()` for JSON-formatted logs:

```python
from manchego.utils.logging_config import setup_logger

logger = setup_logger(__name__, log_subdir="receipts")
```

Logs written to: `data/logs/{log_subdir}/{module}.log` in JSON format.

**See Also:** [Rule 600: Logging Configuration](.cursor/rules/600-logging-configuration.mdc)

#### Operation ID Tracing

Every operation generates a unique operation_id that appears in all related logs:

```python
from manchego.utils.logging_helpers import generate_operation_id

# Generate at CLI entry point (always)
operation_id = generate_operation_id("process_files")
# Returns: "process_files_20251011_182001_a3d5e8f4"

# Pass to all business functions
def process_files(operation_id: str | None = None) -> dict:
    if operation_id is None:
        operation_id = generate_operation_id("process_files")
    
    logger.info("Starting operation", extra={
        "operation_id": operation_id,
        "data": {"limit": 50}
    })
```

**Format**: `{operation_name}_{YYYYMMDD}_{HHMMSS}_{short_uuid}`

**See Also:** [Rule 610: Operation ID Tracing](.cursor/rules/610-operation-id-tracing.mdc)

#### Module Logging Pattern

Every batch operation should follow this lifecycle:

```python
from manchego.utils.logging_helpers import (
    generate_operation_id,
    log_operation_start,
    log_file_success,
    log_file_failure,
    log_operation_summary
)

def process_all_files() -> dict:
    """Process all files in the input directory."""
    operation_id = generate_operation_id("process_files")
    
    # 1. Log operation start
    log_operation_start(logger, "process_files", operation_id, 
                       limit=None, recurse=False)
    
    results = {"succeeded": [], "failed": []}
    
    for file in files:
        try:
            result = process_file(file, operation_id)
            # 2. Log per-file success
            log_file_success(logger, file.name, operation_id,
                           rows=result['rows'], hash=result['hash'])
            results["succeeded"].append(result)
        except Exception as e:
            # 3. Log per-file failure
            log_file_failure(logger, file.name, operation_id, e,
                           file_path=str(file), file_size=file.stat().st_size)
            results["failed"].append({"item": file.name, "reason": str(e)})
    
    # 4. Log operation summary
    summary = {
        "success": len(results["failed"]) == 0,
        "total": len(files),
        "succeeded": len(results["succeeded"]),
        "failed": len(results["failed"]),
        "failures": results["failed"]
    }
    log_operation_summary(logger, "process_files", operation_id, summary)
    
    return summary
```

**See Also:** [Rule 602: Module Logging Patterns](.cursor/rules/602-module-logging-patterns.mdc)

### Database Patterns

#### Connection Management

Always use context managers for database connections:

```python
from manchego.database import DatabaseConnection

with DatabaseConnection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vendors WHERE name = ?", (vendor_name,))
    results = cursor.fetchall()
# Auto-commits on success, rolls back on exception
```

**See Also:** [Rule 500: Database Patterns](.cursor/rules/500-database-patterns.mdc)

#### Parameterized Queries

Always use parameterized queries for values (never string interpolation):

```python
# ✅ Correct
cursor.execute(
    "SELECT * FROM vendors WHERE name = ?",
    (vendor_name,)
)

# ❌ Wrong - SQL injection vulnerability
cursor.execute(f"SELECT * FROM vendors WHERE name = '{vendor_name}'")
```

**See Also:** [Rule 500: Database Patterns](.cursor/rules/500-database-patterns.mdc)

#### Schema Conventions

- **Table names**: lowercase with underscores, plural for entities (`vendors`, `receipts`)
- **Column names**: lowercase with underscores (`transaction_date`, `vendor_id`)
- **Primary keys**: UUID (TEXT) for entities, natural keys for housekeeping
- **Foreign keys**: `{table}_id` pattern, always enable foreign keys
- **Timestamps**: `created_at`, `updated_at` (TEXT, ISO 8601 UTC)
- **Money**: REAL type, positive = income, negative = expenses

**See Also:** [Rule 502: Schema Conventions](.cursor/rules/502-schema-conventions.mdc)

### Module Responsibilities Separation

**CLI modules**: User communication, command parsing, result formatting. Never implement business logic.

**Business modules**: Core logic, data processing, database operations. Never print to console.

```python
# ✅ Correct separation
def preprocess_all(operation_id: str | None = None):
    """Business logic - no prints."""
    if operation_id is None:
        operation_id = generate_operation_id("preprocess_receipts")
    
    log_operation_summary(logger, "preprocess_receipts", operation_id, stats)
    return stats  # Return structured data

def cli_preprocess():
    """CLI layer - user communication."""
    try:
        typer.echo("🔄 Starting preprocessing...")  # User communication
        stats = preprocess_all()
        if stats['created'] > 0:
            typer.echo(f"✅ Created {stats['created']} processed receipts")
    except Exception as e:
        typer.echo(f"❌ Failed: {e}", err=True)
        raise typer.Exit(1)
```

**See Also:** [Rule 622: Module Responsibilities](.cursor/rules/622-module-responsibilities.mdc)

### Return Structures

All business functions must return consistent dict structures:

```python
# Batch operations
{
    "success": bool,           # Overall success (all items succeeded)
    "total": int,              # Total items processed
    "succeeded": int,          # Successfully processed items
    "failed": int,             # Failed items
    "skipped": int,            # Skipped items (optional)
    "elapsed_s": float,        # Time taken (optional)
    "failures": [              # Details of failures (optional)
        {"item": str, "reason": str}
    ]
}

# Single operations
{
    "success": bool,
    "item": str,               # What was processed
    "result": Any,             # Operation result (optional)
    "error": str               # Error message if success=False (optional)
}
```

**Example:**

```python
def process_files(limit: int = None) -> dict:
    """Process files from input directory."""
    results = {"succeeded": [], "failed": []}
    start = time.time()
    
    for file in get_files(limit):
        try:
            process_single_file(file)
            results["succeeded"].append(file.name)
        except Exception as e:
            results["failed"].append({"item": file.name, "reason": str(e)})
    
    return {
        "success": len(results["failed"]) == 0,
        "total": len(results["succeeded"]) + len(results["failed"]),
        "succeeded": len(results["succeeded"]),
        "failed": len(results["failed"]),
        "elapsed_s": time.time() - start,
        "failures": results["failed"] if results["failed"] else []
    }
```

**See Also:** [Rule 605: Business Return Structures](.cursor/rules/605-business-return-structures.mdc)

### Testing Patterns

#### Test Structure

Tests mirror source structure:
- `tests/receipts/test_*.py` for receipt module tests
- `tests/cli/test_*.py` for CLI tests
- `tests/database/test_*.py` for database tests
- `tests/conftest.py`: Shared fixtures

#### Isolation Requirements

- Use `tmp_path` for ALL file I/O; never touch project data directories
- Mock external APIs (Google, OpenAI) with fixtures
- No real network calls
- No writes outside `tmp_path`

**Example:**

```python
def test_discover_filters_hidden_files(tmp_path, touch):
    """Test file discovery excludes hidden files."""
    touch(tmp_path / "visible.jpg")
    touch(tmp_path / ".hidden.jpg")
    
    paths = intake.discover_receipt_paths(root=tmp_path)
    
    assert len(paths) == 1
    assert paths[0].name == "visible.jpg"
```

**See Also:** [Rule 700: Testing Standards](.cursor/rules/700-testing-standards.mdc)

#### Directory Isolation Pattern

Use autouse fixtures to redirect module directories:

```python
@pytest.fixture(autouse=True)
def _redirect_module_dirs(tmp_path, monkeypatch):
    """Redirect all module directories to tmp_path."""
    from manchego import global_config
    
    raw_dir = tmp_path / "module" / "raw"
    staged_dir = tmp_path / "module" / "staged"
    
    raw_dir.mkdir(parents=True, exist_ok=True)
    staged_dir.mkdir(parents=True, exist_ok=True)
    
    monkeypatch.setattr(global_config, "MODULE_RAW_DIR", raw_dir)
    monkeypatch.setattr(target_module, "MODULE_STAGED_DIR", staged_dir)
```

**See Also:** [Rule 706: Autouse Directory Isolation](.cursor/rules/706-autouse-directory-isolation.mdc)

### File Discovery Pattern

Data pipeline modules should use standardized file discovery functions:

```python
# ============================================================================
# FILE DISCOVERY
# ============================================================================

def get_raw_geofency_files() -> list[Path]:
    """
    Find Geofency CSV files in raw directory.

    Returns:
        list[Path]: List of Geofency CSV files.
    """
    return list(GEOFENCY_RAW_DIR.glob("*.csv"))
```

**See Also:** [Rule 800: File Discovery Pattern](.cursor/rules/800-file-discovery-pattern.mdc)

---

## Docstring Examples

Use **Google-style docstrings** for all Python code. Keep documentation direct, functional, and minimal.

### Public Functions and Classes

Always include full docstrings with summary, parameters, return values, and raised exceptions:

```python
def process_files(limit: int | None = None, operation_id: str | None = None) -> dict:
    """
    Process files from input directory.
    
    Args:
        limit: Maximum number of files to process (None = all)
        operation_id: Operation ID for log tracing (auto-generated if None)
    
    Returns:
        dict: Operation results with counts and timing:
            - success (bool): Overall success
            - total (int): Total items processed
            - succeeded (int): Successfully processed items
            - failed (int): Failed items
            - failures (list): List of failure details
    
    Raises:
        ValueError: If limit is negative
        FileNotFoundError: If input directory does not exist
    """
```

### Private Functions and Methods

Use short 1-2 line docstrings summarizing purpose, inputs, and outputs:

```python
def _normalize_vendor(name: str) -> str:
    """Clean and normalize vendor names for consistency."""
```

### Classes

Document class purpose and attributes:

```python
class Receipt:
    """Represents a parsed receipt with vendor and total.
    
    Attributes:
        vendor (str): The vendor name.
        total (float): The total amount.
        items (list[dict]): List of receipt items.
    """
    
    def __init__(self, vendor: str, total: float) -> None:
        self.vendor = vendor
        self.total = total
        self.items = []
```

### Modules

Always include module-level docstring at the top:

```python
"""
Module for parsing receipts into structured records.

Handles reading processed receipt images, running parsing logic,
and writing structured outputs to Google Sheets.
"""
```

### Config Files

Add module docstring describing what the config contains:

```python
"""
Global configuration for manchego paths and settings.

Defines dataset paths, database paths, log paths, and API configuration.
All paths use Path objects from pathlib.
"""
```

**See Also:** [Rule 100: Docstring Standards](.cursor/rules/100-docstring-standards.mdc)

---

## Configuration

### Global Config Paths

Expected paths in `manchego/global_config.py`:

```python
# Dataset paths
DATA_ROOT = Path("data")
DATASETS_ROOT = DATA_ROOT / "datasets"
RAW_DIR = DATASETS_ROOT / "{dataset}" / "raw"
STAGED_DIR = DATASETS_ROOT / "{dataset}" / "staged"

# Database paths
DB_ROOT = Path("db")
DATABASE_PATH = DB_ROOT / "manchego_{env}.db"  # env: dev, stage, prod

# Log paths
LOGS_ROOT = DATA_ROOT / "logs"
LOG_DIR = LOGS_ROOT / "{module}"
```

### Environment Variables

- `MANCHEGO_ENV`: Database environment (`dev`, `stage`, `prod`, defaults to `dev`)
- `OPENAI_API_KEY`: OpenAI API key for receipt parsing
- `GOOGLE_CREDENTIALS_PATH`: Path to Google service account credentials

### Database Configuration

Database path depends on `MANCHEGO_ENV`:
- `dev`: `db/manchego_dev.db`
- `stage`: `db/manchego_stage.db`
- `prod`: `db/manchego_prod.db`

**See Also:** [Rule 500: Database Patterns](.cursor/rules/500-database-patterns.mdc)

---

## Data Directory Structure

### Complete Tree

```
data/
├── datasets/                    # Dataset-specific data
│   ├── receipts/
│   │   ├── raw/                 # Raw receipt images
│   │   └── staged/              # Processed/normalized receipts
│   ├── transactions/
│   │   ├── raw/                 # Raw transaction files
│   │   └── staged/              # Processed transactions
│   ├── rescuetime/
│   │   ├── raw/                 # Raw RescueTime exports
│   │   └── staged/              # Processed data
│   ├── screentime/
│   │   ├── raw/                 # Raw ScreenTime exports
│   │   └── staged/              # Processed data
│   └── geofency/
│       ├── raw/                 # Raw Geofency CSV files
│       └── staged/              # Processed location data
└── logs/                        # JSON-formatted logs
    ├── cli/
    │   └── commands.log         # CLI audit trail
    ├── receipts/
    │   ├── preprocess.log
    │   ├── parse_gpt.log
    │   └── stage.log
    ├── ledger/
    │   └── stage_statements.log
    ├── time/
    │   ├── geofency.log
    │   ├── rescuetime.log
    │   └── screentime.log
    └── database/
        └── loaders/
            ├── receipts.log
            └── transactions.log
```

### Database Directory Structure

```
db/
├── manchego_dev.db              # Development database
├── manchego_stage.db            # Staging database (if exists)
├── manchego_prod.db             # Production database (if exists)
├── migrations/                  # Versioned schema changes
│   └── YYYYMMDDHHMM_description.sql
└── snapshots/                   # Compressed database backups
    └── YYYYMMDDHHMM_manchego_{env}.db.gz
```

### SQL Directory Structure

```
sql/
├── schema.sql                   # Baseline schema snapshot
├── queries/                     # Complex analytical queries
│   ├── monthly_spending.sql
│   └── vendor_summary.sql
└── views/                       # View definitions
    └── receipt_summary.sql
```

**See Also:** [Rule 500: Database Patterns](.cursor/rules/500-database-patterns.mdc)

---

## Development Workflow

### Package Installation

**Always use conda-forge (mamba preferred):**

```bash
# Step 1: Test first (mandatory dry-run)
mamba install -c conda-forge --dry-run pandas numpy

# Step 2: If dry-run succeeds, install
mamba install -c conda-forge pandas numpy
```

**Never use pip** unless explicitly approved after conda-forge fails.

**See Also:** [Rule 200: Conda-Forge Only](.cursor/rules/200-conda-forge-only.mdc)

### Testing Workflow

Run tests with pytest:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/receipts/test_preprocess.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=manchego
```

**Test Requirements:**
- All tests use `tmp_path` for file I/O
- Mock external APIs (Google, OpenAI)
- No real network calls
- No writes outside `tmp_path`

**See Also:** [Rule 700: Testing Standards](.cursor/rules/700-testing-standards.mdc)

### Migration Workflow

#### Creating Migrations

1. Generate timestamp: `date +"%Y%m%d%H%M"`
2. Create file: `db/migrations/{timestamp}_{description}.sql`
3. Write SQL changes in UP section
4. Document rollback in DOWN section (commented)

**Migration naming format:** `YYYYMMDDHHMM_description.sql`

**Example:** `202501031430_add_receipts_table.sql`

#### Applying Migrations

```bash
# Manual application (current)
sqlite3 db/manchego_dev.db < db/migrations/202501031430_add_receipts_table.sql
```

#### After Migration

1. Update `sql/schema.sql` to reflect current state
2. Commit both migration file and updated schema
3. Document any manual steps required

**See Also:** [Rule 501: Migration Naming](.cursor/rules/501-migration-naming.mdc)

### Rule Creation Workflow

When creating new rules, follow the meta-rule pattern:

**File naming:** `[###]-[rule-name].mdc` with 3-digit prefix

**Numbering convention:**
- 0XX: Meta rules
- 1XX: Code documentation and style
- 2XX: Package management
- 5XX: Database conventions
- 6XX: Logging, console output, error handling
- 7XX: Testing conventions
- 8XX: Module organization patterns

**See Also:** [Rule 001: Meta Rules](.cursor/rules/001-meta-rules.mdc)

---

## Command Structure

### Format

```
manchego <dataset>:<verb>
```

### Examples

```bash
manchego receipts:process          # Process raw receipt images
manchego receipts:parse            # Parse processed receipts
manchego receipts:import           # Import parsed receipts to database
manchego transactions:import       # Import transactions to database
manchego stage:all                 # Bulk operation across all datasets
```

### Why Colon Separation?

- Clearer visual grouping
- Standard in many CLIs (Heroku, Rails, Laravel)
- Better tab completion
- Less ambiguous in documentation

**See Also:** [docs/rebuild/CLI-IMPLEMENTATION.md](docs/rebuild/CLI-IMPLEMENTATION.md)

---

## Rule References

### Meta Rules (0XX)

- **[001-meta-rules.mdc](.cursor/rules/001-meta-rules.mdc)**: Rule creation guidelines and structure

### Code Documentation and Style (1XX)

- **[100-docstring-standards.mdc](.cursor/rules/100-docstring-standards.mdc)**: Docstring and documentation standards for Python code

### Package Management (2XX)

- **[200-conda-forge-only.mdc](.cursor/rules/200-conda-forge-only.mdc)**: Mamba/Conda-Forge package installation with mandatory dry-run validation

### Database Conventions (5XX)

- **[500-database-patterns.mdc](.cursor/rules/500-database-patterns.mdc)**: Database directory structure, responsibilities, and core patterns
- **[501-migration-naming.mdc](.cursor/rules/501-migration-naming.mdc)**: Migration file naming conventions and workflow
- **[502-schema-conventions.mdc](.cursor/rules/502-schema-conventions.mdc)**: Schema design conventions for table structure, naming, data types, and constraints
- **[503-db-browser-workflow.mdc](.cursor/rules/503-db-browser-workflow.mdc)**: DB Browser for SQLite workflow patterns
- **[503-seed-data-patterns.mdc](.cursor/rules/503-seed-data-patterns.mdc)**: Patterns for seed data that populates reference tables

### Logging, Console Output, and Error Handling (6XX)

- **[600-logging-configuration.mdc](.cursor/rules/600-logging-configuration.mdc)**: Centralized logging configuration with JSON format and operation tracing
- **[601-log-level-guidelines.mdc](.cursor/rules/601-log-level-guidelines.mdc)**: Clear guidelines for when to use DEBUG, INFO, WARNING, and ERROR log levels
- **[602-module-logging-patterns.mdc](.cursor/rules/602-module-logging-patterns.mdc)**: Standardized logging patterns for module-level functions with operation tracing
- **[603-cli-audit-trail.mdc](.cursor/rules/603-cli-audit-trail.mdc)**: Audit logging for all CLI command invocations with arguments and results
- **[604-transaction-integrity.mdc](.cursor/rules/604-transaction-integrity.mdc)**: Rollback patterns ensuring failed operations leave no partial state
- **[605-business-return-structures.mdc](.cursor/rules/605-business-return-structures.mdc)**: Standardized return structures for business functions
- **[606-performance-logging.mdc](.cursor/rules/606-performance-logging.mdc)**: Performance metrics logging to identify bottlenecks
- **[607-secret-sanitization.mdc](.cursor/rules/607-secret-sanitization.mdc)**: Prevent logging of sensitive information like API keys, passwords, and tokens
- **[609-console-vs-file-logging.mdc](.cursor/rules/609-console-vs-file-logging.mdc)**: Clear separation between file logs (JSON, machine-readable) and console output (text, human-readable)
- **[610-operation-id-tracing.mdc](.cursor/rules/610-operation-id-tracing.mdc)**: Operation ID generation and propagation for tracing all logs related to a single operation
- **[611-log-entry-schema.mdc](.cursor/rules/611-log-entry-schema.mdc)**: Standard JSON schema for all log entries ensuring consistent machine-readable format
- **[612-cli-command-pattern.mdc](.cursor/rules/612-cli-command-pattern.mdc)**: Complete template pattern for CLI commands with audit logging and operation tracing
- **[620-cli-output-standards.mdc](.cursor/rules/620-cli-output-standards.mdc)**: User-friendly console output patterns for CLI commands
- **[621-error-handling-patterns.mdc](.cursor/rules/621-error-handling-patterns.mdc)**: Consistent error handling patterns across modules
- **[622-module-responsibilities.mdc](.cursor/rules/622-module-responsibilities.mdc)**: Clear separation of responsibilities between CLI and module-level functions

### Testing Conventions (7XX)

- **[700-testing-standards.mdc](.cursor/rules/700-testing-standards.mdc)**: Testing conventions for pytest-based tests
- **[701-cli-testing.mdc](.cursor/rules/701-cli-testing.mdc)**: CLI testing patterns focusing on command parsing and user output validation
- **[702-test-isolation.mdc](.cursor/rules/702-test-isolation.mdc)**: Test isolation and mocking patterns for external dependencies
- **[703-test-fixture-usage.mdc](.cursor/rules/703-test-fixture-usage.mdc)**: Mandatory test fixture usage patterns
- **[704-cli-mocking-consistency.mdc](.cursor/rules/704-cli-mocking-consistency.mdc)**: Consistent mocking targets for CLI tests
- **[705-test-data-isolation.mdc](.cursor/rules/705-test-data-isolation.mdc)**: Data isolation patterns to prevent tests from affecting real data
- **[706-autouse-directory-isolation.mdc](.cursor/rules/706-autouse-directory-isolation.mdc)**: Autouse fixture pattern for test data directory isolation
- **[707-testing-module-logging.mdc](.cursor/rules/707-testing-module-logging.mdc)**: Patterns for mocking logs in tests
- **[708-test-migration-patterns.mdc](.cursor/rules/708-test-migration-patterns.mdc)**: Systematic patterns for updating tests after refactoring code

### Module Organization Patterns (8XX)

- **[800-file-discovery-pattern.mdc](.cursor/rules/800-file-discovery-pattern.mdc)**: Standard pattern for file discovery functions in data pipeline modules

---

## Additional Documentation

- **[docs/rebuild/ARCHITECTURE-OVERVIEW.md](docs/rebuild/ARCHITECTURE-OVERVIEW.md)**: Detailed architecture decisions
- **[docs/rebuild/CLI-IMPLEMENTATION.md](docs/rebuild/CLI-IMPLEMENTATION.md)**: CLI structure and patterns
- **[docs/rebuild/ENVIRONMENT-SETUP.md](docs/rebuild/ENVIRONMENT-SETUP.md)**: Environment setup instructions
- **[docs/rebuild/REBUILD-PLAN.md](docs/rebuild/REBUILD-PLAN.md)**: Rebuild plan and phases
- **[docs/rebuild/RULES-EVALUATION.md](docs/rebuild/RULES-EVALUATION.md)**: Rules evaluation strategy

---

**Last Updated**: 2025-01-11  
**Project Version**: 0.1.0  
**Python Version**: >=3.12

