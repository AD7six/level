from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path

from level.checks.base import Check, Finding, FixResult
from level.config import Context

Entity = Path
Finder = Callable[[Context], Iterable[Entity]]


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


def lint_domain(context: Context, domain: Domain) -> list[Finding]:
    issues: list[Finding] = []

    for entity in domain.finder(context):
        for check in domain.checks:
            findings = check.lint(context, entity)
            for finding in findings:
                issues.append(finding)

    return issues


def fix_domain(context: Context, domain: Domain) -> list[FixResult]:
    actions: list[FixResult] = []

    for entity in domain.finder(context):
        for check in domain.checks:
            if not check.supports_fix():
                continue

            findings = check.lint(context, entity)

            # Only attempt fix if there are fixable findings
            if not any(f.fixable for f in findings):
                continue

            results = check.fix(context, entity)
            if results:
                actions.extend(results)

    return actions
