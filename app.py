"""
CodeTune Studio - ML Model Fine-tuning Application

DEPRECATED: This is a backward-compatible wrapper for existing deployments.
The actual application has been moved to src/app.py.

For new deployments, use the CLI: `codetune-studio`
For development, run: `python -m src.app`
"""

import sys
import warnings

warnings.warn(
    "Running app.py from the root directory is deprecated. "
    "Please use 'codetune-studio' CLI command or 'python -m src.app' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Import and run from the new location
from src.app import main

if __name__ == "__main__":
    main()
