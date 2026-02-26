from datetime import date

from level.config import build_context
from level.domains.plan import (
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
        target_roles=["Engineer"],
        target_industries=[],
        target_locations=[],
        work_modes=[],
        preferred_track=None,
        target_company_stages=[],
        risk_tolerance=None,
        target_total_comp_min=50000,
        target_total_comp_max=75000,
        comp_currency=None,
        horizon_years=3,
        primary_focus="Platform Leadership",
        last_reviewed=date(2026, 2, 20),
    )

    save_plan(context, original)

    loaded = load_plan(context)

    assert loaded == original


# ---------------------------------------------------------------------------
# structure
# ---------------------------------------------------------------------------


def test_save_creates_notes_file(tmp_path, monkeypatch):
    context = _context(tmp_path, monkeypatch)

    plan = Plan()

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

    assert "meta.toml is missing" in issues[0].message


def test_fix_creates_missing_meta(tmp_path, monkeypatch):
    context = _context(tmp_path, monkeypatch)

    # Create plan directory without meta.toml
    (tmp_path / "plan").mkdir()

    actions = fix_plan(context)

    meta_path = tmp_path / "plan" / "meta.toml"

    assert meta_path.exists()
    assert any("Created meta.toml" in a.message for a in actions)


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

    assert isinstance(second, list)


# ---------------------------------------------------------------------------
# validation
# ---------------------------------------------------------------------------


def test_lint_detects_invalid_currency(tmp_path, monkeypatch):
    context = _context(tmp_path, monkeypatch)

    plan = Plan(comp_currency="eur")  # invalid (not uppercase)
    save_plan(context, plan)

    issues = lint_plan(context)

    assert any("comp_currency" in i.message for i in issues)


def test_lint_detects_invalid_track(tmp_path, monkeypatch):
    context = _context(tmp_path, monkeypatch)

    plan = Plan(preferred_track="Director")  # invalid value
    save_plan(context, plan)

    issues = lint_plan(context)

    assert any("preferred_track" in i.message for i in issues)


def test_as_display_dict_aggregates_comp():
    plan = Plan(
        target_total_comp_min=120000,
        target_total_comp_max=180000,
        comp_currency="EUR",
    )

    display = plan.as_display_dict()

    assert "Target Total Compensation" in display
    assert "120,000" in display["Target Total Compensation"]
    assert "180,000" in display["Target Total Compensation"]


def test_as_display_dict_handles_empty_values():
    plan = Plan()
    display = plan.as_display_dict()

    # Ensure keys exist and empty values render as dash
    assert display["Target Roles"] == "—"
    assert display["Target Total Compensation"] == "—"
