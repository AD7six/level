import pytest


@pytest.fixture(autouse=True)
def _clear_output(capsys):
    """
    Ensure every command test starts and ends
    with a clean stdout/stderr capture buffer.
    """
    capsys.readouterr()
    yield
    capsys.readouterr()
