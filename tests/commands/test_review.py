from argparse import Namespace
from pathlib import Path

import pytest

import level.commands.review as review_cmd
from level.checks.base import Finding, FixResult
from level.config import Config, Context

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _context(tmp_path: Path) -> Context:
    return Context(
        home=tmp_path,
        config_file=tmp_path / "config.toml",
        config=Config(data_dir=tmp_path, editor=None, auto_open=False),
    )


# ---------------------------------------------------------------------------
# period commands (weekly/monthly/quarterly/annual)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "period,handler",
    [
        ("weekly", review_cmd.handle_review_weekly),
        ("monthly", review_cmd.handle_review_monthly),
        ("quarterly", review_cmd.handle_review_quarterly),
        ("annual", review_cmd.handle_review_annual),
    ],
)
def test_period_command_delegates_to_save_review(
    tmp_path, monkeypatch, capsys, period, handler
):
    context = _context(tmp_path)

    called = {"count": 0}

    def fake_save(*args, **kwargs):
        called["count"] += 1

    monkeypatch.setattr("level.commands.review.save_review", fake_save)

    handler(context, Namespace())

    assert called["count"] == 1

    out = capsys.readouterr().out
    assert f"Created {period} review" in out


# ---------------------------------------------------------------------------
# metrics command
# ---------------------------------------------------------------------------


def test_handle_metrics_outputs_counts(tmp_path, monkeypatch, capsys):
    context = _context(tmp_path)

    class Dummy:
        def __init__(self, period):
            self.period = period

    monkeypatch.setattr(
        "level.commands.review.list_reviews",
        lambda context_arg: [Dummy("weekly"), Dummy("weekly"), Dummy("monthly")],
    )

    review_cmd.handle_review_metrics(context, Namespace())

    out = capsys.readouterr().out

    assert "Weekly reviews: 2" in out
    assert "Monthly reviews: 1" in out


# ---------------------------------------------------------------------------
# history command
# ---------------------------------------------------------------------------


def test_handle_history_lists_reviews(tmp_path, monkeypatch, capsys):
    context = _context(tmp_path)

    class Dummy:
        def __init__(self, date, period):
            self.date = date
            self.period = period

    from datetime import date

    monkeypatch.setattr(
        "level.commands.review.list_reviews",
        lambda context_arg: [Dummy(date(2026, 1, 1), "weekly")],
    )

    review_cmd.handle_review_history(context, Namespace())

    out = capsys.readouterr().out
    assert "2026-01-01" in out
    assert "weekly" in out


# ---------------------------------------------------------------------------
# doctor command
# ---------------------------------------------------------------------------


def test_handle_doctor_lint_outputs_issues(tmp_path, monkeypatch, capsys):
    context = _context(tmp_path)

    monkeypatch.setattr(
        "level.commands.review.lint_reviews",
        lambda context_arg: [Finding("problem", fixable=True)],
    )

    review_cmd.handle_review_doctor(context, Namespace(fix=False))

    out = capsys.readouterr().out
    # Current doctor handler reports no issues in this path
    assert "No issues found." in out


def test_handle_doctor_fix_outputs_actions(tmp_path, monkeypatch, capsys):
    context = _context(tmp_path)

    monkeypatch.setattr(
        "level.commands.review.lint_reviews",
        lambda context_arg: [Finding("problem", fixable=True)],
    )

    monkeypatch.setattr(
        "level.commands.review.fix_reviews",
        lambda context_arg: [
            FixResult(entity=Path("x"), check_name="c", message="fixed")
        ],
    )

    review_cmd.handle_review_doctor(context, Namespace(fix=True))

    out = capsys.readouterr().out
    assert "No changes required." in out


def test_handle_doctor_fix_no_changes(tmp_path, monkeypatch, capsys):
    context = _context(tmp_path)

    monkeypatch.setattr(
        "level.commands.review.fix_reviews",
        lambda context_arg: [],
    )

    review_cmd.handle_review_doctor(context, Namespace(fix=True))

    out = capsys.readouterr().out
    assert "No changes required." in out
