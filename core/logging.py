"""
Centralized logging configuration for CodeTune Studio.

This module provides structured logging with configurable log levels,
formatters, and handlers for production environments.
"""

import json
import logging
import os
import sys
import uuid
from contextvars import ContextVar
from logging import LogRecord
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Dict, Optional


request_id_ctx: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


class RequestIdFilter(logging.Filter):
    """Inject the current request id into log records."""

    def filter(self, record: LogRecord) -> bool:
        record.request_id = request_id_ctx.get() or "n/a"
        return True


class JsonFormatter(logging.Formatter):
    """Emit structured JSON logs with timestamps and request identifiers."""

    def format(self, record: LogRecord) -> str:  # noqa: D401 - short override
        log_payload: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "pathname": record.pathname,
            "lineno": record.lineno,
            "request_id": getattr(record, "request_id", "n/a"),
        }

        # Capture extra attributes while avoiding built-ins
        builtin_fields = set(log_payload.keys()) | {
            "args",
            "created",
            "exc_info",
            "exc_text",
            "filename",
            "funcName",
            "levelno",
            "module",
            "msecs",
            "msg",
            "name",
            "process",
            "processName",
            "relativeCreated",
            "stack_info",
            "thread",
            "threadName",
        }

        extra_attributes = {
            key: value
            for key, value in record.__dict__.items()
            if key not in builtin_fields and not key.startswith("__")
        }

        if extra_attributes:
            log_payload["extra"] = extra_attributes

        if record.exc_info:
            log_payload["exc_info"] = self.formatException(record.exc_info)

        return json.dumps(log_payload, ensure_ascii=False)


def set_request_id(request_id: Optional[str] = None) -> str:
    """Assign a request id to the logging context."""

    new_id = request_id or str(uuid.uuid4())
    request_id_ctx.set(new_id)
    return new_id


def get_request_id() -> Optional[str]:
    """Fetch the current request id from context."""

    return request_id_ctx.get()


def clear_request_id() -> None:
    """Clear the request id from context to avoid leakage across requests."""

    request_id_ctx.set(None)


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
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
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Common filter ensures request ids are available
    request_filter = RequestIdFilter()

    # Console handler with JSON output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.addFilter(request_filter)
    console_formatter = JsonFormatter(datefmt="%Y-%m-%dT%H:%M:%SZ")
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
        file_handler.addFilter(request_filter)
        file_formatter = JsonFormatter(datefmt="%Y-%m-%dT%H:%M:%SZ")
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    
    # Log initial setup
    logger = logging.getLogger(__name__)
    logger.info("Logging configured", extra={"log_level": log_level})
    if log_file:
        logger.info("Log file configured", extra={"log_file": log_file})


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
