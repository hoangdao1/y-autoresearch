"""Autoresearch-style improvement loop: validate → fix → repeat."""

from __future__ import annotations
import csv
import os
import time
import anthropic
from pathlib import Path
from rich.console import Console
from rich.table import Table
from .models import AppBlueprint, IterationRecord, ValidationResult
from .prompts import FIXER_SYSTEM
from .validator import validate

console = Console()


def _ask_claude_to_fix(code: str, result: ValidationResult) -> str:
    """Call Claude with the broken code + errors, get back fixed code."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    error_text = "\n".join(result.errors)
    warning_text = "\n".join(result.warnings)
    issues = f"Errors:\n{error_text or 'none'}\n\nWarnings:\n{warning_text or 'none'}"

    message = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=4096,
        system=FIXER_SYSTEM,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Fix this Yggdrasil app code.\n\n"
                    f"## Validation issues\n{issues}\n\n"
                    f"## Current code\n```python\n{code}\n```\n\n"
                    "Return only the corrected Python file."
                ),
            }
        ],
    )

    fixed = message.content[0].text.strip()
    # Strip accidental fences
    if fixed.startswith("```"):
        parts = fixed.split("```")
        fixed = parts[1]
        if fixed.startswith("python"):
            fixed = fixed[6:]
    return fixed.strip()


def _append_tsv(log_path: Path, record: IterationRecord) -> None:
    write_header = not log_path.exists()
    with log_path.open("a", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        if write_header:
            writer.writerow(["iteration", "score", "delta", "status", "description"])
        writer.writerow(
            [record.iteration, f"{record.score:.3f}", f"{record.delta:+.3f}",
             record.status, record.description]
        )


def improve(
    code: str,
    blueprint: AppBlueprint,
    max_iterations: int = 0,
    log_path: Path | None = None,
) -> tuple[str, list[IterationRecord]]:
    """
    Run an autoresearch-style loop that validates `code` and asks Claude to fix
    any issues until the code passes or `max_iterations` is exhausted.

    Returns (final_code, history_of_iterations).
    """
    if log_path is None:
        log_path = Path("autoresearch-results.tsv")

    records: list[IterationRecord] = []
    best_code = code
    best_score = -1.0

    # ── Phase 0: Baseline ────────────────────────────────────────────────────
    baseline = validate(code, blueprint)
    record = IterationRecord(
        iteration=0,
        score=baseline.score,
        delta=0.0,
        status="baseline",
        description="Initial generated code",
    )
    records.append(record)
    _append_tsv(log_path, record)
    best_score = baseline.score

    console.print(f"\n[bold]Baseline[/bold] score={baseline.score:.3f}")
    if baseline.errors:
        for e in baseline.errors:
            console.print(f"  [red]✗[/red] {e}")
    if baseline.warnings:
        for w in baseline.warnings:
            console.print(f"  [yellow]⚠[/yellow] {w}")

    if baseline.passed:
        console.print("[green]✓ Code passes validation — no improvement needed.[/green]")
        return code, records

    # ── Improvement loop ─────────────────────────────────────────────────────
    current_code = code
    consecutive_no_op = 0
    i = 1

    while max_iterations <= 0 or i <= max_iterations:
        limit_str = f"/{max_iterations}" if max_iterations > 0 else ""
        console.rule(f"Iteration {i}{limit_str}")

        # Phase 1: Review
        result = validate(current_code, blueprint)
        if result.score == best_score and i > 1:
            consecutive_no_op += 1
        else:
            consecutive_no_op = 0

        if consecutive_no_op >= 3:
            console.print("[yellow]Plateau detected — stopping early.[/yellow]")
            break

        if result.passed:
            console.print("[green]✓ Validation passed.[/green]")
            best_code = current_code
            break

        # Phase 2: Fix
        console.print(f"Score={result.score:.3f} — asking Claude to fix {len(result.errors)} error(s)…")
        start = time.time()
        fixed_code = _ask_claude_to_fix(current_code, result)
        elapsed = time.time() - start

        # Phase 3: Re-validate
        new_result = validate(fixed_code, blueprint)
        delta = new_result.score - result.score

        if len(fixed_code.strip()) < 50:
            status = "crash"
            description = "Claude returned empty/unusable code"
        elif fixed_code.strip() == current_code.strip():
            status = "no-op"
            description = "No change produced"
        elif new_result.score > result.score:
            status = "keep"
            description = f"Fixed {len(result.errors) - len(new_result.errors)} error(s)"
            current_code = fixed_code
            if new_result.score > best_score:
                best_score = new_result.score
                best_code = fixed_code
        else:
            status = "discard"
            description = f"Score did not improve ({result.score:.3f} → {new_result.score:.3f})"

        record = IterationRecord(
            iteration=i,
            score=new_result.score,
            delta=delta,
            status=status,
            description=description,
        )
        records.append(record)
        _append_tsv(log_path, record)

        icon = {"keep": "[green]✓[/green]", "discard": "[red]✗[/red]",
                "no-op": "[dim]–[/dim]", "crash": "[red]![/red]"}.get(status, "")
        console.print(
            f"  {icon} [{status}] score={new_result.score:.3f} "
            f"(Δ{delta:+.3f}) — {description} ({elapsed:.1f}s)"
        )

        if new_result.passed:
            console.print("[green]✓ All validation checks pass.[/green]")
            best_code = current_code
            break

        i += 1

    return best_code, records


def print_summary(records: list[IterationRecord]) -> None:
    table = Table(title="Autoresearch Results", show_lines=True)
    table.add_column("Iter", justify="right")
    table.add_column("Score", justify="right")
    table.add_column("Delta", justify="right")
    table.add_column("Status")
    table.add_column("Description")

    for r in records:
        color = {"baseline": "cyan", "keep": "green", "discard": "red",
                 "no-op": "dim", "crash": "red"}.get(r.status, "white")
        table.add_row(
            str(r.iteration),
            f"{r.score:.3f}",
            f"{r.delta:+.3f}" if r.iteration > 0 else "—",
            f"[{color}]{r.status}[/{color}]",
            r.description,
        )

    console.print(table)
