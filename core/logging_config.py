"""Centralized logging configuration for CodeTuneStudio.

This module provides a single source of truth for logging configuration
across the entire application, preventing duplicate logging.basicConfig()
calls and ensuring consistent log formatting.
"""

import logging
import sys
from typing import Optional


# Global flag to ensure logging is configured only once
_logging_configured = False


def setup_logging(
    level: int = logging.INFO,
    format_string: Optional[str] = None,
    force: bool = False,
) -> None:
    """
    Configure logging for the entire application.

    This should be called once at application startup. Subsequent calls
    will be ignored unless force=True.

    Args:
        level: Logging level (default: logging.INFO)
        format_string: Custom format string (optional)
        force: Force reconfiguration even if already configured
    """
    global _logging_configured

    if _logging_configured and not force:
        return

    if format_string is None:
        format_string = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "%(filename)s:%(lineno)d - %(message)s"
        )

    logging.basicConfig(
        level=level,
        format=format_string,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
        force=force,
    )

    _logging_configured = True


def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """
    Get a configured logger instance.

    Args:
        name: Logger name (typically __name__)
        level: Optional override for logger level

    Returns:
        Configured logger instance
    """
    # Ensure logging is configured
    setup_logging()

    logger = logging.getLogger(name)

    if level is not None:
        logger.setLevel(level)

    return logger


def set_level(level: int) -> None:
    """
    Change the logging level for the root logger.

    Args:
        level: New logging level (e.g., logging.DEBUG, logging.WARNING)
    """
    logging.getLogger().setLevel(level)


def disable_logger(name: str) -> None:
    """
    Disable a specific logger (useful for silencing verbose third-party libraries).

    Args:
        name: Logger name to disable
    """
    logging.getLogger(name).setLevel(logging.CRITICAL + 1)
