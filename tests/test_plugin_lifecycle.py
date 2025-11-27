"""
Tests for standardized plugin lifecycle.
"""

import pytest

from utils.plugins.base import AgentTool, ToolMetadata


class MockTool(AgentTool):
    """Mock tool for testing."""

    def __init__(self):
        super().__init__()
        self.metadata = ToolMetadata(
            name="mock_tool",
            description="A mock tool for testing",
            version="1.0.0",
            author="Test Author",
            tags=["test"],
        )
        self.execute_count = 0

    def execute(self, inputs):
        """Execute the mock tool."""
        self.execute_count += 1
        return {"result": "success", "input": inputs}

    def validate_inputs(self, inputs):
        """Validate inputs - requires 'data' key."""
        return "data" in inputs


class TestPluginLifecycle:
    """Test cases for plugin lifecycle management."""

    def test_initialization(self):
        """Test plugin initialization."""
        tool = MockTool()
        assert not tool._initialized

    def test_init_lifecycle(self):
        """Test init() lifecycle method."""
        tool = MockTool()
        tool.init()
        assert tool._initialized

    def test_init_idempotent(self):
        """Test that init() can be called multiple times safely."""
        tool = MockTool()
        tool.init()
        tool.init()  # Should not raise error
        assert tool._initialized

    def test_run_without_init(self):
        """Test that run() auto-initializes if needed."""
        tool = MockTool()
        result = tool.run({"data": "test"})
        assert tool._initialized
        assert result["result"] == "success"

    def test_run_with_init(self):
        """Test run() after explicit init()."""
        tool = MockTool()
        tool.init()
        result = tool.run({"data": "test"})
        assert result["result"] == "success"

    def test_run_validates_inputs(self):
        """Test that run() validates inputs."""
        tool = MockTool()
        with pytest.raises(ValueError):
            tool.run({"invalid": "data"})

    def test_run_calls_execute(self):
        """Test that run() calls execute()."""
        tool = MockTool()
        tool.run({"data": "test"})
        assert tool.execute_count == 1

    def test_teardown_lifecycle(self):
        """Test teardown() lifecycle method."""
        tool = MockTool()
        tool.init()
        tool.teardown()
        assert not tool._initialized

    def test_teardown_without_init(self):
        """Test teardown() without init() doesn't raise error."""
        tool = MockTool()
        tool.teardown()  # Should not raise error
        assert not tool._initialized

    def test_context_manager(self):
        """Test using plugin as context manager."""
        tool = MockTool()
        assert not tool._initialized

        with tool:
            assert tool._initialized
            result = tool.run({"data": "test"})
            assert result["result"] == "success"

        # After context, tool should be torn down
        assert not tool._initialized

    def test_context_manager_with_exception(self):
        """Test context manager properly tears down on exception."""
        tool = MockTool()

        with pytest.raises(ValueError):
            with tool:
                assert tool._initialized
                raise ValueError("Test error")

        # Tool should still be torn down
        assert not tool._initialized

    def test_metadata_property(self):
        """Test metadata property."""
        tool = MockTool()
        metadata = tool.metadata
        assert metadata.name == "mock_tool"
        assert metadata.version == "1.0.0"

    def test_str_representation(self):
        """Test string representation."""
        tool = MockTool()
        assert str(tool) == "mock_tool v1.0.0"

    def test_resources_cleared_on_teardown(self):
        """Test that resources are cleared on teardown."""
        tool = MockTool()
        tool.init()
        tool._resources["test"] = "value"
        tool.teardown()
        assert len(tool._resources) == 0
