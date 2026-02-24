from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from level.config import Context
from level.core.canonical import rename_to_canonical
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


def _practice_slug(practice_date: date) -> str:
    return practice_date.isoformat()


def create_practice(context: Context, practice_date: date | None = None) -> Practice:
    practice_date = practice_date or date.today()
    slug = _practice_slug(practice_date)

    root = _practice_root(context)
    practice_dir = root / slug
    practice_dir.mkdir(parents=True, exist_ok=False)

    render_template_to_path(
        context=context,
        template_name="practice/start.py.tmpl",
        variables={"date": practice_date.isoformat()},
        output_path=practice_dir / "start.py",
        overwrite=False,
    )

    return Practice(date=practice_date, slug=slug)


def list_practice(context: Context) -> Iterable[Practice]:
    root = _practice_root(context)
    for child in sorted(root.iterdir()):
        if child.is_dir():
            try:
                practice_date = date.fromisoformat(child.name)
                yield Practice(date=practice_date, slug=child.name)
            except ValueError:
                continue


def lint_practice(context: Context) -> list[str]:
    issues: list[str] = []
    root = _practice_root(context)

    for child in root.iterdir():
        if not child.is_dir():
            continue
        try:
            expected = _practice_slug(date.fromisoformat(child.name))
        except ValueError:
            issues.append(f"Invalid practice directory name: {child.name}")
            continue
        if child.name != expected:
            issues.append(f"Non-canonical practice directory: {child.name}")

    return issues


def fix_practice(context: Context) -> list[str]:
    changes: list[str] = []
    root = _practice_root(context)

    for child in root.iterdir():
        if not child.is_dir():
            continue
        try:
            practice_date = date.fromisoformat(child.name)
        except ValueError:
            continue

        expected = _practice_slug(practice_date)
        if child.name != expected:
            new_path = rename_to_canonical(root, child, Path(expected))
            changes.append(f"Renamed {child.name} -> {new_path.name}")

    return changes
