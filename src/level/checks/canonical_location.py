from collections.abc import Callable
from pathlib import Path

from level.config import Context
from level.core.canonical import rename_to_canonical

from .base import Check, Finding, FixResult

CanonicalRel = Callable[[Context, Path], Path | None]
RootResolver = Callable[[Context], Path]


class CanonicalLocation(Check):
    name = "canonical_location"

    def __init__(
        self,
        canonical_rel: CanonicalRel,
        root_resolver: RootResolver,
    ) -> None:
        self._canonical_rel = canonical_rel
        self._root_resolver = root_resolver

    def lint(self, context: Context, entity: Path) -> list[Finding]:
        expected = self._canonical_rel(context, entity)
        if expected is None:
            return []

        if entity.resolve() == expected.resolve():
            return []

        return [
            Finding(
                f"Non-canonical directory: {entity.name} (expected {expected.name})",
                fixable=True,
            )
        ]

    def fix(self, context: Context, entity: Path) -> list[FixResult]:
        expected = self._canonical_rel(context, entity)
        if expected is None:
            return []

        if entity.resolve() == expected.resolve():
            return []

        root = self._root_resolver(context)
        new_path = rename_to_canonical(root, entity, Path(expected.name))

        return [
            FixResult(
                entity=entity,
                check_name=self.name,
                message=f"Renamed {entity.name} -> {new_path.name}",
            )
        ]
