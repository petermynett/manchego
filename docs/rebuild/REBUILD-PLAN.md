# Manchego Rebuild Plan

## Overview

Complete rebuild of Manchego personal finance system with clean slate approach:
- Fresh git repository (clean history)
- Database-first incremental development
- Direct-to-database workflow (no mandatory Google Sheets staging)
- Modular, extensible architecture
- Robust testing from the start

## Key Design Decisions

1. **Data Flow**: Direct to database → Google Sheets for manual review/correction (not staging requirement)
2. **Database**: Build incrementally with migrations from the start
3. **CLI**: Structured CLI implementation (see `CLI-IMPLEMENTATION.md`)
4. **Testing**: Incremental pytest coverage as each module is built
5. **Dependencies**: Start minimal, add as needed

## Architecture Principles

### Design Principles
- **Modularity**: Each module has single, clear responsibility
- **Extensibility**: Design for future growth (20-30 datasets)
- **Testability**: Everything testable, tests written incrementally
- **Database-first**: Schema drives implementation, not the reverse
- **Transaction integrity**: No partial state on failures

### Development Principles
- **Incremental**: Build one module at a time, test as we go
- **Clean code**: Self-explanatory with good docstrings
- **Rules-driven**: Follow established rules, create new ones as patterns emerge
- **Slow and steady**: No urgency, get it right
- **Build it right**: Extensible architecture over quick hacks


## Implementation Phases

### Phase 0: Foundation Setup

1. **Project and Environment Migration**: 
   - Rename existing `manchego` conda environment to `manchego-v1`
   - Rename existing `manchego` project folder to `manchego-v1`
   - This frees up `manchego` for the new project and environment
2. **Fresh Git Repository**: Create new `manchego` folder with clean history, initial commit structure
3. **Rules Migration**: Bring over all rules, then edit down and reduce as needed (see `RULES-EVALUATION.md`)
4. **Environment Setup**: Conda environment named `manchego` with core dependencies (see `ENVIRONMENT-SETUP.md`)
5. **Directory Structure**: Create skeleton with empty `__init__.py` files

### Phase 1: Database Foundation

1. **Initial Schema**: Minimal starting schema (reference tables only)
2. **Database Module**: Connection management, query patterns
3. **Seed Data**: System-required reference tables (account_types, payment_types, vendor_categories, timeline_sources)
4. **Migration System**: Fresh migrations from the start
5. **Database Tests**: Isolated test databases

### Phase 2: Core Infrastructure

1. **Configuration**: `global_config.py` with paths and settings
2. **Logging System**: Structured JSON logging with operation tracing
3. **Utilities**: ID generation, file operations, error handling
4. **Tests**: Infrastructure tests

### Phase 3: First Dataset (Receipts)

1. **Receipts Module**: Intake → preprocess → parse → import
2. **Receipts CLI**: Commands for receipt pipeline
3. **Full Pipeline**: End-to-end for receipts only
4. **Tests**: Comprehensive receipt module tests

### Phase 4: Additional Datasets

1. **Transactions**: Bank transaction processing
2. **Time Tracking**: Rescuetime, screentime, geofency
3. **Each with**: Module, CLI, tests

### Phase 5: External Integrations

1. **Google Sheets**: For manual review/correction (not staging requirement)
2. **OpenAI**: Receipt parsing (simple now, modular for future OCR improvements)

## CLI Architecture

See `CLI-IMPLEMENTATION.md` for CLI structure and patterns.

## Testing Strategy

- **Incremental**: Write tests as modules are built
- **Isolated**: No real file I/O, no network calls
- **Comprehensive**: High coverage, test patterns from rules
- **Important**: Testing is critical, not optional

## Principles

- Build extensibly from the start (not "make it work first, optimize later")
- Modular, extensible design for future growth
- Database-first approach
- Incremental development with comprehensive testing

## Success Criteria

- Clean architecture with clear module boundaries
- Database-first approach with incremental migrations
- Comprehensive testing written incrementally
- Extensible design for 20-30 datasets
- Well-documented with rules capturing patterns
- Working end-to-end pipeline for at least receipts

## Next Steps

1. **Migrate existing project and environment**:
   - Rename old conda environment: `conda rename -n manchego manchego-v1`
   - Rename old project folder: `mv manchego manchego-v1` (from parent directory)
2. Create new `manchego` project folder
3. Review and evaluate rules (see `RULES-EVALUATION.md`)
4. Set up new environment (see `ENVIRONMENT-SETUP.md`)
5. Create fresh git repository
6. Build database foundation incrementally
7. Implement first dataset end-to-end with tests

