"""
CodeTune Studio - Core Package

A production-ready ML model fine-tuning platform with parameter-efficient training,
plugin architecture, and comprehensive experiment tracking.
"""

__all__ = ["__version__", "RefactoringAgent"]
__version__ = "0.2.0"

# Import RefactoringAgent for easy access
from core.refactoring_agent import RefactoringAgent
