from argparse import Namespace
from pathlib import Path

from level.commands import practice as practice_cmd
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
# practice new
# ---------------------------------------------------------------------------


def test_practice_new_prints_created_slug(tmp_path, capsys, monkeypatch):
    context = _context(tmp_path)

    def fake_create(context_arg, practice_date, **kwargs):
        class DummyPractice:
            slug = "2026-02-24-code-session"
            path = tmp_path / "practice" / "2026-02-24-code-session"

        return DummyPractice()

    monkeypatch.setattr(
        "level.commands.practice.create_practice",
        fake_create,
    )
    monkeypatch.setattr(
        "level.commands.practice.open_in_editor",
        lambda *args, **kwargs: False,
    )

    args = Namespace(date="2026-02-24", name=None, random=False, type="code")

    practice_cmd.handle_practice_new(context, args)

    output = capsys.readouterr().out
    assert "Created practice session: 2026-02-24-code-session" in output


# ---------------------------------------------------------------------------
# practice list
# ---------------------------------------------------------------------------


def test_practice_list_outputs_slugs(tmp_path, capsys, monkeypatch):
    context = _context(tmp_path)

    class Dummy:
        def __init__(self, slug):
            self.slug = slug

    monkeypatch.setattr(
        "level.commands.practice.list_practice",
        lambda context_arg: [Dummy("a"), Dummy("b")],
    )

    practice_cmd.handle_practice_list(context, Namespace())

    output = capsys.readouterr().out.strip().splitlines()
    assert output == ["a", "b"]


def test_practice_list_empty(tmp_path, capsys, monkeypatch):
    context = _context(tmp_path)

    monkeypatch.setattr(
        "level.commands.practice.list_practice",
        lambda context_arg: [],
    )

    practice_cmd.handle_practice_list(context, Namespace())

    output = capsys.readouterr().out.strip()
    assert output == "No practice sessions found."


# ---------------------------------------------------------------------------
# practice review
# ---------------------------------------------------------------------------


def test_practice_review_success(tmp_path, capsys, monkeypatch):
    context = _context(tmp_path)

    monkeypatch.setattr(
        "level.commands.practice.review_latest_attempt",
        lambda *args, **kwargs: True,
    )

    args = Namespace(slug="abc")

    practice_cmd.handle_practice_review(context, args)

    output = capsys.readouterr().out.strip()
    assert output == "Reviewed practice session: abc"


def test_practice_review_abort(tmp_path, capsys, monkeypatch):
    context = _context(tmp_path)

    monkeypatch.setattr(
        "level.commands.practice.review_latest_attempt",
        lambda *args, **kwargs: False,
    )

    args = Namespace(slug="abc")

    practice_cmd.handle_practice_review(context, args)

    output = capsys.readouterr().out.strip()
    assert output == "Review aborted; metadata not updated."


# ---------------------------------------------------------------------------
# practice stats
# ---------------------------------------------------------------------------


def test_practice_stats_prints_metrics(tmp_path, capsys, monkeypatch):
    context = _context(tmp_path)

    monkeypatch.setattr(
        "level.commands.practice.practice_metrics",
        lambda context_arg: {"arrays": 3, "graphs": 1},
    )

    practice_cmd.handle_practice_stats(context, Namespace())

    output = capsys.readouterr().out.strip()
    assert "arrays: 3" in output
    assert "graphs: 1" in output


def test_practice_stats_no_data(tmp_path, capsys, monkeypatch):
    context = _context(tmp_path)

    monkeypatch.setattr(
        "level.commands.practice.practice_metrics",
        lambda context_arg: {},
    )

    practice_cmd.handle_practice_stats(context, Namespace())

    output = capsys.readouterr().out.strip()
    assert output == "No practice data available."
