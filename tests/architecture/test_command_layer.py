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
        tree = _parse(file)

        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                pytest.fail(f"{file.name} contains loop logic")

            if isinstance(node, (ast.ListComp, ast.DictComp, ast.SetComp)):
                pytest.fail(f"{file.name} contains comprehension logic")


def test_commands_do_not_aggregate_data() -> None:
    """
    Command layer must not compute metrics.
    Disallow common aggregation calls.
    """
    forbidden_calls = {"sum", "sorted", "min", "max"}

    for file in COMMANDS_DIR.glob("*.py"):
        tree = _parse(file)

        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in forbidden_calls:
                    pytest.fail(f"{file.name} uses aggregation call '{node.func.id}'")


def test_commands_do_not_import_filesystem_modules() -> None:
    """
    Command layer must not touch filesystem directly.
    """
    forbidden_roots = {"os", "pathlib", "tomllib"}

    for file in COMMANDS_DIR.glob("*.py"):
        tree = _parse(file)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".")[0]
                    if root in forbidden_roots:
                        pytest.fail(f"{file.name} imports forbidden module '{root}'")

            if isinstance(node, ast.ImportFrom) and node.module:
                root = node.module.split(".")[0]
                if root in forbidden_roots:
                    pytest.fail(f"{file.name} imports forbidden module '{root}'")
