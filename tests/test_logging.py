import logging

from level.logging import configure_logging


def _reset_logging():
    """Ensure logging is reconfigurable between tests."""
    logging.shutdown()
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)


def test_default_log_level_info(monkeypatch):
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    _reset_logging()

    configure_logging()

    assert logging.getLogger().level == logging.INFO


def test_log_level_from_env(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    _reset_logging()

    configure_logging()

    assert logging.getLogger().level == logging.DEBUG


def test_invalid_log_level_falls_back_to_info(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "NOT_A_LEVEL")
    _reset_logging()

    configure_logging()

    assert logging.getLogger().level == logging.INFO


def test_debug_flag_overrides_env(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "WARNING")
    _reset_logging()

    configure_logging(debug=True)

    assert logging.getLogger().level == logging.DEBUG
