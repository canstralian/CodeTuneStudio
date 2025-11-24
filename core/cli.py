"""
Command-line interface for CodeTune Studio.

This module provides the CLI entrypoint for running the application
with argument parsing and configuration management.
"""

import argparse
import logging
import os
import sys
from typing import Optional

from core import __version__

logger = logging.getLogger(__name__)


def parse_args(args: Optional[list[str]] = None) -> argparse.Namespace:
    """
    Parse command-line arguments for CodeTune Studio.

    Args:
        args: List of arguments to parse. If None, uses sys.argv[1:].

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        prog="codetune-studio",
        description="CodeTune Studio - ML Model Fine-tuning Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start the application with default settings
  codetune-studio

  # Start with custom host and port
  codetune-studio --host 0.0.0.0 --port 8501

  # Enable debug logging
  codetune-studio --log-level DEBUG

  # Specify database URL
  codetune-studio --database-url postgresql://user:pass@localhost/dbname

For more information, visit: https://github.com/canstralian/CodeTuneStudio
        """,
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show version and exit",
    )

    parser.add_argument(
        "--host",
        type=str,
        default=os.environ.get("HOST", "localhost"),
        help="Host to bind the server to (default: localhost, env: HOST)",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("PORT", "7860")),
        help="Port to bind the server to (default: 7860, env: PORT)",
    )

    parser.add_argument(
        "--database-url",
        type=str,
        default=os.environ.get("DATABASE_URL", "sqlite:///database.db"),
        help="Database connection URL (default: sqlite:///database.db, env: DATABASE_URL)",
    )

    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default=os.environ.get("LOG_LEVEL", "INFO"),
        help="Set the logging level (default: INFO, env: LOG_LEVEL)",
    )

    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Don't automatically open browser on startup",
    )

    parser.add_argument(
        "--server-headless",
        action="store_true",
        default=os.environ.get("SERVER_HEADLESS", "false").lower()
        in ("true", "1", "yes"),
        help="Run server in headless mode (default: false, env: SERVER_HEADLESS)",
    )

    return parser.parse_args(args)


def configure_logging(log_level: str) -> None:
    """
    Configure application logging.

    Args:
        log_level: Logging level as a string (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    """
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")

    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )
    logger.info(f"Logging configured at {log_level} level")


def main(args: Optional[list[str]] = None) -> int:
    """
    Main CLI entrypoint for CodeTune Studio.

    Args:
        args: Optional list of arguments. If None, uses sys.argv[1:].

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    try:
        # Parse arguments
        parsed_args = parse_args(args)

        # Configure logging
        configure_logging(parsed_args.log_level)

        logger.info(f"Starting CodeTune Studio v{__version__}")
        logger.info(f"Host: {parsed_args.host}")
        logger.info(f"Port: {parsed_args.port}")
        logger.info(f"Database: {parsed_args.database_url}")

        # Set environment variables for the application
        os.environ["DATABASE_URL"] = parsed_args.database_url
        os.environ["LOG_LEVEL"] = parsed_args.log_level

        # Import and run the Streamlit app
        # We use subprocess to run streamlit as it expects to be run as a script
        import subprocess

        # Build streamlit command
        streamlit_cmd = [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            os.path.join(os.path.dirname(__file__), "..", "app.py"),
            f"--server.address={parsed_args.host}",
            f"--server.port={parsed_args.port}",
        ]

        if parsed_args.server_headless:
            streamlit_cmd.append("--server.headless=true")

        if parsed_args.no_browser:
            streamlit_cmd.append("--server.headless=true")

        logger.info(f"Launching Streamlit: {' '.join(streamlit_cmd)}")

        # Run streamlit
        result = subprocess.run(streamlit_cmd, check=False)
        return result.returncode

    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        return 0
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
