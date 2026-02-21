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

    # Account for rounding when comparing floats. We're storing to 2 decimal
    # places, so current could be up to 0.005% lower than baseline without
    # actually decreasing coverage.
    EPSILON = 0.005  # 0.005% tolerance

    if baseline_file.exists():
        baseline = float(baseline_file.read_text().strip())
        if (current + EPSILON) < baseline:
            print(f"Coverage decreased: {current:.2f}% < {baseline:.2f}%")
            return 1
        print(f"Coverage OK: {current:.2f}% (baseline {baseline:.2f}%)")
    else:
        print(f"No baseline found. Setting baseline to {current:.2f}%")

    baseline_file.write_text(f"{current:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
