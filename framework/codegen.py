"""Generates a standalone Python file from an AppBlueprint."""

from __future__ import annotations
from .models import AppBlueprint


def _var(id_: str) -> str:
    return id_.replace("-", "_").replace(" ", "_")


def _safe_stub(name: str, body: str) -> str:
    """Return a syntactically valid stub function.  Falls back to a no-op if the
    provided body doesn't compile cleanly."""
    candidate = f"def {name}(**kwargs):\n    {body}\n"
    try:
        compile(candidate, "<stub>", "exec")
        return candidate
    except SyntaxError:
        # Body is broken (e.g. mismatched f-string quotes from the LLM).
        return f'def {name}(**kwargs):\n    return f"[stub] {name} called: " + str(kwargs)\n'


def generate_code(blueprint: AppBlueprint) -> str:
    lines: list[str] = []

    # --- Header ---
    lines += [
        f"# Generated app: {blueprint.name}",
        f"# {blueprint.description}",
        "import asyncio",
        "from yggdrasil.app import GraphApp",
        "from yggdrasil.backends.llm import AnthropicBackend",
        "",
    ]

    # --- Tool stub implementations ---
    for tool in blueprint.tools:
        stub = _safe_stub(tool.name, tool.stub_body)
        lines.append(stub)  # already ends with a newline

    # --- main() ---
    lines += ["async def main():", "    backend = AnthropicBackend()"]
    lines.append("    app = GraphApp(backend=backend)")
    lines.append("")

    # Create agents
    lines.append("    # Agents")
    for agent in blueprint.agents:
        v = _var(agent.id)
        lines += [
            f"    {v} = await app.add_agent(",
            f"        name={repr(agent.name)},",
            f"        system_prompt={repr(agent.system_prompt)},",
            f"        model={repr(agent.model)},",
            f"    )",
        ]
    lines.append("")

    # Create tools
    if blueprint.tools:
        lines.append("    # Tools")
        for tool in blueprint.tools:
            v = _var(tool.id)
            lines += [
                f"    {v} = await app.add_tool(",
                f"        name={repr(tool.name)},",
                f"        callable_ref='tools.{tool.name}',",
                f"        description={repr(tool.description)},",
                f"    )",
            ]
        lines.append("")

    # Create context nodes
    if blueprint.context:
        lines.append("    # Context")
        for ctx in blueprint.context:
            v = _var(ctx.id)
            lines += [
                f"    {v} = await app.add_context(",
                f"        name={repr(ctx.name)},",
                f"        content={repr(ctx.content)},",
                f"    )",
            ]
        lines.append("")

    # Wire tools to agents
    wired_tools = False
    for agent in blueprint.agents:
        for tool_id in agent.tool_ids:
            if not wired_tools:
                lines.append("    # Wire tools")
                wired_tools = True
            lines.append(f"    await app.connect_tool({_var(agent.id)}, {_var(tool_id)})")
    if wired_tools:
        lines.append("")

    # Wire context to agents
    wired_ctx = False
    for agent in blueprint.agents:
        for ctx_id in agent.context_ids:
            if not wired_ctx:
                lines.append("    # Wire context")
                wired_ctx = True
            lines.append(f"    await app.connect_context({_var(agent.id)}, {_var(ctx_id)})")
    if wired_ctx:
        lines.append("")

    # Delegate connections
    if blueprint.connections:
        lines.append("    # Routing")
        for conn in blueprint.connections:
            args = f"{_var(conn.from_id)}, {_var(conn.to_id)}"
            if conn.condition:
                args += f", condition={repr(conn.condition)}"
            lines.append(f"    await app.delegate({args})")
        lines.append("")

    # Register tool implementations
    if blueprint.tools:
        lines.append("    # Register tool implementations")
        for tool in blueprint.tools:
            lines.append(f"    app.register_tool({_var(tool.id)}.node_id, {tool.name})")
        lines.append("")

    # Run
    entry = _var(blueprint.entry_agent_id)
    lines += [
        "    # Execute",
        f"    ctx = await app.run(",
        f"        {entry},",
        f"        {repr(blueprint.sample_query)},",
        f"        strategy={repr(blueprint.execution_strategy.value)},",
        f"    )",
        "",
        "    # Print results",
        "    print('\\n=== Results ===')",
    ]
    for agent in blueprint.agents:
        v = _var(agent.id)
        lines += [
            f"    if {v}.node_id in ctx.outputs:",
            f"        print(f'\\n--- {agent.name} ---')",
            f"        print(ctx.outputs[{v}.node_id].get('text', ''))",
        ]

    lines += [
        "",
        "",
        "if __name__ == '__main__':",
        "    asyncio.run(main())",
        "",
    ]

    return "\n".join(lines)
