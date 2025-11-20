"""
CodeTuneStudio CLI

Command-line interface for CodeTuneStudio providing easy access to
the ML model fine-tuning application.
"""

import argparse
import logging
import sys
from typing import Optional

from core import __version__
from core.server import main as server_main


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def cli() -> int:
    """
    Main CLI entry point for codetune-studio command.
    
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    parser = argparse.ArgumentParser(
        prog="codetune-studio",
        description="CodeTuneStudio - ML Model Fine-tuning Platform",
        epilog="For more information, visit: https://github.com/canstralian/CodeTuneStudio"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"CodeTuneStudio {__version__}"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=7860,
        help="Port to run the Streamlit server on (default: 7860)"
    )
    
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="Host to bind the server to (default: localhost)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    logger.info(f"Starting CodeTuneStudio v{__version__}")
    logger.info(f"Server will be available at http://{args.host}:{args.port}")
    
    try:
        # Run the Streamlit application
        server_main()
        return 0
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
        return 0
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        return 1


def main() -> None:
    """Wrapper for CLI entry point."""
    sys.exit(cli())


if __name__ == "__main__":
    main()
