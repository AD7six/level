import ast
from pathlib import Path

import pytest

COMMANDS_DIR = Path(__file__).resolve().parents[2] / "src" / "level" / "commands"


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _parse(file: Path) -> ast.Module:
    return ast.parse(file.read_text())


# ---------------------------------------------------------------------------
# rules
# ---------------------------------------------------------------------------


def test_commands_do_not_use_loops_or_comprehensions() -> None:
    """
    Command layer must not perform domain logic.
    No loops or comprehensions allowed in command files.
    """
    for file in COMMANDS_DIR.glob("*.py"):
        domain = file.stem
        tree = _parse(file)

        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                pytest.fail(
                    f"{file.name} contains loop logic. Move iteration/"
                    f"aggregation into level.domains.{domain} as a function "
                    "and call it from the command."
                )

            if isinstance(node, (ast.ListComp, ast.DictComp, ast.SetComp)):
                pytest.fail(
                    f"{file.name} contains comprehension logic. "
                    f"Implement this inside level.domains.{domain} and "
                    "expose it as a function, then call it from the command."
                )


def test_commands_do_not_aggregate_data() -> None:
    """
    Command layer must not compute metrics.
    Disallow common aggregation calls.
    """
    forbidden_calls = {
        "all",
        "any",
        "filter",
        "map",
        "max",
        "min",
        "sorted",
        "sum",
    }

    for file in COMMANDS_DIR.glob("*.py"):
        domain = file.stem
        tree = _parse(file)

        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in forbidden_calls:
                    pytest.fail(
                        f"{file.name} uses aggregation call '{node.func.id}'. "
                        f"Move this logic into level.domains.{domain} "
                        "(e.g. get_{domain}_metrics(context)) and call it "
                        "from the command."
                    )


def test_commands_do_not_import_filesystem_modules() -> None:
    """
    Command layer must not touch filesystem directly.
    """
    forbidden_roots = {"os", "pathlib", "tomllib"}

    for file in COMMANDS_DIR.glob("*.py"):
        domain = file.stem
        tree = _parse(file)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".")[0]
                    if root in forbidden_roots:
                        pytest.fail(
                            f"{file.name} imports forbidden module '{root}'. "
                            f"Filesystem logic must live in "
                            f"level.domains.{domain} or level.core, not in "
                            "the command layer."
                        )

            if isinstance(node, ast.ImportFrom) and node.module:
                root = node.module.split(".")[0]
                if root in forbidden_roots:
                    pytest.fail(
                        f"{file.name} imports forbidden module '{root}'. "
                        f"Filesystem logic must live in "
                        f"level.domains.{domain} or level.core, not in "
                        "the command layer."
                    )
