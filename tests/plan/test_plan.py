from level.config import build_context
from level.plan.plan import (
    Plan,
    fix_plan,
    lint_plan,
    load_plan,
    save_plan,
)

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _context(tmp_path, monkeypatch):
    monkeypatch.setenv("LEVEL_HOME", str(tmp_path))
    return build_context()


# ---------------------------------------------------------------------------
# load / save
# ---------------------------------------------------------------------------


def test_load_plan_returns_none_if_missing(tmp_path, monkeypatch):
    context = _context(tmp_path, monkeypatch)

    plan = load_plan(context)

    assert plan is None


def test_save_and_load_plan_roundtrip(tmp_path, monkeypatch):
    context = _context(tmp_path, monkeypatch)

    original = Plan(
        target_roles=["Staff Engineer"],
        target_total_comp_min=150000,
        target_total_comp_max=200000,
        horizon_years=3,
        primary_focus="Platform Leadership",
        last_reviewed="2026-02-20",
    )

    save_plan(context, original)

    loaded = load_plan(context)

    assert loaded == original


# ---------------------------------------------------------------------------
# structure
# ---------------------------------------------------------------------------


def test_save_creates_notes_file(tmp_path, monkeypatch):
    context = _context(tmp_path, monkeypatch)

    plan = Plan(
        target_roles=[],
        target_total_comp_min=None,
        target_total_comp_max=None,
        horizon_years=None,
        primary_focus=None,
        last_reviewed=None,
    )

    save_plan(context, plan)

    notes_path = tmp_path / "plan" / "notes.md"
    assert notes_path.exists()


# ---------------------------------------------------------------------------
# doctor
# ---------------------------------------------------------------------------


def test_lint_reports_missing_meta(tmp_path, monkeypatch):
    context = _context(tmp_path, monkeypatch)

    # Create plan directory without meta.toml
    (tmp_path / "plan").mkdir()

    issues = lint_plan(context)

    assert "meta.toml is missing" in issues[0]


def test_fix_creates_missing_meta(tmp_path, monkeypatch):
    context = _context(tmp_path, monkeypatch)

    # Create plan directory without meta.toml
    (tmp_path / "plan").mkdir()

    actions = fix_plan(context)

    meta_path = tmp_path / "plan" / "meta.toml"

    assert meta_path.exists()
    assert any("Created missing meta.toml" in a for a in actions)


def test_fix_is_idempotent(tmp_path, monkeypatch):
    context = _context(tmp_path, monkeypatch)

    plan = Plan(
        target_roles=[],
        target_total_comp_min=None,
        target_total_comp_max=None,
        horizon_years=None,
        primary_focus=None,
        last_reviewed=None,
    )

    save_plan(context, plan)

    fix_plan(context)
    second = fix_plan(context)

    assert second == []
