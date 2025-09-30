"""Centralized logging configuration for CodeTuneStudio."""

import logging
import sys
from pathlib import Path


def setup_logging(
    level: int = logging.INFO,
    log_file: str = "codetunestudio.log",
    log_to_file: bool = True,
) -> None:
    """
    Configure logging for the entire application.

    This should be called once at application startup. All other modules
    should simply use logging.getLogger(__name__) to get their logger.

    Args:
        level: Logging level (default: INFO)
        log_file: Path to log file (default: codetunestudio.log)
        log_to_file: Whether to log to file in addition to console
    """
    # Create formatters
    detailed_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(pathname)s:%(lineno)d",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Create handlers
    handlers = []

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)
    handlers.append(console_handler)

    # File handler (if enabled)
    if log_to_file:
        try:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(level)
            file_handler.setFormatter(detailed_formatter)
            handlers.append(file_handler)
        except Exception as e:
            print(
                f"Warning: Could not create log file {log_file}: {e}", file=sys.stderr
            )

    # Configure root logger
    logging.basicConfig(
        level=level,
        handlers=handlers,
        force=True,  # Override any existing configuration
    )

    # Set specific loggers to higher levels to reduce noise
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("transformers").setLevel(logging.WARNING)
    logging.getLogger("torch").setLevel(logging.WARNING)
    logging.getLogger("streamlit").setLevel(logging.WARNING)

    # Log that logging has been configured
    logger = logging.getLogger(__name__)
    logger.info("Logging configured successfully")
    logger.info(f"Log level: {logging.getLevelName(level)}")
    if log_to_file:
        logger.info(f"Logging to file: {log_file}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the given module name.

    Args:
        name: Module name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
