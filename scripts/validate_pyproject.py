#!/usr/bin/env python3
"""
Validate pyproject.toml syntax.

This script checks if the pyproject.toml file has valid TOML syntax.
It attempts to use tomli (Python < 3.11) or tomllib (Python >= 3.11).
The project standardizes on Python 3.10, so tomli is the primary library used,
but tomllib support is included for forward compatibility.

Exit codes:
    0: Validation successful
    1: Validation failed (invalid TOML syntax)
    2: File not found
"""
import sys
from pathlib import Path


def validate_pyproject(filepath: str = "pyproject.toml") -> bool:
    """
    Validate pyproject.toml file syntax.

    Args:
        filepath: Path to pyproject.toml file

    Returns:
        True if valid, False otherwise
    """
    toml_path = Path(filepath)

    if not toml_path.exists():
        print(f"❌ ERROR: {filepath} not found", file=sys.stderr)
        return False

    # Try to import tomli (primary for Python 3.10) or tomllib (Python >= 3.11)
    # Project uses Python 3.10, so tomli is expected, but tomllib provides forward compatibility
    try:
        import tomli

        load_func = tomli.load
    except ImportError:
        try:
            import tomllib

            load_func = tomllib.load
        except ImportError:
            print("❌ ERROR: Neither tomli nor tomllib is available", file=sys.stderr)
            return False

    # Validate TOML syntax
    try:
        with open(toml_path, "rb") as f:
            load_func(f)
        print(f"✅ {filepath} syntax is valid")
        return True
    except Exception as e:
        print(f"❌ ERROR: {filepath} has invalid syntax: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    filepath = sys.argv[1] if len(sys.argv) > 1 else "pyproject.toml"

    if validate_pyproject(filepath):
        sys.exit(0)
    else:
        if not Path(filepath).exists():
            sys.exit(2)
        sys.exit(1)
