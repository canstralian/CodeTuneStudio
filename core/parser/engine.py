import ast
import importlib
import importlib.util
import logging
from typing import Any

from .types import Language, ParseError, ParseResult

logger = logging.getLogger(__name__)

# Whether the optional ``pyjsparser`` dependency is importable. A fresh parser
# instance is created per invocation (see ``parse_javascript``) because
# ``pyjsparser.PyJsParser`` keeps mutable internal state (``self.index``,
# ``self.lineNumber``) and is therefore not safe to share across threads.
_has_pyjsparser = importlib.util.find_spec("pyjsparser") is not None


def detect_language(code: str, filename: str | None = None) -> Language:
    """
    Infer the programming language of a code snippet using filename extension and code heuristics.

    Parameters:
        code (str): Source code to analyze.
        filename (str | None): Optional filename whose extension is used first to guide detection.

    Returns:
        Language: One of Language.PYTHON, Language.JAVASCRIPT, Language.BASH, or Language.UNKNOWN.
    """
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
    """
    Parse Python source code into a compact AST representation.
    
    Returns:
        ParseResult: A module summary on success; errors and success=False on failure.
    """
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
    """
    Parse JavaScript source code into an abstract syntax tree.
    
    Parameters:
        code (str): JavaScript source code to parse.
    
    Returns:
        ParseResult: The parsed AST on success; error details if parsing fails.
    """
    if not _has_pyjsparser:
        return ParseResult(
            language=Language.JAVASCRIPT,
            ast_data={},
            errors=[ParseError("JavaScript parser dependency is not installed.", 0, 0)],
            success=False,
        )

    try:
        from pyjsparser import PyJsParser

        # Instantiate per call: PyJsParser is stateful and not thread-safe.
        ast_data = PyJsParser().parse(code)
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
    """
    Detect the language of the given code and parse it accordingly.
    
    Parameters:
        code (str): Source code to parse.
        filename (str | None): Optional filename to improve language detection.
    
    Returns:
        ParseResult: Parsed result including detected language, AST metadata, errors (if any), and a success flag.
    """
    if not isinstance(code, str):
        return ParseResult(
            language=Language.UNKNOWN,
            ast_data={},
            errors=[ParseError("Input code must be a string.", 0, 0)],
            success=False,
        )
    if filename is not None and not isinstance(filename, str):
        return ParseResult(
            language=Language.UNKNOWN,
            ast_data={},
            errors=[ParseError("Filename must be a string when provided.", 0, 0)],
            success=False,
        )

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
