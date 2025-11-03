---
description: AI-optimized git commit workflow with adaptive detail based on change complexity
---

# Commit Workflow

AI-optimized commit workflow with adaptive detail based on change complexity. Human-readable first line, rest optimized for AI review.

## Adaptive Strategy

- **Small changes** (1-3 files, trivial/simple): Brief commit (50-100 words)
- **Medium changes** (4-10 files, moderate complexity): Moderate commit (100-200 words)
- **Large changes** (10+ files, complex features): Detailed commit (200-400 words)
- **Trivial changes** (docs, formatting only): Auto-brief, skip detailed analysis

## Phase 1: Safety Checks

Run these checks **in order** and handle appropriately:

### Check 1: Uncommitted Changes
```bash
git status --porcelain
```
- If output is empty: "No changes to commit. Working directory is clean." (exit gracefully)
- If changes exist: Continue to next check

### Check 2: Remote Sync Status
```bash
git fetch
git status
```
- If behind remote: **BLOCK** - "⚠️ Behind remote. Pull first with `git pull`"
- Wait for user instruction before proceeding

### Check 3: Merge Conflicts
```bash
git diff --name-only --diff-filter=U
```
- If conflicts exist: **BLOCK** - "⚠️ Unresolved merge conflicts. Resolve first."
- Wait for user instruction before proceeding

### Check 4: Secret Files Detection (Warning Only)
Check for untracked files matching: `.env`, `*.key`, `*credentials*`, `*secret*`, `*token*`
- If found: **WARN** - "⚠️ Potential secrets detected: [list files]. Confirm these are safe?"
- Wait for confirmation, then proceed

### Check 5: Large Changeset (Info Only)
```bash
git status --porcelain | wc -l
```
- If >20 files: **INFO** - "Large changeset ([N] files). Proceeding with detailed commit."
- Continue (informational only)

### Check 6: Test Coverage (Warning Only)
- Code files: `git diff --name-only | grep -E '\.(py|js|ts)$'`
- Test files: `git diff --name-only | grep -E '(test_|_test\.|spec\.)'`
- If code changed but no tests: **WARN** - "⚠️ Code modified but no tests changed. Intentional?"
- Continue (don't block)

## Phase 2: Determine Complexity

### Count Changes
```bash
# Files changed
git status --porcelain | wc -l

# Lines changed
git diff --stat | tail -1
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

1. **Get file-level overview**: 
   ```bash
   git status --porcelain
   git diff --stat
   ```

2. **Get actual changes**: 
   ```bash
   git diff
   ```

3. **Get previous context**: 
   ```bash
   git log -1 --oneline
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

## Phase 5: User Review & Execution

**ALWAYS show generated message and ask for confirmation:**

1. Display full commit message in a code block
2. Ask user: "Commit with this message? (yes/no/edit)"
3. If yes → execute:
   ```bash
   git add -A
   git commit -m "[full message]"
   git push
   ```
4. If no → exit gracefully
5. If edit → allow user to modify message, then ask for confirmation again

**Success response**: "✓ Committed and pushed [hash]: [summary line]"

**Push failure**: Show exact error message and suggest next steps (e.g., `git pull`, resolve conflicts)

## Error Handling

- **No changes**: "No changes detected. Working directory is clean."
- **Push failure**: Show exact error, suggest `git pull` or conflict resolution
- **Safety check failures**: Clear explanation, wait for user instruction

## Key Principles

1. **Adaptive detail**: More for complex, less for simple
2. **AI-optimized**: Structured sections, specific technical details
3. **Human-readable first line**: Summary is all humans need
4. **Selective insights**: Only extract for genuinely complex sessions
5. **Always confirm**: Never auto-commit without user approval
6. **Rule references**: Always include when patterns from `.cursor/rules/` applied

