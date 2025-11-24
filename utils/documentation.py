import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class DocItem:
    """Represents a documented item (function, class, module)"""

    name: str
    docstring: str
    type: str  # 'function', 'class', or 'module'
    source_file: str
    signature: str | None = None
    methods: list[Any] = None  # Will contain DocItems for class methods
    parameters: list[dict[str, str]] = None


class DocumentationGenerator:
    """Generates documentation from Python source code"""

    def __init__(self, root_dir: str = ".") -> None:
        self.root_dir = Path(root_dir)

    def parse_file(self, file_path: Path) -> list[DocItem]:
        """
        Parse a Python file and extract documentation

        Args:
            file_path: Path to the Python file

        Returns:
            List of DocItem objects containing documentation
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            module = ast.parse(content)
            docs = []

            # Get module docstring
            module_doc = ast.get_docstring(module)
            if module_doc:
                docs.append(
                    DocItem(
                        name=file_path.stem,
                        docstring=module_doc,
                        type="module",
                        source_file=str(file_path),
                    )
                )

            for node in ast.walk(module):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Parse function
                    docstring = ast.get_docstring(node) or ""
                    signature = self._get_function_signature(node)
                    params = self._get_function_parameters(node)

                    docs.append(
                        DocItem(
                            name=node.name,
                            docstring=docstring,
                            type="function",
                            source_file=str(file_path),
                            signature=signature,
                            parameters=params,
                        )
                    )

                elif isinstance(node, ast.ClassDef):
                    # Parse class
                    docstring = ast.get_docstring(node) or ""
                    methods = []

                    for item in node.body:
                        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            method_doc = ast.get_docstring(item) or ""
                            method_signature = self._get_function_signature(item)
                            method_params = self._get_function_parameters(item)

                            methods.append(
                                DocItem(
                                    name=item.name,
                                    docstring=method_doc,
                                    type="function",
                                    source_file=str(file_path),
                                    signature=method_signature,
                                    parameters=method_params,
                                )
                            )

                    docs.append(
                        DocItem(
                            name=node.name,
                            docstring=docstring,
                            type="class",
                            source_file=str(file_path),
                            methods=methods,
                        )
                    )

            return docs

        except Exception as e:
            logger.exception(f"Failed to parse file {file_path}: {e!s}")
            return []

    def _get_function_signature(self, node: ast.FunctionDef) -> str:
        """Extract function signature as string"""
        args = []
        for arg in node.args.args:
            args.append(arg.arg)
        return f"{node.name}({', '.join(args)})"

    def _get_function_parameters(self, node: ast.FunctionDef) -> list[dict[str, str]]:
        """Extract function parameters with type hints and defaults"""
        params = []
        for arg in node.args.args:
            param = {"name": arg.arg}
            if arg.annotation and hasattr(arg.annotation, "id"):
                param["type"] = arg.annotation.id
            params.append(param)
        return params

    def generate_documentation(self) -> dict[str, list[DocItem]]:
        """
        Generate documentation for all Python files in the project

        Returns:
            Dictionary mapping file paths to lists of DocItems
        """
        documentation = {}

        for file_path in self.root_dir.rglob("*.py"):
            if not any(part.startswith(".") for part in file_path.parts):
                relative_path = file_path.relative_to(self.root_dir)
                docs = self.parse_file(file_path)
                if docs:
                    documentation[str(relative_path)] = docs

        return documentation
