from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path

from level.config import Context

Entity = Path
Finder = Callable[[Context], Iterable[Entity]]


# A Check encapsulates lint + fix behavior for a single invariant.
@dataclass
class Check:
    lint: Callable[[Context, Entity], list[str]]
    fix: Callable[[Context, Entity], list[str]]


@dataclass
class Domain:
    """
    Domain contract.

    Each domain must provide:
    - finder: how to enumerate entities
    - checks: list of invariant checks to apply
    """

    finder: Finder
    checks: list[Check]


def lint_domain(context: Context, domain: Domain) -> list[str]:
    issues: list[str] = []

    for entity in domain.finder(context):
        for check in domain.checks:
            results = check.lint(context, entity)
            if results:
                issues.extend(results)

    return issues


def fix_domain(context: Context, domain: Domain) -> list[str]:
    actions: list[str] = []

    for entity in domain.finder(context):
        for check in domain.checks:
            results = check.fix(context, entity)
            if results:
                actions.extend(results)

    return actions
