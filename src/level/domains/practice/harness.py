import time
from collections.abc import Callable, Iterable, Sequence
from typing import Any


def run_tests(
    solve_fn: Callable[..., Any],
    test_cases: Iterable[tuple[Sequence[Any], Any, str]],
) -> None:
    """
    Execute test cases in a style similar to interview platforms.

    Each test case is a tuple:
        (inputs, expected_output, description)
    """

    test_cases = list(test_cases)
    total = len(test_cases)

    total_start = time.perf_counter()
    passed = 0

    for i, (inputs, expected, message) in enumerate(test_cases, 1):
        start = time.perf_counter()

        try:
            result = solve_fn(*inputs)
        except Exception as exc:
            duration = (time.perf_counter() - start) * 1000
            print(f"✗ Test {i} ({message}) crashed after {duration:.3f}ms")
            print(f"  input:    {inputs}")
            print(f"  error:    {exc}")
            break

        duration = (time.perf_counter() - start) * 1000

        if result == expected:
            print(f"✓ Test {i} ({message}) passed in {duration:.3f}ms")
            passed += 1
            continue

        print(f"✗ Test {i} ({message}) failed in {duration:.3f}ms")
        print(f"  input:    {inputs}")
        print(f"  expected: {expected}")
        print(f"  got:      {result}")
        break

    total_duration = (time.perf_counter() - total_start) * 1000

    print()
    if passed == total:
        print(f"✓ {passed}/{total} tests passed in {total_duration:.3f}ms")
    else:
        print(f"✗ {passed}/{total} tests passed in {total_duration:.3f}ms")


def run_interview(
    solve_fn: Callable[..., Any],
    phases: Iterable[tuple[str, Iterable[tuple[Sequence[Any], Any, str]]]],
) -> None:
    """
    Execute progressive interview phases.

    Each phase is a tuple:
        (phase_name, test_cases)

    Phases are gated: the next phase will not execute unless all tests in the
    previous phase pass. This mirrors real interview workflows where new
    constraints are introduced only after the base problem works.
    """

    for phase_index, (phase_name, test_cases) in enumerate(phases, 1):
        print(f"\n=== Phase {phase_index}: {phase_name} ===\n")

        test_cases = list(test_cases)
        total = len(test_cases)

        total_start = time.perf_counter()
        passed = 0

        for i, (inputs, expected, message) in enumerate(test_cases, 1):
            start = time.perf_counter()

            try:
                result = solve_fn(*inputs)
            except Exception as exc:
                duration = (time.perf_counter() - start) * 1000
                print(f"✗ Test {i} ({message}) crashed after {duration:.3f}ms")
                print(f"  input:    {inputs}")
                print(f"  error:    {exc}")
                break

            duration = (time.perf_counter() - start) * 1000

            if result == expected:
                print(f"✓ Test {i} ({message}) passed in {duration:.3f}ms")
                passed += 1
                continue

            print(f"✗ Test {i} ({message}) failed in {duration:.3f}ms")
            print(f"  input:    {inputs}")
            print(f"  expected: {expected}")
            print(f"  got:      {result}")
            break

        total_duration = (time.perf_counter() - total_start) * 1000

        print()
        if passed == total:
            print(f"✓ {passed}/{total} tests passed in {total_duration:.3f}ms")
            continue

        print(f"✗ {passed}/{total} tests passed in {total_duration:.3f}ms")
        return  ## Do not progress to next phase if any test fails
