"""
CodeTuneStudio Version Information

This module provides centralized version management for the application.
"""

__version__ = "1.0.0"
__version_info__ = (1, 0, 0)
__release_date__ = "2024-12-19"
__author__ = "CodeTuneStudio Team"
__license__ = "MIT"

# Semantic Versioning Components
MAJOR = 1
MINOR = 0
PATCH = 0

# Release Information
RELEASE_NAME = "Genesis"
RELEASE_STATUS = "stable"  # alpha, beta, rc, stable

# Compatibility Information
MIN_PYTHON_VERSION = "3.9"
RECOMMENDED_PYTHON_VERSION = "3.11"


def get_version() -> str:
    """
    Get the current version string.

    Returns:
        Version string in format "MAJOR.MINOR.PATCH"
    """
    return __version__


def get_version_info() -> tuple[int, int, int]:
    """
    Get the version information as a tuple.

    Returns:
        Tuple of (MAJOR, MINOR, PATCH) version numbers
    """
    return __version_info__


def get_full_version() -> str:
    """
    Get the full version string with release name.

    Returns:
        Full version string including release name
    """
    return f"{__version__} ({RELEASE_NAME})"
