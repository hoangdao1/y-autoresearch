Read `.claude/skills/ygg-build/SKILL.md` and `.claude/skills/ygg-build/references/architect-protocol.md`.

Extract the description from the user's input (everything after `/ygg-build:preview`).

If no description is provided, use `AskUserQuestion` to ask: "What app would you like to preview a blueprint for?"

Execute **Phase 1 (Architect) only** from the build protocol. Do NOT generate code or write any files.

Print the full blueprint JSON followed by the plain-text summary. End with:
```
No files written. Run `/ygg-build <same description>` to generate the code.
```

EXECUTE IMMEDIATELY — do not deliberate before reading the protocol.
