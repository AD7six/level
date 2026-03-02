from level.domains.practice.harness import run_interview, run_tests


def test_run_tests_passes(capsys):
    def solve(x):
        return x * 2

    cases = [
        ((2,), 4, "double 2"),
        ((3,), 6, "double 3"),
    ]

    run_tests(solve, cases)

    captured = capsys.readouterr()
    assert "2 tests passed" in captured.out


def test_run_tests_fails(capsys):
    def solve(x):
        return x + 1

    cases = [
        ((2,), 5, "incorrect expectation"),
    ]

    run_tests(solve, cases)

    captured = capsys.readouterr()
    assert "failed" in captured.out


def test_run_interview_phases_pass(capsys):
    def solve(x):
        return x * 2

    phases = [
        (
            "phase 1",
            [((2,), 4, "double")],
        ),
        (
            "phase 2",
            [((3,), 6, "double again")],
        ),
    ]

    run_interview(solve, phases)

    captured = capsys.readouterr()
    assert "Phase 1" in captured.out
    assert "Phase 2" in captured.out
    assert "Phase 1 passed" in captured.out
    assert "Phase 2 passed" in captured.out


def test_run_interview_phase_gating(capsys):
    def solve(x):
        return x * 2

    phases = [
        (
            "phase 1",
            [((2,), 5, "should fail")],
        ),
        (
            "phase 2",
            [((3,), 6, "would pass but should not run")],
        ),
    ]

    run_interview(solve, phases)

    captured = capsys.readouterr()

    # Phase 1 should appear
    assert "Phase 1" in captured.out

    # Phase 2 should NOT run because phase 1 failed
    assert "Phase 2" not in captured.out
