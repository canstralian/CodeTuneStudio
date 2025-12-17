"""
AI Code Review Gate - Drop-in CI/CD check for GitHub Actions.

Reviews pull requests like a senior engineer and fails builds when code violates
agreed-upon standards for safety, clarity, and maintainability—without ever
modifying code automatically.
"""

__version__ = "0.1.0"
__author__ = "CodeTuneStudio"

from .types import (
    ReviewResult,
    Finding,
    Severity,
    Category,
    PRChanges,
    ContextCheck,
    ReviewStatus,
)

__all__ = [
    "ReviewResult",
    "Finding",
    "Severity",
    "Category",
    "PRChanges",
    "ContextCheck",
    "ReviewStatus",
]
