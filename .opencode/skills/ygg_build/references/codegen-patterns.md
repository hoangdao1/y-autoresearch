# Codegen Patterns — Writing Yggdrasil Apps

## File Structure

Every generated file must follow this exact structure (in order):

```python
# Generated app: <App Name>
# <one-line description>
import asyncio
from yggdrasil.app import GraphApp
from yggdrasil.backends.llm import AnthropicBackend

# --- Tool stubs (BEFORE main) ---
def <tool_name>(**kwargs):
    return f'...'

# --- Main ---
async def main():
    backend = AnthropicBackend()
    app = GraphApp(backend=backend)

    # Agents
    ...

    # Tools (if any)
    ...

    # Context (if any)
    ...

    # Wire tools (if any)
    ...

    # Wire context (if any)
    ...

    # Routing
    ...

    # Register tool implementations (if any)
    ...

    # Execute
    ctx = await app.run(entry_agent, sample_query, strategy="sequential")

    # Print results
    print('\n=== Results ===')
    for each agent...

if __name__ == '__main__':
    asyncio.run(main())
```

---

## API Reference

### Creating Agents

```python
agent = await app.add_agent(
    name="Researcher",
    system_prompt="You are a research specialist...",
    model="claude-opus-4-7",
)
```

- `name`: human-readable string
- `system_prompt`: the agent's full instructions
- `model`: always `"claude-opus-4-7"` unless specified otherwise
- Returns an `AgentNode` — store in a variable named after the agent's id

### Creating Tools

```python
tool = await app.add_tool(
    name="web_search",
    callable_ref="tools.web_search",
    description="Search the web for information",
)
```

- `name`: valid Python identifier (matches the stub function name)
- `callable_ref`: always `"tools.<name>"`
- Returns a `ToolNode`

### Creating Context Nodes

```python
ctx_node = await app.add_context(
    name="FAQ Knowledge Base",
    content="Q: What is your return policy?...",
)
```

- Returns a `ContextNode`

### Wiring: Tools to Agents

```python
await app.connect_tool(agent_node, tool_node)
```

### Wiring: Context to Agents

```python
await app.connect_context(agent_node, context_node)
```

### Routing: Agent Delegation

```python
# Unconditional
await app.delegate(from_agent, to_agent)

# Conditional
await app.delegate(from_agent, to_agent, condition="state.get('severity') == 'high'")
```

### Registering Tool Implementations

```python
# Must come AFTER creating the tool node, BEFORE app.run()
app.register_tool(tool_node.node_id, tool_function)
```

`tool_function` is the stub defined at module level.

### Running the App

```python
ctx = await app.run(
    entry_agent,
    "The user's query here",
    strategy="sequential",   # or "parallel" or "topological"
)
```

### Reading Results

```python
if agent.node_id in ctx.outputs:
    text = ctx.outputs[agent.node_id].get("text", "")
    print(f"\n--- {agent.name} ---\n{text}")
```

---

## Naming Conventions

| Blueprint field | Python variable |
|----------------|----------------|
| `id: "research_agent"` | `research_agent` |
| `id: "web-search-tool"` | `web_search_tool` |
| `id: "faq context"` | `faq_context` |

Rule: replace `-` and spaces with `_`.

---

## Pattern Templates

### Linear Pipeline (A → B → C)

```python
async def main():
    app = GraphApp(backend=AnthropicBackend())

    a = await app.add_agent(name="A", system_prompt="...", model="claude-opus-4-7")
    b = await app.add_agent(name="B", system_prompt="...", model="claude-opus-4-7")
    c = await app.add_agent(name="C", system_prompt="...", model="claude-opus-4-7")

    await app.delegate(a, b)
    await app.delegate(b, c)

    ctx = await app.run(a, "query", strategy="sequential")
```

### Supervisor / Worker Fan-out

```python
async def main():
    app = GraphApp(backend=AnthropicBackend())

    supervisor = await app.add_agent(name="Supervisor", system_prompt="...", model="claude-opus-4-7")
    worker1    = await app.add_agent(name="Worker1",    system_prompt="...", model="claude-opus-4-7")
    worker2    = await app.add_agent(name="Worker2",    system_prompt="...", model="claude-opus-4-7")
    merger     = await app.add_agent(name="Merger",     system_prompt="...", model="claude-opus-4-7")

    await app.delegate(supervisor, worker1)
    await app.delegate(supervisor, worker2)
    await app.delegate(worker1, merger)
    await app.delegate(worker2, merger)

    ctx = await app.run(supervisor, "query", strategy="parallel")
```

### Tool-augmented Agent

```python
def web_search(**kwargs):
    return f'[stub] search: {kwargs.get("query", "")}'

async def main():
    app = GraphApp(backend=AnthropicBackend())

    searcher = await app.add_agent(name="Searcher", system_prompt="...", model="claude-opus-4-7")
    search_tool = await app.add_tool(name="web_search", callable_ref="tools.web_search",
                                     description="Search the web")

    await app.connect_tool(searcher, search_tool)
    app.register_tool(search_tool.node_id, web_search)

    ctx = await app.run(searcher, "query", strategy="sequential")
```

### Context-grounded Agent

```python
async def main():
    app = GraphApp(backend=AnthropicBackend())

    agent = await app.add_agent(name="Support", system_prompt="...", model="claude-opus-4-7")
    kb = await app.add_context(name="FAQ", content="Q: How do I return? A: ...")

    await app.connect_context(agent, kb)

    ctx = await app.run(agent, "query", strategy="sequential")
```

---

## Common Mistakes to Avoid

| Wrong | Correct |
|-------|---------|
| `app.add_agent(...)` | `await app.add_agent(...)` |
| `app.connect_tool(...)` | `await app.connect_tool(...)` |
| `app.delegate(...)` | `await app.delegate(...)` |
| `def main():` | `async def main():` |
| Tool stub uses double quotes: `f"...{kwargs.get("q")}"` | Use single quotes: `f'...{kwargs.get("q")}'` |
| Missing entry point | Always end with `if __name__ == '__main__': asyncio.run(main())` |
| `app.register_tool` inside a coroutine before node exists | Register AFTER `add_tool`, BEFORE `app.run` |
