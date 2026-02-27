from __future__ import annotations

import tomllib
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from level.checks.base import Finding, FixResult
from level.checks.canonical_location import CanonicalLocation
from level.checks.meta_readable import MetaReadable
from level.checks.meta_schema import MetaSchema
from level.config import Context, get_data_root
from level.core.canonical import build_slug, resolve_collision
from level.core.doctor import Domain, fix_domain, lint_domain
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

    root = _applications_root(context)
    base_rel = _canonical_rel_path("drafts", meta)
    path = resolve_collision(root, base_rel)
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

    root = _applications_root(context)
    base_rel = _canonical_rel_path(new_state, meta)
    target = resolve_collision(
        root,
        base_rel,
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


def list_application_rows(
    context: Context,
    *,
    state: str | None = None,
    include_terminal: bool = False,
) -> list[dict[str, str]]:
    applications = list(list_applications(context, state=state))

    # Filter terminal states if needed
    if not include_terminal:
        from .schema import TERMINAL_STATES

        applications = [app for app in applications if app.state not in TERMINAL_STATES]

    # Sort by state, then date (desc), then slug
    applications.sort(
        key=lambda app: (
            app.state,
            app.created_at or "",
            app.slug,
        ),
        reverse=True,
    )

    return [
        {
            "state": app.state,
            "date": app.created_at or "",
            "company": app.company or "",
            "role": app.role or "",
            "slug": app.slug,
        }
        for app in applications
    ]


# ---------------------------------------------------------------------------
# Doctor / Lint
# ---------------------------------------------------------------------------


def _applications_finder(context: Context) -> list[Path]:
    root = _applications_root(context)
    if not root.exists():
        return []
    return [meta.parent for meta in root.rglob("meta.toml")]


def _applications_canonical_rel(context: Context, entity: Path) -> Path | None:
    try:
        raw = _load_meta(entity)
        meta = ApplicationMeta.from_dict(raw)
    except Exception:
        return None

    rel = entity.relative_to(_applications_root(context))
    parts = rel.parts

    if not parts:
        return None

    state = parts[0]
    if state not in STATES:
        return None

    root = _applications_root(context)
    expected_rel = _canonical_rel_path(state, meta)
    return root / expected_rel


_applications_domain = Domain(
    finder=_applications_finder,
    checks=[
        MetaReadable(),
        MetaSchema(),
        CanonicalLocation(
            canonical_rel=_applications_canonical_rel,
            root_resolver=_applications_root,
        ),
    ],
)


def lint_applications(context: Context) -> list[Finding]:
    return lint_domain(context, _applications_domain)


def fix_applications(context: Context) -> list[FixResult]:
    return fix_domain(context, _applications_domain)
