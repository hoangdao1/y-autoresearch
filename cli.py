#!/usr/bin/env python3
"""CLI entry point: ygg-build"""

import asyncio
import os
import sys
from pathlib import Path

import click
from dotenv import load_dotenv
from rich.console import Console

load_dotenv()
console = Console()


@click.group()
def main():
    """y-autoresearch: Build yggdrasil-powered apps from natural language."""


@main.command()
@click.argument("request", required=False)
@click.option("--file", "-f", "request_file", type=click.Path(exists=True),
              help="Read request from a file")
@click.option("--output-dir", "-o", default="generated", show_default=True,
              help="Directory to write the generated app")
@click.option("--iterations", "-n", default=5, show_default=True,
              help="Max autoresearch improvement iterations")
def build(request: str | None, request_file: str | None, output_dir: str, iterations: int):
    """Build a yggdrasil app from a natural language REQUEST.

    Examples:

      ygg-build "Build a research assistant that searches the web and summarizes findings"

      ygg-build --file examples/customer_support.md

      echo "Build a code review agent" | ygg-build -
    """
    if not os.environ.get("ANTHROPIC_API_KEY"):
        console.print("[red]Error:[/red] ANTHROPIC_API_KEY is not set. Add it to .env or export it.")
        sys.exit(1)

    # Resolve request text
    if request_file:
        request = Path(request_file).read_text()
    elif request == "-":
        request = sys.stdin.read()
    elif not request:
        console.print("[red]Error:[/red] Provide a request string, --file, or pipe via stdin.")
        sys.exit(1)

    from framework.builder import build_app

    out = asyncio.run(
        build_app(
            request=request,
            output_dir=Path(output_dir),
            max_iterations=iterations,
        )
    )
    console.print(f"\n[bold green]Done![/bold green] App written to [bold]{out}[/bold]")


@main.command()
@click.argument("request_file", type=click.Path(exists=True))
def preview(request_file: str):
    """Preview the blueprint that would be generated (no code written)."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        console.print("[red]Error:[/red] ANTHROPIC_API_KEY is not set.")
        sys.exit(1)

    import asyncio
    from framework.architect import design_app
    import json

    request = Path(request_file).read_text()
    blueprint = asyncio.run(design_app(request))
    console.print_json(json.dumps(blueprint.model_dump(), indent=2))


if __name__ == "__main__":
    main()
