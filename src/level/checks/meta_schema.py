from pathlib import Path

from level.config import Context

from .base import Check, Finding


class MetaSchema(Check):
    name = "meta_schema"

    def lint(self, context: Context, entity: Path) -> list[Finding]:
        return []
