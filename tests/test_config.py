from pathlib import Path

import pytest

from level.config import (
    build_context,
    initialize_defaults,
    load_config,
    resolve_level_home,
    run_diagnostics,
    save_config,
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
        ("editor = 123\n", None, True),
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


def test_initialize_defaults_preserves_existing(tmp_path, monkeypatch):
    monkeypatch.setenv("LEVEL_HOME", str(tmp_path))

    config_file = tmp_path / "config.toml"
    config_file.write_text('editor = "nano"\n')

    context = build_context()
    initialize_defaults(context)

    content = config_file.read_text()
    assert 'editor = "nano"' in content


# ---------------------------------------------------------------------------
# diagnostics (registry-based)
# ---------------------------------------------------------------------------


def test_run_diagnostics_reports_missing_level_home(tmp_path, monkeypatch):
    # Use non-existent LEVEL_HOME
    missing_home = tmp_path / "missing_home"
    monkeypatch.setenv("LEVEL_HOME", str(missing_home))

    context = build_context()
    results = run_diagnostics(context, fix=False)

    assert any(not r.ok and "LEVEL_HOME missing" in r.message for r in results)


def test_run_diagnostics_fix_creates_level_home(tmp_path, monkeypatch):
    missing_home = tmp_path / "missing_home"
    monkeypatch.setenv("LEVEL_HOME", str(missing_home))

    context = build_context()
    results = run_diagnostics(context, fix=True)

    assert missing_home.exists()
    assert any(r.ok and "LEVEL_HOME created" in r.message for r in results)


def test_run_diagnostics_managed_domains(tmp_path, monkeypatch):
    monkeypatch.setenv("LEVEL_HOME", str(tmp_path))

    context = build_context()

    # Ensure no managed domains exist yet
    results = run_diagnostics(context, fix=False)

    assert any(
        (not r.ok and "Missing managed domains" in r.message)
        or ("managed domain" in r.message)
        for r in results
    )

    # Now fix
    results = run_diagnostics(context, fix=True)

    # After fix, managed domains should exist
    results = run_diagnostics(context, fix=False)
    assert all(
        r.ok for r in results if "managed" in r.message or "All required" in r.message
    )
