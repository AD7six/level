from __future__ import annotations

import json
import tomllib
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path

from level.config import Context, get_data_root

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
    def from_dict(cls, data: Mapping[str, object]) -> "ApplicationMeta":
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
# Helpers
# ---------------------------------------------------------------------------


def _write_meta_toml(path: Path, data: Mapping[str, object]) -> None:
    lines: list[str] = []
    for key, value in data.items():
        if value is None:
            continue
        if isinstance(value, str):
            # Use JSON encoding to safely escape quotes and newlines
            lines.append(f"{key} = {json.dumps(value)}")
        else:
            lines.append(f"{key} = {value}")
    path.write_text("\n".join(lines) + "\n")


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
    context: Context, company: str, role: str, date: str
) -> Application:
    _ensure_structure(context)

    # Normalize company for slug
    normalized = company.strip().lower().replace(" ", "-")
    slug = f"{date.replace('-', '')}-{normalized}"

    # Normalize display values
    company = company.strip().title()
    role = role.strip().title()

    if _application_path(context, slug) is not None:
        raise ValueError(f"Application already exists: {slug}")

    path = _state_dir(context, "drafts") / slug
    path.mkdir(parents=True)

    meta = ApplicationMeta(
        company=company,
        role=role,
        created_at=date,
    )
    _write_meta_toml(path / "meta.toml", meta.to_dict())
    (path / "notes.md").write_text("")
    (path / "artifacts").mkdir()

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

            # Direct application directory (state/slug)
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
                continue

            # Nested company directory (state/company/slug)
            for nested in sorted(entry.iterdir(), key=lambda e: e.name):
                if not nested.is_dir():
                    continue
                if (nested / "meta.toml").exists():
                    raw = _load_meta(nested)
                    meta = ApplicationMeta.from_dict(raw)
                    yield Application(
                        slug=nested.name,
                        state=s,
                        path=nested,
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

    new_path = _state_dir(context, new_state) / slug
    app.path.rename(new_path)

    raw = _load_meta(new_path)
    meta = ApplicationMeta.from_dict(raw)
    return Application(
        slug=slug,
        state=new_state,
        path=new_path,
        company=meta.company,
        role=meta.role,
        created_at=meta.created_at,
    )


# ---------------------------------------------------------------------------
# Doctor / Lint
# ---------------------------------------------------------------------------


def lint_applications(context: Context) -> list[str]:
    """
    Return list of structural issues found in applications directory.
    """
    issues: list[str] = []
    root = _applications_root(context)

    for state in STATES:
        state_dir = root / state
        if not state_dir.exists():
            continue

        for entry in state_dir.iterdir():
            if not entry.is_dir():
                continue

            # Canonical: state/<slug>
            if (entry / "meta.toml").exists():
                continue

            # Nested structure detected
            issues.append(f"Nested structure detected: {entry}")

    return issues


def fix_applications(context: Context) -> list[str]:
    """
    Attempt to flatten nested application directories.
    """
    actions: list[str] = []
    root = _applications_root(context)

    for state in STATES:
        state_dir = root / state
        if not state_dir.exists():
            continue

        for entry in list(state_dir.iterdir()):
            if not entry.is_dir():
                continue

            if (entry / "meta.toml").exists():
                continue

            # Flatten state/company/slug → state/slug
            for nested in entry.iterdir():
                if not nested.is_dir():
                    continue
                if not (nested / "meta.toml").exists():
                    continue

                target = state_dir / nested.name
                if target.exists():
                    raise ValueError(f"Slug collision during fix: {nested.name}")

                nested.rename(target)
                actions.append(f"Moved {nested} → {target}")

            # Remove empty company folder
            try:
                entry.rmdir()
            except OSError:
                pass

    return actions
