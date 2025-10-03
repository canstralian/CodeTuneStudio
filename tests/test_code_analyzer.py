import os
import unittest
from unittest.mock import patch

import pytest

from plugins.code_analyzer import CodeAnalyzerTool


class TestCodeAnalyzerTool(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = CodeAnalyzerTool()

    def test_init(self) -> None:
        assert self.tool.metadata.name == "code_analyzer"
        assert (
            self.tool.metadata.description
            == "Analyzes Python code structure and complexity"
        )
        assert self.tool.metadata.version == "0.1.0"
        assert self.tool.metadata.author == "CodeTuneStudio"
        assert self.tool.metadata.tags == ["code-analysis", "python"]

    def test_validate_inputs_valid(self) -> None:
        inputs = {"code": "def foo(): pass"}
        assert self.tool.validate_inputs(inputs)

    def test_validate_inputs_missing_code(self) -> None:
        inputs = {}
        assert not self.tool.validate_inputs(inputs)

    def test_validate_inputs_code_not_string(self) -> None:
        inputs = {"code": 123}
        assert not self.tool.validate_inputs(inputs)

    def test_execute_valid_code(self) -> None:
        code = """

def foo():
    pass

class Bar:
    pass

def baz():
    pass
"""
        inputs = {"code": code}
        result = self.tool.execute(inputs)
        assert result["num_functions"] == 2
        assert result["num_classes"] == 1
        assert "os" in result["imports"]
        assert "sys" in result["imports"]
        assert result["complexity"] > 0

    def test_execute_empty_code(self) -> None:
        inputs = {"code": ""}
        result = self.tool.execute(inputs)
        assert result["num_functions"] == 0
        assert result["num_classes"] == 0
        assert result["imports"] == []
        assert result["complexity"] > 0

    def test_execute_no_functions_classes(self) -> None:
        code = "x = 1 + 2"
        inputs = {"code": code}
        result = self.tool.execute(inputs)
        assert result["num_functions"] == 0
        assert result["num_classes"] == 0
        assert result["imports"] == []
        assert result["complexity"] > 0

    def test_execute_invalid_inputs(self) -> None:
        inputs = {"code": 123}
        with pytest.raises(ValueError):
            self.tool.execute(inputs)

    def test_execute_syntax_error(self) -> None:
        code = "def foo("  # Incomplete function
        inputs = {"code": code}
        with pytest.raises(RuntimeError):
            self.tool.execute(inputs)


if __name__ == "__main__":
    unittest.main()
