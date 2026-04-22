Read `.opencode/skills/ygg_build/SKILL.md` and `.opencode/skills/ygg_build/references/architect-protocol.md`.

Extract the description from the user's input (everything after `/ygg_build_preview`).

If no description is provided, ask: "What app would you like to preview a blueprint for?"

Execute **Phase 1 (Architect) only**. Do NOT generate code or write any files.

Print the full blueprint JSON followed by the plain-text summary. End with:
```
No files written. Run `/ygg_build <same description>` to generate the code.
```

EXECUTE IMMEDIATELY — do not deliberate before reading the protocol.
