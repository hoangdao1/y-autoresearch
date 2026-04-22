# Improvement Loop Protocol

Autoresearch-style validation and repair loop for generated Yggdrasil code.

## Overview

```
Phase 0: Baseline — validate initial code, establish score
Phase 1–N: Review → Identify issue → Fix → Re-validate → Log → Repeat
Stop when: score = 1.0, max iterations reached, or 3 consecutive no-ops
```

**Metric**: Code quality score from 0.0 to 1.0 (see Scoring below).

---

## Phase 0 — Baseline

1. Read the generated file.
2. Run the full validation checklist (see below).
3. Record: `iteration=0, score=<X>, status=baseline`.
4. If score = 1.0, print "✓ No issues found" and stop.

---

## Validation Checklist (run every iteration)

Score starts at 1.0. Deduct for each failing check:

| Check | Deduction | How to verify |
|-------|-----------|---------------|
| Python syntax valid | −0.5 | Mentally parse; look for unmatched parens, quotes, indentation |
| `import asyncio` present | −0.1 | Text search |
| `from yggdrasil.app import GraphApp` present | −0.1 | Text search |
| `from yggdrasil.backends.llm import AnthropicBackend` present | −0.1 | Text search |
| `async def main()` present | −0.1 | Text search |
| `asyncio.run(main())` in `__main__` block | −0.1 | Text search |
| `app.run(` present | −0.1 | Text search |
| All `add_agent/add_tool/add_context/delegate/connect_*` calls are awaited | −0.1 | Scan each call |
| Tool stub functions defined before `main()` | −0.1 | Check function order |
| Entry agent variable used in `app.run(` | −0.1 | Cross-reference |
| No double-quote conflicts in f-strings | −0.1 | Inspect string literals |

Clamp result: score = max(0.0, computed_score), rounded to 3 decimals.

---

## Phases 1–N — Improvement Iterations

### Step 1 — Review

- Re-read the current file.
- Run the validation checklist.
- List all failing checks.
- Check the last iteration's log to avoid repeating the same fix.

### Step 2 — Identify the single most impactful fix

Priority order:
1. Syntax errors (score deduction ≥ 0.5) — fix these first, everything else is blocked
2. Missing imports
3. Missing entry point
4. Missing `app.run(` call
5. Un-awaited async calls
6. Tool registration issues
7. Style / warning-level issues

Pick ONE fix. Write a one-sentence description: "Fix: <what>".

### Step 3 — Apply the fix

Edit the file with the single targeted change. Do not fix multiple issues in one iteration.

### Step 4 — Re-validate

Run the checklist again. Compute new score.

### Step 5 — Decide

| Condition | Action |
|-----------|--------|
| `new_score > old_score` | **keep** — log it, continue |
| `new_score == old_score` AND file changed | **discard** — revert the change, log "no-op" |
| `new_score < old_score` | **discard** — revert the change, log "discard" |
| File is empty or unparseable after edit | **crash** — restore previous version, log "crash" |

To revert: restore the file to its state before this iteration.

### Step 6 — Log

Append to the results table:

```
<iter> | <score> | <delta> | <status> | <description>
```

### Step 7 — Check stopping conditions

Stop if any of these are true:
- `score = 1.0` → print "✓ All checks pass"
- `iteration >= max_iterations` → print "Reached iteration limit"
- 3 consecutive iterations with status `no-op` or `discard` → print "Plateau detected — stopping"

Otherwise, go to Step 1.

---

## Scoring Examples

**Score 0.0**: Syntax error in generated code — nothing else can be evaluated.

**Score 0.571**: Syntax OK, imports OK, `main()` defined, but missing `asyncio.run`, missing `app.run(`, and one un-awaited call.

**Score 0.857**: All structural checks pass; one tool stub uses double quotes that conflict in an f-string.

**Score 1.0**: All checks pass. File is ready to run.

---

## Results Table Format

Print at end of loop:

```
╔══════════════════════════════════════════════════════════════╗
║                   Autoresearch Results                       ║
╠══════╦═══════╦════════╦══════════╦══════════════════════════╣
║ Iter ║ Score ║  Delta ║ Status   ║ Description              ║
╠══════╬═══════╬════════╬══════════╬══════════════════════════╣
║  0   ║ 0.857 ║   —    ║ baseline ║ Initial generated code   ║
║  1   ║ 1.000 ║ +0.143 ║ keep     ║ Fixed f-string quotes    ║
╚══════╩═══════╩════════╩══════════╩══════════════════════════╝
```

Color convention (if terminal supports it):
- `keep` → green
- `discard` / `crash` → red
- `no-op` → dim
- `baseline` → cyan
