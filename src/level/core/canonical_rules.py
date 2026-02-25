from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import tomllib

from level.config import Context
from level.core.canonical import rename_to_canonical


def meta_exists_and_valid_lint(context: Context, entity: Path) -> list[str]:
    meta_path = entity / "meta.toml"

    if not meta_path.exists():
        return [f"meta.toml missing in: {entity.name}"]

    try:
        with meta_path.open("rb") as f:
            tomllib.load(f)
    except Exception:
        return [f"Invalid meta.toml in: {entity.name}"]

    return []


def meta_exists_and_valid_fix(context: Context, entity: Path) -> list[str]:
    # Meta validation is lint-only for now.
    return []


# canonical_rel returns the expected absolute path for the entity,
# or None if canonical location cannot be determined.
CanonicalRel = Callable[[Context, Path], Path | None]
RootResolver = Callable[[Context], Path]


def canonical_location_lint(
    context: Context,
    entity: Path,
    *,
    canonical_rel: CanonicalRel,
) -> list[str]:
    """
    Generic canonical location linter.

    Compares the entity's current path with its expected canonical path
    derived from domain-specific canonical_rel().
    """
    issues: list[str] = []

    expected = canonical_rel(context, entity)
    if expected is None:
        return issues

    if entity.resolve() == expected.resolve():
        return issues

    issues.append(f"Non-canonical directory: {entity.name} (expected {expected.name})")

    return issues


def canonical_location_fix(
    context: Context,
    entity: Path,
    *,
    canonical_rel: CanonicalRel,
    root_resolver: RootResolver,
) -> list[str]:
    """
    Generic canonical location fixer.

    Renames entity to its canonical path if necessary.
    """
    changes: list[str] = []

    expected = canonical_rel(context, entity)
    if expected is None:
        return changes

    if entity.resolve() == expected.resolve():
        return changes

    root = root_resolver(context)

    # rename_to_canonical expects the target as a relative path from root
    new_path = rename_to_canonical(root, entity, Path(expected.name))

    changes.append(f"Renamed {entity.name} -> {new_path.name}")

    return changes
