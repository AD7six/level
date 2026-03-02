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
# policy
# ---------------------------------------------------------------------------

FORBIDDEN_AGGREGATION_CALLS = {
    "all",
    "any",
    "filter",
    "map",
    "max",
    "min",
    "sum",
    "next",
}

FORBIDDEN_FS_IMPORT_ROOTS = {"os", "pathlib", "tomllib"}


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


def _fail(file: Path, node: ast.AST, message: str) -> None:
    lineno = getattr(node, "lineno", "?")
    pytest.fail(f"src/level/commands/{file.name}:{lineno} {message}")


def _assert_no_loops(file: Path, node: ast.AST, source: str, domain: str) -> None:
    if not isinstance(node, ast.For):
        return

    line = source.splitlines()[node.lineno - 1]
    _fail(
        file,
        node,
        f"contains loop logic:\n"
        f"    {line}\n\n"
        f"Move iteration/aggregation into "
        f"level.domains.{domain} or a presentation helper "
        "and call it from the command.",
    )


def _assert_no_aggregation(file: Path, node: ast.AST, source: str, domain: str) -> None:
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        if node.func.id in FORBIDDEN_AGGREGATION_CALLS:
            _fail(
                file,
                node,
                f"uses aggregation call '{node.func.id}'. "
                f"Expose a function in level.domains.{domain} or a "
                "presentation helper and call it from the command.",
            )


def _assert_no_filesystem_imports(
    file: Path, node: ast.AST, source: str, domain: str
) -> None:
    if isinstance(node, ast.Import):
        for alias in node.names:
            root = alias.name.split(".")[0]
            if root in FORBIDDEN_FS_IMPORT_ROOTS:
                _fail(
                    file,
                    node,
                    f"imports forbidden module '{root}'. "
                    f"Filesystem logic must live in "
                    f"level.domains.{domain} or level.core, not in "
                    "the command layer.",
                )

    if isinstance(node, ast.ImportFrom) and node.module:
        root = node.module.split(".")[0]
        if root in FORBIDDEN_FS_IMPORT_ROOTS:
            _fail(
                file,
                node,
                f"imports forbidden module '{root}'. "
                f"Filesystem logic must live in "
                f"level.domains.{domain} or level.core, not in "
                "the command layer.",
            )


RULES = [
    _assert_no_loops,
    _assert_no_aggregation,
    _assert_no_filesystem_imports,
]

# ---------------------------------------------------------------------------
# The test
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("file", list(_domain_command_files()))
def test_command_file_architecture(file: Path) -> None:
    """
    Each command file must respect architectural boundaries.
    Rules are evaluated per file and fail fast.
    """

    command_name = file.stem
    domain = COMMAND_DOMAIN_MAP.get(command_name)
    assert domain is not None, f"No domain mapping for {file.name}"

    tree = _parse(file)
    source = file.read_text()

    for node in ast.walk(tree):
        for rule in RULES:
            rule(file, node, source, domain)
