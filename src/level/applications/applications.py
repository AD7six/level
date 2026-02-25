from __future__ import annotations

import tomllib
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from level.config import Context, get_data_root
from level.core.canonical import (
    build_slug,
    is_canonical_location,
)
from level.core.meta import write_meta_toml
from level.templates.renderer import render_template_directory

from .schema import STATES

# ---------------------------------------------------------------------------
# State machine
# ---------------------------------------------------------------------------

TRANSITIONS: dict[str, set[str]] = {
    "drafts": {"applied", "withdrawn"},
    "applied": {"interviewing", "stalled", "rejected", "withdrawn"},
    "interviewing": {"offer", "stalled", "rejected", "withdrawn"},
    "offer": {"withdrawn"},
    "stalled": {"interviewing", "withdrawn", "rejected"},
    "rejected": set(),
    "withdrawn": set(),
}

# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Application:
    slug: str
    state: str
    path: Path
    company: str
    role: str
    created_at: str


# ---------------------------------------------------------------------------
# Meta Model
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ApplicationMeta:
    company: str
    role: str
    created_at: str

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> ApplicationMeta:
        return cls(
            company=str(data.get("company", "")),
            role=str(data.get("role", "")),
            created_at=str(data.get("created_at", "")),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "company": self.company,
            "role": self.role,
            "created_at": self.created_at,
        }


# ---------------------------------------------------------------------------
# Canonical path helpers
# ---------------------------------------------------------------------------


def _canonical_slug_from_meta(meta: ApplicationMeta) -> str:
    # Opinionated canonical format: YYYY-MM-DD-{name}
    return build_slug(
        date.fromisoformat(meta.created_at),
        meta.company,
    )


def _canonical_rel_path(state: str, meta: ApplicationMeta) -> Path:
    return Path(state) / _canonical_slug_from_meta(meta)


def _resolve_target_path(
    context: Context,
    state: str,
    meta: ApplicationMeta,
    current_path: Path | None = None,
) -> Path:
    """
    Resolve a usable filesystem path for an application.

    - Uses canonical slug
    - Appends numeric suffix if collision occurs
    - Ignores collision with current_path (for fix operations)
    """
    root = _applications_root(context)
    base_rel = _canonical_rel_path(state, meta)
    target = root / base_rel

    if current_path is not None and current_path == target:
        return target

    final_target = target
    counter = 1

    while final_target.exists() and final_target != current_path:
        final_target = target.parent / f"{target.name}-{counter}"
        counter += 1

    return final_target


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_meta(path: Path) -> dict[str, object]:
    toml_path = path / "meta.toml"

    if toml_path.exists():
        with toml_path.open("rb") as f:
            return tomllib.load(f)

    raise ValueError(f"No meta.toml file found in {path}")


def _applications_root(context: Context) -> Path:
    return get_data_root(context) / "applications"


def _state_dir(context: Context, state: str) -> Path:
    if state not in STATES:
        raise ValueError(f"Invalid state: {state}")
    return _applications_root(context) / state


def _application_path(context: Context, slug: str) -> Path | None:
    root = _applications_root(context)
    for state in STATES:
        candidate = root / state / slug
        if candidate.exists():
            return candidate
    return None


