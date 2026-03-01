import subprocess

import pytest

from level.editor import open_in_editor


def test_open_in_editor_invokes_subprocess(monkeypatch, tmp_path):
    called = {}

    def fake_run(cmd, check):
        called["cmd"] = cmd
        called["check"] = check

        class Result:
            returncode = 0

        return Result()

    monkeypatch.setattr(subprocess, "run", fake_run)

    test_file = tmp_path / "file.txt"
    test_file.write_text("content")

    open_in_editor(test_file, auto_open=True, editor="🐈")

    assert called["cmd"] == ["🐈", str(test_file)]
    assert called["check"] is False


@pytest.mark.parametrize(
    "auto_open,editor",
    [
        (True, ""),  # Editor not set
        (False, "🐈"),  # Auto-open disabled
    ],
)
def test_open_in_editor_does_nothing(monkeypatch, tmp_path, auto_open, editor):
    called = {}

    def fake_run(cmd, check):
        called["cmd"] = cmd
        called["check"] = check

    monkeypatch.setattr(subprocess, "run", fake_run)

    test_file = tmp_path / "file.txt"
    test_file.write_text("content")

    open_in_editor(test_file, auto_open=auto_open, editor=editor)

    assert called == {}
