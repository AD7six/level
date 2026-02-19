import pytest

from level.applications.applications import (
    TRANSITIONS,
    create_application,
    get_application,
    list_applications,
    move_application,
)
from level.applications.schema import STATES
from level.config import build_context

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _context(tmp_path, monkeypatch):
    monkeypatch.setenv("LEVEL_HOME", str(tmp_path))
    return build_context()


# ---------------------------------------------------------------------------
# create
# ---------------------------------------------------------------------------


def test_create_application_creates_structure(tmp_path, monkeypatch):
    context = _context(tmp_path, monkeypatch)

    app = create_application(context, "Acme", "SRE", "2026-01-01")

    assert app.slug == "20260101-acme"
    assert app.state == "drafts"
    assert app.path.exists()
    assert (app.path / "meta.toml").exists()
    assert (app.path / "notes.md").exists()
    assert (app.path / "artifacts").exists()


def test_create_application_duplicate_slug(tmp_path, monkeypatch):
    context = _context(tmp_path, monkeypatch)

    create_application(context, "Dup", "Role", "2026-01-01")

    with pytest.raises(ValueError):
        create_application(context, "Dup", "Role", "2026-01-01")


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------


def test_list_applications_by_state(tmp_path, monkeypatch):
    context = _context(tmp_path, monkeypatch)

    create_application(context, "A", "Role", "2026-01-01")
    create_application(context, "B", "Role", "2026-01-02")

    apps = list(list_applications(context, state="drafts"))

    slugs = {a.slug for a in apps}
    assert slugs == {"20260101-a", "20260102-b"}


# ---------------------------------------------------------------------------
# get
# ---------------------------------------------------------------------------


def test_get_application(tmp_path, monkeypatch):
    context = _context(tmp_path, monkeypatch)

    create_application(context, "Foo", "Role", "2026-01-01")

    app = get_application(context, "20260101-foo")

    assert app.slug == "20260101-foo"
    assert app.state == "drafts"


def test_get_application_missing(tmp_path, monkeypatch):
    context = _context(tmp_path, monkeypatch)

    with pytest.raises(ValueError):
        get_application(context, "missing")


# ---------------------------------------------------------------------------
# transitions
# ---------------------------------------------------------------------------


def test_valid_transition(tmp_path, monkeypatch):
    context = _context(tmp_path, monkeypatch)

    create_application(context, "Foo", "Role", "2026-01-01")

    app = move_application(context, "20260101-foo", "applied")

    assert app.state == "applied"


def test_invalid_transition(tmp_path, monkeypatch):
    context = _context(tmp_path, monkeypatch)

    create_application(context, "Foo", "Role", "2026-01-01")

    with pytest.raises(ValueError):
        move_application(context, "20260101-foo", "interviewing")  # invalid from drafts


# ---------------------------------------------------------------------------
# state machine integrity
# ---------------------------------------------------------------------------


def test_states_and_transitions_consistency():
    # All transition keys must be valid states
    assert set(TRANSITIONS.keys()) == set(STATES)

    # All transition targets must be valid states
    for targets in TRANSITIONS.values():
        assert targets.issubset(set(STATES))
