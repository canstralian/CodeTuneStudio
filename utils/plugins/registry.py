from typing import Dict, List, Type, Optional
import importlib
import inspect
import logging
import os
from pathlib import Path
from .base import AgentTool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PluginRegistry:
    """Registry for managing agent tools"""

    def __init__(self):
        self._tools: Dict[str, Type[AgentTool]] = {}

    def register_tool(self, tool_class: Type[AgentTool]) -> None:
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
            logger.error(f"Failed to register tool {tool_class.__name__}: {str(e)}")
            raise

    def get_tool(self, name: str) -> Optional[Type[AgentTool]]:
        """
        Get tool by name

        Args:
            name: Tool name

        Returns:
            Tool class if found, None otherwise
        """
        return self._tools.get(name)

    def list_tools(self) -> List[str]:
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
            plugin_path = Path(plugin_dir)
            if not plugin_path.exists():
                logger.warning(f"Plugin directory {plugin_dir} does not exist")
                return

            for file_path in plugin_path.glob("*.py"):
                if file_path.name.startswith("__"):
                    continue

                try:
                    # Import module
                    module_name = f"{plugin_dir}.{file_path.stem}"
                    spec = importlib.util.find_spec(module_name)
                    if not spec:
                        logger.warning(f"Could not find spec for module: {module_name}")
                        continue

                    module = importlib.import_module(module_name)

                    # Find and register tool classes
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and 
                            issubclass(obj, AgentTool) and 
                            obj != AgentTool):
                            self.register_tool(obj)

                except Exception as e:
                    logger.error(f"Failed to load plugin {file_path}: {str(e)}")

        except Exception as e:
            logger.error(f"Error discovering plugins: {str(e)}")
            raise

# Global plugin registry instance
registry = PluginRegistry()