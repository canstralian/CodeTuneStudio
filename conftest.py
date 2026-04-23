"""
Root conftest.py – ensures the project root is on sys.path so that
top-level packages (plugins, core, db_check, manage, …) are importable
when pytest is invoked from any working directory.
"""

import sys
from pathlib import Path

# Insert the project root at the front of sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))
