"""
CodeTuneStudio Core Module

This module contains the core application logic for CodeTuneStudio,
providing ML model fine-tuning with PEFT/LoRA, plugin architecture,
and experiment tracking capabilities.
"""

from core.__version__ import __version__, __version_info__
from core.server import MLFineTuningApp, main

__all__ = [
    "__version__",
    "__version_info__",
    "MLFineTuningApp",
    "main",
]
