# y-autoresearch

Describe an AI app in plain English. Get working Python code.

y-autoresearch combines two frameworks:
- **[Yggdrasil](https://github.com/hoangdao1/yggdrasil)** — graph-native multi-agent orchestration (the target)
- **[Autoresearch](https://github.com/uditgoenka/autoresearch)** — autonomous improvement loop (the method)

You describe what you want. The framework designs the agent graph, generates the code, then iterates until the code is correct.

## How it works

```
Your description
      │
      ▼
 [Architect]   Claude interprets the request → AppBlueprint
      │           (agents, tools, context, routing, execution strategy)
      ▼
 [Codegen]     Blueprint → standalone Python file using Yggdrasil APIs
      │
      ▼
 [Loop]        Validate → fix → revalidate → repeat
      │           (autoresearch-style: score 0–1, TSV log, plateau detection)
      ▼
 generated/<name>.py   Ready to run
```

## Quickstart

```bash
git clone https://github.com/hoangdao1/y-autoresearch
cd y-autoresearch
pip install -e .

cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env

ygg-build "Build a research assistant that searches the web and summarizes findings"
```

The generated app appears in `generated/research_assistant.py`. Run it:

```bash
python generated/research_assistant.py
```

## CLI

```bash
# Build from a string
ygg-build build "Build a customer support triage system with severity routing"

# Build from a file
ygg-build build --file examples/research_assistant.md

# Build from stdin
echo "Build a parallel document analyzer" | ygg-build build -

# Control improvement iterations (default: 5)
ygg-build build --iterations 10 "Build a code review pipeline"

# Preview the blueprint without generating code
ygg-build preview examples/customer_support.md
```

## Claude Code skills

If you use [Claude Code](https://claude.ai/code), the skills are already in `.claude/`. No installation needed when working in this directory.

```
/ygg-build Build a research assistant that searches the web and summarizes findings
/ygg-build:preview Build a customer support triage system with severity routing
/ygg-build:improve generated/research_assistant.py
```

**Install globally** (available in all your projects):

```bash
./scripts/install.sh global
```

## OpenCode commands

```
/ygg_build Build a research assistant that searches the web and summarizes findings
/ygg_build_preview Build a customer support triage system
/ygg_build_improve generated/research_assistant.py
```

**Install into your project:**

```bash
./scripts/install-opencode.sh
```

## What gets generated

Every generated file is a complete, runnable Yggdrasil app:

```python
# Generated app: Research Assistant
import asyncio
from yggdrasil.app import GraphApp
from yggdrasil.backends.llm import AnthropicBackend

def web_search(**kwargs):
    return f'[stub] search: {kwargs.get("query", "")}'

async def main():
    app = GraphApp(backend=AnthropicBackend())

    researcher  = await app.add_agent(name="Researcher",  system_prompt="...", model="claude-opus-4-7")
    synthesizer = await app.add_agent(name="Synthesizer", system_prompt="...", model="claude-opus-4-7")
    search_tool = await app.add_tool(name="web_search", callable_ref="tools.web_search",
                                     description="Search the web")

    await app.connect_tool(researcher, search_tool)
    await app.delegate(researcher, synthesizer)
    app.register_tool(search_tool.node_id, web_search)

    ctx = await app.run(researcher, "What are recent advances in quantum computing?",
                        strategy="sequential")

    if synthesizer.node_id in ctx.outputs:
        print(ctx.outputs[synthesizer.node_id].get("text", ""))

if __name__ == "__main__":
    asyncio.run(main())
```

Tool stubs are clearly marked — replace them with real implementations (e.g. a Brave Search API call) before running in production.

## Supported patterns

| Pattern | Description | Strategy |
|---------|-------------|----------|
| Linear pipeline | A → B → C, each step processes the previous output | `sequential` |
| Supervisor / worker | One coordinator fans out to parallel specialists | `parallel` |
| Conditional routing | Branches based on state (e.g. severity, topic) | `sequential` + route rules |
| Tool-augmented | Agent calls external tools (search, database, APIs) | any |
| Context-grounded | Agent answers using injected knowledge (FAQ, docs) | any |
| Topological DAG | Complex dependencies, multiple merge points | `topological` |

## The improvement loop

After generating code, the framework runs a static validation loop inspired by autoresearch:

```
Iter | Score | Delta  | Status   | Description
-----|-------|--------|----------|----------------------------------
0    | 0.714 |   —    | baseline | Initial generated code
1    | 0.857 | +0.143 | keep     | Fixed un-awaited app.delegate call
2    | 1.000 | +0.143 | keep     | Fixed f-string quote conflict in stub
```

**Metric** (0.0 – 1.0): checks syntax, required imports, async correctness, entry point, API usage.  
**Log**: every run appends to `generated/autoresearch-results.tsv`.  
**Stopping**: score reaches 1.0, iteration limit hit, or 3 consecutive iterations without improvement.

## Project structure

```
y-autoresearch/
├── framework/
│   ├── architect.py      # Natural language → AppBlueprint (calls Claude)
│   ├── codegen.py        # AppBlueprint → Python source (pure function)
│   ├── validator.py      # Static analysis, 0–1 score
│   ├── loop.py           # Autoresearch improvement loop
│   ├── builder.py        # Orchestrates all phases
│   ├── models.py         # Pydantic models
│   └── prompts.py        # System prompts for architect and fixer
├── cli.py                # ygg-build CLI entry point
├── examples/             # Sample request files
├── generated/            # Output directory
├── .claude/              # Claude Code skills (/ygg-build)
├── .opencode/            # OpenCode commands (/ygg_build)
└── scripts/
    ├── install.sh         # Install Claude Code skill (global or local)
    └── install-opencode.sh
```

## Requirements

- Python 3.11+
- `ANTHROPIC_API_KEY`
- Git (for Yggdrasil install from source)
