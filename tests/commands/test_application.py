import argparse

from level.applications.applications import create_application
from level.commands.application import (
    handle_application_list,
    handle_application_move,
    handle_application_new,
    handle_application_show,
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


def test_application_new_creates_application(tmp_path, monkeypatch, capsys):
    context = _context(tmp_path, monkeypatch)

    args = argparse.Namespace(company="Acme", role="SRE", date="2026-01-01")
    handle_application_new(context, args)

    captured = capsys.readouterr()

    assert "Created 2026-01-01-acme" in captured.out
    assert (tmp_path / "applications" / "drafts" / "2026-01-01-acme").exists()


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------


def test_application_list_outputs_entries(tmp_path, monkeypatch, capsys):
    context = _context(tmp_path, monkeypatch)

    create_application(context, "A", "Role", "2026-01-01")
    create_application(context, "B", "Role", "2026-01-02")

    args = argparse.Namespace(state=None, all=False)
    handle_application_list(context, args)

    captured = capsys.readouterr()

    assert "2026-01-01" in captured.out
    assert "2026-01-02" in captured.out
    assert "A" in captured.out
    assert "B" in captured.out


# ---------------------------------------------------------------------------
# show
# ---------------------------------------------------------------------------


def test_application_show_outputs_details(tmp_path, monkeypatch, capsys):
    context = _context(tmp_path, monkeypatch)
    create_application(context, "Foo", "Role", "2026-01-01")

    args = argparse.Namespace(slug="2026-01-01-foo")
    handle_application_show(context, args)

    captured = capsys.readouterr()

    assert "Slug:" in captured.out
    assert "2026-01-01-foo" in captured.out


# ---------------------------------------------------------------------------
# move
# ---------------------------------------------------------------------------


def test_application_move_moves_application(tmp_path, monkeypatch, capsys):
    context = _context(tmp_path, monkeypatch)
    create_application(context, "Foo", "Role", "2026-01-01")

    args = argparse.Namespace(slug="2026-01-01-foo", state="applied")
    handle_application_move(context, args)

    captured = capsys.readouterr()

    assert "Moved" in captured.out
    assert (tmp_path / "applications" / "applied" / "2026-01-01-foo").exists()
