# CLI Implementation

CLI structure and patterns for manchego.

## Command Structure

### Format
`manchego <dataset>:<verb>`

### Examples
```bash
manchego receipts:process
manchego receipts:parse
manchego receipts:import
manchego transactions:import
manchego stage:all            # Bulk operation across all datasets
```

### Why Colon Separation?

- Clearer visual grouping
- Standard in many CLIs (Heroku, Rails, Laravel)
- Better tab completion
- Less ambiguous in documentation

## File Organization

```
cli/
├── main.py              # Entry point, routing, global commands
├── base.py              # Shared utilities (format, validate, error handling)
├── orchestration.py     # Multi-dataset workflows
├── receipts.py          # Receipt commands
├── transactions.py      # Transaction commands
├── geofency.py          # Geofency commands
├── rescuetime.py        # RescueTime commands
├── screentime.py        # ScreenTime commands
└── database.py          # Database commands
```

## Module Responsibilities

### main.py
- CLI entry point
- Module registration (add_typer for each dataset)
- Global commands (config, validate, bulk operations)

### base.py
- Shared CLI utilities
- Result formatting
- Error handling patterns
- Environment validation

### orchestration.py
- Multi-dataset workflows
- Bulk operations (stage:all, import:all, sync:all)
- Coordinates across modules

### Dataset CLI Files
- One file per dataset/domain
- Commands for that dataset's operations
- User communication (start messages, success/failure)
- Calls business logic from modules

## Separation of Concerns

- **CLI modules**: User communication, command parsing, result formatting
- **Business modules**: Core logic, data processing, database operations
- **Never mix**: No prints in modules, no business logic in CLI

CLI formats output, modules do work.

## Error Handling

- Catch exceptions in CLI
- Log errors with context
- Show user-friendly messages
- Return appropriate exit codes

## Output Standards

- Use emojis for status: 🔄 (starting), ✅ (success), ❌ (failure)
- Human-readable console output
- Structured logs (JSON) to files
- Clear, concise messaging

