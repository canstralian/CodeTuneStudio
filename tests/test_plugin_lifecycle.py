"""
Tests for Plugin Lifecycle

Unit tests for the standardized plugin lifecycle (init, run, teardown).
"""

import unittest
from unittest.mock import MagicMock, patch

from utils.plugins.base import AgentTool, ToolMetadata


class MockTool(AgentTool):
    """Mock tool implementation for testing."""

    def __init__(self):
        super().__init__()
        self.metadata = ToolMetadata(
            name="mock_tool",
            description="Mock tool for testing",
            version="0.1.0",
        )
        self.init_called = False
        self.teardown_called = False
        self.execute_called = False

    def init(self):
        """Override init to track calls."""
        super().init()
        self.init_called = True

    def teardown(self):
        """Override teardown to track calls."""
        super().teardown()
        self.teardown_called = True

    def execute(self, inputs):
        """Mock execute implementation."""
        self.execute_called = True
        return {"status": "success", "result": "mock_result"}

    def validate_inputs(self, inputs):
        """Mock validate_inputs implementation."""
        return "data" in inputs


class TestPluginLifecycle(unittest.TestCase):
    """Test cases for plugin lifecycle methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.tool = MockTool()

    def test_tool_not_initialized_initially(self):
        """Test that tool is not initialized on creation."""
        self.assertFalse(self.tool.is_initialized)
        self.assertFalse(self.tool.init_called)

    def test_init_sets_initialized_flag(self):
        """Test that init sets the initialized flag."""
        self.tool.init()
        self.assertTrue(self.tool.is_initialized)
        self.assertTrue(self.tool.init_called)

    def test_teardown_resets_initialized_flag(self):
        """Test that teardown resets the initialized flag."""
        self.tool.init()
        self.assertTrue(self.tool.is_initialized)
        self.tool.teardown()
        self.assertFalse(self.tool.is_initialized)
        self.assertTrue(self.tool.teardown_called)

    def test_run_initializes_if_needed(self):
        """Test that run initializes the tool if not initialized."""
        self.assertFalse(self.tool.is_initialized)
        result = self.tool.run({"data": "test"})
        self.assertTrue(self.tool.init_called)
        self.assertTrue(self.tool.execute_called)
        self.assertEqual(result["status"], "success")

    def test_run_with_initialized_tool(self):
        """Test that run works with already initialized tool."""
        self.tool.init()
        result = self.tool.run({"data": "test"})
        self.assertTrue(self.tool.execute_called)
        self.assertEqual(result["status"], "success")

    def test_context_manager_init(self):
        """Test that context manager calls init on entry."""
        with self.tool as t:
            self.assertTrue(t.is_initialized)
            self.assertTrue(t.init_called)

    def test_context_manager_teardown(self):
        """Test that context manager calls teardown on exit."""
        with self.tool:
            pass
        self.assertTrue(self.tool.teardown_called)
        self.assertFalse(self.tool.is_initialized)

    def test_context_manager_usage(self):
        """Test full context manager lifecycle."""
        self.assertFalse(self.tool.is_initialized)
        with self.tool as t:
            self.assertTrue(t.is_initialized)
            result = t.run({"data": "test"})
            self.assertEqual(result["status"], "success")
        self.assertFalse(self.tool.is_initialized)
        self.assertTrue(self.tool.teardown_called)

    def test_metadata_access(self):
        """Test metadata property access."""
        self.assertEqual(self.tool.metadata.name, "mock_tool")
        self.assertEqual(self.tool.metadata.version, "0.1.0")

    def test_str_representation(self):
        """Test string representation."""
        expected = "mock_tool v0.1.0"
        self.assertEqual(str(self.tool), expected)


if __name__ == "__main__":
    unittest.main()
