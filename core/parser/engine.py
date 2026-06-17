import ast
import json
from typing import Optional, Any, Dict
from .types import Language, ParseResult, ParseError

try:
    from pyjsparser import PyJsParser

    js_parser = PyJsParser()
except ImportError:
    js_parser = None


def detect_language(code: str, filename: Optional[str] = None) -> Language:
    """Detect the language of the provided code snippet."""
    if filename:
        if filename.endswith(".py"):
            return Language.PYTHON
        if filename.endswith((".js", ".jsx", ".ts", ".tsx")):
            return Language.JAVASCRIPT
        if filename.endswith(".sh"):
            return Language.BASH

    # Heuristics for snippets without filenames
    # Tighten JS heuristics to prevent false Python matches
    if "const " in code or "let " in code or "function " in code or " => " in code:
        return Language.JAVASCRIPT
    if "import " in code and (" from " in code or "{" in code):
        return Language.JAVASCRIPT

    if "def " in code or ("import " in code and "from " in code):
        return Language.PYTHON

    if code.startswith("#!"):
        return Language.BASH

    return Language.UNKNOWO


def parse_python(code: str) -> ParseResult:
    """Parse Python code into an AST representation."""
    try:
        tree = ast.parse(code)
        ast_data = {"type": "Module", "body_count": len(tree.body)}
        return ParseResult(language=Language.PYTHON, ast_data=ast_data)
    except SyntaxError as e:
        error = ParseError(
            message=e.msg, line=e.lineno or 0, column=e.offset or 0, source=e.text or ""
        )
        return ParseResult(
            language=Language.PYTHON, ast_data={}, errors=[error], success=False
        )


def parse_javascript(code: str) -> ParseResult:
    """Parse JavaScript code using pyjsparser."""
    if not js_parser:
        return ParseResult(
            language=Language.JAVASCRIPT,
            ast_data={},
            errors=[ParseError("pyjsparser library not installed", 0, 0, "")],
            success=False,
        )

    try:
        ast_data = js_parser.parse(code)
        return ParseResult(language=Language.JAVASCRIPT, ast_data=ast_data)
    except Exception as e:
        return ParseResult(
            language=Language.JAVASCRIPT,
            ast_data={},
            errors=[ParseError(str(e), 0, 0, "")],
            success=False,
        )


def parse_code(code: str, filename: Optional[str] = None) -> ParseResult:
    """Primary API for the Code Parsing Pipeline."""
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
