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
    Parse Python source into a compact AST summary.

    On success returns a ParseResult with language set to Language.PYTHON and ast_data containing a summary
    of the module (for example {'type': 'Module', 'body_count': ...}). On failure returns a ParseResult
    with a single ParseError describing the syntax or parsing failure and success set to False.

    Returns:
        ParseResult: Parsed AST summary on success; on failure contains one ParseError and success=False.
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
    Parse JavaScript source into an AST-like structure using the installed pyjsparser.

    Parameters:
        code (str): JavaScript source code to parse.

    Returns:
        ParseResult: On success, contains Language.JAVASCRIPT and the parser's AST in `ast_data`.
        On failure, `success` is False and `errors` contains a single ParseError describing one of:
          - the JavaScript parser dependency is not installed,
          - invalid JavaScript syntax,
          - or an unexpected parser failure. In failure cases the returned `language` is Language.JAVASCRIPT and error positions default to (0, 0).
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
    Detects the input language and returns a parsing result for the code.

    Parameters:
        code (str): Source code to analyze and parse.
        filename (str | None): Optional filename used to improve language detection (by extension or shebang).

    Returns:
        ParseResult: An object containing detected language, parsed AST metadata when parsing succeeds, a list of parsing errors when parsing fails, and a success flag. If no parser is implemented for the detected language, `errors` will include a message indicating the parser is not implemented and `success` will be `False`. Non-string ``code`` (or a non-string ``filename``) yields a failed ``ParseResult`` with a structured ``ParseError`` rather than raising.
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
