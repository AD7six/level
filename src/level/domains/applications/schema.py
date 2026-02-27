"""
Applications domain schema definition.

This module defines the canonical structural contract for the
applications domain. It is the single source of truth for:

- Supported schema version
- Valid states
- Terminal states
- Layout strategy
- Slug expectations
"""

from __future__ import annotations

from typing import Final

# ---------------------------------------------------------------------------
# Canonical Schema Definition
# ---------------------------------------------------------------------------

CURRENT_SCHEMA_VERSION: Final[int] = 1

LAYOUT: Final[str] = "state-first"

STATES: Final[list[str]] = [
    "drafts",
    "applied",
    "interviewing",
    "offer",
    "stalled",
    "rejected",
    "withdrawn",
]

SORTED_STATES: Final[list[str]] = sorted(STATES)

TERMINAL_STATES: Final[set[str]] = {
    "rejected",
    "withdrawn",
}

# ---------------------------------------------------------------------------
# Materialization
# ---------------------------------------------------------------------------


def default_schema_dict() -> dict[str, object]:
    """
    Return the canonical schema representation as a dict,
    suitable for serialization to .schema.toml.
    """
    return {
        "version": CURRENT_SCHEMA_VERSION,
        "layout": LAYOUT,
        "terminal_states": sorted(TERMINAL_STATES),
        "states": sorted(STATES),
    }


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_schema(data: dict[str, object]) -> None:
    """
    Validate a loaded .schema.toml file against the supported schema.

    Raises:
        ValueError if unsupported or invalid.
    """
    version = data.get("version")
    if version != CURRENT_SCHEMA_VERSION:
        raise ValueError(
            f"Unsupported applications schema version: {version} "
            f"(expected {CURRENT_SCHEMA_VERSION})"
        )

    raw_states = data.get("states")
    if not isinstance(raw_states, list) or not all(
        isinstance(s, str) for s in raw_states
    ):
        raise ValueError("Invalid applications schema states definition.")

    if raw_states != STATES:
        raise ValueError("Applications schema states mismatch.")

    raw_terminal = data.get("terminal_states")
    if not isinstance(raw_terminal, list) or not all(
        isinstance(s, str) for s in raw_terminal
    ):
        raise ValueError("Invalid applications schema terminal states definition.")

    terminal = set(raw_terminal)
    if terminal != TERMINAL_STATES:
        raise ValueError("Applications schema terminal states mismatch.")
