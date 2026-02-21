#!/usr/bin/env python3

import json
from pathlib import Path


def main() -> int:
    baseline_file = Path(".coverage_baseline")
    coverage_file = Path("coverage.json")

    if not coverage_file.exists():
        print("coverage.json not found")
        return 1

    data = json.loads(coverage_file.read_text())
    current = float(data["totals"]["percent_covered"])

    # Convert to integer basis points (2 decimal places)
    current_bp = int(round(current * 100))

    if baseline_file.exists():
        baseline = float(baseline_file.read_text().strip())
        baseline_bp = int(round(baseline * 100))

        if current_bp < baseline_bp:
            print(f"Coverage decreased: {current_bp/100:.2f}% < {baseline_bp/100:.2f}%")
            return 1

        print(
            f"Coverage OK: {current_bp/100:.2f}% " f"(baseline {baseline_bp/100:.2f}%)"
        )
    else:
        print(f"No baseline found. Setting baseline to {current_bp/100:.2f}%")

    # Store baseline at 2 decimal precision
    baseline_file.write_text(f"{current_bp/100:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
