import time
from collections.abc import Callable, Iterable, Sequence
from typing import Any

TestCase = tuple[Sequence[Any], Any, str]


def run_tests(
    solve_fn: Callable[..., Any],
    test_cases: Iterable[TestCase],
) -> None:
    total_start = time.perf_counter()

    for i, (inputs, expected, message) in enumerate(test_cases, 1):
        start = time.perf_counter()

        try:
            result = solve_fn(*inputs)
        except Exception as exc:
            raise AssertionError(
                f"Test {i} ({message}) raised {type(exc).__name__}: {exc}"
            ) from exc

        duration = (time.perf_counter() - start) * 1000

        if result != expected:
            raise AssertionError(
                f"Test {i} ({message}) failed! " f"Expected {expected}, got {result}"
            )

        print(f"✓ Test {i} ({message}) passed in {duration:.3f}ms")

    total_duration = (time.perf_counter() - total_start) * 1000
    print(f"\n✓ {i} tests passed in {total_duration:.3f}ms total")
