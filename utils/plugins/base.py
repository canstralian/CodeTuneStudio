from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ToolMetadata:
    """Metadata for agent tools"""

    def __init__(
        self,
        name: str,
        description: str,
        version: str = "0.1.0",
        author: str = "",
        tags: List[str] = None,
    ):
        self.name = name
        self.description = description
        self.version = version
        self.author = author
        self.tags = tags or []


class AgentTool(ABC):
    """Base class for all agent tools"""

    def __init__(self):
        self._metadata: Optional[ToolMetadata] = None

    @property
    def metadata(self) -> ToolMetadata:
        """Get tool metadata"""
        if not self._metadata:
            raise ValueError("Tool metadata not initialized")
        return self._metadata

    @metadata.setter
    def metadata(self, meta: ToolMetadata):
        """Set tool metadata"""
        self._metadata = meta

    @abstractmethod
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the tool's main functionality

        Args:
            inputs: Dictionary containing tool inputs

        Returns:
            Dictionary containing tool outputs
        """
        pass

    @abstractmethod
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """
        Validate tool inputs

        Args:
            inputs: Dictionary containing tool inputs

        Returns:
            True if inputs are valid, False otherwise
        """
        pass

    def __str__(self) -> str:
        return f"{self.metadata.name} v{self.metadata.version}"
