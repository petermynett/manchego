# Architecture Overview

High-level architecture decisions.

## System Boundaries

**Manchego IS:**
- Personal finance and time tracking data management
- CLI tool for data pipeline operations
- Database-first data storage
- Modular, extensible architecture

**Manchego IS NOT:**
- Web application
- API server
- Real-time system

## Core Domains

### Financial Data
- **Receipts**: Image receipt processing → parse → database
- **Transactions**: Bank statement processing → database
- **Ledger**: Matching receipts to transactions

### Time Tracking
- **Rescuetime**: Activity tracking
- **Screentime**: Device usage
- **Geofency**: Location tracking

## Data Flow

Data flows from raw sources through processing into the database. Google Sheets may be used for manual review and correction.

## Module Organization

### Package Structure

```
manchego/
├── cli/              # CLI commands (user interface)
├── database/         # Database connection, queries, loaders
├── receipts/         # Receipt processing module
├── transactions/     # Transaction processing module
├── ledger/           # Receipt-transaction matching
├── time/             # Time tracking modules
├── google/            # Google API integration (Sheets only initially)
├── utils/             # Shared utilities
└── global_config.py   # Configuration
```

### Module Responsibilities

- **CLI modules**: User communication, command parsing, result formatting
- **Business modules**: Core logic, data processing, database operations
- **Utils**: Shared helpers (logging, file ops, IDs)
- **Database**: Data access layer, migrations, loaders

Clear separation: CLI formats output, modules do work.

## Database Design

Database-first approach: schema drives implementation. Design will be determined incrementally during development.

## Testing Structure

Mirrors source structure:
- `tests/receipts/test_*.py`
- `tests/cli/test_*.py`
- `tests/database/test_*.py`
- `tests/conftest.py`: Shared fixtures

All tests:
- Use `tmp_path` for file I/O
- Mock external APIs (Google, OpenAI)
- Isolated, no shared state

## Configuration

### Global Config
- Paths: `data/datasets/{dataset}/{stage}/`
- Database: `db/manchego_{env}.db`
- Logs: `data/logs/{module}/`
- Google Sheets IDs and names
- API keys (from environment)

### Module Configs
Large modules may have their own config:
- `receipts/config.py`: Receipt-specific paths/settings
- `time/config.py`: Time tracking settings

## Key Design Decisions

1. **Database-first**: Schema drives implementation
2. **Incremental**: Build one dataset at a time
3. **Modular**: Each module is self-contained
4. **Extensible**: Easy to add new datasets
5. **Tested**: Tests written incrementally
6. **Clean separation**: CLI vs business logic

