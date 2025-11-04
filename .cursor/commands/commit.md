---
description: AI-optimized git commit workflow with adaptive detail based on change complexity
---

# Commit Workflow

AI-optimized commit workflow with adaptive detail based on change complexity. Human-readable first line, rest optimized for AI review.

**Output Mode**: All intermediate git commands run silently. Only final summary or errors are displayed to reduce noise.

## Adaptive Strategy

- **Small changes** (1-3 files, trivial/simple): Brief commit (50-100 words)
- **Medium changes** (4-10 files, moderate complexity): Moderate commit (100-200 words)
- **Large changes** (10+ files, complex features): Detailed commit (200-400 words)
- **Trivial changes** (docs, formatting only): Auto-brief, skip detailed analysis

## Phase 1: Safety Checks

Run these checks **in order** silently, only outputting warnings/errors:

### Check 1: Uncommitted Changes
```bash
git status --porcelain 2>/dev/null
```
- If output is empty: "No changes to commit. Working directory is clean." (exit gracefully)
- If changes exist: Continue silently to next check

### Check 2: Remote Sync Status
```bash
git fetch >/dev/null 2>&1
git status --porcelain 2>/dev/null
```
- Capture status output, check if behind remote
- If behind remote: **BLOCK** - "⚠️ Behind remote. Pull first with `git pull`"
- Wait for user instruction before proceeding
- Otherwise: Continue silently

### Check 3: Merge Conflicts
```bash
git diff --name-only --diff-filter=U 2>/dev/null
```
- If conflicts exist: **BLOCK** - "⚠️ Unresolved merge conflicts. Resolve first."
- Wait for user instruction before proceeding
- Otherwise: Continue silently

### Check 4: Secret Files Detection (Warning Only)
```bash
git status --porcelain | grep -E '\.(env|key|credentials|secret|token)' 2>/dev/null || true
```
- Capture output silently
- If found: **WARN** - "⚠️ Potential secrets detected: [list files]. Confirm these are safe?"
- Wait for confirmation, then proceed
- Otherwise: Continue silently

### Check 5: Large Changeset (Info Only)
```bash
git status --porcelain | wc -l | tr -d ' '
```
- Capture count silently
- If >20 files: **INFO** - "Large changeset ([N] files). Proceeding with detailed commit."
- Continue (informational only)

### Check 6: Test Coverage (Warning Only)
```bash
git diff --name-only --cached 2>/dev/null | grep -E '\.(py|js|ts)$' || true
git diff --name-only --cached 2>/dev/null | grep -E '(test_|_test\.|spec\.)' || true
```
- Capture output silently
- If code changed but no tests: **WARN** - "⚠️ Code modified but no tests changed. Intentional?"
- Continue (don't block)

## Phase 2: Determine Complexity

### Count Changes
```bash
# Files changed (capture silently)
git status --porcelain 2>/dev/null | wc -l | tr -d ' '

# Lines changed (capture silently)
git diff --stat 2>/dev/null | tail -1
```

### Classify Change Type
- **Trivial**: Docs only, formatting only, config only → Brief mode
- **Small**: 1-3 files, <100 lines → Brief mode
- **Medium**: 4-10 files, 100-500 lines → Moderate mode
- **Large**: 10+ files, 500+ lines, or complex feature → Detailed mode

### Check Session Complexity
Review conversation for indicators:
- Multi-step workflow: multiple phases, multiple modules touched
- Problem-solving: mentions of "issue", "error", "bug", "problem"
- Decisions: "decided to", "chose", "went with"
- If complex session AND large/medium change → extract insights

## Phase 3: Analyze Changes

Run all commands silently, capture output internally:

1. **Get file-level overview**: 
   ```bash
   git status --porcelain 2>/dev/null
   git diff --stat 2>/dev/null
   ```

2. **Get actual changes**: 
   ```bash
   git diff 2>/dev/null
   ```
   (or `git diff --cached` if files already staged)

3. **Get previous context**: 
   ```bash
   git log -1 --oneline 2>/dev/null
   ```

4. **Extract session insights** (only for complex sessions with large/medium changes):
   - Key difficulties and resolutions
   - Important realizations ("figured out", "discovered", "better approach")
   - Decisions made ("decided to", "chose", "opted for")
   - Rule references ("Rule 6XX", "Rule 5XX")
   - Future considerations ("todo", "later", "tech debt")

## Phase 4: Generate Commit Message

### Format Template

```
<type>: <human-readable summary (max 72 chars)>

## Changes
- [3-8 specific bullets with function/class names]
- Include file paths and what changed
- Technical and specific

## Context
- Problem solved (if non-obvious)
- Key decisions/rules applied (Rule XXX if applicable)
- Breaking changes (if any)

## Session Insights
- [1-3 key insights - only for complex sessions with large/medium changes]

## Metadata
- Files: [N]
- Rules: [list rule numbers if applicable]
- Tests: [Yes/No/N/A]
```

### Message Length by Mode

**Brief Mode (Trivial/Small):**
- Summary + 3-5 change bullets
- Minimal context (only if needed)
- No session insights
- Target: 50-100 words

**Moderate Mode:**
- Summary + 5-8 change bullets
- Context section (problem + decisions)
- Session insights only if complex session
- Target: 100-200 words

**Detailed Mode:**
- Summary + 8-12 change bullets
- Full context + session insights (if complex session)
- Technical details + rationale
- Target: 200-400 words

### Type Selection

- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code restructuring
- `test`: Test changes
- `docs`: Documentation
- `chore`: Maintenance/multiple unrelated updates
- `perf`: Performance improvements
- `style`: Formatting/style only

## Phase 5: Execute Git Commands

**Execute directly without user confirmation, suppress output:**

```bash
git add -A >/dev/null 2>&1
COMMIT_OUTPUT=$(git commit -m "[full message]" 2>&1)
COMMIT_HASH=$(git log -1 --format=%H 2>/dev/null)
PUSH_OUTPUT=$(git push 2>&1)
```

**Success response**: Only show final summary - "✓ Committed and pushed [hash]: [summary line]"

**Error handling**: 
- Capture all command output but don't display it
- Extract commit hash from `git log -1 --format=%H` after successful commit
- If commit fails: Parse `COMMIT_OUTPUT` and show error message only
- If push fails: Parse `PUSH_OUTPUT` and show exact error with suggested next steps
- Only display final summary on success, or error message on failure

## Error Handling

- **No changes**: "No changes detected. Working directory is clean."
- **Push failure**: Show exact error, suggest `git pull` or conflict resolution
- **Safety check failures**: Clear explanation, wait for user instruction

## Key Principles

1. **Adaptive detail**: More for complex, less for simple
2. **AI-optimized**: Structured sections, specific technical details
3. **Human-readable first line**: Summary is all humans need
4. **Selective insights**: Only extract for genuinely complex sessions
5. **Direct execution**: Execute commit immediately when command is invoked (no confirmation needed)
6. **Rule references**: Always include when patterns from `.cursor/rules/` applied
7. **Quiet mode**: Suppress all intermediate output, only show final summary or errors

