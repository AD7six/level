import math
import os
import time
from collections.abc import Callable, Iterable, Sequence
from typing import Any

# For performance tests, we want to ensure that observed durations are large
# enough to be meaningful if they complete too fast timer/bootstrap noise
# dominates and we can't reliably know how long tests take to run. This
# threshold is somewhat arbitrary and can be adjusted based on typical test
# characteristics.
MIN_TEST_DURATION_MS = 1.0


def _normalize_case(
    case: tuple[Any, ...] | tuple[Any, Any] | tuple[Any, Any, str],
) -> tuple[Sequence[Any], Any, str]:
    """Normalize test definitions so authors can write shorter cases."""

    if len(case) == 2:
        inputs, expected = case
        message = ""
    else:
        inputs, expected, message = case

    if not isinstance(inputs, tuple):
        inputs = (inputs,)

    return inputs, expected, message


def _resolve_cases(cases: Iterable[Any] | Callable[[], Iterable[Any]]) -> list[Any]:
    """Allow phases to provide either a list or a generator function."""

    if callable(cases):
        cases = cases()

    return list(cases)


def _run_performance_check(durations: list[float]) -> bool:
    """
    Analyze scaling behavior assuming each test doubles input size.

    Returns True if performance is acceptable, False if it clearly
    violates expected linear growth.
    """
    if len(durations) < 2:
        return True

    # Guard 1: Durations too small to be reliable (timer noise dominates)
    if max(durations) < MIN_TEST_DURATION_MS:
        print("\n⚠️ Performance check skipped: durations too small to be reliable.")
        print(
            f"   Max observed duration: {max(durations):.3f}ms "
            f"(threshold {MIN_TEST_DURATION_MS}ms)"
        )
        return True

    # Guard 2: Durations should generally increase if input size increases
    if any(durations[i] <= durations[i - 1] for i in range(1, len(durations))):
        print("\n⚠️ Performance check skipped: non-monotonic durations detected.")
        print(
            "   Ensure performance test inputs increase consistently "
            "(e.g., doubling size)."
        )
        return True

    ratios = [
        durations[i] / durations[i - 1]
        for i in range(1, len(durations))
        if durations[i - 1] > 0
    ]

    if not ratios:
        return True

    avg_ratio = sum(ratios) / len(ratios)

    # Estimate polynomial exponent k where T(2n) ≈ 2^k · T(n)
    estimated_exponent = math.log2(avg_ratio) if avg_ratio > 0 else 0.0

    # Heuristic classification
    if avg_ratio < 1.5:
        complexity_hint = "⭐ O(1)"
    elif avg_ratio < 2.5:
        complexity_hint = "🟢 O(n)"
    elif avg_ratio < 3.2:
        complexity_hint = "🟡 O(n log n) or noisy O(n)"
    elif avg_ratio < 6:
        complexity_hint = "❗ O(n²)"
    else:
        complexity_hint = f"🔥 O(n^{round(estimated_exponent)})"

    print(f"\nEstimated heuristic complexity: {complexity_hint}")
    print(
        f"  Estimated exponent k ≈ {estimated_exponent:.2f} "
        f"(from avg ratio {avg_ratio:.2f}x)"
    )
    for idx, r in enumerate(ratios, 1):
        print(f"    Test {idx} → {idx+1}: {r:.2f}x")

    # Fail only if clearly worse than linear
    if any(r > 3 for r in ratios):
        print("\n❌ Performance scaling check failed.")
        print("  Expected roughly ~2x time increase when input size doubles.")
        return False

    return True


def run_interview(
    solve_fn: Callable[..., Any],
    phases: Iterable[
        tuple[str, Iterable[tuple[Sequence[Any], Any, str]]]
        | tuple[str, Iterable[tuple[Sequence[Any], Any, str]], dict[str, Any]]
    ],
    followups: Iterable[str | tuple[str, str]] | None = None,
) -> bool:
    """
    Execute progressive interview phases.

    Each phase is either:
        (phase_name, test_cases)
    or:
        (phase_name, test_cases, options_dict)

    Supported options:
        - "performance_check": bool
            If True, apply scaling heuristics to this phase.

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

    for idx, phase in enumerate(phases):
        if len(phase) == 2:
            phase_name, phase_cases = phase
            phase_options: dict[str, Any] = {}
        else:
            phase_name, phase_cases, phase_options = phase

        phase_index = idx + 1
        is_last_phase = idx == last_phase_index

        if is_last_phase:
            print(f"\n=== Phase {phase_index}: {phase_name} ===\n")

        test_cases = _resolve_cases(phase_cases)
        total = len(test_cases)

        total_start = time.perf_counter()
        passed = 0
        durations: list[float] = []

        for i, raw_case in enumerate(test_cases, 1):
            inputs, expected, message = _normalize_case(raw_case)
            start = time.perf_counter()

            try:
                result = solve_fn(*inputs)
            except Exception as exc:
                duration = (time.perf_counter() - start) * 1000
                print(f"❌ Test {i} ({message}) crashed after {duration:.3f}ms")
                print(f"  input:    {inputs}")
                print(f"  error:    {exc}")
                break

            duration = (time.perf_counter() - start) * 1000
            durations.append(duration)

            if result == expected:
                if is_last_phase:
                    print(f"✅ Test {i} ({message}) passed in {duration:.3f}ms")
                passed += 1
                continue

            if not is_last_phase:
                print(f"\n=== Phase {phase_index}: {phase_name} ===\n")
            print(f"❌ Test {i} ({message}) failed in {duration:.3f}ms")
            print(f"  input:    {inputs}")
            print(f"  expected: {expected}")
            print(f"  got:      {result}")
            break

        total_duration = (time.perf_counter() - total_start) * 1000

        # Optional scaling check
        if phase_options.get("performance_check"):
            total += 1  # count as a test
            if _run_performance_check(durations):
                passed += 1  # and count as passed

        if passed == total:
            if is_last_phase:
                print()
            print(
                f"✅ Phase {phase_index} passed ({passed}/{total}) in "
                f"{total_duration:.3f}ms"
            )
            continue

        print()
        print(
            f"❌ Phase {phase_index} failed ({passed}/{total}) in "
            f"{total_duration:.3f}ms"
        )
        return False

    if followups:
        followups = list(followups)
        print("\n=== Follow-ups ===\n")

        show_hints = os.getenv("SHOW_HINTS") == "1"
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
