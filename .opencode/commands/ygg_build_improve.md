Read `.opencode/skills/ygg_build/SKILL.md` and `.opencode/skills/ygg_build/references/improvement-loop.md`.

Parse arguments:
- File path: first argument (required)
- `--iterations N`: max iterations (default: 5)

If no file path provided, ask: "Which generated file should I improve? (e.g. generated/my_app.py)"

Steps:
1. Read the file. If it does not exist, print an error and stop.
2. Infer the blueprint structure from the file content.
3. Execute **Phase 3 (Autoresearch Improvement Loop)** only.
4. Run up to `--iterations N` cycles.
5. Write the improved file back to the same path.
6. Print the results table and final score.

EXECUTE IMMEDIATELY — do not deliberate before reading the protocol.
