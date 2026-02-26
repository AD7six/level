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
                pytest.fail(
                    f"{file.name} contains loop logic. Move iteration/aggregation into the appropriate domain module (level.domains.<x>) as a function and call that from the command."
                )

            if isinstance(node, (ast.ListComp, ast.DictComp, ast.SetComp)):
                pytest.fail(
                    f"{file.name} contains comprehension logic. Implement this data processing inside level.domains.<x> and expose it as a function, then call it from the command layer."
                )


def test_commands_do_not_aggregate_data() -> None:
    """
    Command layer must not compute metrics.
    Disallow common aggregation calls.
    """
    forbidden_calls = {
        "all"
        "any",
        "filter",
        "map",
        "max",
        "min", 
        "sorted", 
        "sum", 
    }

    for file in COMMANDS_DIR.glob("*.py"):
        tree = _parse(file)

        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in forbidden_calls:
                    pytest.fail(
                        f"{file.name} uses aggregation call '{node.func.id}'. Aggregation belongs in level.domains.<x> (e.g. get_<thing>_metrics(context)). Move this logic into the domain and call it from the command."
                    )


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
                        pytest.fail(
                            f"{file.name} imports forbidden module '{root}'. Filesystem and parsing logic must live in level.domains.<x> or level.core, not in the command layer."
                        )

            if isinstance(node, ast.ImportFrom) and node.module:
                root = node.module.split(".")[0]
                if root in forbidden_roots:
                    pytest.fail(
                        f"{file.name} imports forbidden module '{root}'. Filesystem and parsing logic must live in level.domains.<x> or level.core, not in the command layer."
                    )
