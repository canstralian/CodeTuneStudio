"""
CodeTuneStudio CLI - Command-line interface for CodeTuneStudio

This module provides a unified command-line interface for running the
application, managing database operations, and performing various tasks.
"""

import argparse
import logging
import os
import sys
from typing import List, Optional

# Handle imports for both installed package and direct script execution
try:
    from codetunestudio.__version__ import __version__
except ImportError:
    # Add parent directory to path for direct script execution
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from codetunestudio.__version__ import __version__

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def run_streamlit(args: argparse.Namespace) -> int:
    """
    Run the Streamlit web application.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    try:
        import subprocess

        port = args.port or 7860
        host = args.host or "0.0.0.0"

        logger.info(f"Starting Streamlit on {host}:{port}")

        cmd = [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "app.py",
            "--server.port",
            str(port),
            "--server.address",
            host,
        ]

        if args.headless:
            cmd.extend(["--server.headless", "true"])

        result = subprocess.run(cmd, check=False)
        return result.returncode

    except Exception as e:
        logger.error(f"Failed to start Streamlit: {e}")
        return 1


def run_flask(args: argparse.Namespace) -> int:
    """
    Run the Flask API backend.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    try:
        logger.info("Starting Flask backend...")

        # Import the Flask app
        sys.path.insert(0, ".")
        from app import MLFineTuningApp

        app_instance = MLFineTuningApp()
        flask_app = app_instance.flask_app

        port = args.port or 5000
        host = args.host or "0.0.0.0"
        debug = args.debug or False

        # Keep app_instance reference to prevent garbage collection
        _ = app_instance
        flask_app.run(host=host, port=port, debug=debug)
        return 0

    except Exception as e:
        logger.error(f"Failed to start Flask: {e}")
        return 1


def check_database(args: argparse.Namespace) -> int:
    """
    Check database connection and status.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    try:
        logger.info("Checking database connection...")
        import db_check

        result = db_check.check_database()
        return 0 if result else 1

    except Exception as e:
        logger.error(f"Database check failed: {e}")
        return 1


def init_database(args: argparse.Namespace) -> int:
    """
    Initialize database schema.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    try:
        logger.info("Initializing database...")
        sys.path.insert(0, ".")
        from app import MLFineTuningApp

        # Initialize app which creates database
        _ = MLFineTuningApp()
        logger.info("Database initialized successfully")
        return 0

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return 1


def show_version(args: argparse.Namespace) -> int:
    """
    Display version information.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (always 0)
    """
    print(f"CodeTuneStudio v{__version__}")
    print("ML Model Fine-Tuning Platform")
    print("https://github.com/canstralian/CodeTuneStudio")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    """
    Main entry point for the CLI.

    Args:
        argv: Command-line arguments (defaults to sys.argv)

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    parser = argparse.ArgumentParser(
        prog="codetune-studio",
        description="CodeTuneStudio - ML Model Fine-Tuning Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run Streamlit web interface (default)
  codetune-studio

  # Run on specific port
  codetune-studio --port 8080

  # Run Flask API backend
  codetune-studio flask --port 5000

  # Check database connection
  codetune-studio db check

  # Initialize database
  codetune-studio db init

  # Show version
  codetune-studio version

For more information, visit: https://github.com/canstralian/CodeTuneStudio
        """,
    )

    parser.add_argument(
        "--version", action="version", version=f"CodeTuneStudio v{__version__}"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Streamlit command (default)
    streamlit_parser = subparsers.add_parser(
        "streamlit", help="Run Streamlit web interface (default)"
    )
    streamlit_parser.add_argument(
        "--port", type=int, default=7860, help="Port to run on (default: 7860)"
    )
    streamlit_parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)",
    )
    streamlit_parser.add_argument(
        "--headless", action="store_true", help="Run in headless mode"
    )
    streamlit_parser.set_defaults(func=run_streamlit)

    # Flask command
    flask_parser = subparsers.add_parser("flask", help="Run Flask API backend")
    flask_parser.add_argument(
        "--port", type=int, default=5000, help="Port to run on (default: 5000)"
    )
    flask_parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)",
    )
    flask_parser.add_argument(
        "--debug", action="store_true", help="Run in debug mode"
    )
    flask_parser.set_defaults(func=run_flask)

    # Database commands
    db_parser = subparsers.add_parser("db", help="Database management commands")
    db_subparsers = db_parser.add_subparsers(
        dest="db_command", help="Database commands"
    )

    check_parser = db_subparsers.add_parser("check", help="Check database connection")
    check_parser.set_defaults(func=check_database)

    init_parser = db_subparsers.add_parser("init", help="Initialize database schema")
    init_parser.set_defaults(func=init_database)

    # Version command
    version_parser = subparsers.add_parser("version", help="Show version information")
    version_parser.set_defaults(func=show_version)

    # Parse arguments
    args = parser.parse_args(argv)

    # If no command specified, default to streamlit
    if not args.command:
        args.command = "streamlit"
        args.port = 7860
        args.host = "0.0.0.0"
        args.headless = False
        args.func = run_streamlit

    # Execute the appropriate function
    if hasattr(args, "func"):
        return args.func(args)
    else:
        parser.print_help()
        return 1


def cli_entry_point() -> None:
    """Entry point for console_scripts."""
    sys.exit(main())


if __name__ == "__main__":
    sys.exit(main())
