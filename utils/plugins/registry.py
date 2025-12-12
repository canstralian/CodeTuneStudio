import importlib.util
import inspect
import logging
import sys
from pathlib import Path

from .base import AgentTool

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

    def _validate_plugin_directory(self, plugin_dir: str) -> Path | None:
        """
        Validate and resolve the plugin directory path

        Args:
            plugin_dir: Directory containing plugin files

        Returns:
            Resolved Path object if valid, None otherwise
        """
        plugin_path = Path(plugin_dir).resolve()
        if not plugin_path.exists():
            logger.warning(f"Plugin directory {plugin_dir} does not exist")
            return None
        return plugin_path

    def _ensure_path_accessible(self, plugin_path: Path) -> None:
        """
        Ensure the plugin parent directory is in sys.path

        Args:
            plugin_path: Path to the plugin directory
        """
        plugin_parent = str(plugin_path.parent)
        if plugin_parent not in sys.path:
            sys.path.insert(0, plugin_parent)

    def _load_module_from_file(self, file_path: Path) -> object | None:
        """
        Load a Python module from a file path

        Args:
            file_path: Path to the Python file

        Returns:
            Loaded module object or None if loading fails
        """
        module_name = file_path.stem
        spec = importlib.util.spec_from_file_location(module_name, str(file_path))

        if not spec or not spec.loader:
            logger.warning(f"Could not find spec for module: {module_name}")
            return None

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def _extract_tool_classes(self, module: object) -> list[type[AgentTool]]:
        """
        Extract AgentTool subclasses from a module

        Args:
            module: Python module to inspect

        Returns:
            List of AgentTool subclass types found in the module
        """
        tool_classes = []
        for _name, obj in inspect.getmembers(module):
            if (
                inspect.isclass(obj)
                and issubclass(obj, AgentTool)
                and obj != AgentTool
            ):
                tool_classes.append(obj)
        return tool_classes

    def discover_tools(self, plugin_dir: str = "plugins") -> None:
        """
        Discover and load tools from plugin directory

        Args:
            plugin_dir: Directory containing plugin files
        """
        try:
            plugin_path = self._validate_plugin_directory(plugin_dir)
            if not plugin_path:
                return

            self._ensure_path_accessible(plugin_path)

            for file_path in plugin_path.glob("*.py"):
                if file_path.name.startswith("__"):
                    continue

                try:
                    module = self._load_module_from_file(file_path)
                    if not module:
                        continue

                    tool_classes = self._extract_tool_classes(module)
                    for tool_class in tool_classes:
                        self.register_tool(tool_class)

                except Exception as e:
                    logger.exception(f"Failed to load plugin {file_path}: {e!s}")
                    logger.debug("Exception details:", exc_info=True)

        except Exception as e:
            logger.exception(f"Error discovering plugins: {e!s}")
            logger.debug("Exception details:", exc_info=True)
            raise


# Global plugin registry instance
registry = PluginRegistry()
