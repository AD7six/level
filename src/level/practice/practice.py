from __future__ import annotations

import tomllib
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from level.checks.base import Finding, FixResult
from level.checks.canonical_location import CanonicalLocation
from level.checks.meta_readable import MetaReadable
from level.checks.meta_schema import MetaSchema
from level.config import Context
from level.core.canonical import build_slug
from level.core.doctor import Domain, fix_domain, lint_domain
from level.core.meta import write_meta_toml
from level.templates.loader import TemplateNotFoundError
from level.templates.renderer import render_template_to_path


@dataclass(frozen=True)
class Practice:
    date: date
    slug: str


def _practice_root(context: Context) -> Path:
    assert context.config.data_dir is not None
    root = context.config.data_dir / "practice"
    root.mkdir(parents=True, exist_ok=True)
    return root


def _practice_slug(practice_date: date, name: str) -> str:
    return build_slug(practice_date, name)


def create_practice(
    context: Context,
    practice_date: date | None = None,
    name: str = "session",
) -> Practice:
    practice_date = practice_date or date.today()
    root = _practice_root(context)

    base_slug = _practice_slug(practice_date, name)
    slug = base_slug
    counter = 1

    # Handle collisions by appending numeric suffix
    while (root / slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    practice_dir = root / slug
    practice_dir.mkdir(parents=True, exist_ok=False)

    # Write meta.toml
    write_meta_toml(
        practice_dir / "meta.toml",
        {
            "date": practice_date,
            "name": name,
        },
    )

    # Prefer drill-specific template if it exists, otherwise fallback to default
    specific_template = f"practice/{name}.py.tmpl"
    output_file = practice_dir / "00-start.py"

    try:
        render_template_to_path(
            context=context,
            template_name=specific_template,
            variables={"date": practice_date.isoformat()},
            output_path=output_file,
            overwrite=False,
        )
    except TemplateNotFoundError:
        render_template_to_path(
            context=context,
            template_name="practice/default.py.tmpl",
            variables={"date": practice_date.isoformat()},
            output_path=output_file,
            overwrite=False,
        )

    return Practice(date=practice_date, slug=slug)


def list_practice(context: Context) -> Iterable[Practice]:
    root = _practice_root(context)
    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue

        parts = child.name.split("-", 3)
        if len(parts) < 3:
            continue

        try:
            practice_date = date.fromisoformat("-".join(parts[:3]))
        except ValueError:
            continue

        yield Practice(date=practice_date, slug=child.name)


def _practice_finder(context: Context) -> Iterable[Path]:
    root = _practice_root(context)
    for child in root.iterdir():
        if child.is_dir():
            yield child


def _practice_canonical_rel(context: Context, entity: Path) -> Path | None:
    meta_path = entity / "meta.toml"
    if not meta_path.exists():
        return None

    try:
        with meta_path.open("rb") as f:
            raw = tomllib.load(f)
    except Exception:
        return None

    practice_date = raw.get("date")
    name = raw.get("name")

    if not practice_date or not name:
        return None

    try:
        parsed_date = date.fromisoformat(str(practice_date))
    except ValueError:
        return None

    root = _practice_root(context)
    expected_slug = build_slug(parsed_date, str(name))
    return root / expected_slug


_practice_domain = Domain(
    finder=_practice_finder,
    checks=[
        MetaReadable(),
        MetaSchema(),
        CanonicalLocation(
            canonical_rel=_practice_canonical_rel,
            root_resolver=_practice_root,
        ),
    ],
)


def lint_practice(context: Context) -> list[Finding]:
    return lint_domain(context, _practice_domain)


def fix_practice(context: Context) -> list[FixResult]:
    return fix_domain(context, _practice_domain)
