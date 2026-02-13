import argparse


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------


def handle_plan_show(args: argparse.Namespace) -> None:
    print("[level] Current career plan (not yet implemented)")


def handle_plan_edit(args: argparse.Namespace) -> None:
    print("[level] Editing career plan (not yet implemented)")


def handle_plan_gap(args: argparse.Namespace) -> None:
    print("[level] Showing skill gap analysis (not yet implemented)")


def handle_plan_goals(args: argparse.Namespace) -> None:
    print("[level] Listing defined goals (not yet implemented)")


def handle_plan_review(args: argparse.Namespace) -> None:
    print("[level] Running quarterly / periodic review (not yet implemented)")


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


def register(subparsers: argparse._SubParsersAction) -> None:
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
