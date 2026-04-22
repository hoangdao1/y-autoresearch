"""Static validation of generated code against the AppBlueprint."""

from __future__ import annotations
import ast
from .models import AppBlueprint, ValidationResult


def validate(code: str, blueprint: AppBlueprint) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []

    # 1. Syntax check
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return ValidationResult(score=0.0, errors=[f"SyntaxError: {exc}"])

    # Collect all names defined/used at module and function level
    all_source = code

    # 2. Required imports
    if "from yggdrasil.app import GraphApp" not in all_source:
        errors.append("Missing import: from yggdrasil.app import GraphApp")
    if "from yggdrasil.backends.llm import AnthropicBackend" not in all_source:
        errors.append("Missing import: from yggdrasil.backends.llm import AnthropicBackend")
    if "import asyncio" not in all_source:
        errors.append("Missing import: asyncio")

    # 3. Must have async def main() and entry point
    func_names = {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef))
    }
    if "main" not in func_names:
        errors.append("Missing async def main()")
    if "__name__" not in all_source or "asyncio.run(main())" not in all_source:
        errors.append("Missing entry point: if __name__ == '__main__': asyncio.run(main())")

    # 4. Blueprint agent variable names appear in source
    for agent in blueprint.agents:
        vname = agent.id.replace("-", "_").replace(" ", "_")
        if vname not in all_source:
            warnings.append(f"Agent variable '{vname}' not found in generated code")

    # 5. Tool stubs are defined before main()
    for tool in blueprint.tools:
        if f"def {tool.name}" not in all_source:
            errors.append(f"Tool stub function '{tool.name}' is missing")

    # 6. app.run call must be present
    if "app.run(" not in all_source:
        errors.append("Missing app.run() call")

    # 7. Entry agent variable used in app.run
    entry_var = blueprint.entry_agent_id.replace("-", "_").replace(" ", "_")
    if entry_var not in all_source:
        errors.append(f"Entry agent variable '{entry_var}' not found in source")

    total_checks = 7
    error_weight = len(errors)
    warning_weight = len(warnings) * 0.1

    score = max(0.0, 1.0 - (error_weight / total_checks) - warning_weight)
    score = round(score, 3)

    return ValidationResult(score=score, errors=errors, warnings=warnings)
