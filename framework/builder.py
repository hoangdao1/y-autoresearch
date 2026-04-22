"""Main orchestrator: request → blueprint → code → improvement loop → output."""

from __future__ import annotations
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from .architect import design_app
from .codegen import generate_code
from .loop import improve, print_summary
from .models import AppBlueprint

console = Console()


async def build_app(
    request: str,
    output_dir: Path = Path("generated"),
    max_iterations: int = 0,
) -> Path:
    """
    Full pipeline:
      1. Architect: interpret `request` → AppBlueprint
      2. Codegen: AppBlueprint → Python source
      3. Autoresearch loop: validate + fix until passing or exhausted
      4. Write final file to `output_dir/<app_name>.py`

    Returns the path to the generated file.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # ── Step 1: Architect ────────────────────────────────────────────────────
    console.rule("[bold blue]Step 1: Architect")
    console.print(Panel(request, title="User Request", border_style="blue"))
    console.print("Designing app blueprint…")

    blueprint: AppBlueprint = await design_app(request)

    console.print(f"[green]✓[/green] Blueprint: [bold]{blueprint.name}[/bold]")
    console.print(f"  Agents : {', '.join(a.name for a in blueprint.agents)}")
    if blueprint.tools:
        console.print(f"  Tools  : {', '.join(t.name for t in blueprint.tools)}")
    if blueprint.connections:
        routing = " → ".join(
            f"{c.from_id}→{c.to_id}" for c in blueprint.connections
        )
        console.print(f"  Flow   : {routing}")
    console.print(f"  Strategy: {blueprint.execution_strategy.value}")

    # ── Step 2: Code generation ──────────────────────────────────────────────
    console.rule("[bold blue]Step 2: Code Generation")
    code = generate_code(blueprint)
    console.print(f"Generated {len(code.splitlines())} lines of Python.")

    # ── Step 3: Autoresearch improvement loop ────────────────────────────────
    console.rule("[bold blue]Step 3: Autoresearch Loop")
    log_path = output_dir / "autoresearch-results.tsv"
    final_code, records = improve(
        code,
        blueprint,
        max_iterations=max_iterations,
        log_path=log_path,
    )

    # ── Step 4: Write output ─────────────────────────────────────────────────
    safe_name = blueprint.name.lower().replace(" ", "_").replace("-", "_")
    out_path = output_dir / f"{safe_name}.py"
    out_path.write_text(final_code)

    console.rule("[bold blue]Summary")
    print_summary(records)

    final_score = records[-1].score if records else 0.0
    status_color = "green" if final_score >= 1.0 else "yellow" if final_score >= 0.5 else "red"
    console.print(
        f"\n[{status_color}]Final score: {final_score:.3f}[/{status_color}]  "
        f"→  [bold]{out_path}[/bold]"
    )
    if log_path.exists():
        console.print(f"Iteration log: {log_path}")

    return out_path
