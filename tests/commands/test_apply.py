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

    args = argparse.Namespace(company="Acme", role="SRE", date="2026-01-01")
    handle_apply_new(args)

    captured = capsys.readouterr()

    assert "Created 20260101-acme" in captured.out
    assert (tmp_path / "applications" / "drafts" / "20260101-acme").exists()


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------


def test_apply_list_outputs_entries(tmp_path, monkeypatch, capsys):
    context = _context(tmp_path, monkeypatch)

    create_application(context, "A", "Role", "2026-01-01")
    create_application(context, "B", "Role", "2026-01-02")

    args = argparse.Namespace(state=None, all=False)
    handle_apply_list(args)

    captured = capsys.readouterr()

    assert "2026-01-01" in captured.out
    assert "2026-01-02" in captured.out
    assert "A" in captured.out
    assert "B" in captured.out


# ---------------------------------------------------------------------------
# show
# ---------------------------------------------------------------------------


def test_apply_show_outputs_details(tmp_path, monkeypatch, capsys):
    context = _context(tmp_path, monkeypatch)
    create_application(context, "Foo", "Role", "2026-01-01")

    args = argparse.Namespace(slug="20260101-foo")
    handle_apply_show(args)

    captured = capsys.readouterr()

    assert "Slug:" in captured.out
    assert "20260101-foo" in captured.out


# ---------------------------------------------------------------------------
# status
# ---------------------------------------------------------------------------


def test_apply_status_moves_application(tmp_path, monkeypatch, capsys):
    context = _context(tmp_path, monkeypatch)
    create_application(context, "Foo", "Role", "2026-01-01")

    args = argparse.Namespace(slug="20260101-foo", state="applied")
    handle_apply_status(args)

    captured = capsys.readouterr()

    assert "Moved" in captured.out
    assert (tmp_path / "applications" / "applied" / "20260101-foo").exists()
