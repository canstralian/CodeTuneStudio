"""
Centralized logging configuration for CodeTune Studio.

This module provides structured logging with configurable log levels,
formatters, and handlers for production environments. It supports both
human-readable colored output and JSON-formatted logging with request ID
tracking for enhanced observability.
"""

import json
import logging
import os
import re
import sys
import uuid
from contextvars import ContextVar
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Dict, Optional


# Context variable for storing request ID across async operations
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)

# Sensitive keys that should never be logged
SENSITIVE_KEYS = {
    "password",
    "passwd",
    "pwd",
    "secret",
    "api_key",
    "apikey",
    "token",
    "auth",
    "authorization",
    "session",
    "cookie",
    "csrf",
    "private_key",
    "access_token",
    "refresh_token",
}

# Precompile regex for faster sensitive key matching
SENSITIVE_PATTERN = re.compile(
    "|".join(re.escape(k) for k in SENSITIVE_KEYS), re.IGNORECASE
)


def generate_request_id() -> str:
    """
    Generate a unique request ID.

    Returns:
        A unique UUID-based request identifier.
    """
    return str(uuid.uuid4())


def get_request_id() -> Optional[str]:
    """
    Get the current request ID from context.

    Returns:
        Current request ID or None if not set.
    """
    return request_id_var.get()


def set_request_id(request_id: str) -> None:
    """
    Set the request ID in the current context.

    Args:
        request_id: The request ID to set.
    """
    request_id_var.set(request_id)


def sanitize_for_logging(
    data: Any, max_depth: int = 5, _visited: Optional[set] = None
) -> Any:
    """
    Sanitize data to prevent logging sensitive information.

    Args:
        data: Data to sanitize (can be dict, list, or primitive).
        max_depth: Maximum recursion depth to prevent infinite loops.
        _visited: Internal parameter to track visited objects for circular
                  reference detection. Do not pass this parameter directly.

    Returns:
        Sanitized data with sensitive values replaced.

    Note:
        This function sanitizes data structures but does NOT sanitize log message
        strings. Never include sensitive data directly in log message strings
        (e.g., logger.info(f"Password: {password}") is unsafe). Always pass
        sensitive data via the `extra` parameter where it will be sanitized.
    """
    if _visited is None:
        _visited = set()

    # Check for circular references using id()
    if isinstance(data, (dict, list)):
        obj_id = id(data)
        if obj_id in _visited:
            return "***CIRCULAR_REFERENCE***"
        _visited.add(obj_id)

    if max_depth <= 0:
        return "***MAX_DEPTH***"

    try:
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                # Check if key contains any sensitive keywords using precompiled regex
                if SENSITIVE_PATTERN.search(str(key)):
                    sanitized[key] = "***REDACTED***"
                else:
                    sanitized[key] = sanitize_for_logging(
                        value, max_depth - 1, _visited
                    )
            return sanitized
        elif isinstance(data, (list, tuple)):
            sanitized = [
                sanitize_for_logging(item, max_depth - 1, _visited) for item in data
            ]
            return tuple(sanitized) if isinstance(data, tuple) else sanitized
        elif isinstance(data, str):
            # Don't log very long strings (potential tokens/keys)
            if len(data) > 1000:
                return f"***TRUNCATED:{len(data)}chars***"
            return data
        else:
            return data
    finally:
        # Remove object from visited set after processing to allow
        # the same object appearing in different branches
        if isinstance(data, (dict, list)):
            _visited.discard(id(data))


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging with request ID tracking.

    This formatter outputs logs in JSON format with standardized fields
    including timestamp, level, message, request_id, and additional context.
    """

    def __init__(self, include_extras: bool = True, *args, **kwargs):
        """
        Initialize the JSON formatter.

        Args:
            include_extras: Whether to include extra fields from log record.
        """
        super().__init__(*args, **kwargs)
        self.include_extras = include_extras

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record as JSON.

        Args:
            record: The log record to format.

        Returns:
            JSON-formatted log string.
        """
        log_data: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": get_request_id(),
        }

        # Add location information
        if record.pathname and record.lineno:
            log_data["location"] = {
                "file": record.pathname,
                "line": record.lineno,
                "function": record.funcName,
            }

        # Add exception information if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info),
            }

        # Add extra fields (sanitized)
        if self.include_extras:
            # Get all custom attributes
            extras = {}
            for key, value in record.__dict__.items():
                if key not in [
                    "name",
                    "msg",
                    "args",
                    "created",
                    "filename",
                    "funcName",
                    "levelname",
                    "levelno",
                    "lineno",
                    "module",
                    "msecs",
                    "message",
                    "pathname",
                    "process",
                    "processName",
                    "relativeCreated",
                    "thread",
                    "threadName",
                    "exc_info",
                    "exc_text",
                    "stack_info",
                ]:
                    extras[key] = value

            if extras:
                log_data["extras"] = sanitize_for_logging(extras)

        try:
            return json.dumps(log_data, default=str)
        except (TypeError, ValueError) as e:
            # Fallback to a safe representation
            fallback = {
                "timestamp": log_data.get("timestamp"),
                "level": log_data.get("level"),
                "message": f"Error formatting log: {e}",
                "original_message": str(record.getMessage()),
            }
            return json.dumps(fallback, default=str)


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter with structured log output and color support.
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
        Format the log record with optional color support and request ID.

        Args:
            record: The log record to format.

        Returns:
            Formatted log string.
        """
        # Add request ID if available, otherwise use '-' as placeholder
        request_id = get_request_id()
        record.request_id = request_id if request_id else "-"

        if self.use_color:
            levelname = record.levelname
            color = self.COLORS.get(levelname, self.COLORS["RESET"])
            record.levelname = f"{color}{levelname}{self.COLORS['RESET']}"

        return super().format(record)


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    enable_color: bool = True,
    json_format: Optional[bool] = None,
) -> None:
    """
    Configure application-wide logging.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
                  Defaults to LOG_LEVEL env var or INFO.
        log_file: Optional log file path. Enables file logging if provided.
        enable_color: Whether to use colored console output (default: True).
        json_format: Use JSON format. Defaults to LOG_JSON env var or False.
    """
    # Determine log level
    if log_level is None:
        log_level = os.environ.get("LOG_LEVEL", "INFO")

    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")

    # Create formatters - include request_id in human-readable format
    simple_format = (
        "%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(message)s"
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler with color support
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)

    if json_format:
        console_formatter = JSONFormatter()
    else:
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

        # Always use JSON format for file logs for better parsing
        file_formatter = JSONFormatter(include_extras=True)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    # Log initial setup
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured at {log_level} level")
    logger.info(f"JSON format: {json_format}")
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
