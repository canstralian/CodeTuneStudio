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

    This class provides a unified API for plugin lifecycle management
    with standardized init(), run(), and teardown() methods.

    Lifecycle:
        1. init() - Initialize the tool and resources
        2. run() - Execute the tool's main functionality
        3. teardown() - Clean up resources

    Subclasses must implement:
        - execute(): Core tool functionality
        - validate_inputs(): Input validation logic
    """

    def __init__(self) -> None:
        self._metadata: ToolMetadata | None = None
        self._initialized: bool = False
        self._resources: dict[str, Any] = {}

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

        This method should be called before run(). Subclasses can override
        to perform custom initialization (e.g., loading models, connecting
        to databases, etc.).

        Sets:
            _initialized: True after successful initialization
        """
        if self._initialized:
            logger.warning(f"Tool {self.metadata.name} already initialized")
            return

        logger.info(f"Initializing tool: {self.metadata.name}")
        self._initialized = True

    def run(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """
        Run the tool with given inputs (standardized lifecycle method).

        This is the main entry point for executing the tool. It validates
        inputs, ensures initialization, and delegates to execute().

        Args:
            inputs: Dictionary containing tool inputs

        Returns:
            Dictionary containing tool outputs

        Raises:
            RuntimeError: If tool is not initialized
            ValueError: If inputs are invalid
        """
        if not self._initialized:
            logger.info(f"Auto-initializing tool: {self.metadata.name}")
            self.init()

        if not self.validate_inputs(inputs):
            raise ValueError(
                f"Invalid inputs for tool {self.metadata.name}: {inputs}"
            )

        logger.debug(f"Running tool: {self.metadata.name}")
        return self.execute(inputs)

    def teardown(self) -> None:
        """
        Clean up resources and perform teardown operations.

        This method should be called when the tool is no longer needed.
        Subclasses can override to perform custom cleanup (e.g., closing
        connections, releasing memory, etc.).

        Sets:
            _initialized: False after teardown
        """
        if not self._initialized:
            logger.warning(
                f"Tool {self.metadata.name} not initialized, "
                "nothing to tear down"
            )
            return

        logger.info(f"Tearing down tool: {self.metadata.name}")
        self._resources.clear()
        self._initialized = False

    @abstractmethod
    def execute(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """
        Execute the tool's main functionality.

        This method should be implemented by subclasses to provide
        the core tool functionality.

        Args:
            inputs: Dictionary containing tool inputs (pre-validated)

        Returns:
            Dictionary containing tool outputs
        """

    @abstractmethod
    def validate_inputs(self, inputs: dict[str, Any]) -> bool:
        """
        Validate tool inputs.

        This method should be implemented by subclasses to validate
        that all required inputs are present and correctly formatted.

        Args:
            inputs: Dictionary containing tool inputs

        Returns:
            True if inputs are valid, False otherwise
        """

    def __str__(self) -> str:
        return f"{self.metadata.name} v{self.metadata.version}"

    def __enter__(self):
        """Context manager entry - initialize tool"""
        self.init()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - teardown tool"""
        self.teardown()
        return False
