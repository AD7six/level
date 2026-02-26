import ast
from pathlib import Path

import pytest

COMMANDS_DIR = Path(__file__).resolve().parents[2] / "src" / "level" / "commands"

COMMAND_DOMAIN_MAP = {
    "application": "applications",
    "plan": "plan",
    "practice": "practice",
    "resume": "resumes",
    "review": "reviews",
}


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _parse(file: Path) -> ast.Module:
    return ast.parse(file.read_text())


def _domain_command_files():
    """
    Yield public domain command entrypoint modules only.
    Skip private helpers (e.g. _doctor.py).
    And commands that do not have a corresponding domain mapping.
    """
    for file in COMMANDS_DIR.glob("*.py"):
        if file.name.startswith("_"):
            continue

        domain = COMMAND_DOMAIN_MAP.get(file.stem)
        if not domain:
            continue

        yield file


# ---------------------------------------------------------------------------
# rules
# ---------------------------------------------------------------------------


def test_commands_do_not_use_loops_or_comprehensions() -> None:
    """
    Command layer must not perform domain logic.
    No loops or comprehensions allowed in command files.
    """
    for file in _domain_command_files():

        command_name = file.stem
        domain = COMMAND_DOMAIN_MAP.get(command_name)

        tree = _parse(file)
        source = file.read_text()
        allow_override = "# architecture: allow" in source

        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                if not allow_override:
                    pytest.fail(
                        f"{file.name} contains loop logic. Move iteration/"
                        f"aggregation into level.domains.{domain} as a function "
                        "and call it from the command."
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
        "next",
    }

    for file in _domain_command_files():
        command_name = file.stem
        domain = COMMAND_DOMAIN_MAP.get(command_name)

        tree = _parse(file)
        source = file.read_text()
        allow_override = "# architecture: allow" in source

        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in forbidden_calls:
                    if not allow_override:
                        pytest.fail(
                            f"{file.name} uses aggregation call '{node.func.id}'. "
                            f"Expose a function in level.domains.{domain} and call it "
                            "from the command."
                        )
            if isinstance(node, ast.Lambda):
                if not allow_override:
                    pytest.fail(
                        f"{file.name} contains lambda. Domain logic should live "
                        f"in level.domains.{domain}."
                    )


def test_commands_do_not_import_filesystem_modules() -> None:
    """
    Command layer must not touch filesystem directly.
    """
    forbidden_roots = {"os", "pathlib", "tomllib"}

    for file in _domain_command_files():
        command_name = file.stem
        domain = COMMAND_DOMAIN_MAP.get(command_name)

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
