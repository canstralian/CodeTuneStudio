import ast
import json
from typing import Any

from core.parser.types import Language, ParseError, ParseResult

try:
    from pyjsparser import PyJsParser
except ImportError:  # pragma: no cover - optional dependency
    PyJsParser = None

js_parser = PyJsParser() if PyJsParser is not None else None


def detect_language(code: str, filename: str | None = None) -> Language:
    """Detect the language of the provided code snippet."""
    if filename:
        if filename.endswith(".py"):
            return Language.PYTHON
        if filename.endswith((".js", ".jsx", ".ts", ".tsx")):
            return Language.JAVASCRIPT
        if filename.endswith(".sh"):
            return Language.BASH

    # Heuristics for snippets without filenames. Check JavaScript first to avoid
    # treating ES module imports as Python imports.
    if (
        "const " in code
        or "let " in code
        or "function " in code
        or " => " in code
    ):
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
    Parse Python source code and produce a ParseResult summarizing the parsed AST or syntax errors.
    
    On successful parse, `ast_data` will contain a summary with `"type": "Module"` and a `"body_count"` integer. If a SyntaxError occurs, the result has `success=False`, `ast_data={}`, and `errors` containing a ParseError with `message`, `line`, `column`, and `source` extracted from the SyntaxError.
    
    Parameters:
    	code (str): Python source code to parse.
    
    Returns:
    	ParseResult: A ParseResult for Language.PYTHON containing either `ast_data` (on success) or `errors` and `success=False` (on syntax error).
    """
    try:
        tree = ast.parse(code)
        ast_data = {"type": "Module", "body_count": len(tree.body)}
        return ParseResult(language=Language.PYTHON, ast_data=ast_data)
    except SyntaxError as e:
        error = ParseError(
            message=e.msg,
            line=e.lineno or 0,
            column=e.offset or 0,
            source=e.text or "",
        )
        return ParseResult(
            language=Language.PYTHON,
            ast_data={},
            errors=[error],
            success=False,
        )


def parse_javascript(code: str) -> ParseResult:
    """
    Parse JavaScript source into a ParseResult using the installed pyjsparser.
    
    On success the returned ParseResult contains the parser's AST-like dictionary in `ast_data`. If pyjsparser is not available or parsing fails, the returned ParseResult has `ast_data` empty, `errors` containing one or more ParseError entries describing the problem, and `success` set to False.
        
    Returns:
        ParseResult: Parsed AST in `ast_data` on success; on failure `errors` contains ParseError(s) and `success` is False.
    """
    if not js_parser:
        return ParseResult(
            language=Language.JAVASCRIPT,
            ast_data={},
            errors=[ParseError("pyjsparser library not installed", 0, 0, "")],
            success=False,
        )

    try:
        ast_data: dict[str, Any] = js_parser.parse(code)
        return ParseResult(language=Language.JAVASCRIPT, ast_data=ast_data)
    except Exception as e:
        return ParseResult(
            language=Language.JAVASCRIPT,
            ast_data={},
            errors=[ParseError(str(e), 0, 0, "")],
            success=False,
        )


def parse_code(code: str, filename: str | None = None) -> ParseResult:
    """
    Detect the source language and parse the provided code, returning a ParseResult describing the outcome.
    
    If a language parser is available for the detected language, parsing is performed and its result is returned. If no parser is implemented for the detected language, the returned ParseResult indicates failure and includes an explanatory ParseError.
    
    Parameters:
        code (str): Source code to parse.
        filename (str | None): Optional filename used to help detect the language (affects heuristics); may be None.
    
    Returns:
        ParseResult: Object containing the detected language, any AST or summary data, a list of ParseError objects when parsing failed, and a boolean `success` flag.
    """
    lang = detect_language(code, filename)

    if lang == Language.PYTHON:
        return parse_python(code)

    if lang == Language.JAVASCRIPT:
        return parse_javascript(code)

    return ParseResult(
        language=lang,
        ast_data={},
        errors=[ParseError(f"Parser for {lang.value} not yet implemented", 0, 0, "")],
        success=False,
    )


def parse_code_to_json(code: str, filename: str | None = None) -> str:
    """
    Serialize the parser output into a CLI-friendly JSON string.
    
    Returns a JSON string with the following keys:
    - "language": the language name
    - "ast_data": parser AST or summary data
    - "errors": a list of error objects (each represented as a dict with the ParseError fields)
    - "success": boolean parse success flag
    
    Parameters:
        filename (str | None): Optional filename used to assist language detection; may be None.
    
    Returns:
        str: The serialized JSON representation described above.
    """
    result = parse_code(code, filename)
    return json.dumps(
        {
            "language": result.language.value,
            "ast_data": result.ast_data,
            "errors": [error.__dict__ for error in result.errors],
            "success": result.success,
        }
    )
