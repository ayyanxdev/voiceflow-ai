"""Structured logging configuration."""

import logging
import sys


def setup_logging() -> logging.Logger:
    """Configure structured logging for the application."""
    logger = logging.getLogger("voiceflow")
    logger.setLevel(logging.DEBUG if __debug__ else logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG if __debug__ else logging.INFO)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


log = setup_logging()
