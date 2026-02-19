from level.applications.schema import STATES

# ---------------------------------------------------------------------------
# basic schema integrity
# ---------------------------------------------------------------------------


def test_states_is_non_empty():
    assert STATES
    assert isinstance(STATES, (list, set, tuple))


def test_states_are_unique():
    assert len(STATES) == len(set(STATES))


def test_expected_core_states_present():
    # These are foundational states the application logic depends on
    expected = {"drafts", "applied", "interviewing", "rejected"}
    assert expected.issubset(set(STATES))


def test_states_are_strings():
    for state in STATES:
        assert isinstance(state, str)
        assert state == state.strip()
        assert state != ""


# ---------------------------------------------------------------------------
# transition consistency (lightweight guard)
# ---------------------------------------------------------------------------


def test_states_are_lowercase():
    for state in STATES:
        assert state == state.lower()
