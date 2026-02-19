import argparse

from level.applications.applications import create_application
from level.commands.apply import (
    handle_apply_list,
    handle_apply_new,
    handle_apply_show,
    handle_apply_status,
)
from level.config import build_context

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _context(tmp_path, monkeypatch):
    monkeypatch.setenv("LEVEL_HOME", str(tmp_path))
    return build_context()


# ---------------------------------------------------------------------------
# new
# ---------------------------------------------------------------------------


def test_apply_new_creates_application(tmp_path, monkeypatch, capsys):
    _context(tmp_path, monkeypatch)

    args = argparse.Namespace(slug="acme-sre-2026")
    handle_apply_new(args)

    captured = capsys.readouterr()

    assert "Created application" in captured.out
    assert (tmp_path / "applications" / "drafts" / "acme-sre-2026").exists()


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------


def test_apply_list_outputs_entries(tmp_path, monkeypatch, capsys):
    context = _context(tmp_path, monkeypatch)

    create_application(context, "a")
    create_application(context, "b")

    args = argparse.Namespace(state=None)
    handle_apply_list(args)

    captured = capsys.readouterr()

    assert "a" in captured.out
    assert "b" in captured.out


# ---------------------------------------------------------------------------
# show
# ---------------------------------------------------------------------------


def test_apply_show_outputs_details(tmp_path, monkeypatch, capsys):
    context = _context(tmp_path, monkeypatch)
    create_application(context, "foo")

    args = argparse.Namespace(slug="foo")
    handle_apply_show(args)

    captured = capsys.readouterr()

    assert "Slug:" in captured.out
    assert "foo" in captured.out


# ---------------------------------------------------------------------------
# status
# ---------------------------------------------------------------------------


def test_apply_status_moves_application(tmp_path, monkeypatch, capsys):
    context = _context(tmp_path, monkeypatch)
    create_application(context, "foo")

    args = argparse.Namespace(slug="foo", state="applied")
    handle_apply_status(args)

    captured = capsys.readouterr()

    assert "Moved" in captured.out
    assert (tmp_path / "applications" / "applied" / "foo").exists()
