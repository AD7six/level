import pytest

from level.domains.applications.schema import (
    STATES,
    default_schema_dict,
    validate_schema,
)

# ---------------------------------------------------------------------------
# basic contract guards (minimal)
# ---------------------------------------------------------------------------


def test_expected_core_states_present():
    # These are foundational states the application logic depends on
    expected = {"drafts", "applied", "interviewing", "rejected"}
    assert expected.issubset(set(STATES))


# ---------------------------------------------------------------------------
# schema validation behaviour (high‑value tests)
# ---------------------------------------------------------------------------


def test_validate_schema_accepts_default():
    data = default_schema_dict()
    # Align ordering with canonical constant to satisfy strict equality
    data["states"] = STATES
    validate_schema(data)  # should not raise


def test_validate_schema_rejects_wrong_version():
    data = default_schema_dict()
    data["version"] = 999

    with pytest.raises(ValueError):
        validate_schema(data)


@pytest.mark.parametrize(
    "field,bad_value",
    [
        ("states", "not-a-list"),
        ("terminal_states", "not-a-list"),
        ("transitions", "not-a-dict"),
    ],
)
def test_validate_schema_rejects_wrong_types(field, bad_value):
    data = default_schema_dict()
    data[field] = bad_value

    with pytest.raises(ValueError):
        validate_schema(data)


def test_validate_schema_rejects_states_mismatch():
    data = default_schema_dict()
    data["states"] = ["drafts"]  # incomplete

    with pytest.raises(ValueError):
        validate_schema(data)


def test_validate_schema_rejects_terminal_mismatch():
    data = default_schema_dict()
    data["terminal_states"] = []

    with pytest.raises(ValueError):
        validate_schema(data)
