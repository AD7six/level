import argparse
from pathlib import Path

import pytest

from level.commands.config import (
    handle_config_doctor,
    handle_config_set,
)
from level.config import build_context

# ---------------------------------------------------------------------------
# config set (command layer)
# ---------------------------------------------------------------------------


def test_config_set_invalid_key(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("LEVEL_HOME", str(tmp_path))

    args = argparse.Namespace(key="invalid", value="value", fix=False)
    context = build_context()
    handle_config_set(context, args)

    captured = capsys.readouterr()
    assert "Invalid config key" in captured.out


def test_config_set_valid_key(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LEVEL_HOME", str(tmp_path))

    args = argparse.Namespace(key="editor", value="nano", fix=False)
    context = build_context()
    handle_config_set(context, args)

    config_file = tmp_path / "config.toml"
    assert config_file.exists()
    assert 'editor = "nano"' in config_file.read_text()


def test_config_set_initialize_defaults(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("LEVEL_HOME", str(tmp_path))

    args = argparse.Namespace(key=None, value=None, fix=False)
    context = build_context()
    handle_config_set(context, args)

    config_file = tmp_path / "config.toml"
    content = config_file.read_text()

    assert "editor" in content
    assert "data_dir" in content


# ---------------------------------------------------------------------------
# config doctor
# ---------------------------------------------------------------------------


def test_config_doctor_reports_missing_dirs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("LEVEL_HOME", str(tmp_path / "missing_home"))

    args = argparse.Namespace(fix=False)
    context = build_context()
    handle_config_doctor(context, args)

    captured = capsys.readouterr()
    assert "LEVEL_HOME missing" in captured.out or "data_root missing" in captured.out


def test_config_doctor_fix_creates_dirs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    level_home = tmp_path / "missing_home"
    monkeypatch.setenv("LEVEL_HOME", str(level_home))

    args = argparse.Namespace(fix=True)
    context = build_context()
    handle_config_doctor(context, args)

    captured = capsys.readouterr()

    assert level_home.exists()
    assert "created" in captured.out
