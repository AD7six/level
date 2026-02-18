import pytest

from level.applications import (
    STATES,
    TRANSITIONS,
    archive_application,
    create_application,
    get_application,
    list_applications,
    move_application,
)
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

    app = create_application(context, "acme-sre-2026")

    assert app.slug == "acme-sre-2026"
    assert app.state == "drafts"
    assert app.path.exists()
    assert (app.path / "meta.toml").exists()
    assert (app.path / "notes.md").exists()
    assert (app.path / "artifacts").exists()


def test_create_application_duplicate_slug(tmp_path, monkeypatch):
    context = _context(tmp_path, monkeypatch)

    create_application(context, "dup")

    with pytest.raises(ValueError):
        create_application(context, "dup")


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------


def test_list_applications_by_state(tmp_path, monkeypatch):
    context = _context(tmp_path, monkeypatch)

    create_application(context, "a")
    create_application(context, "b")

    apps = list(list_applications(context, state="drafts"))

    slugs = {a.slug for a in apps}
    assert slugs == {"a", "b"}


# ---------------------------------------------------------------------------
# get
# ---------------------------------------------------------------------------


def test_get_application(tmp_path, monkeypatch):
    context = _context(tmp_path, monkeypatch)

    create_application(context, "foo")

    app = get_application(context, "foo")

    assert app.slug == "foo"
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

    create_application(context, "foo")

    app = move_application(context, "foo", "applied")

    assert app.state == "applied"


def test_invalid_transition(tmp_path, monkeypatch):
    context = _context(tmp_path, monkeypatch)

    create_application(context, "foo")

    with pytest.raises(ValueError):
        move_application(context, "foo", "interviewing")  # invalid from drafts


# ---------------------------------------------------------------------------
# archive
# ---------------------------------------------------------------------------


def test_archive_application(tmp_path, monkeypatch):
    context = _context(tmp_path, monkeypatch)

    create_application(context, "foo")

    app = archive_application(context, "foo")

    assert app.state == "archived"


# ---------------------------------------------------------------------------
# state machine integrity
# ---------------------------------------------------------------------------


def test_states_and_transitions_consistency():
    # All transition keys must be valid states
    assert set(TRANSITIONS.keys()) == STATES

    # All transition targets must be valid states
    for targets in TRANSITIONS.values():
        assert targets.issubset(STATES)
