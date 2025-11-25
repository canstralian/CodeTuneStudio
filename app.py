"""
CodeTune Studio - ML Model Fine-tuning Application

This is the legacy entrypoint maintained for backward compatibility.
The actual application logic has been refactored to core.server module.

For new deployments, use the CLI: `codetune-studio`
"""

# Import the run_app function from the new core.server module
from core.server import run_app


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
