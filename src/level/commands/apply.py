"""
Apply command module.

Responsible for registering and handling `level apply` subcommands.
"""

import argparse
from datetime import date, datetime

from level.applications.applications import (
    Application,
    create_application,
    get_application,
    list_applications,
    move_application,
)
from level.applications.schema import STATES, TERMINAL_STATES
from level.config import build_context

# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------


def handle_apply_new(args: argparse.Namespace) -> None:
    context = build_context()

    company = args.company
    role = args.role

    interactive = company is None or role is None

    try:
        while not company:
            company = input("Company: ").strip()
    except EOFError:
        raise SystemExit("Aborted.") from None

    try:
        while not role:
            role = input("Role: ").strip()
    except EOFError:
        raise SystemExit("Aborted.") from None

    if interactive:
        default_date = args.date
        try:
            date_input = input(
                f"Application date (YYYY-MM-DD) [{default_date}]: "
            ).strip()
        except EOFError:
            raise SystemExit("Aborted.") from None
        if date_input:
            args.date = date_input

    try:
        validated_date = datetime.strptime(args.date, "%Y-%m-%d").date()
    except ValueError:
        raise SystemExit("Invalid date format. Use YYYY-MM-DD.") from None

    app = create_application(context, company, role, validated_date.isoformat())
    print(f"✔ Created {app.slug}")
    print(f"  Company: {app.company}")
    print(f"  Role:    {app.role}")
    print(f"  State:   {app.state}")


def handle_apply_list(args: argparse.Namespace) -> None:
    context = build_context()
    apps = list(list_applications(context, state=args.state))

    # Filter terminal states unless --all is provided
    if not getattr(args, "all", False):
        apps = [a for a in apps if a.state not in TERMINAL_STATES]

    if not apps:
        return

    # Group by state in canonical order
    grouped: dict[str, list[Application]] = {}
    for app in apps:
        grouped.setdefault(app.state, []).append(app)

    for state in STATES:
        if state not in grouped:
            continue

        print(state.upper())

        # Sort by created_at descending if available, else by slug
        state_apps = grouped[state]
        state_apps.sort(
            key=lambda a: (a.created_at or "", a.slug),
            reverse=True,
        )

        for app in state_apps:
            created = app.created_at or ""
            company = app.company or ""
            role = app.role or ""
            print(f"  {created:12}  {company:<22} {role}")

        print()


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
    apply_new_parser.add_argument(
        "--date", help="Application date", default=date.today().strftime("%Y-%m-%d")
    )
    apply_new_parser.add_argument("--company", help="Company name")
    apply_new_parser.add_argument("--role", help="Role title")
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
    apply_list_parser.add_argument(
        "--all",
        action="store_true",
        help="Include terminal states",
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
