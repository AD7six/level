from collections.abc import Callable
from pathlib import Path

from level.config import Context
from level.core.canonical import (
    is_valid_suffixed_slug,
    rename_to_canonical,
    resolve_collision,
)

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

        base = expected.name
        name = entity.name

        # Exact canonical match
        if entity.resolve() == expected.resolve():
            return []

        # Allow valid numeric suffixes
        if is_valid_suffixed_slug(base, name):
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

        base = expected.name
        name = entity.name

        # Already canonical or valid suffixed
        if entity.resolve() == expected.resolve() or is_valid_suffixed_slug(base, name):
            return []

        root = self._root_resolver(context)
        target = resolve_collision(root, Path(expected.name), current_path=entity)
        new_path = rename_to_canonical(root, entity, Path(target.name))

        return [
            FixResult(
                entity=new_path,
                check_name=self.name,
                message=f"Renamed {entity.name} -> {new_path.name}",
            )
        ]
