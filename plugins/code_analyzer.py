import ast
from typing import Any

from utils.plugins.base import AgentTool, ToolMetadata


class CodeAnalyzerTool(AgentTool):
    """CodeAnalyzerTool: Analyzes Python code structure and complexity."""

    def __init__(self) -> None:
        """
        Initialize the CodeAnalyzerTool and configure its tool metadata.
        
        Sets self.metadata to a ToolMetadata instance with name "code_analyzer", description "Analyzes Python code structure and complexity", version "0.1.0", author "CodeTuneStudio", and tags ["code-analysis", "python"].
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
        Check that the inputs include a "code" field containing Python source as a string.
        
        Parameters:
            inputs (dict[str, Any]): Mapping expected to contain a "code" key with Python source code.
        
        Returns:
            bool: True if `inputs["code"]` exists and is a `str`, False otherwise.
        """
        return isinstance(inputs.get("code"), str)

    def execute(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """
        Analyze a Python source string and return structural metrics or a standardized error payload.
        
        Parameters:
            inputs (dict[str, Any]): Input dictionary that must include a "code" key whose value is a Python source string.
        
        Returns:
            dict[str, Any]: On success, a dictionary with keys:
                - "num_functions" (int): Number of top-level and nested function definitions.
                - "num_classes" (int): Number of class definitions.
                - "imports" (list[str]): List of imported module names collected from `import` and `from ... import` statements.
                - "complexity" (int): Total number of AST nodes in the parsed tree.
                - "status" (str): The string "success".
              On failure, a dictionary with keys:
                - "error" (str): Human-readable error message.
                - "status" (str): The string "error".
        """
        if not self.validate_inputs(inputs):
            return {
                "error": "Invalid input. 'code' field is missing or not a string.",
                "status": "error",
            }

        try:
            tree = ast.parse(inputs["code"])
        except SyntaxError:
            return {"error": "Invalid Python syntax.", "status": "error"}
        except Exception:
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
            return {"error": "Unable to analyze Python code.", "status": "error"}
