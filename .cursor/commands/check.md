---
description: Run code quality checks (ruff check --fix, ruff format, pytest) with auto-fix and comprehensive summary
---

# Check Workflow

Run code quality checks with auto-fix capabilities. Runs ruff check --fix, ruff format, and pytest sequentially, fixes issues automatically, and provides a comprehensive summary.

**Output Mode**: All intermediate commands run silently. Only final summary or errors are displayed to reduce noise.

## Phase 1: Pre-flight Checks

Run these checks **in order** silently, only outputting warnings (don't block):

### Check 1: Git Working Directory Status
```bash
git status --porcelain 2>/dev/null
```
- Capture output silently
- If dirty: **WARN** - "⚠️ Working directory has uncommitted changes. Proceeding with checks."
- Continue (warning only, don't block)

### Check 2: Remote Sync Status
```bash
git fetch >/dev/null 2>&1
git status --porcelain 2>/dev/null
```
- Capture status output silently, check if behind remote
- If behind remote: **WARN** - "⚠️ Behind remote. Consider pulling before checks."
- Continue (warning only, don't block)

## Phase 2: Ruff Check --fix

Run ruff check with auto-fix, capture output silently:

```bash
ruff check --fix >/dev/null 2>&1
```

**Capture output internally:**
- Parse output to count:
  - Issues fixed (lines like "Found X issues, fixed Y")
  - Issues remaining (unfixable errors)
  - File paths and line numbers for remaining issues
- Store results for summary

**Exit code handling:**
- Ruff may exit non-zero if unfixable issues exist
- Continue regardless (don't stop workflow)
- Capture exit code for final summary

## Phase 3: Ruff Format

Run ruff format, capture output silently:

```bash
ruff format >/dev/null 2>&1
```

**Capture output internally:**
- Parse output to count:
  - Files reformatted (lines like "X files reformatted")
  - Files unchanged (if any)
- Store results for summary

**Exit code handling:**
- Ruff format typically exits 0
- Continue regardless (don't stop workflow)
- Capture exit code for final summary

## Phase 4: Pytest

Run pytest silently (always run, no override mechanism):

```bash
pytest >/dev/null 2>&1
```

**Capture output internally:**
- Parse pytest output to extract:
  - Total tests passed/failed
  - Test failure details (file::test_name - error type)
  - Coverage percentage (if available)
  - Coverage gap vs target (80% from pyproject.toml)
- Store results for summary

**Exit code handling:**
- Pytest will exit non-zero if tests fail
- Continue regardless (don't stop workflow)
- Capture exit code for final summary

## Phase 5: Generate Summary

### Determine Overall Status

Check all exit codes and results:
- **All pass**: All checks passed, no issues found
- **All fixed**: Issues found but all auto-fixed, checks now pass
- **Partial failure**: Some checks failed, some passed
- **All failed**: All checks failed

### Summary Format

**Success (All Pass):**
```
✓ All checks passed

Ruff check: 0 issues
Ruff format: 0 files changed
Pytest: 15 passed, 80% coverage
```

**Success (All Fixed):**
```
✓ All checks passed (3 issues auto-fixed)

Ruff check: 3 issues fixed, 0 remain
Ruff format: 2 files reformatted
Pytest: 15 passed, 80% coverage
```

**Failure (Partial):**
```
✗ 2 checks failed

Ruff check: 3 issues fixed, 2 remain (unfixable)
  - manchego/cli/main.py:45:15 - E501 line too long (89 > 88 characters)
  - manchego/utils/helpers.py:12:8 - F821 undefined name 'foo'

Ruff format: 5 files reformatted

Pytest: 12 passed, 3 failed
  - tests/test_parsing.py::test_extract_data - AssertionError: Expected 'foo', got 'bar'
  - tests/test_cli.py::test_command_help - TypeError: NoneType object is not callable
  Coverage: 75% (target: 80%)
```

**Failure (All Failed):**
```
✗ All checks failed

Ruff check: 0 issues fixed, 5 remain (unfixable)
  - manchego/cli/main.py:45:15 - E501 line too long
  - manchego/utils/helpers.py:12:8 - F821 undefined name 'foo'
  - manchego/ledger/processor.py:23:4 - B006 mutable default argument

Ruff format: 0 files reformatted

Pytest: 0 passed, 15 failed
  - [list all test failures]
  Coverage: 45% (target: 80%)
```

### Summary Details

**For Success:**
- Minimal detail: Summary line + counts for each check
- No file-by-file breakdown
- Show coverage if available

**For Failure:**
- Detailed breakdown by check type
- List all unfixable ruff issues with file:line:code and description
- List all pytest failures with test name and error type
- Show coverage gap vs target
- Include file counts for formatting

## Phase 6: Exit Code

Determine final exit code based on results:

- **Exit 0**: All checks passed (either initially or after auto-fix)
- **Exit 1**: One or more checks failed (unfixable issues or test failures)

**Logic:**
- If ruff check has unfixable issues → exit 1
- If pytest has failures → exit 1
- If ruff format fails (rare) → exit 1
- Only exit 0 if all checks pass

## Error Handling

- **Ruff check failures**: Capture unfixable issues, continue to next check
- **Ruff format failures**: Capture error, continue to pytest
- **Pytest failures**: Capture test failures, continue to summary
- **Command not found**: Show clear error "ruff/pytest not found. Install dependencies first."
- **Parse errors**: If output parsing fails, show raw output for that check

## Key Principles

1. **Auto-fix first**: Fix everything that can be fixed automatically
2. **Continue on failure**: Never stop workflow, report all failures at end
3. **Quiet mode**: Suppress all intermediate output, only show final summary
4. **Detailed failures**: Provide actionable information for unfixable issues
5. **Distinguish fixed vs failed**: Clear indication of what was fixed vs what remains
6. **Always run pytest**: No override mechanism, always execute pytest
7. **Exit codes**: Exit 0 only if all checks pass, non-zero otherwise
8. **Minimal pre-flight**: Warn about git state but don't block execution

