#!/usr/bin/env python3

import argparse
import json
import sys
from pathlib import Path

TOLERANCE = 1.0  # 1% tolerance for coverage decrease


def load_percent(path: Path) -> tuple[bool, float, str | None]:
    if not path.exists():
        return False, 0.0, f"{path} not found"

    try:
        with path.open() as f:
            data = json.load(f)
    except json.JSONDecodeError:
        return False, 0.0, f"{path} is not valid JSON"

    try:
        value = float(data["totals"]["percent_covered"])
    except KeyError, TypeError, ValueError:
        return (
            False,
            0.0,
            f"{path} does not contain totals.percent_covered as a numeric value",
        )

    return True, value, None


def check_coverage(
    current_file: str = ".coverage.json",
    comparison_file: str = ".coverage_baseline.json",
    strict: bool = True,
) -> int:
    current_path = Path(current_file)
    comparison_path = Path(comparison_file)

    ok, current_pc, err = load_percent(current_path)
    if not ok:
        print(err)
        return 1

    if not comparison_path.exists():
        if strict:
            print(f"{comparison_file} not found, cannot compare coverage")
            return 1
        print(f"{comparison_file} not found, creating baseline from {current_file}")
        minimal = {"totals": {"percent_covered": current_pc}}
        comparison_path.write_text(json.dumps(minimal))

    ok, comparison_pc, err = load_percent(comparison_path)
    if not ok:
        print(err)
        return 1

    current_cov = int(round(current_pc * 100))
    comparison_cov = int(round(comparison_pc * 100))

    tolerance = int(round(TOLERANCE * 100))
    delta = comparison_cov - current_cov

    if delta > tolerance:
        print(
            f"Coverage decreased by {delta/100:.2f}%: "
            f"{current_cov/100:.2f}% (current) < {comparison_cov/100:.2f}% (baseline)"
        )
        return 1
    elif delta > 0:
        print(
            f"Coverage decreased by {delta/100:.2f}% (within tolerance): "
            f"{current_cov/100:.2f}% < {comparison_cov/100:.2f}%"
        )
    else:
        print(
            f"Coverage OK: "
            f"{current_cov/100:.2f}% (current) >= {comparison_cov/100:.2f}% (baseline)"
        )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--compare", nargs=2, metavar=("PR", "MAIN"))
    parser.add_argument("--update", action="store_true")
    args = parser.parse_args()

    # Explicit baseline update (local dev only)
    baseline = Path(".coverage_baseline.json")
    if args.update and not args.compare:
        print("Updating coverage baseline")
        baseline.unlink(missing_ok=True)

    # CI comparison mode
    if args.compare:
        return check_coverage(args.compare[0], args.compare[1], strict=True)

    # Local comparison mode
    return check_coverage(strict=False)


if __name__ == "__main__":
    sys.exit(main())
