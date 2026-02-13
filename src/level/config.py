"""
Configuration and runtime context for level.

Responsible for:
- Resolving LEVEL_HOME
- Loading configuration
- Providing a shared Context object to commands
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ENV_VAR = "LEVEL_HOME"
DEFAULT_DIR_NAME = ".level"
CONFIG_FILE_NAME = "config.toml"


# ---------------------------------------------------------------------------
# Context
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Context:
    """
    Shared runtime context passed to all command handlers.
    """

    home: Path
    config_file: Path


# ---------------------------------------------------------------------------
# Resolution
# ---------------------------------------------------------------------------


def resolve_level_home(explicit: Optional[str] = None) -> Path:
    """
    Resolve the level home directory using the following precedence:

    1. Explicit argument
    2. LEVEL_HOME environment variable
    3. ~/.level
    """

    if explicit:
        return Path(explicit).expanduser().resolve()

    env_value = os.environ.get(ENV_VAR)
    if env_value:
        return Path(env_value).expanduser().resolve()

    return (Path.home() / DEFAULT_DIR_NAME).resolve()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def build_context(explicit_home: Optional[str] = None) -> Context:
    """
    Build the runtime Context.

    This does NOT create directories automatically.
    Commands are responsible for initialization behavior.
    """

    home = resolve_level_home(explicit_home)
    config_file = home / CONFIG_FILE_NAME

    return Context(
        home=home,
        config_file=config_file,
    )
