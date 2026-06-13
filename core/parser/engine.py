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
    """
    Determine the programming language of a code snippet using the filename extension first, then simple content heuristics.
    
    Parameters:
        code (str): Source code to analyze.
        filename (str | None): Optional filename; when provided, its extension is used before examining code content.
    
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
    Parse Python source into a compact AST summary.
    
    If parsing succeeds, returns a ParseResult with language set to Language.PYTHON and ast_data containing a module summary (e.g. {'type': 'Module', 'body_count': N}). If a SyntaxError occurs, returns a ParseResult with a single ParseError(message="Invalid Python syntax.", line=..., column=...) and success=False. On any other unexpected exception the failure is logged and a ParseResult with ParseError("Unable to parse Python code.", 0, 0) and success=False is returned.
    
    Returns:
        ParseResult: On success contains the AST summary and Language.PYTHON; on failure contains one ParseError and success=False.
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
    Parse JavaScript source into an AST-like structure using the installed JavaScript parser.
    
    Returns:
        ParseResult: On success, `language` is Language.JAVASCRIPT and `ast_data` contains the parser result.
        On failure, `language` is Language.JAVASCRIPT, `success` is False, and `errors` contains a single `ParseError` (error positions default to (0, 0)).
    """
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
    """
    Detects the language of the provided source and returns a ParseResult describing the parse outcome.
    
    Parameters:
        code (str): Source code to analyze.
        filename (str | None): Optional filename used to improve language detection via extension or shebang.
    
    Returns:
        ParseResult: Contains the detected language, parsed AST metadata on success, a list of ParseError on failure, and a boolean `success` flag. If no parser is implemented for the detected language, `errors` will include a message stating the parser is not implemented and `success` will be `False`.
    """
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
