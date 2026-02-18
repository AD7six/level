

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final, Iterable

import tomllib

from level.config import Context, get_data_root


# ---------------------------------------------------------------------------
# State machine
# ---------------------------------------------------------------------------

STATES: Final[set[str]] = {
    "drafts",
    "applied",
    "interviewing",
    "stalled",
    "archived",
}

TRANSITIONS: Final[dict[str, set[str]]] = {
    "drafts": {"applied", "archived"},
    "applied": {"interviewing", "stalled", "archived"},
    "interviewing": {"stalled", "archived"},
    "stalled": {"interviewing", "archived"},
    "archived": set(),
}


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Application:
    slug: str
    state: str
    path: Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


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


def create_application(context: Context, slug: str) -> Application:
    _ensure_structure(context)

    if _application_path(context, slug) is not None:
        raise ValueError(f"Application already exists: {slug}")

    path = _state_dir(context, "drafts") / slug
    path.mkdir(parents=True)

    (path / "meta.toml").write_text(f'slug = "{slug}"\nstate = "drafts"\n')
    (path / "notes.md").write_text("")
    (path / "artifacts").mkdir()

    return Application(slug=slug, state="drafts", path=path)


def list_applications(context: Context, state: str | None = None) -> Iterable[Application]:
    root = _applications_root(context)

    states = {state} if state else STATES

    for s in states:
        if s not in STATES:
            raise ValueError(f"Invalid state: {s}")
        state_dir = root / s
        if not state_dir.exists():
            continue
        for entry in state_dir.iterdir():
            if entry.is_dir():
                yield Application(slug=entry.name, state=s, path=entry)


def get_application(context: Context, slug: str) -> Application:
    path = _application_path(context, slug)
    if path is None:
        raise ValueError(f"Application not found: {slug}")

    state = path.parent.name
    return Application(slug=slug, state=state, path=path)


def move_application(context: Context, slug: str, new_state: str) -> Application:
    if new_state not in STATES:
        raise ValueError(f"Invalid state: {new_state}")

    app = get_application(context, slug)

    if new_state not in TRANSITIONS[app.state]:
        raise ValueError(f"Invalid transition: {app.state} → {new_state}")

    new_path = _state_dir(context, new_state) / slug
    app.path.rename(new_path)

    meta_file = new_path / "meta.toml"
    if meta_file.exists():
        data = tomllib.loads(meta_file.read_text())
        data["state"] = new_state
        meta_file.write_text(
            f'slug = "{data["slug"]}"\nstate = "{new_state}"\n'
        )

    return Application(slug=slug, state=new_state, path=new_path)


def archive_application(context: Context, slug: str) -> Application:
    return move_application(context, slug, "archived")
