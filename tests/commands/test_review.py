from argparse import Namespace
from pathlib import Path

import pytest

import level.commands.review as review_cmd
import level.editor as editor_module
from level.config import Config, Context


@pytest.fixture(autouse=True)
def _stub_editor(monkeypatch):
    monkeypatch.setattr(editor_module, "open_in_editor", lambda *a, **k: None)


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
def test_period_command_creates_review(tmp_path, monkeypatch, period, handler):
    context = Context(
        home=Path(tmp_path),
        config_file=Path(tmp_path / "config.toml"),
        config=Config(data_dir=Path(tmp_path), editor=None, auto_open=False),
    )

    args = Namespace(date=None, auto_open=False)

    # Act
    handler(context, args)

    # Assert (black-box: one directory created under reviews)
    reviews_dir = tmp_path / "reviews"
    assert reviews_dir.exists()

    dirs = list(reviews_dir.iterdir())
    assert len(dirs) == 1

    created = dirs[0]
    assert (created / "meta.toml").exists()


# ---------------------------------------------------------------------------
# metrics command
# ---------------------------------------------------------------------------


def test_handle_metrics_outputs_counts(tmp_path, monkeypatch, capsys):
    context = Context(
        home=Path(tmp_path),
        config_file=Path(tmp_path / "config.toml"),
        config=Config(data_dir=Path(tmp_path), editor=None, auto_open=False),
    )

    args = Namespace(date=None, auto_open=False)

    # Create two weekly reviews
    review_cmd.handle_review_weekly(context, args)
    review_cmd.handle_review_weekly(context, args)

    review_cmd.handle_review_metrics(context, Namespace())

    captured = capsys.readouterr()
    assert "Weekly reviews:" in captured.out


# ---------------------------------------------------------------------------
# history command
# ---------------------------------------------------------------------------


def test_handle_history_lists_reviews(tmp_path, monkeypatch, capsys):
    context = Context(
        home=Path(tmp_path),
        config_file=Path(tmp_path / "config.toml"),
        config=Config(data_dir=Path(tmp_path), editor=None, auto_open=False),
    )

    args = Namespace(date=None, auto_open=False)

    # Create one review
    review_cmd.handle_review_weekly(context, args)

    review_cmd.handle_review_history(context, Namespace())

    captured = capsys.readouterr()
    assert "weekly" in captured.out.lower()


# ---------------------------------------------------------------------------
# doctor command
# ---------------------------------------------------------------------------


def test_handle_doctor_lint_and_fix(tmp_path, monkeypatch, capsys):
    context = Context(
        home=Path(tmp_path),
        config_file=Path(tmp_path / "config.toml"),
        config=Config(data_dir=Path(tmp_path), editor=None, auto_open=False),
    )

    args = Namespace(date=None, auto_open=False)

    # Create review
    review_cmd.handle_review_weekly(context, args)

    # Break canonical directory
    reviews_dir = tmp_path / "reviews"
    original = next(reviews_dir.iterdir())
    broken = reviews_dir / "broken-name"
    original.rename(broken)

    # Lint mode (no --fix)
    review_cmd.handle_review_doctor(context, Namespace(fix=False))
    captured = capsys.readouterr()
    assert "Issues detected" in captured.out

    # Fix mode
    review_cmd.handle_review_doctor(context, Namespace(fix=True))
    captured = capsys.readouterr()
    assert "Actions performed" in captured.out
