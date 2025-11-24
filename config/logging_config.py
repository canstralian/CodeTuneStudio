"""
Centralized Logging Configuration

This module provides logging configuration for the CodeTune Studio application,
allowing environment-specific overrides and consistent logging across modules.
"""

import logging
import os
from typing import Optional


def get_log_level() -> int:
    """
    Get the logging level from environment or default to INFO.

    Supports environment variable LOG_LEVEL with values:
    - DEBUG, INFO, WARNING, ERROR, CRITICAL

    Returns:
        Logging level constant from logging module
    """
    level_name = os.environ.get("LOG_LEVEL", "INFO").upper()
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    return level_map.get(level_name, logging.INFO)


def get_log_format() -> str:
    """
    Get the log format string.

    Can be customized via LOG_FORMAT environment variable.

    Returns:
        Log format string
    """
    default_format = (
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s - "
        "%(pathname)s:%(lineno)d"
    )
    return os.environ.get("LOG_FORMAT", default_format)


def setup_logging(
    level: Optional[int] = None,
    format_string: Optional[str] = None,
    log_file: Optional[str] = None,
) -> None:
    """
    Configure application-wide logging settings.

    This function sets up logging with consistent formatting and optional
    file output. It should be called once at application startup.

    Args:
        level: Logging level (defaults to environment or INFO)
        format_string: Log message format (defaults to environment or standard)
        log_file: Optional file path for log output

    Example:
        >>> setup_logging(level=logging.DEBUG, log_file='app.log')
        >>> logger = logging.getLogger(__name__)
        >>> logger.info("Application started")
    """
    if level is None:
        level = get_log_level()

    if format_string is None:
        format_string = get_log_format()

    handlers = [logging.StreamHandler()]

    if log_file:
        # Ensure log directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=level,
        format=format_string,
        handlers=handlers,
        force=True,  # Override any existing configuration
    )

    logger = logging.getLogger(__name__)
    logger.info(
        f"Logging configured: level={logging.getLevelName(level)}, "
        f"file={'None' if not log_file else log_file}"
    )


def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """
    Get a configured logger instance for a specific module.

    This is a convenience function for getting loggers with consistent
    configuration across the application.

    Args:
        name: Logger name (typically __name__ from calling module)
        level: Optional override for this logger's level

    Returns:
        Configured logger instance

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Module initialized")
    """
    logger = logging.getLogger(name)
    if level is not None:
        logger.setLevel(level)
    return logger
