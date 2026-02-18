import argparse

from level.commands.init import (
    handle_init,
)
from level.config import build_context, get_data_root

# ---------------------------------------------------------------------------
# init
#
# Note these tests overlap with config doctor --fix, but we want to ensure the
# init command properly delegates to the diagnostics engine.
# ---------------------------------------------------------------------------


def test_init_always_fixes(tmp_path, monkeypatch):
    level_home = tmp_path / "missing_home"
    monkeypatch.setenv("LEVEL_HOME", str(level_home))

    handle_init(argparse.Namespace())

    assert level_home.exists()


def test_init_creates_managed_domains(tmp_path, monkeypatch):
    monkeypatch.setenv("LEVEL_HOME", str(tmp_path))

    handle_init(argparse.Namespace())

    assert (tmp_path / "applications").exists()


def test_init_is_idempotent(tmp_path, monkeypatch):
    monkeypatch.setenv("LEVEL_HOME", str(tmp_path))

    handle_init(argparse.Namespace())
    handle_init(argparse.Namespace())

    assert (tmp_path / "applications").exists()


def test_init_respects_data_dir(tmp_path, monkeypatch):
    level_home = tmp_path / "level_home"
    data_dir = tmp_path / "career_data"

    monkeypatch.setenv("LEVEL_HOME", str(level_home))

    # Create LEVEL_HOME and config with explicit data_dir
    level_home.mkdir(parents=True, exist_ok=True)
    config_file = level_home / "config.toml"
    config_file.write_text(f'data_dir = "{data_dir}"\n')

    handle_init(argparse.Namespace())

    context = build_context()
    data_root = get_data_root(context)

    assert data_root == data_dir
    assert (data_root / "applications").exists()
