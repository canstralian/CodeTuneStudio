import logging
from abc import ABC, abstractmethod
from typing import Any

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
        tags: list[str] | None = None,
    ) -> None:
        self.name = name
        self.description = description
        self.version = version
        self.author = author
        self.tags = tags or []


class AgentTool(ABC):
    """
    Base class for all agent tools with standardized lifecycle.
    
    All plugins must implement the standard lifecycle methods:
    - init(): Initialize resources
    - execute(): Main functionality
    - teardown(): Cleanup resources
    
    This ensures consistent behavior across all plugins.
    """

    def __init__(self) -> None:
        self._metadata: ToolMetadata | None = None
        self._initialized: bool = False

    @property
    def metadata(self) -> ToolMetadata:
        """Get tool metadata"""
        if not self._metadata:
            msg = "Tool metadata not initialized"
            raise ValueError(msg)
        return self._metadata

    @metadata.setter
    def metadata(self, meta: ToolMetadata) -> None:
        """Set tool metadata"""
        self._metadata = meta

    def init(self) -> None:
        """
        Initialize the tool and allocate resources.
        
        This method is called once before the tool is used. Override this
        method to perform initialization tasks such as loading models,
        establishing connections, or allocating resources.
        
        The default implementation sets the initialized flag. Subclasses
        should call super().init() when overriding.
        
        Raises:
            RuntimeError: If initialization fails
        """
        self._initialized = True
        logger.info(f"Tool {self.metadata.name} initialized")

    def teardown(self) -> None:
        """
        Clean up resources and perform shutdown tasks.
        
        This method is called when the tool is no longer needed. Override
        this method to release resources such as closing connections,
        freeing memory, or saving state.
        
        The default implementation resets the initialized flag. Subclasses
        should call super().teardown() when overriding.
        """
        self._initialized = False
        logger.info(f"Tool {self.metadata.name} teardown complete")

    @property
    def is_initialized(self) -> bool:
        """Check if the tool has been initialized."""
        return self._initialized

    def run(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """
        Run the tool with automatic initialization check.
        
        This method wraps execute() with initialization verification and
        error handling. Use this method instead of calling execute() directly.
        
        Args:
            inputs: Dictionary containing tool inputs
            
        Returns:
            Dictionary containing tool outputs
            
        Raises:
            RuntimeError: If tool is not initialized
        """
        if not self._initialized:
            logger.warning(
                f"Tool {self.metadata.name} not initialized, initializing now"
            )
            self.init()
        
        return self.execute(inputs)

    @abstractmethod
    def execute(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """
        Execute the tool's main functionality.

        Args:
            inputs: Dictionary containing tool inputs

        Returns:
            Dictionary containing tool outputs
        """

    @abstractmethod
    def validate_inputs(self, inputs: dict[str, Any]) -> bool:
        """
        Validate tool inputs.

        Args:
            inputs: Dictionary containing tool inputs

        Returns:
            True if inputs are valid, False otherwise
        """

    def __str__(self) -> str:
        return f"{self.metadata.name} v{self.metadata.version}"
    
    def __enter__(self):
        """Context manager entry - initializes the tool."""
        self.init()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - tears down the tool."""
        self.teardown()
        return False
