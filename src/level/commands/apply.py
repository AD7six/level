"""
Apply command module.

Responsible for registering and handling `level apply` subcommands.
"""

import argparse

from level.applications import (
    STATES,
    create_application,
    get_application,
    list_applications,
    move_application,
)
from level.config import build_context

# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------


def handle_apply_new(args: argparse.Namespace) -> None:
    context = build_context()
    app = create_application(context, args.slug)
    print(f"✔ Created application '{app.slug}' in state '{app.state}'")


def handle_apply_list(args: argparse.Namespace) -> None:
    context = build_context()
    apps = list_applications(context, state=args.state)

    for app in apps:
        print(f"{app.state:14} {app.slug}")


def handle_apply_show(args: argparse.Namespace) -> None:
    context = build_context()
    app = get_application(context, args.slug)
    print(f"Slug:  {app.slug}")
    print(f"State: {app.state}")
    print(f"Path:  {app.path}")


def handle_apply_status(args: argparse.Namespace) -> None:
    context = build_context()
    app = move_application(context, args.slug, args.state)
    print(f"✔ Moved '{app.slug}' to '{app.state}'")


def handle_apply_timeline(args: argparse.Namespace) -> None:
    # Timeline not yet implemented – placeholder for future domain expansion
    print("Timeline not yet implemented.")


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


def register(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    apply_parser = subparsers.add_parser(
        "apply",
        help="Application tracking commands",
    )

    apply_subparsers = apply_parser.add_subparsers(dest="apply_command")

    # apply new
    apply_new_parser = apply_subparsers.add_parser(
        "new",
        help="Create new application entry",
    )
    apply_new_parser.add_argument("slug", help="Unique application slug")
    apply_new_parser.set_defaults(func=handle_apply_new)

    # apply list
    apply_list_parser = apply_subparsers.add_parser(
        "list",
        help="List applications",
    )
    apply_list_parser.add_argument(
        "--state",
        choices=sorted(STATES),
        help="Filter by state",
    )
    apply_list_parser.set_defaults(func=handle_apply_list)

    # apply show
    apply_show_parser = apply_subparsers.add_parser(
        "show",
        help="Show application details",
    )
    apply_show_parser.add_argument("slug", help="Application slug")
    apply_show_parser.set_defaults(func=handle_apply_show)

    # apply status
    apply_status_parser = apply_subparsers.add_parser(
        "status",
        help="Move between pipeline stages",
    )
    apply_status_parser.add_argument("slug", help="Application slug")
    apply_status_parser.add_argument(
        "state",
        choices=sorted(STATES),
        help="New state",
    )
    apply_status_parser.set_defaults(func=handle_apply_status)

    # apply timeline
    apply_timeline_parser = apply_subparsers.add_parser(
        "timeline",
        help="Show application timeline",
    )
    apply_timeline_parser.add_argument("slug", help="Application slug")
    apply_timeline_parser.set_defaults(func=handle_apply_timeline)
