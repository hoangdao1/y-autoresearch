# Architect Protocol — Designing the AppBlueprint

## Your Job

Interpret the user's natural language description and produce a minimal, correct AppBlueprint that:
- Uses the simplest graph topology that satisfies the request
- Assigns clear, focused roles to each agent
- Chooses the right execution strategy
- Includes only the tools and context nodes that are explicitly needed

---

## Step 1 — Identify the Pattern

Read the description and classify it into one (or a combination) of these patterns:

| Pattern | Signals in the description | `execution_strategy` |
|---------|---------------------------|----------------------|
| **Linear pipeline** | "then", "passes to", "followed by", sequential verbs | `sequential` |
| **Supervisor / worker** | "parallel", "at the same time", "simultaneously", "fan out" | `parallel` |
| **Conditional routing** | "if", "when escalated", "based on", "depending on" | `sequential` (with route_rules) |
| **Tool-augmented** | "search the web", "look up", "call an API", "database" | `sequential` |
| **Context-grounded** | "using our docs", "based on the knowledge base", "FAQ" | `sequential` |
| **Topological DAG** | Multiple dependencies, "after both X and Y complete" | `topological` |

---

## Step 2 — Design Agents

For each logical role in the description, create one `AgentSpec`:

```
id          : snake_case, unique, descriptive  (e.g. "research_agent")
name        : Human-readable                  (e.g. "Researcher")
role        : One-sentence job description
system_prompt: Detailed instructions (3–8 sentences). Cover:
              - What inputs to expect
              - What processing to perform
              - What to output and in what format
              - Any constraints or style guidelines
model       : "claude-opus-4-7"
tool_ids    : [list of tool IDs this agent can call]
context_ids : [list of context IDs injected into this agent]
```

**Rules:**
- Every agent must have a distinct, non-overlapping role.
- The entry agent is the one that receives the user's raw query.
- Supervisor agents should have brief prompts (they coordinate, not process).
- Worker agents should have detailed, task-specific prompts.
- Do NOT create agents for things a tool can do (web search ≠ agent).

---

## Step 3 — Design Tools

Create a `ToolSpec` for every external capability mentioned (search, database, calculator, etc.):

```
id          : snake_case                      (e.g. "web_search_tool")
name        : valid Python identifier         (e.g. "web_search")
description : What this tool does (used in the agent's tool prompt)
stub_body   : Python function body (single line, MUST use single quotes for string literals)
              Example: return f'Search results for: {kwargs.get("query", "")}'
```

**Stub body rules:**
- Accept `**kwargs` (always).
- Use single quotes for any strings inside the f-string to avoid quote conflicts.
- Keep it to one line — no imports, no logic.
- Return a plausible placeholder string.

---

## Step 4 — Design Context Nodes

Create a `ContextSpec` for each knowledge chunk the description explicitly mentions:

```
id      : snake_case                        (e.g. "faq_context")
name    : Human-readable
content : The actual text content (can be a summary/placeholder if not provided)
weight  : 1.0 (default); increase for high-priority context
```

Only create context nodes if the description explicitly mentions a knowledge base, FAQ, documentation, or similar static information source.

---

## Step 5 — Design Connections

Create a `ConnectionSpec` for every handoff between agents:

```
from_id   : source agent id
to_id     : destination agent id
condition : null (unconditional) OR a Python-evaluable condition string
            e.g. "state.get('severity') == 'high'"
```

**Rules:**
- Linear pipeline: one chain of connections (A → B → C).
- Supervisor/worker: supervisor connects to each worker (S → W1, S → W2, S → W3).
- Conditional routing: multiple connections from the same agent with different conditions.
- Do NOT add cycles.

---

## Step 6 — Choose entry_agent_id and sample_query

- `entry_agent_id`: The agent that receives the user's raw query first.
- `sample_query`: A realistic one-sentence test input that exercises the full pipeline.

---

## Output Format

Produce the blueprint as a JSON object matching this schema exactly:

```json
{
  "name": "App Name",
  "description": "One-sentence description",
  "entry_agent_id": "agent_id",
  "execution_strategy": "sequential",
  "sample_query": "...",
  "agents": [ { "id", "name", "role", "system_prompt", "model", "tool_ids", "context_ids" } ],
  "tools":   [ { "id", "name", "description", "stub_body" } ],
  "context": [ { "id", "name", "content", "weight" } ],
  "connections": [ { "from_id", "to_id", "condition" } ]
}
```

Then summarize it in plain text for the user (see Phase 1 output format in SKILL.md).
