import pytest

from level.config import build_context
from level.domains.applications import (
    STATES,
    TRANSITIONS,
    create_application,
    fix_applications,
    get_application,
    lint_applications,
    list_applications,
    move_application,
)

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

    assert app.slug == "2026-01-01-acme"
    assert app.state == "drafts"
    assert app.path.exists()
    assert (app.path / "meta.toml").exists()
    assert (app.path / "README.md").exists()
    assert (app.path / "cover-letter.md").exists()
    assert (app.path / "resume.md").exists()


def test_create_application_duplicate_slug(tmp_path, monkeypatch):
    context = _context(tmp_path, monkeypatch)

    first = create_application(context, "Dup", "Role", "2026-01-01")
    second = create_application(context, "Dup", "Role", "2026-01-01")

    assert first.slug == "2026-01-01-dup"
    assert second.slug == "2026-01-01-dup-1"
    assert second.path.exists()


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------


def test_list_applications_by_state(tmp_path, monkeypatch):
    context = _context(tmp_path, monkeypatch)

    create_application(context, "A", "Role", "2026-01-01")
    create_application(context, "B", "Role", "2026-01-02")

    apps = list(list_applications(context, state="drafts"))

    slugs = {a.slug for a in apps}
    assert slugs == {"2026-01-01-a", "2026-01-02-b"}


# ---------------------------------------------------------------------------
# get
# ---------------------------------------------------------------------------


def test_get_application(tmp_path, monkeypatch):
    context = _context(tmp_path, monkeypatch)

    create_application(context, "Foo", "Role", "2026-01-01")

    app = get_application(context, "2026-01-01-foo")

    assert app.slug == "2026-01-01-foo"
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

    app = move_application(context, "2026-01-01-foo", "applied")

    assert app.state == "applied"


def test_invalid_transition(tmp_path, monkeypatch):
    context = _context(tmp_path, monkeypatch)

    create_application(context, "Foo", "Role", "2026-01-01")

    with pytest.raises(ValueError):
        move_application(
            context, "2026-01-01-foo", "interviewing"
        )  # invalid from drafts


# ---------------------------------------------------------------------------
# state machine integrity
# ---------------------------------------------------------------------------


def test_states_and_transitions_consistency():
    # All transition keys must be valid states
    assert set(TRANSITIONS.keys()) == set(STATES)

    # All transition targets must be valid states
    for targets in TRANSITIONS.values():
        assert targets.issubset(set(STATES))


# ---------------------------------------------------------------------------
# lint / fix
# ---------------------------------------------------------------------------


def test_lint_detects_non_canonical_path(tmp_path, monkeypatch):
    context = _context(tmp_path, monkeypatch)

    # Create canonical app
    app = create_application(context, "Acme", "Role", "2026-01-01")

    # Manually rename to non-canonical slug
    bad_path = app.path.parent / "wrong-slug"
    app.path.rename(bad_path)

    issues = lint_applications(context)

    assert any("Non-canonical directory" in f.message for f in issues)


def test_lint_allows_numeric_suffix(tmp_path, monkeypatch):
    context = _context(tmp_path, monkeypatch)

    create_application(context, "Dup", "Role", "2026-01-01")
    create_application(context, "Dup", "Role", "2026-01-01")

    # second has -1 suffix
    issues = lint_applications(context)

    # No issues should be reported for valid suffixes
    assert issues == []


def test_fix_moves_to_canonical_location(tmp_path, monkeypatch):
    context = _context(tmp_path, monkeypatch)

    app = create_application(context, "Acme", "Role", "2026-01-01")

    # Break canonical path
    bad_path = app.path.parent / "wrong-slug"
    app.path.rename(bad_path)

    actions = fix_applications(context)

    assert any("Renamed" in r.message for r in actions)

    # Canonical path should now exist
    canonical = tmp_path / "applications" / "drafts" / "2026-01-01-acme"
    assert canonical.exists()


def test_fix_adds_numeric_suffix_on_collision(tmp_path, monkeypatch):
    context = _context(tmp_path, monkeypatch)

    create_application(context, "Dup", "Role", "2026-01-01")

    # Create a non-canonical directory that should canonicalize
    # to the same slug as the existing application
    conflict = tmp_path / "applications" / "drafts" / "wrong-slug"
    conflict.mkdir(parents=True)
    (conflict / "meta.toml").write_text(
        'company = "Dup"\nrole = "Role"\ncreated_at = "2026-01-01"\n'
    )

    fix_applications(context)

    # Should create a suffixed directory
    suffixed = tmp_path / "applications" / "drafts" / "2026-01-01-dup-1"
    assert suffixed.exists()


def test_fix_is_idempotent(tmp_path, monkeypatch):
    context = _context(tmp_path, monkeypatch)

    create_application(context, "Acme", "Role", "2026-01-01")

    fix_applications(context)
    second = fix_applications(context)

    # Second run should do nothing
    assert second == []
