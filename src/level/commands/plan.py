import argparse
import subprocess
from typing import Any

from level.config import build_context, get_data_root
from level.plan.plan import (
    load_plan,
    save_plan,
    lint_plan,
    fix_plan,
    Plan,
)


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------


def handle_plan_show(args: argparse.Namespace) -> None:
    context = build_context()
    plan = load_plan(context)

    if plan is None:
        print("No plan defined.")
        return

    print("Career Plan")
    print("-----------")
    print(f"Target Roles: {', '.join(plan.target_roles) if plan.target_roles else '—'}")
    print(f"Comp Range: {plan.target_total_comp_min} - {plan.target_total_comp_max}")
    print(f"Horizon (years): {plan.horizon_years}")
    print(f"Primary Focus: {plan.primary_focus}")
    print(f"Last Reviewed: {plan.last_reviewed}")


def handle_plan_edit(args: argparse.Namespace) -> None:
    context = build_context()

    # Ensure plan exists
    plan = load_plan(context)
    if plan is None:
        save_plan(
            context,
            Plan(
                target_roles=[],
                target_total_comp_min=None,
                target_total_comp_max=None,
                horizon_years=None,
                primary_focus=None,
                last_reviewed=None,
            ),
        )

    data_root = get_data_root(context)
    meta_path = data_root / "plan" / "meta.toml"
    editor = context.config.editor or "vi"

    subprocess.run([editor, str(meta_path)])


def handle_plan_gap(args: argparse.Namespace) -> None:
    print("Skill gap analysis not yet implemented.")


def handle_plan_goals(args: argparse.Namespace) -> None:
    print("Goal listing not yet implemented.")


def handle_plan_review(args: argparse.Namespace) -> None:
    print("Review workflow not yet implemented.")


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


def register(subparsers: argparse._SubParsersAction[Any]) -> None:
    plan_parser = subparsers.add_parser(
        "plan",
        help="Career planning commands",
    )

    plan_subparsers = plan_parser.add_subparsers(dest="plan_command")

    # plan show
    plan_show_parser = plan_subparsers.add_parser(
        "show",
        help="Show current long-term plan",
    )
    plan_show_parser.set_defaults(func=handle_plan_show)

    # plan edit
    plan_edit_parser = plan_subparsers.add_parser(
        "edit",
        help="Edit goals / target roles",
    )
    plan_edit_parser.set_defaults(func=handle_plan_edit)

    # plan gap
    plan_gap_parser = plan_subparsers.add_parser(
        "gap",
        help="Show skill gap analysis",
    )
    plan_gap_parser.set_defaults(func=handle_plan_gap)

    # plan goals
    plan_goals_parser = plan_subparsers.add_parser(
        "goals",
        help="List defined goals",
    )
    plan_goals_parser.set_defaults(func=handle_plan_goals)

    # plan review
    plan_review_parser = plan_subparsers.add_parser(
        "review",
        help="Quarterly / periodic review",
    )
    plan_review_parser.set_defaults(func=handle_plan_review)
