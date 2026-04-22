Read `.claude/skills/ygg-build/SKILL.md` and `.claude/skills/ygg-build/references/improvement-loop.md`.

Parse arguments from the user's input:
- File path: first argument after `/ygg-build:improve` (required)
- `--iterations N`: max iterations (default: 5)

If no file path provided, use `AskUserQuestion` to ask: "Which generated file should I improve? (e.g. generated/my_app.py)"

**Steps:**

1. Read the file at the given path. If it does not exist, print an error and stop.
2. Infer the blueprint structure from the file content (read agent names, tools, connections from the code).
3. Skip directly to **Phase 3 (Autoresearch Improvement Loop)** from the build protocol.
4. Run up to `--iterations N` improvement cycles.
5. Write the improved file back to the same path.
6. Print the results table and final score.

EXECUTE IMMEDIATELY — do not deliberate before reading the protocol.
