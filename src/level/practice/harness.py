import time
from collections.abc import Callable, Iterable, Sequence
from typing import Any


def run_tests(
    solve_fn: Callable[..., Any],
    test_cases: Iterable[tuple[Sequence[Any], Any, str]],
) -> None:
    test_cases = list(test_cases)
    total_start = time.perf_counter()

    for i, (inputs, expected, message) in enumerate(test_cases, 1):
        start = time.perf_counter()
        result = solve_fn(*inputs)
        duration = (time.perf_counter() - start) * 1000

        assert result == expected, (
            f"Test {i} ({message}) failed! " f"Expected {expected}, got {result}"
        )

        print(f"✓ Test {i} ({message}) passed in {duration:.3f}ms")

    total_duration = (time.perf_counter() - total_start) * 1000
    print(f"\n✓ {len(test_cases)} tests passed in {total_duration:.3f}ms total")
