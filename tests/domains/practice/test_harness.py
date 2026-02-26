from level.domains.practice.harness import run_tests


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


def test_run_tests_fails():
    def solve(x):
        return x + 1

    cases = [
        ((2,), 5, "incorrect expectation"),
    ]

    try:
        run_tests(solve, cases)
    except AssertionError as e:
        assert "failed" in str(e)
    else:
        raise AssertionError("Expected AssertionError")
