from __future__ import annotations

import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from level.config import Context, get_data_root

# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Plan:
    target_roles: list[str]
    target_total_comp_min: int | None
    target_total_comp_max: int | None
    horizon_years: int | None
    primary_focus: str | None
    last_reviewed: str | None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _plan_root(context: Context) -> Path:
    return get_data_root(context) / "plan"


def _plan_meta_path(context: Context) -> Path:
    return _plan_root(context) / "meta.toml"


def _write_meta_toml(path: Path, data: Mapping[str, object]) -> None:
    lines: list[str] = []

    for key, value in data.items():
        if value is None:
            continue

        if isinstance(value, str):
            lines.append(f'{key} = "{value}"')
        elif isinstance(value, list):
            items = ", ".join(f'"{v}"' for v in value)
            lines.append(f"{key} = [{items}]")
        else:
            lines.append(f"{key} = {value}")

    path.write_text("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def load_plan(context: Context) -> Plan | None:
    path = _plan_meta_path(context)

    if not path.exists():
        return None

    with path.open("rb") as f:
        raw = tomllib.load(f)

    return Plan(
        target_roles=list(raw.get("target_roles", [])),
        target_total_comp_min=raw.get("target_total_comp_min"),
        target_total_comp_max=raw.get("target_total_comp_max"),
        horizon_years=raw.get("horizon_years"),
        primary_focus=raw.get("primary_focus"),
        last_reviewed=raw.get("last_reviewed"),
    )


def save_plan(context: Context, plan: Plan) -> None:
    root = _plan_root(context)
    root.mkdir(parents=True, exist_ok=True)

    data = {
        "target_roles": plan.target_roles,
        "target_total_comp_min": plan.target_total_comp_min,
        "target_total_comp_max": plan.target_total_comp_max,
        "horizon_years": plan.horizon_years,
        "primary_focus": plan.primary_focus,
        "last_reviewed": plan.last_reviewed,
    }

    _write_meta_toml(_plan_meta_path(context), data)

    # Ensure notes file exists
    notes_path = root / "notes.md"
    if not notes_path.exists():
        notes_path.write_text("")


# ---------------------------------------------------------------------------
# Doctor
# ---------------------------------------------------------------------------


def lint_plan(context: Context) -> list[str]:
    issues: list[str] = []
    root = _plan_root(context)

    if not root.exists():
        return issues

    meta_path = _plan_meta_path(context)

    if not meta_path.exists():
        issues.append("Plan directory exists but meta.toml is missing")

    return issues


def fix_plan(context: Context) -> list[str]:
    actions: list[str] = []
    root = _plan_root(context)

    if not root.exists():
        return actions

    meta_path = _plan_meta_path(context)

    if not meta_path.exists():
        default = Plan(
            target_roles=[],
            target_total_comp_min=None,
            target_total_comp_max=None,
            horizon_years=None,
            primary_focus=None,
            last_reviewed=None,
        )
        save_plan(context, default)
        actions.append("Created missing meta.toml for plan")

    return actions
