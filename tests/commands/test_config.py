import argparse
from pathlib import Path

import pytest

from level.commands.init import handle_init
from level.config import build_context

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _context(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("LEVEL_HOME", str(tmp_path))
    return build_context()


# ---------------------------------------------------------------------------
# tests
# ---------------------------------------------------------------------------


def test_init_delegates_to_diagnostics_with_fix(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    context = _context(tmp_path, monkeypatch)

    called = {"args": None}

    def fake_run(context_arg, fix):
        called["args"] = (context_arg, fix)

        class Result:
            def __init__(self, ok, message):
                self.ok = ok
                self.message = message

        return [Result(True, "ok")]

    monkeypatch.setattr("level.commands.init.run_diagnostics", fake_run)

    handle_init(context, argparse.Namespace())

    assert called["args"] == (context, True)

    out = capsys.readouterr().out
    assert "Initializing level repository" in out
    assert "ok" in out


def test_init_prints_failures(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    context = _context(tmp_path, monkeypatch)

    def fake_run(context_arg, fix):
        class Result:
            def __init__(self, ok, message):
                self.ok = ok
                self.message = message

        return [Result(False, "problem")]

    monkeypatch.setattr("level.commands.init.run_diagnostics", fake_run)

    handle_init(context, argparse.Namespace())

    out = capsys.readouterr().out
    assert "problem" in out
