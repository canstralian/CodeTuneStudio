"""
Plugin system for CodeTuneStudio.

This package contains the plugin registry and base classes for creating extensions.
"""

from .base import AgentTool, ToolMetadata
from .registry import registry

__all__ = [
    "AgentTool",
    "ToolMetadata",
    "registry",
]
