import argparse
from datetime import date

from level.commands.plan import (
    handle_plan_doctor,
    handle_plan_show,
)
from level.config import build_context
from level.domains.plan.plan import Plan, save_plan

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _context(tmp_path, monkeypatch):
    monkeypatch.setenv("LEVEL_HOME", str(tmp_path))
    return build_context()


# ---------------------------------------------------------------------------
# show
# ---------------------------------------------------------------------------


def test_plan_show_no_plan(tmp_path, monkeypatch, capsys):
    context = _context(tmp_path, monkeypatch)

    args = argparse.Namespace()
    handle_plan_show(context, args)

    captured = capsys.readouterr()
    assert "No plan defined" in captured.out


def test_plan_show_outputs_display_dict(tmp_path, monkeypatch, capsys):
    context = _context(tmp_path, monkeypatch)

    plan = Plan(
        target_roles=["Engineer"],
        target_total_comp_min=50000,
        target_total_comp_max=70000,
        comp_currency="EUR",
        last_reviewed=date(2026, 2, 20),
    )

    save_plan(context, plan)

    args = argparse.Namespace()
    handle_plan_show(context, args)

    captured = capsys.readouterr()

    assert "Target Roles" in captured.out
    assert "Engineer" in captured.out
    assert "50,000" in captured.out
    assert "70,000" in captured.out


# ---------------------------------------------------------------------------
# doctor
# ---------------------------------------------------------------------------


def test_plan_doctor_detects_missing_meta(tmp_path, monkeypatch, capsys):
    context = _context(tmp_path, monkeypatch)

    args = argparse.Namespace(fix=False)
    handle_plan_doctor(context, args)

    captured = capsys.readouterr()
    assert (
        "meta.toml is missing" in captured.out
        or "Plan directory does not exist" in captured.out
    )


def test_plan_doctor_fix_creates_meta(tmp_path, monkeypatch, capsys):
    context = _context(tmp_path, monkeypatch)

    args = argparse.Namespace(fix=True)
    handle_plan_doctor(context, args)

    captured = capsys.readouterr()
    assert "Created meta.toml" in captured.out or "Actions performed" in captured.out
