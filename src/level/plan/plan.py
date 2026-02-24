from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from level.config import Context, get_data_root
from level.core.meta import write_meta_toml

# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Plan:
    target_roles: list[str] = field(
        default_factory=list,
        metadata={"comment": "Roles you are actively targeting"},
    )
    target_industries: list[str] = field(
        default_factory=list,
        metadata={"comment": "Industries or domains of interest"},
    )
    target_locations: list[str] = field(
        default_factory=list,
        metadata={"comment": "Preferred geographic locations"},
    )
    work_modes: list[str] = field(
        default_factory=list,
        metadata={"comment": "Preferred work modes (remote, hybrid, in-office)"},
    )

    preferred_track: str | None = field(
        default=None,
        metadata={"comment": "Preferred career track (IC, EM, Both)"},
    )
    target_company_stages: list[str] = field(
        default_factory=list,
        metadata={"comment": "Preferred company stages (e.g. Seed, Series C, Public)"},
    )
    risk_tolerance: str | None = field(
        default=None,
        metadata={"comment": "Risk tolerance (low, medium, high)"},
    )

    target_total_comp_min: int | None = field(
        default=None,
        metadata={"comment": "Minimum acceptable total compensation"},
    )
    target_total_comp_max: int | None = field(
        default=None,
        metadata={"comment": "Maximum target total compensation"},
    )
    comp_currency: str | None = field(
        default=None,
        metadata={"comment": "Currency for compensation (e.g. EUR, USD)"},
    )

    horizon_years: int | None = field(
        default=None,
        metadata={"comment": "Strategic time horizon in years"},
    )
    primary_focus: str | None = field(
        default=None,
        metadata={"comment": "Primary strategic focus area"},
    )

    last_reviewed: date | None = field(
        default=None,
        metadata={"comment": "Date the plan was last formally reviewed"},
    )

    def as_display_dict(self) -> dict[str, str]:
        result: dict[str, str] = {}

        # Roles & positioning
        result["Target Roles"] = (
            ", ".join(self.target_roles) if self.target_roles else "—"
        )
        result["Target Industries"] = (
            ", ".join(self.target_industries) if self.target_industries else "—"
        )
        result["Target Locations"] = (
            ", ".join(self.target_locations) if self.target_locations else "—"
        )
        result["Work Modes"] = ", ".join(self.work_modes) if self.work_modes else "—"

        result["Preferred Track"] = self.preferred_track or "—"
        result["Company Stages"] = (
            ", ".join(self.target_company_stages) if self.target_company_stages else "—"
        )
        result["Risk Tolerance"] = self.risk_tolerance or "—"

        # Compensation (aggregate)
        if self.target_total_comp_min or self.target_total_comp_max:
            currency = self.comp_currency or ""
            min_tc = (
                f"{self.target_total_comp_min:,}"
                if self.target_total_comp_min is not None
                else "?"
            )
            max_tc = (
                f"{self.target_total_comp_max:,}"
                if self.target_total_comp_max is not None
                else "?"
            )
            result["Target Total Compensation"] = (
                f"{currency} {min_tc} - {max_tc}".strip()
            )
        else:
            result["Target Total Compensation"] = "—"

        result["Horizon (Years)"] = (
            str(self.horizon_years) if self.horizon_years else "—"
        )
        result["Primary Focus"] = self.primary_focus or "—"
        result["Last Reviewed"] = (
            self.last_reviewed.isoformat() if self.last_reviewed else "—"
        )

        return result


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _plan_root(context: Context) -> Path:
    return get_data_root(context) / "plan"


