# src/level/commands/_doctor.py

import argparse
from collections.abc import Callable

from level.config import Context


def make_doctor_handler(
    lint_fn: Callable[[Context], list[str]],
    fix_fn: Callable[[Context], list[str]],
) -> Callable[[Context, argparse.Namespace], None]:
    def handler(context: Context, args: argparse.Namespace) -> None:

        if args.fix:
            actions = fix_fn(context)
            if actions:
                print("Actions performed:")
                for a in actions:
                    print(f"  - {a}")
            else:
                print("No changes required.")
        else:
            issues = lint_fn(context)
            if issues:
                print("Issues detected:")
                for i in issues:
                    print(f"  - {i}")
            else:
                print("No issues found.")

    return handler
