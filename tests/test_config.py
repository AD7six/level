import os
from pathlib import Path

import pytest

from level.config import (
    resolve_level_home,
    load_config,
    save_config,
    initialize_defaults,
    build_context,
)


# ---------------------------------------------------------------------------
# resolve_level_home
# ---------------------------------------------------------------------------


def test_resolve_level_home_explicit(tmp_path):
    explicit = tmp_path / "explicit_home"
    result = resolve_level_home(str(explicit))
    assert result == explicit.resolve()


def test_resolve_level_home_env(monkeypatch, tmp_path):
    env_home = tmp_path / "env_home"
    monkeypatch.setenv("LEVEL_HOME", str(env_home))

    result = resolve_level_home()
    assert result == env_home.resolve()


def test_resolve_level_home_default(monkeypatch):
    monkeypatch.delenv("LEVEL_HOME", raising=False)
    result = resolve_level_home()
    assert result == (Path.home() / ".level").resolve()


# ---------------------------------------------------------------------------
# load_config
# ---------------------------------------------------------------------------


def test_load_config_empty(tmp_path):
    config_file = tmp_path / "config.toml"
    config = load_config(config_file)

    assert config.data_dir is None
    assert config.editor is None


def test_load_config_valid(tmp_path):
    config_file = tmp_path / "config.toml"
    config_file.write_text('editor = "vim"\n')

    config = load_config(config_file)
    assert config.editor == "vim"


def test_load_config_unknown_key(tmp_path):
    config_file = tmp_path / "config.toml"
    config_file.write_text('unknown = "value"\n')

    with pytest.raises(ValueError):
        load_config(config_file)


def test_load_config_invalid_type(tmp_path):
    config_file = tmp_path / "config.toml"
    config_file.write_text("editor = 123\n")

    with pytest.raises(ValueError):
        load_config(config_file)


# ---------------------------------------------------------------------------
# save_config + initialize_defaults
# ---------------------------------------------------------------------------


def test_save_config_writes_file(tmp_path, monkeypatch):
    monkeypatch.setenv("LEVEL_HOME", str(tmp_path))
    context = build_context()

    save_config(context, {"editor": "nano"})

    config_file = tmp_path / "config.toml"
    assert config_file.exists()
    content = config_file.read_text()
    assert 'editor = "nano"' in content


def test_initialize_defaults_creates_missing(tmp_path, monkeypatch):
    monkeypatch.setenv("LEVEL_HOME", str(tmp_path))
    context = build_context()

    initialize_defaults(context)

    config_file = tmp_path / "config.toml"
    content = config_file.read_text()

    assert 'editor = "vim"' in content
    assert 'data_dir = ' in content


def test_initialize_defaults_preserves_existing(tmp_path, monkeypatch):
    monkeypatch.setenv("LEVEL_HOME", str(tmp_path))

    config_file = tmp_path / "config.toml"
    config_file.write_text('editor = "nano"\n')

    context = build_context()
    initialize_defaults(context)

    content = config_file.read_text()
    assert 'editor = "nano"' in content
