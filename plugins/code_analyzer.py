import ast
from typing import Any

from utils.plugins.base import AgentTool, ToolMetadata


class CodeAnalyzerTool(AgentTool):
    """CodeAnalyzerTool: Analyzes Python code structure and complexity.

    This class extends AgentTool to provide static analysis of Python code
    using the Abstract Syntax Tree (AST) module. It extracts metrics such
    as the number of functions, classes, imports, and a simple complexity
    score based on the total number of AST nodes.

    Attributes:
        metadata (ToolMetadata): Metadata describing the tool, including
            name, description, version, author, and tags.
    Methods:
        __init__(): Initializes the tool and sets up metadata.
        validate_inputs(inputs: Dict[str, Any]) -> bool:
            Validates that the input dictionary contains a 'code' key
            with a string value.
                inputs (Dict[str, Any]): Input dictionary to validate.
                bool: True if inputs are valid, False otherwise.
        execute(inputs: Dict[str, Any]) -> Dict[str, Any]:
            Analyzes the provided Python code and returns structural metrics.
                inputs (Dict[str, Any]): Dictionary containing:
                    - code (str): The Python code to analyze.
                Dict[str, Any]: Dictionary with analysis results:
                    - num_functions (int): Number of function definitions.
                    - num_classes (int): Number of class definitions.
                    - imports (List[str]): List of imported modules.
                    - complexity (int): Estimated complexity based on AST node count.
            Raises:
                ValueError: If inputs are invalid.
                RuntimeError: If code parsing or analysis fails.
    """

    def __init__(self) -> None:
        super().__init__()
        self.metadata = ToolMetadata(
            name="code_analyzer",
            description="Analyzes Python code structure and complexity",
            version="0.1.0",
            author="CodeTuneStudio",
            tags=["code-analysis", "python"],
        )

    def validate_inputs(self, inputs: dict[str, Any]) -> bool:
        """Validate that required inputs are present"""
        if "code" not in inputs:
            return False
        return isinstance(inputs["code"], str)

    def execute(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """
        Analyze Python code structure

        Args:
            inputs: Dictionary containing:
                - code: String containing Python code to analyze

        Returns:
            Dictionary containing:
                - num_functions: Number of functions
                - num_classes: Number of classes
                - imports: List of imported modules
                - complexity: Estimated code complexity
        """
        if not self.validate_inputs(inputs):
            msg = "Invalid inputs"
            raise ValueError(msg)

        try:
            tree = ast.parse(inputs["code"])

            # Count functions and classes
            num_functions = len(
                [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            )
            num_classes = len(
                [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            )

            # Get imports
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.extend(n.name for n in node.names)
                elif isinstance(node, ast.ImportFrom):
                    imports.append(node.module)

            # Simple complexity metric based on number of nodes
            complexity = len(list(ast.walk(tree)))

            return {
                "num_functions": num_functions,
                "num_classes": num_classes,
                "imports": imports,
                "complexity": complexity,
            }

        except Exception as e:
            msg = f"Failed to analyze code: {e!s}"
            raise RuntimeError(msg)
