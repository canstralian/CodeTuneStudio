import importlib.util
import inspect
import logging
import sys
from pathlib import Path

from utils.plugins.base import AgentTool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PluginRegistry:
    """Registry for managing agent tools"""

    def __init__(self) -> None:
        self._tools: dict[str, type[AgentTool]] = {}

    def register_tool(self, tool_class: type[AgentTool]) -> None:
        """
        Register a new tool

        Args:
            tool_class: Tool class to register
        """
        try:
            # Create temporary instance to get metadata
            tool = tool_class()
            tool_name = tool.metadata.name

            if tool_name in self._tools:
                logger.warning(f"Tool {tool_name} already registered, updating...")

            self._tools[tool_name] = tool_class
            logger.info(f"Successfully registered tool: {tool_name}")

        except Exception as e:
            logger.exception(f"Failed to register tool {tool_class.__name__}: {e!s}")
            raise

    def get_tool(self, name: str) -> type[AgentTool] | None:
        """
        Get tool by name

        Args:
            name: Tool name

        Returns:
            Tool class if found, None otherwise
        """
        return self._tools.get(name)

    def list_tools(self) -> list[str]:
        """Get list of registered tool names"""
        return list(self._tools.keys())

    def clear_tools(self) -> None:
        """Clear all registered tools"""
        self._tools.clear()
        logger.info("Cleared all registered tools")

    def discover_tools(self, plugin_dir: str = "plugins") -> None:
        """
        Discover and load tools from plugin directory

        Args:
            plugin_dir: Directory containing plugin files
        """
        try:
            # Convert to absolute path
            plugin_path = Path(plugin_dir).resolve()
            if not plugin_path.exists():
                logger.warning(f"Plugin directory {plugin_dir} does not exist")
                return

            # Add plugin directory to Python path if not already there
            plugin_parent = str(plugin_path.parent)
            if plugin_parent not in sys.path:
                sys.path.insert(0, plugin_parent)

            for file_path in plugin_path.glob("*.py"):
                if file_path.name.startswith("__"):
                    continue

                try:
                    # Import module using spec
                    module_name = file_path.stem
                    spec = importlib.util.spec_from_file_location(
                        module_name, str(file_path)
                    )

                    if not spec or not spec.loader:
                        logger.warning(f"Could not find spec for module: {module_name}")
                        continue

                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # Find and register tool classes
                    for _name, obj in inspect.getmembers(module):
                        if (
                            inspect.isclass(obj)
                            and issubclass(obj, AgentTool)
                            and obj != AgentTool
                        ):
                            self.register_tool(obj)

                except Exception as e:
                    logger.exception(f"Failed to load plugin {file_path}: {e!s}")
                    logger.debug("Exception details:", exc_info=True)

        except Exception as e:
            logger.exception(f"Error discovering plugins: {e!s}")
            logger.debug("Exception details:", exc_info=True)
            raise


# Global plugin registry instance
registry = PluginRegistry()
