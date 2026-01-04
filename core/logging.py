"""
Centralized logging configuration for CodeTune Studio.

This module provides structured logging with configurable log levels,
formatters, and handlers for production environments.
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter that provides structured log output with color support in terminals.
    """

    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
        "RESET": "\033[0m",  # Reset
    }

    def __init__(self, use_color: bool = True, *args, **kwargs):
        """
        Initialize the structured formatter.

        Args:
            use_color: Whether to use ANSI color codes in output.
        """
        super().__init__(*args, **kwargs)
        self.use_color = use_color and sys.stdout.isatty()

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record with optional color support.

        Args:
            record: The log record to format.

        Returns:
            Formatted log string.
        """
        if self.use_color:
            levelname = record.levelname
            color = self.COLORS.get(levelname, self.COLORS["RESET"])
            record.levelname = f"{color}{levelname}{self.COLORS['RESET']}"

        return super().format(record)


def setup_logging(
    log_level: str | None = None,
    log_file: str | None = None,
    enable_color: bool = True,
) -> None:
    """
    Configure application-wide logging.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
                  If None, reads from LOG_LEVEL environment variable or defaults to INFO.
        log_file: Optional path to log file. If provided, logs are also written to file.
        enable_color: Whether to use colored output in console (default: True).
    """
    # Determine log level
    if log_level is None:
        log_level = os.environ.get("LOG_LEVEL", "INFO")

    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")

    # Create formatters
    detailed_format = (
        "%(asctime)s - %(name)s - %(levelname)s - "
        "%(message)s - [%(pathname)s:%(lineno)d]"
    )
    simple_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler with color support
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_formatter = StructuredFormatter(
        use_color=enable_color,
        fmt=simple_format,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
        )
        file_handler.setLevel(numeric_level)
        file_formatter = logging.Formatter(
            fmt=detailed_format,
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    # Log initial setup
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured at {log_level} level")
    if log_file:
        logger.info(f"Logs will be written to: {log_file}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.

    Args:
        name: Name for the logger (typically __name__ of the calling module).

    Returns:
        Configured logger instance.
    """
    return logging.getLogger(name)


# Configure default logging when module is imported
if "LOG_LEVEL" not in os.environ:
    os.environ["LOG_LEVEL"] = "INFO"

# Only setup if not already configured
if not logging.getLogger().handlers:
    setup_logging()
