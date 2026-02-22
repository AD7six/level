import logging
import os


def configure_logging(debug: bool = False) -> None:
    """
    Configure application-wide logging.

    Priority:
    1. Explicit debug flag
    2. LOG_LEVEL environment variable
    3. Default to INFO
    """
    if debug:
        level = logging.DEBUG
    else:
        level_name = os.getenv("LOG_LEVEL", "INFO").upper()
        level = getattr(logging, level_name, logging.INFO)

    logging.basicConfig(
        level=level,
        format="%(levelname)s | %(name)s | %(message)s",
    )


logger = logging.getLogger("level")
