# ygg_build — Yggdrasil App Builder

Build production-ready [Yggdrasil](https://github.com/hoangdao1/yggdrasil) multi-agent apps from a natural language description, using an autoresearch-style improvement loop to validate and refine the generated code.

## Commands

| Command | Purpose |
|---------|---------|
| `/ygg_build <description>` | Build a full yggdrasil app from scratch |
| `/ygg_build_preview <description>` | Design and display the blueprint without writing code |
| `/ygg_build_improve <file>` | Re-run the improvement loop on an existing generated file |

## Setup Gate

**CRITICAL:** Before executing, verify the description is present and clear. If the user typed `/ygg_build` with no argument or an ambiguous description, ask (in one batch):

1. What should the app do? (purpose and domain)
2. What agents are needed? (roles, how many)
3. Are there tools (web search, database, APIs)? If yes, what?
4. Is this sequential (pipeline), parallel (fan-out), or routing-based (conditional branching)?

Do not proceed without a clear description.

## Build Protocol

When invoked as `/ygg_build <description>`, execute these phases in order. Stream output live — never run in background.

### Phase 1 — Architect

Read `.opencode/skills/ygg_build/references/architect-protocol.md` and follow it to design an `AppBlueprint`. Output a summary:

```
Blueprint: <App Name>
Strategy : sequential | parallel | topological
Agents   : <name> (<role>), ...
Tools    : <name>, ... (or none)
Context  : <name>, ... (or none)
Flow     : agent_a → agent_b → ...
Sample Q : "<sample_query>"
```

### Phase 2 — Code Generation

Read `.opencode/skills/ygg_build/references/codegen-patterns.md` and generate the complete Python file. Write it to `generated/<snake_case_name>.py`.

The file must include:
- All imports
- Tool stub functions (before `main()`)
- `async def main()` with the full app setup
- `if __name__ == "__main__": asyncio.run(main())`

### Phase 3 — Autoresearch Improvement Loop

Read `.opencode/skills/ygg_build/references/improvement-loop.md` and run the validation loop.

Default: up to **5 iterations**. Override with `--iterations N`.

Print a results table when done:

```
Iter | Score | Delta | Status   | Description
-----|-------|-------|----------|------------
0    | 0.857 |   —   | baseline | Initial generated code
1    | 1.000 | +0.143| keep     | Fixed missing asyncio.run entry point
```

### Phase 4 — Output

Print:
```
✓ App written to generated/<name>.py
  Score  : 1.000
  Agents : <count>
  Run with: cd <project> && ANTHROPIC_API_KEY=... python generated/<name>.py
```

## Argument Parsing

Extract configuration from user input first, before reading anything else:
- `--iterations N` → max improvement iterations (default 5)
- `--output <dir>` → output directory (default `generated/`)
- Everything else → description text

## Critical Rules

1. **Read the reference files** before each phase.
2. **One atomic change per improvement iteration**.
3. **Validate before and after** every change.
4. **Stream output live** — never batch or background.
5. **Write complete files** — never partial snippets.
6. **Plateau detection**: stop after 3 consecutive iterations with no score improvement.

EXECUTE IMMEDIATELY — do not deliberate, do not ask clarifying questions before reading the protocol.
