from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from level.config import Context


@dataclass(frozen=True)
class Finding:
    """
    A structured result produced by a Check.

    message: human-readable description of the issue
    fixable: whether this specific finding can be auto-fixed
    severity: classification level ("error", "warning", etc.)
    """

    message: str
    fixable: bool = True
    severity: str = "error"


@dataclass(frozen=True)
class FixResult:
    entity: Path
    check_name: str
    message: str


class CheckNotFixableError(RuntimeError):
    pass


class Check:
    """
    Base class for domain checks.

    A Check is responsible for:
    - Producing structured findings via lint()
    - Optionally applying deterministic fixes via fix()
    """

    name: str = "unnamed"

    def lint(self, context: Context, entity: Path) -> list[Finding]:
        """
        Analyze the entity and return structured findings.
        """
        raise NotImplementedError("lint method must be implemented by subclasses")

    def supports_fix(self) -> bool:
        """
        Indicates whether this check is capable of performing fixes.
        """
        return True

    def fix(self, context: Context, entity: Path) -> list[FixResult]:
        """
        Apply deterministic fixes for this entity.

        Should only mutate state when lint() would produce
        fixable findings.
        """
        if not self.supports_fix():
            raise CheckNotFixableError(f"Check '{self.name}' does not support fixing.")

        raise NotImplementedError(
            f"Check '{self.name}' supports fixing but does not implement fix()."
        )
