from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path

from level.config import Context

# An entity is represented by its root directory Path
Entity = Path

# Finder returns iterable of entities for a domain
Finder = Callable[[Context], Iterable[Entity]]

# Linter returns a list of issue strings for a single entity
Linter = Callable[[Context, Entity], list[str]]

# Fixer returns a list of action strings for a single entity
Fixer = Callable[[Context, Entity], list[str]]


@dataclass
class DomainDoctor:
    finder: Finder
    linters: list[Linter]
    fixers: list[Fixer]


def lint_domain(context: Context, doctor: DomainDoctor) -> list[str]:
    """
    Run all linters for all entities in the domain.

    Returns a flat list of issue strings.
    """
    issues: list[str] = []

    for entity in doctor.finder(context):
        for linter in doctor.linters:
            try:
                results = linter(context, entity)
                if results:
                    issues.extend(results)
            except Exception as e:
                issues.append(f"Linter error in {entity}: {e}")

    return issues


def fix_domain(context: Context, doctor: DomainDoctor) -> list[str]:
    """
    Run all fixers for all entities in the domain.

    Returns a flat list of action strings.
    """
    actions: list[str] = []

    for entity in doctor.finder(context):
        for fixer in doctor.fixers:
            try:
                results = fixer(context, entity)
                if results:
                    actions.extend(results)
            except Exception as e:
                actions.append(f"Fixer error in {entity}: {e}")

    return actions
