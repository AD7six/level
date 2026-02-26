"""
Apply command module.

Responsible for registering and handling `level application` subcommands.
"""

import argparse
from datetime import date, datetime

from level.commands._doctor import make_doctor_handler
from level.config import Context
from level.domains.applications.applications import (
    Application,
    create_application,
    fix_applications,
    get_application,
    lint_applications,
    list_applications,
    move_application,
)
from level.domains.applications.schema import STATES, TERMINAL_STATES

# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------


def handle_application_new(context: Context, args: argparse.Namespace) -> None:

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


def handle_application_list(context: Context, args: argparse.Namespace) -> None:
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
            print(f"  {created:12}  {company:<22} {role:<40} ({app.slug})")

        print()


def handle_application_show(context: Context, args: argparse.Namespace) -> None:
    app = get_application(context, args.slug)

    print(f"Slug:       {app.slug}")
    print(f"State:      {app.state}")
    print(f"Company:    {app.company}")
    print(f"Role:       {app.role}")
    print(f"Created At: {app.created_at}")
    print(f"Path:       {app.path}")


def handle_application_move(context: Context, args: argparse.Namespace) -> None:
    app = move_application(context, args.slug, args.state)
    print(f"✔ Moved '{app.slug}' to '{app.state}'")


def handle_application_timeline(context: Context, args: argparse.Namespace) -> None:
    # Timeline not yet implemented – placeholder for future domain expansion
    print("Timeline not yet implemented.")


# ---------------------------------------------------------------------------
# Doctor Handler
# ---------------------------------------------------------------------------

handle_application_doctor = make_doctor_handler(
    lint_applications,
    fix_applications,
)

# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


def register(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    application_parser = subparsers.add_parser(
        "application",
        help="Application tracking commands",
    )

    application_subparsers = application_parser.add_subparsers(
        dest="application_command"
    )

    # application new
    application_new_parser = application_subparsers.add_parser(
        "new",
        help="Create new application entry",
    )
    application_new_parser.add_argument(
        "--date", help="Application date", default=date.today().strftime("%Y-%m-%d")
    )
    application_new_parser.add_argument("--company", help="Company name")
    application_new_parser.add_argument("--role", help="Role title")
    application_new_parser.set_defaults(func=handle_application_new)

    # application list
    application_list_parser = application_subparsers.add_parser(
        "list",
        help="List applications",
    )
    application_list_parser.add_argument(
        "--state",
        choices=sorted(STATES),
        help="Filter by state",
    )
    application_list_parser.add_argument(
        "--all",
        action="store_true",
        help="Include terminal states",
    )
    application_list_parser.set_defaults(func=handle_application_list)

    # application show
    application_show_parser = application_subparsers.add_parser(
        "show",
        help="Show application details",
    )
    application_show_parser.add_argument("slug", help="Application slug")
    application_show_parser.set_defaults(func=handle_application_show)

    # application move
    application_move_parser = application_subparsers.add_parser(
        "move",
        help="Move between pipeline stages",
    )
    application_move_parser.add_argument("slug", help="Application slug")
    application_move_parser.add_argument(
        "state",
        choices=sorted(STATES),
        help="New state",
    )
    application_move_parser.set_defaults(func=handle_application_move)

    # application doctor
    application_doctor_parser = application_subparsers.add_parser(
        "doctor",
        help="Lint and optionally fix application structure",
    )
    application_doctor_parser.add_argument(
        "--fix",
        action="store_true",
        help="Apply fixes",
    )
    application_doctor_parser.set_defaults(func=handle_application_doctor)

    # application timeline
    application_timeline_parser = application_subparsers.add_parser(
        "timeline",
        help="Show application timeline",
    )
    application_timeline_parser.add_argument("slug", help="Application slug")
    application_timeline_parser.set_defaults(func=handle_application_timeline)
