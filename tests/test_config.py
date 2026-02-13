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


@pytest.mark.parametrize(
    "explicit, env_value, expect_default",
    [
        ("explicit_home", None, False),
        (None, "env_home", False),
        (None, None, True),
    ],
)
def test_resolve_level_home(monkeypatch, tmp_path, explicit, env_value, expect_default):
    monkeypatch.delenv("LEVEL_HOME", raising=False)

    if env_value is not None:
        monkeypatch.setenv("LEVEL_HOME", str(tmp_path / env_value))

    if explicit is not None:
        result = resolve_level_home(str(tmp_path / explicit))
        assert result == (tmp_path / explicit).resolve()
    elif env_value is not None:
        result = resolve_level_home()
        assert result == (tmp_path / env_value).resolve()
    else:
        result = resolve_level_home()
        assert result == (Path.home() / ".level").resolve()


# ---------------------------------------------------------------------------
# load_config
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "content, expected_editor, should_raise",
    [
        (None, None, False),
        ('editor = "vim"\n', "vim", False),
        ('unknown = "value"\n', None, True),
        ('editor = 123\n', None, True),
    ],
)
def test_load_config(tmp_path, content, expected_editor, should_raise):
    config_file = tmp_path / "config.toml"

    if content is not None:
        config_file.write_text(content)

    if should_raise:
        with pytest.raises(ValueError):
            load_config(config_file)
    else:
        config = load_config(config_file)
        assert config.editor == expected_editor


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
