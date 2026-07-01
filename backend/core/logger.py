import logging
import sys

from backend.core.config import settings


def setup_logger(name: str = "research_writer") -> logging.Logger:
    logger = logging.getLogger(name)

    # Check if handlers are already configured to avoid double adding
    if logger.handlers:
        return logger

    log_level_str = settings.LOG_LEVEL.upper()
    level = getattr(logging, log_level_str, logging.INFO)
    logger.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    # Semi-structured production-ready formatting: timestamp | level | logger_name | message
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Disable propagation to avoid duplicate logs in default uvicorn setup
    logger.propagate = False

    return logger

logger = setup_logger()
