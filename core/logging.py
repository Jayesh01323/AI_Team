"""
Centralized logging configuration.

All modules should use::

    from core.logging import get_logger
    logger = get_logger(__name__)
"""

import logging
import sys

from core.config import LOG_FORMAT, LOG_LEVEL


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger for the given module name."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(handler)
        logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
        logger.propagate = False

    return logger
