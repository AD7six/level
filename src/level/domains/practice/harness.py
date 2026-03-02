import os
import time
from collections.abc import Callable, Iterable, Sequence
from typing import Any


def _normalize_case(case: tuple[Any, ...] | tuple[Any, Any] | tuple[Any, Any, str]) -> tuple[Sequence[Any], Any, str]:
    """Normalize test definitions so authors can write shorter cases."""

    if len(case) == 2:
        inputs, expected = case
        message = ""
    else:
        inputs, expected, message = case

    if not isinstance(inputs, (tuple, list)):
        inputs = (inputs,)

    return inputs, expected, message


def _resolve_cases(cases: Iterable | Callable[[], Iterable]) -> list:
    """Allow phases to provide either a list or a generator function."""

    if callable(cases):
        cases = cases()

    return list(cases)


def run_tests(
    solve_fn: Callable[..., Any],
    test_cases: Iterable[tuple[Sequence[Any], Any, str]],
) -> bool:
    """
    Execute test cases in a style similar to interview platforms.

    Each test case is a tuple:
        (inputs, expected_output, description)
    """

    test_cases = list(test_cases)
    total = len(test_cases)

    total_start = time.perf_counter()
    passed = 0

    for i, raw_case in enumerate(test_cases, 1):
        inputs, expected, message = _normalize_case(raw_case)
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
        return True

    print(f"✗ {passed}/{total} tests passed in {total_duration:.3f}ms")
    return False


def run_interview(
    solve_fn: Callable[..., Any],
    phases: Iterable[tuple[str, Iterable[tuple[Sequence[Any], Any, str]]]],
    followups: Iterable[str | tuple[str, str]] | None = None,
) -> bool:
    """
    Execute progressive interview phases.

    Each phase is a tuple:
        (phase_name, test_cases)

    Phases are gated: the next phase will not execute unless all tests in the
    previous phase pass. This mirrors real interview workflows where new
    constraints are introduced only after the base problem works.

    Optional followups may be provided. These are discussion prompts shown
    only after all phases pass, simulating the conceptual follow-up questions
    that typically appear at the end of real interviews.

    Each follow-up may be either:
        - a string (the question), or
        - a tuple of (question, hint)

    Hints are optional guidance that can help after attempting the question.
    """
    phases = list(phases)
    last_phase_index = len(phases) - 1

    for idx, (phase_name, phase_cases) in enumerate(phases):
        phase_index = idx + 1
        is_last_phase = idx == last_phase_index

        if is_last_phase:
            print(f"\n=== Phase {phase_index}: {phase_name} ===\n")

        test_cases = _resolve_cases(phase_cases)
        total = len(test_cases)

        total_start = time.perf_counter()
        passed = 0

        for i, raw_case in enumerate(test_cases, 1):
            inputs, expected, message = _normalize_case(raw_case)
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
                if is_last_phase:
                    print(f"✓ Test {i} ({message}) passed in {duration:.3f}ms")
                passed += 1
                continue

            if not is_last_phase:
                print(f"\n=== Phase {phase_index}: {phase_name} ===\n")
            print(f"✗ Test {i} ({message}) failed in {duration:.3f}ms")
            print(f"  input:    {inputs}")
            print(f"  expected: {expected}")
            print(f"  got:      {result}")
            break

        total_duration = (time.perf_counter() - total_start) * 1000

        if passed == total:
            if is_last_phase:
                print()
                print(f"✓ Phase {phase_index} passed ({passed}/{total}) in {total_duration:.3f}ms")
            else:
                print(f"✓ Phase {phase_index} passed ({passed}/{total}) in {total_duration:.3f}ms")
            continue

        print()
        print(f"✗ Phase {phase_index} failed ({passed}/{total}) in {total_duration:.3f}ms")
        return False

    if followups:
        print("\n=== Follow-ups ===\n")

        show_hints = bool(os.getenv("SHOW_HINTS"))
        hints_exist = any(isinstance(item, tuple) and item[1] for item in followups)

        for i, item in enumerate(followups, 1):
            if isinstance(item, tuple):
                question, hint = item
                print(f"{i}. {question}")
                if show_hints and hint:
                    print(f"   Hint: {hint}")
            else:
                print(f"{i}. {item}")

        if hints_exist and not show_hints:
            print("\nRun with SHOW_HINTS=1 to see hints.")

    return True
