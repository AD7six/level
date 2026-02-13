"""
Configuration and runtime context for level.

This module owns:
- LEVEL_HOME resolution
- Config schema definition
- Config loading
- Config validation
- Config persistence
"""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, fields
from pathlib import Path


def _allowed_keys() -> set[str]:
    return {f.name for f in fields(Config)}


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ENV_VAR = "LEVEL_HOME"
DEFAULT_DIR_NAME = ".level"
CONFIG_FILE_NAME = "config.toml"

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Config:
    data_dir: Path | None = None
    editor: str | None = None


@dataclass(frozen=True)
class Context:
    home: Path
    config_file: Path
    config: Config


# ---------------------------------------------------------------------------
# Resolution
# ---------------------------------------------------------------------------


def resolve_level_home(explicit: str | None = None) -> Path:
    """
    Resolve LEVEL_HOME using:
    1. Explicit override
    2. Environment variable
    3. ~/.level
    """
    if explicit:
        return Path(explicit).expanduser().resolve()

    env_value = os.environ.get(ENV_VAR)
    if env_value:
        return Path(env_value).expanduser().resolve()

    return (Path.home() / DEFAULT_DIR_NAME).resolve()


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------


def load_config(config_file: Path) -> Config:
    """
    Load and validate configuration.
    """
    if not config_file.exists():
        return Config()

    with config_file.open("rb") as f:
        data = tomllib.load(f)

    unknown = set(data.keys()) - _allowed_keys()
    if unknown:
        raise ValueError(f"Unknown config keys: {unknown}")

    data_dir = None
    if "data_dir" in data:
        value = data["data_dir"]
        if not isinstance(value, str):
            raise ValueError("data_dir must be a string")
        data_dir = Path(value).expanduser().resolve()

    editor = None
    if "editor" in data:
        value = data["editor"]
        if not isinstance(value, str):
            raise ValueError("editor must be a string")
        editor = value

    return Config(data_dir=data_dir, editor=editor)


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------


def _write_config(path: Path, data: dict[str, str]) -> None:
    """
    Write config deterministically.
    """
    lines = []
    for key in sorted(data.keys()):
        value = data[key]
        lines.append(f'{key} = "{value}"')
    path.write_text("\n".join(lines) + "\n")


def save_config(context: Context, updates: dict[str, str]) -> None:
    """
    Persist updated config values.
    """
    context.home.mkdir(parents=True, exist_ok=True)

    existing: dict[str, str] = {}

    if context.config_file.exists():
        with context.config_file.open("rb") as f:
            existing = tomllib.load(f)

    for key, value in updates.items():
        if key not in _allowed_keys():
            raise ValueError(f"Invalid config key: {key}")
        existing[key] = value

    _write_config(context.config_file, existing)


# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------


def initialize_defaults(context: Context) -> None:
    """
    Initialize missing config keys using sane defaults.
    Existing values are preserved.
    """
    existing: dict[str, str] = {}

    if context.config_file.exists():
        with context.config_file.open("rb") as f:
            existing = tomllib.load(f)

    defaults = {
        "data_dir": str(context.home / "data"),
        "editor": "vim",
    }

    updated = dict(existing)

    for key in _allowed_keys():
        if key not in updated:
            updated[key] = defaults[key]

    _write_config(context.config_file, updated)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def build_context(explicit_home: str | None = None) -> Context:
    home = resolve_level_home(explicit_home)
    config_file = home / CONFIG_FILE_NAME
    config = load_config(config_file)

    return Context(
        home=home,
        config_file=config_file,
        config=config,
    )
