from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from level.config import Context
from level.core.canonical import build_slug, rename_to_canonical
from level.templates.renderer import render_template_to_path
from level.templates.loader import TemplateNotFoundError


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


def lint_practice(context: Context) -> list[str]:
    issues: list[str] = []
    root = _practice_root(context)

    for child in root.iterdir():
        if not child.is_dir():
            continue

        parts = child.name.split("-", 3)
        if len(parts) < 4:
            issues.append(f"Invalid practice directory name: {child.name}")
            continue

        try:
            practice_date = date.fromisoformat("-".join(parts[:3]))
        except ValueError:
            issues.append(f"Invalid practice directory name: {child.name}")
            continue

        # Canonical slug should start with YYYY-MM-DD-
        if not child.name.startswith(practice_date.isoformat() + "-"):
            issues.append(f"Non-canonical practice directory: {child.name}")

    return issues


def fix_practice(context: Context) -> list[str]:
    changes: list[str] = []
    root = _practice_root(context)

    for child in root.iterdir():
        if not child.is_dir():
            continue

        parts = child.name.split("-", 3)
        if len(parts) < 4:
            continue

        try:
            practice_date = date.fromisoformat("-".join(parts[:3]))
        except ValueError:
            continue

        # Rebuild canonical slug from extracted date and remainder
        name_part = child.name[len(practice_date.isoformat()) + 1 :]
        expected = build_slug(practice_date, name_part)

        if child.name != expected:
            new_path = rename_to_canonical(root, child, Path(expected))
            changes.append(f"Renamed {child.name} -> {new_path.name}")

    return changes