def _plan_meta_path(context: Context) -> Path:
    return _plan_root(context) / "meta.toml"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def load_plan(context: Context) -> Plan | None:
    path = _plan_meta_path(context)

    if not path.exists():
        return None

    with path.open("rb") as f:
        raw = tomllib.load(f)

    def _get_list(key: str) -> list[str]:
        value = raw.get(key, [])
        if isinstance(value, list):
            return [str(v) for v in value]
        return []

    def _get_int(key: str) -> int | None:
        value = raw.get(key)
        if value == "" or value is None:
            return None
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
        return None

    def _get_str(key: str) -> str | None:
        value = raw.get(key)
        if value == "" or value is None:
            return None
        if isinstance(value, str):
            return value
        return str(value)

    def _get_date(key: str) -> date | None:
        value = raw.get(key)
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            try:
                return date.fromisoformat(value)
            except ValueError:
                return None
        return None

    return Plan(
        target_roles=_get_list("target_roles"),
        target_industries=_get_list("target_industries"),
        target_locations=_get_list("target_locations"),
        work_modes=_get_list("work_modes"),
        preferred_track=_get_str("preferred_track"),
        target_company_stages=_get_list("target_company_stages"),
        risk_tolerance=_get_str("risk_tolerance"),
        target_total_comp_min=_get_int("target_total_comp_min"),
        target_total_comp_max=_get_int("target_total_comp_max"),
        comp_currency=_get_str("comp_currency"),
        horizon_years=_get_int("horizon_years"),
        primary_focus=_get_str("primary_focus"),
        last_reviewed=_get_date("last_reviewed"),
    )


def save_plan(context: Context, plan: Plan) -> None:
    root = _plan_root(context)
    root.mkdir(parents=True, exist_ok=True)

    write_meta_toml(_plan_meta_path(context), plan)

    notes_path = root / "notes.md"
    if not notes_path.exists():
        notes_path.write_text("")


def _default_plan() -> Plan:
    return Plan()


# ---------------------------------------------------------------------------
# Doctor
# ---------------------------------------------------------------------------


def lint_plan(context: Context) -> list[str]:
    issues: list[str] = []
    root = _plan_root(context)

    if not root.exists():
        issues.append("Plan directory does not exist")
        return issues

    meta_path = _plan_meta_path(context)

    if not meta_path.exists():
        issues.append("meta.toml is missing")
        return issues

    try:
        plan = load_plan(context)
    except Exception:
        issues.append("meta.toml could not be parsed")
        return issues

    if plan is None:
        issues.append("meta.toml is invalid")
        return issues

    # Validate list fields
    for name in [
        "target_roles",
        "target_industries",
        "target_locations",
        "work_modes",
        "target_company_stages",
    ]:
        value = getattr(plan, name)
        if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
            issues.append(f"{name} must be a list of strings")

    # Validate numeric fields
    if plan.target_total_comp_min is not None and not isinstance(
        plan.target_total_comp_min, int
    ):
        issues.append("target_total_comp_min must be an integer")

    if plan.target_total_comp_max is not None and not isinstance(
        plan.target_total_comp_max, int
    ):
        issues.append("target_total_comp_max must be an integer")

    if plan.horizon_years is not None and not isinstance(plan.horizon_years, int):
        issues.append("horizon_years must be an integer")

    # Validate currency
    if plan.comp_currency:
        if (
            not isinstance(plan.comp_currency, str)
            or len(plan.comp_currency) != 3
            or not plan.comp_currency.isupper()
        ):
            issues.append("comp_currency must be a 3-letter uppercase currency code")

    # Validate preferred_track
    if plan.preferred_track:
        if plan.preferred_track not in {"IC", "EM", "Both"}:
            issues.append("preferred_track must be one of: IC, EM, Both")

    # Validate risk_tolerance
    if plan.risk_tolerance:
        if plan.risk_tolerance not in {"low", "medium", "high"}:
            issues.append("risk_tolerance must be one of: low, medium, high")

    # Validate date
    if plan.last_reviewed is not None and not isinstance(plan.last_reviewed, date):
        issues.append("last_reviewed must be a valid date")

    return issues


def fix_plan(context: Context) -> list[str]:
    actions: list[str] = []
    root = _plan_root(context)
    root.mkdir(parents=True, exist_ok=True)

    meta_path = _plan_meta_path(context)

    if not meta_path.exists():
        save_plan(context, _default_plan())
        actions.append("Created meta.toml for plan")
        return actions

    plan = load_plan(context)
    if plan is None:
        save_plan(context, _default_plan())
        actions.append("Recreated invalid meta.toml")
        return actions

    save_plan(context, plan)
    actions.append("Normalized plan meta.toml structure")

    return actions
