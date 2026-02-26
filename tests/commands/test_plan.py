import argparse

from level.commands.plan import (
    handle_plan_doctor,
    handle_plan_show,
)
from level.config import build_context

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

    monkeypatch.setattr("level.commands.plan.load_plan", lambda context: None)

    handle_plan_show(context, argparse.Namespace())

    captured = capsys.readouterr()
    assert "No plan defined" in captured.out


def test_plan_show_prints_display_dict(tmp_path, monkeypatch, capsys):
    context = _context(tmp_path, monkeypatch)

    class DummyPlan:
        def as_display_dict(self):
            return {"Key": "Value"}

    monkeypatch.setattr("level.commands.plan.load_plan", lambda context: DummyPlan())

    handle_plan_show(context, argparse.Namespace())

    captured = capsys.readouterr()

    assert "Career Plan" in captured.out
    assert "Key: Value" in captured.out


# ---------------------------------------------------------------------------
# doctor
# ---------------------------------------------------------------------------


def test_plan_doctor_lint_outputs_issues(tmp_path, monkeypatch, capsys):
    context = _context(tmp_path, monkeypatch)

    monkeypatch.setattr("level.commands.plan.lint_plan", lambda context: ["problem"])

    handle_plan_doctor(context, argparse.Namespace(fix=False))

    captured = capsys.readouterr()

    assert "Issues detected:" in captured.out
    assert "problem" in captured.out


def test_plan_doctor_fix_outputs_actions(tmp_path, monkeypatch, capsys):
    context = _context(tmp_path, monkeypatch)

    monkeypatch.setattr("level.commands.plan.fix_plan", lambda context: ["fixed"])

    handle_plan_doctor(context, argparse.Namespace(fix=True))

    captured = capsys.readouterr()

    assert "Actions performed:" in captured.out
    assert "fixed" in captured.out


def test_plan_doctor_fix_no_changes(tmp_path, monkeypatch, capsys):
    context = _context(tmp_path, monkeypatch)

    monkeypatch.setattr("level.commands.plan.fix_plan", lambda context: [])

    handle_plan_doctor(context, argparse.Namespace(fix=True))

    captured = capsys.readouterr()

    assert "No changes required." in captured.out
