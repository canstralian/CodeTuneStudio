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
        Format a LogRecord into a string, applying ANSI color to the record's level name when color is enabled.
        
        Parameters:
            record (logging.LogRecord): The log record to format.
        
        Returns:
            str: The formatted log message.
        """
        if self.use_color:
            levelname = record.levelname
            color = self.COLORS.get(levelname, self.COLORS["RESET"])
            record.levelname = f"{color}{levelname}{self.COLORS['RESET']}"

        return super().format(record)


def redact_url(value: str) -> str:
    """
    Redact any username in a URL's network location by replacing it with '***'.
    
    If `value` is falsy or contains no network location, returns it unchanged. The scheme, host (IPv6 bracket formatting preserved), port, path, query, and fragment are retained; when a username is present it is replaced with `***`.
    
    Parameters:
        value (str): The URL string to redact.
    
    Returns:
        str: The URL with the username replaced by `***`, or the original value if no redaction was performed.
    """
    from urllib.parse import urlsplit, urlunsplit

    if not value:
        return value

    parts = urlsplit(value)
    if not parts.netloc:
        return value

    host = parts.hostname or ""
    if ":" in host and not host.startswith("["):
        host = f"[{host}]"

    redacted_netloc = host
    if parts.port:
        redacted_netloc = f"{redacted_netloc}:{parts.port}"
    if parts.username is not None:
        redacted_netloc = f"{parts.username}:***@{redacted_netloc}"

    return urlunsplit(
        (parts.scheme, redacted_netloc, parts.path, parts.query, parts.fragment)
    )


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    enable_color: bool = True,
) -> None:
    """
    Configure the root logger with a console handler (optionally ANSI-colored) and an optional rotating file handler.
    
    Parameters:
        log_level (Optional[str]): Logging level name (e.g., "DEBUG", "INFO"). If None, reads the LOG_LEVEL environment variable or defaults to "INFO".
        log_file (Optional[str]): Path to a log file. If provided, a rotating file handler is added (10 MB max per file, 5 backups); parent directories are created if needed.
        enable_color (bool): Enable ANSI-colored console output when stdout is a TTY.
    
    Raises:
        ValueError: If `log_level` does not correspond to a valid logging level name.
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
