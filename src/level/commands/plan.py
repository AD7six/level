import argparse
import subprocess
from typing import Any
from dataclasses import fields

from level.config import build_context, get_data_root
from level.plan.plan import (
    Plan,
    fix_plan,
    lint_plan,
    load_plan,
    save_plan,
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

    for k, v in plan.as_display_dict().items():
        print(f"{k}: {v}")

def handle_plan_edit(args: argparse.Namespace) -> None:
    context = build_context()

    # Ensure plan directory and canonical structure exist
    fix_plan(context)

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


def handle_plan_doctor(args: argparse.Namespace) -> None:
    context = build_context()

    if args.fix:
        actions = fix_plan(context)
        if not actions:
            print("No changes required.")
            return

        print("Actions performed:")
        for action in actions:
            print(f"  - {action}")
        return

    issues = lint_plan(context)

    if not issues:
        print("No issues detected.")
        return

    print("Issues detected:")
    for issue in issues:
        print(f"  - {issue}")


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

    # plan doctor
    plan_doctor_parser = plan_subparsers.add_parser(
        "doctor",
        help="Validate and optionally repair plan structure",
    )
    plan_doctor_parser.add_argument(
        "--fix",
        action="store_true",
        help="Automatically fix detected issues",
    )
    plan_doctor_parser.set_defaults(func=handle_plan_doctor)
