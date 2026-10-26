import ast
import logging
from typing import Any

from utils.plugins.base import AgentTool, ToolMetadata

logger = logging.getLogger(__name__)


class CodeAnalyzerTool(AgentTool):
    """CodeAnalyzerTool: Analyzes Python code structure and complexity."""

    def __init__(self) -> None:
        """
        Initialize the tool with code analysis metadata.
        """
        super().__init__()
        self.metadata = ToolMetadata(
            name="code_analyzer",
            description="Analyzes Python code structure and complexity",
            version="0.1.0",
            author="CodeTuneStudio",
            tags=["code-analysis", "python"],
        )

    def validate_inputs(self, inputs: dict[str, Any]) -> bool:
        """
        Verify that the input contains a string-valued 'code' field.

        Returns:
            bool: True if the 'code' field exists and is a string, False otherwise.
        """
        return isinstance(inputs.get("code"), str)

    def execute(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """
        Analyze Python source code and compute structural metrics.

        Parameters:
            inputs (dict[str, Any]): Input dictionary containing a "code" key with a Python source string.

        Returns:
            dict[str, Any]: On success, a dictionary with "num_functions", "num_classes", "imports", "complexity", and "status": "success". On error, a dictionary with "error" and "status": "error".
        """
        if not self.validate_inputs(inputs):
            return {
                "error": "Invalid input. 'code' field is missing or not a string.",
                "status": "error",
            }

        try:
            tree = ast.parse(inputs["code"])
        except SyntaxError:
            logger.info("code_analyzer: invalid Python syntax in submitted code")
            return {"error": "Invalid Python syntax.", "status": "error"}
        except Exception:
            logger.exception("code_analyzer: unexpected failure parsing Python code")
            return {"error": "Unable to parse Python code.", "status": "error"}

        try:
            num_functions = len(
                [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            )
            num_classes = len(
                [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            )

            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.extend(n.name for n in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.append(node.module)

            complexity = len(list(ast.walk(tree)))

            return {
                "num_functions": num_functions,
                "num_classes": num_classes,
                "imports": imports,
                "complexity": complexity,
                "status": "success",
            }
        except Exception:
            logger.exception("code_analyzer: unexpected failure analyzing Python code")
            return {"error": "Unable to analyze Python code.", "status": "error"}
