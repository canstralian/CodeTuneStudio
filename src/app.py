"""
CodeTune Studio - ML Model Fine-tuning Application

This module provides the main application entry point for running directly with Python.
The actual application logic is in the core.server module.

For production use, prefer the CLI: `codetune-studio`
For development: `python -m src.app`
"""

# Import the run_app function from the new core.server module
from src.core.server import run_app


def main() -> None:
    """
    Legacy application entry point.

    This function maintains backward compatibility with existing deployments
    that directly run app.py. New deployments should use the CLI entrypoint
    via `codetune-studio` command.
    """
    run_app()


if __name__ == "__main__":
    main()
