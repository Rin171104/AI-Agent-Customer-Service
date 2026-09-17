"""
Logger - Structured logging configuration
"""
import logging
import sys
from typing import Optional

from src.utils.config import settings


def setup_logger(name: Optional[str] = None) -> logging.Logger:
    """Setup logger with structured formatting."""
    logger = logging.getLogger(name or __name__)

    # Only configure if not already configured
    if logger.handlers:
        return logger

    # Get log level
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(level)

    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    # Format
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


# Default logger
logger = setup_logger(__name__)
