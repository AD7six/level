from __future__ import annotations

import tomllib
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Protocol

from level.checks.base import Finding, FixResult
from level.checks.canonical_location import CanonicalLocation
from level.checks.meta_readable import MetaReadable
from level.checks.meta_schema import MetaSchema
from level.config import Context
from level.core.canonical import build_slug, resolve_collision
from level.core.doctor import Domain, fix_domain, lint_domain
from level.core.meta import write_meta_toml
from level.templates.loader import list_templates
from level.templates.renderer import render_template_to_path


class EditorOpener(Protocol):
    def __call__(self, path: Path, *, auto_open: bool, editor: str | None) -> bool: ...


@dataclass(frozen=True)
class Practice:
    date: date
    slug: str
    path: Path | None = None
    template: str | None = None
    start_filename: str | None = None

    def start_file(self) -> Path | None:
        if self.path is None or self.start_filename is None:
            return None
        return self.path / self.start_filename


def _practice_root(context: Context) -> Path:
    assert context.config.data_dir is not None
    root = context.config.data_dir / "practice"
    root.mkdir(parents=True, exist_ok=True)
    return root


def _practice_slug(practice_date: date, name: str) -> str:
    return build_slug(practice_date, name)


def list_practice_types(context: Context) -> list[str]:
    """Return distinct practice types derived from template paths."""
    types: set[str] = set()

    for tmpl in list_templates(context, "practice"):
        parts = tmpl.split("/")
        # Only consider templates inside a type directory (e.g. code/default.py.tmpl)
        if len(parts) > 1:
            types.add(parts[0])

    return sorted(types)


def create_practice(
    context: Context,
    practice_date: date | None = None,
    practice_type: str = "code",
    name: str = "session",
) -> Practice:
    practice_date = practice_date or date.today()
    root = _practice_root(context)

    base_slug = _practice_slug(practice_date, name)
    base_rel = Path(base_slug)
    practice_dir = resolve_collision(root, base_rel)
    slug = practice_dir.name
    practice_dir.mkdir(parents=True, exist_ok=False)

    # Resolve template directory (name-specific or default)
    template_base = f"practice/{practice_type}"
    available_templates = list_templates(context, template_base)

    # Extract top-level template directories
    template_dirs: set[str] = set()
    for tmpl in available_templates:
        parts = Path(tmpl).parts
        if parts:
            template_dirs.add(parts[0])

    if name in template_dirs:
        template_dir = f"{template_base}/{name}"
    else:
        template_dir = f"{template_base}/default"

    template_used = template_dir

    # Render all files within the template directory
    rendered_start_file: str | None = None

    for tmpl in available_templates:
        parts = Path(tmpl).parts
        if not parts:
            continue
        if parts[0] != Path(template_dir).name:
            continue

        rel_path = Path(*parts[1:])
        output_path = practice_dir / rel_path.with_suffix("")

        render_template_to_path(
            context=context,
            template_name=f"{template_base}/{tmpl}",
            variables={"date": practice_date.isoformat()},
            output_path=output_path,
            overwrite=False,
        )

        if output_path.name.startswith("00-"):
            rendered_start_file = output_path.name

    if rendered_start_file is None:
        raise RuntimeError(
            f"Template '{template_dir}' did not produce a 00-* start file."
        )

    # Write meta.toml (template recorded for future use)
    write_meta_toml(
        practice_dir / "meta.toml",
        {
            "date": practice_date,
            "type": practice_type,
            "name": name,
            "template": template_used,
            "start_file": rendered_start_file,
            "reviewed_count": 0,
            "last_reviewed": None,
        },
    )

    return Practice(
        date=practice_date,
        slug=slug,
        path=practice_dir,
        template=template_used,
        start_filename=rendered_start_file,
    )


def list_practice(context: Context) -> Iterable[Practice]:
    root = _practice_root(context)
    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue

        meta_path = child / "meta.toml"
        if not meta_path.exists():
            continue

        try:
            with meta_path.open("rb") as f:
                raw = tomllib.load(f)
        except Exception:
            continue

        practice_date = raw.get("date")
        if not practice_date:
            continue

        try:
            parsed_date = date.fromisoformat(str(practice_date))
        except ValueError:
            continue

        yield Practice(
            date=parsed_date,
            slug=child.name,
            path=child,
            template=raw.get("template"),
            start_filename=raw.get("start_file"),
        )


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


def review_practice(context: Context, slug: str) -> None:
    """
    Increment review frequency metadata for a practice session.
    """
    root = _practice_root(context)
    practice_dir = root / slug

    meta_path = practice_dir / "meta.toml"
    if not meta_path.exists():
        raise FileNotFoundError(f"Practice session not found: {slug}")

    with meta_path.open("rb") as f:
        raw = tomllib.load(f)

    reviewed_count = int(raw.get("reviewed_count", 0)) + 1
    raw["reviewed_count"] = reviewed_count
    raw["last_reviewed"] = date.today()

    write_meta_toml(meta_path, raw)


def review_latest_attempt(
    context: Context,
    slug: str,
    *,
    open_editor: EditorOpener,
    auto_open: bool,
    editor: str | None,
) -> bool:
    """
    Locate the latest attempt file for a practice session, open it in the editor,
    and update review metadata if the edit session completes successfully.
    """
    root = _practice_root(context)
    practice_dir = root / slug

    if not practice_dir.exists():
        raise FileNotFoundError(f"Practice session not found: {slug}")

    attempt_files = sorted(
        (p for p in practice_dir.glob("*.py") if p.name[:2].isdigit()),
        key=lambda p: p.name,
    )

    if not attempt_files:
        raise FileNotFoundError("No attempt files found for this practice session.")

    latest = attempt_files[-1]

    success = open_editor(latest, auto_open=auto_open, editor=editor)

    if success:
        review_practice(context, slug)

    return success


def practice_metrics(context: Context) -> dict[str, int]:
    """
    Minimal stats integration hook for practice domain.
    Returns basic aggregate metrics.
    """
    total_sessions = 0
    total_reviews = 0

    for entity in _practice_finder(context):
        total_sessions += 1
        meta_path = entity / "meta.toml"
        if not meta_path.exists():
            continue

        try:
            with meta_path.open("rb") as f:
                raw = tomllib.load(f)
        except Exception:
            continue

        total_reviews += int(raw.get("reviewed_count", 0))

    return {
        "total_sessions": total_sessions,
        "total_reviews": total_reviews,
    }
