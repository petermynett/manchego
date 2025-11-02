# Rules Evaluation for Rebuild

**Strategy**: Bring over all rules first, then edit down and reduce as needed during development.

This approach allows us to:
- Keep useful patterns and conventions
- See what we have before deciding what to remove
- Reduce rules incrementally as patterns are refined
- Avoid losing valuable conventions

## High-Priority Rules (Likely Bring Over)

### Database Patterns (500-503 series)
- **500-database-patterns.mdc**: ✅ **Bring Over** - Core database structure
- **501-migration-naming.mdc**: ✅ **Bring Over** - Migration conventions
- **502-schema-conventions.mdc**: ✅ **Bring Over** - Schema design patterns
- **503-db-browser-workflow.mdc**: ✅ **Bring Over** - Database tooling workflow
- **503-seed-data-patterns.mdc**: ✅ **Bring Over** - Seed data organization

### Logging Standards (600-612 series)
- **600-logging-configuration.mdc**: ✅ **Bring Over** - Core logging setup
- **601-log-level-guidelines.mdc**: ✅ **Bring Over** - When to use each level
- **602-module-logging-patterns.mdc**: ✅ **Bring Over** - How modules should log
- **603-cli-audit-trail.mdc**: ✅ **Bring Over** - CLI command logging
- **604-transaction-integrity.mdc**: ✅ **Bring Over** - Rollback patterns
- **605-business-return-structures.mdc**: ✅ **Bring Over** - Consistent return dicts
- **606-performance-logging.mdc**: ⚠️ **Review** - May be overkill initially
- **607-secret-sanitization.mdc**: ✅ **Bring Over** - Security critical
- **609-console-vs-file-logging.mdc**: ✅ **Bring Over** - Output separation
- **610-operation-id-tracing.mdc**: ✅ **Bring Over** - Operation correlation
- **611-log-entry-schema.mdc**: ✅ **Bring Over** - JSON log structure
- **612-cli-command-pattern.mdc**: ✅ **Bring Over** - CLI implementation template

### Testing Standards (700-708 series)
- **700-testing-standards.mdc**: ✅ **Bring Over** - Foundation
- **701-cli-testing.mdc**: ✅ **Bring Over** - CLI test patterns
- **702-test-isolation.mdc**: ✅ **Bring Over** - Critical for good tests
- **703-test-fixture-usage.mdc**: ✅ **Bring Over** - Fixture patterns
- **704-cli-mocking-consistency.mdc**: ✅ **Bring Over** - Mocking targets
- **705-test-data-isolation.mdc**: ✅ **Bring Over** - Data isolation
- **706-autouse-directory-isolation.mdc**: ✅ **Bring Over** - Auto isolation
- **707-testing-module-logging.mdc**: ✅ **Bring Over** - Log mocking
- **708-test-migration-patterns.mdc**: ✅ **Bring Over** - Test updates after refactoring

## Medium-Priority Rules (Review/Adapt)

### Code Quality (100-200 series)
- **100-docstring-standards.mdc**: ✅ **Bring Over** - Documentation standards
- **200-conda-forge-only.mdc**: ✅ **Bring Over** - Dependency management

### CLI & Output (620-622 series)
- **620-cli-output-standards.mdc**: ✅ **Bring Over** - User-friendly output
- **621-error-handling-patterns.mdc**: ✅ **Bring Over** - Error handling
- **622-module-responsibilities.mdc**: ✅ **Bring Over** - CLI vs module separation

### Module Patterns (800 series)
- **800-file-discovery-pattern.mdc**: ✅ **Bring Over** - File discovery standards

## Meta Rules

- **001-meta-rules.mdc**: ✅ **Bring Over** - Rule creation guidelines

## Process

1. **Initial Setup**: Copy all rules from `.cursor/rules/` to new workspace
2. **During Development**: Review and reduce rules as patterns emerge
3. **Edit Down**: Remove rules that don't fit new architecture
4. **Adapt**: Update rules if patterns have changed
5. **Create New**: Add new rules as new patterns emerge

## Priority Rules to Keep

These rules are definitely worth keeping:

- **Database patterns** (500-503 series): Core database structure and conventions
- **Logging standards** (600-612 series): Structured logging is essential
- **Testing standards** (700-708 series): Comprehensive testing is critical
- **CLI patterns** (620-622 series): CLI structure and separation of concerns
- **Module patterns** (800 series): File discovery and module organization
- **Meta rules** (001): Rule creation guidelines