def _ensure_structure(context: Context) -> None:
    root = _applications_root(context)
    for state in STATES:
        (root / state).mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def create_application(
    context: Context,
    company: str,
    role: str,
    date: str,
    resume_template: str = "base",
) -> Application:
    _ensure_structure(context)

    company = company.strip().title()
    role = role.strip().title()

    meta = ApplicationMeta(
        company=company,
        role=role,
        created_at=date,
    )

    path = _resolve_target_path(context, "drafts", meta)
    slug = path.name

    if path.exists():
        raise ValueError(f"Application already exists: {slug}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.mkdir(parents=True)

    write_meta_toml(path / "meta.toml", meta)

    # Render application templates
    context_data = {
        "company": company,
        "role": role,
        "date": date,
        "state": "drafts",
        "slug": slug,
    }

    render_template_directory(
        context=context,
        template_subdir="application",
        variables=context_data,
        output_dir=path,
    )

    # Render single resume template (one resume per application)
    from level.templates.renderer import render_template_to_path

    resume_output = path / "resume.md"

    render_template_to_path(
        context=context,
        template_name=f"resume/{resume_template}.md.tmpl",
        variables=context_data,
        output_path=resume_output,
        strict=False,
    )

    return Application(
        slug=slug,
        state="drafts",
        path=path,
        company=company,
        role=role,
        created_at=date,
    )


def list_applications(
    context: Context, state: str | None = None
) -> Iterable[Application]:
    root = _applications_root(context)

    states = {state} if state else STATES

    for s in states:
        if s not in STATES:
            raise ValueError(f"Invalid state: {s}")

        state_dir = root / s
        if not state_dir.exists():
            continue

        for entry in sorted(state_dir.iterdir(), key=lambda e: e.name):
            if not entry.is_dir():
                continue

            if (entry / "meta.toml").exists():
                raw = _load_meta(entry)
                meta = ApplicationMeta.from_dict(raw)
                yield Application(
                    slug=entry.name,
                    state=s,
                    path=entry,
                    company=meta.company,
                    role=meta.role,
                    created_at=meta.created_at,
                )


def get_application(context: Context, slug: str) -> Application:
    path = _application_path(context, slug)
    if path is None:
        raise ValueError(f"Application not found: {slug}")

    state = path.parent.name
    raw = _load_meta(path)
    meta = ApplicationMeta.from_dict(raw)

    return Application(
        slug=slug,
        state=state,
        path=path,
        company=meta.company,
        role=meta.role,
        created_at=meta.created_at,
    )


def move_application(context: Context, slug: str, new_state: str) -> Application:
    if new_state not in STATES:
        raise ValueError(f"Invalid state: {new_state}")

    app = get_application(context, slug)

    if new_state not in TRANSITIONS[app.state]:
        raise ValueError(f"Invalid transition: {app.state} → {new_state}")

    raw = _load_meta(app.path)
    meta = ApplicationMeta.from_dict(raw)

    target = _resolve_target_path(
        context,
        new_state,
        meta,
        current_path=app.path,
    )

    target.parent.mkdir(parents=True, exist_ok=True)
    app.path.rename(target)

    return Application(
        slug=target.name,
        state=new_state,
        path=target,
        company=meta.company,
        role=meta.role,
        created_at=meta.created_at,
    )


# ---------------------------------------------------------------------------
# Doctor / Lint
# ---------------------------------------------------------------------------


def lint_applications(context: Context) -> list[str]:
    issues: list[str] = []
    root = _applications_root(context)

    if not root.exists():
        return issues

    for meta_file in root.rglob("meta.toml"):
        app_dir = meta_file.parent
        rel = app_dir.relative_to(root)
        parts = rel.parts

        if not parts:
            continue

        state = parts[0]

        if state not in STATES:
            issues.append(f"Application '{rel}' has unknown state: {state}")
            continue

        raw = _load_meta(app_dir)
        meta = ApplicationMeta.from_dict(raw)

        expected_rel = _canonical_rel_path(state, meta)

        if is_canonical_location(root, app_dir, expected_rel):
            continue

        expected_slug = expected_rel.name
        actual_slug = rel.name

        # Allow numeric suffixes for collision resolution
        if actual_slug == expected_slug:
            continue

        if actual_slug.startswith(expected_slug + "-"):
            suffix = actual_slug[len(expected_slug) + 1 :]
            if suffix.isdigit():
                continue

        issues.append(
            f"Application '{rel}' is not in canonical location '{expected_rel}'"
        )

    return issues


def fix_applications(context: Context) -> list[str]:
    actions: list[str] = []
    root = _applications_root(context)

    if not root.exists():
        return actions

    for meta_file in root.rglob("meta.toml"):
        app_dir = meta_file.parent
        rel = app_dir.relative_to(root)
        parts = rel.parts

        if not parts:
            continue

        state = parts[0]

        if state not in STATES:
            continue

        raw = _load_meta(app_dir)
        meta = ApplicationMeta.from_dict(raw)

        target = _resolve_target_path(context, state, meta, current_path=app_dir)

        if app_dir == target:
            continue

        target.parent.mkdir(parents=True, exist_ok=True)
        app_dir.rename(target)

        actions.append(f"Moved {rel} → {target.relative_to(root)}")

    return actions
