import argparse

from level.config import build_context, run_diagnostics


def handle_init(args: argparse.Namespace) -> None:
    """
    Initialize repository structure.

    This is a thin UX alias for:
        level config doctor --fix

    It delegates entirely to the diagnostics engine with fix=True.
    """
    context = build_context()

    print("Initializing level repository...\n")

    results = run_diagnostics(context, fix=True)

    for result in results:
        status = "✔" if result.ok else "✖"
        print(f"{status} {result.message}")


def register(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    parser = subparsers.add_parser(
        "init",
        help="Initialize repository structure (alias for 'config doctor --fix')",
    )
    parser.set_defaults(func=handle_init)
