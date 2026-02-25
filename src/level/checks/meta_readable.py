import tomllib
from pathlib import Path

from level.config import Context

from .base import Check, Finding


class MetaReadable(Check):
    name = "meta_readable"

    def lint(self, context: Context, entity: Path) -> list[Finding]:
        meta_path = entity / "meta.toml"

        if not meta_path.exists():
            return [
                Finding(
                    f"meta.toml missing in: {entity.name}",
                    fixable=False,
                )
            ]

        try:
            with meta_path.open("rb") as f:
                tomllib.load(f)
        except Exception:
            return [
                Finding(
                    f"Invalid meta.toml in: {entity.name}",
                    fixable=False,
                )
            ]

        return []
