from level.domains.practice.harness import _run_performance_check, run_interview


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


def test_run_performance_check_linear_pass(capsys):
    # Simulate near-linear doubling ratios (~2x)
    durations = [1.0, 2.1, 4.0]
    assert _run_performance_check(durations) is True
    out = capsys.readouterr().out
    assert "Estimated heuristic complexity" in out


def test_run_performance_check_quadratic_fail(capsys):
    # Simulate quadratic scaling (~4x)
    durations = [1.0, 4.2, 16.5]
    assert _run_performance_check(durations) is False
    out = capsys.readouterr().out
    assert "Performance scaling check failed" in out


def test_performance_counts_as_test(monkeypatch, capsys):
    # Avoid real timing by stubbing performance check
    from level.domains.practice import harness

    def fake_perf(_):
        return True

    monkeypatch.setattr(harness, "_run_performance_check", fake_perf)

    def solve(x):
        return x

    phases = [
        (
            "perf phase",
            [((1,), 1, "ok")],
            {"performance_check": True},
        ),
    ]

    run_interview(solve, phases)
    out = capsys.readouterr().out
    # 1 logical test + 1 performance test
    assert "(2/2)" in out


def test_followups_printed_on_success(capsys):
    def solve(x):
        return x

    phases = [("phase", [((1,), 1, "ok")])]
    followups = ["What is the time complexity?"]

    run_interview(solve, phases, followups)
    out = capsys.readouterr().out
    assert "Follow-ups" in out
    assert "What is the time complexity?" in out


def test_crash_handling(capsys):
    def solve(x):
        raise ValueError("boom")

    phases = [("phase", [((1,), 1, "crash")])]

    run_interview(solve, phases)
    out = capsys.readouterr().out
    assert "crashed" in out
    assert "Phase 1 failed" in out
