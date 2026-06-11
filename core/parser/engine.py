import ast
import importlib
import importlib.util
import logging
from typing import Any

from .types import Language, ParseError, ParseResult

logger = logging.getLogger(__name__)

js_parser = None
if importlib.util.find_spec("pyjsparser") is not None:
    js_parser = importlib.import_module("pyjsparser").PyJsParser()


def detect_language(code: str, filename: str | None = None) -> Language:
    """Detect the language of the provided code snippet."""
    if filename:
        if filename.endswith(".py"):
            return Language.PYTHON
        if filename.endswith((".js", ".jsx", ".ts", ".tsx")):
            return Language.JAVASCRIPT
        if filename.endswith(".sh"):
            return Language.BASH

    if "const " in code or "let " in code or "function " in code or " => " in code:
        return Language.JAVASCRIPT
    if "import " in code and (" from " in code or "{" in code):
        return Language.JAVASCRIPT
    if "def " in code or ("import " in code and "from " in code):
        return Language.PYTHON
    if code.startswith("#!"):
        return Language.BASH

    return Language.UNKNOWN


def parse_python(code: str) -> ParseResult:
    """Parse Python code into a compact AST representation."""
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        error = ParseError(
            message="Invalid Python syntax.",
            line=exc.lineno or 0,
            column=exc.offset or 0,
        )
        return ParseResult(
            language=Language.PYTHON,
            ast_data={},
            errors=[error],
            success=False,
        )
    except Exception:
        logger.exception("Python parser failed unexpectedly")
        error = ParseError("Unable to parse Python code.", 0, 0)
        return ParseResult(
            language=Language.PYTHON,
            ast_data={},
            errors=[error],
            success=False,
        )

    ast_data: dict[str, Any] = {"type": "Module", "body_count": len(tree.body)}
    return ParseResult(language=Language.PYTHON, ast_data=ast_data)


def parse_javascript(code: str) -> ParseResult:
    """Parse JavaScript code using pyjsparser when it is installed."""
    if not js_parser:
        return ParseResult(
            language=Language.JAVASCRIPT,
            ast_data={},
            errors=[ParseError("JavaScript parser dependency is not installed.", 0, 0)],
            success=False,
        )

    try:
        ast_data = js_parser.parse(code)
    except SyntaxError:
        return ParseResult(
            language=Language.JAVASCRIPT,
            ast_data={},
            errors=[ParseError("Invalid JavaScript syntax.", 0, 0)],
            success=False,
        )
    except Exception:
        logger.exception("JavaScript parser failed unexpectedly")
        return ParseResult(
            language=Language.JAVASCRIPT,
            ast_data={},
            errors=[ParseError("Unable to parse JavaScript code.", 0, 0)],
            success=False,
        )

    return ParseResult(language=Language.JAVASCRIPT, ast_data=ast_data)


def parse_code(code: str, filename: str | None = None) -> ParseResult:
    """Primary API for the code parsing pipeline."""
    lang = detect_language(code, filename)

    if lang == Language.PYTHON:
        return parse_python(code)
    if lang == Language.JAVASCRIPT:
        return parse_javascript(code)

    return ParseResult(
        language=lang,
        ast_data={},
        errors=[ParseError(f"Parser for {lang.value} is not implemented.", 0, 0)],
        success=False,
    )
