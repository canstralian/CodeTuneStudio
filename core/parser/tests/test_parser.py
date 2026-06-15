from core.parser.engine import parse_code
from core.parser.types import Language


def test_language_detection():
    assert parse_code("def hello(): pass").language == Language.PYTHON
    assert parse_code("const x = 1;").language == Language.JAVASCRIPT
    assert parse_code("#!/bin/bash\necho 1").language == Language.BASH


def test_python_parsing_success():
    code = "def add(a, b): return a + b"
    result = parse_code(code)
    assert result.success is True
    assert result.language == Language.PYTHON
    assert result.ast_data["type"] == "Module"


def test_python_parsing_failure():
    code = "def invalid_syntax("
    result = parse_code(code)
    assert result.success is False
    assert len(result.errors) > 0
    assert result.errors[0].line > 0
    assert result.errors[0].message == "Invalid Python syntax."


def test_javascript_parser_error_is_sanitized(monkeypatch):
    import pytest

    pytest.importorskip("pyjsparser")

    class BrokenParser:
        def parse(self, code):
            """
            Simulate a broken parser that always fails with a raw error message containing the input code.

            Parameters:
                code (str): Source code to parse.

            Raises:
                RuntimeError: Always raised with the message "raw parser detail for {code}" where `{code}` is the provided input.
            """
            raise RuntimeError(f"raw parser detail for {code}")

    # The engine creates a fresh PyJsParser() per call, so patch the class and
    # force availability rather than a module-level shared instance.
    monkeypatch.setattr("core.parser.engine._has_pyjsparser", True)
    monkeypatch.setattr("pyjsparser.PyJsParser", BrokenParser)

    result = parse_code("const x = ;", filename="example.js")

    assert result.success is False
    assert result.errors[0].message == "Unable to parse JavaScript code."


def test_non_string_input_returns_structured_error():
    result = parse_code(12345)
    assert result.success is False
    assert result.language == Language.UNKNOWN
    assert result.errors[0].message == "Input code must be a string."


def test_non_string_filename_returns_structured_error():
    result = parse_code("def f(): pass", filename=123)
    assert result.success is False
    assert result.language == Language.UNKNOWN
    assert result.errors[0].message == "Filename must be a string when provided."


# ─── detect_language tests ──────────────────────────────────────────────────

def test_detect_language_python_by_filename():
    from core.parser.engine import detect_language
    assert detect_language("x = 1", filename="script.py") == Language.PYTHON


def test_detect_language_javascript_by_js_extension():
    from core.parser.engine import detect_language
    assert detect_language("var x = 1", filename="app.js") == Language.JAVASCRIPT


def test_detect_language_javascript_by_ts_extension():
    from core.parser.engine import detect_language
    assert detect_language("var x = 1", filename="app.ts") == Language.JAVASCRIPT


def test_detect_language_javascript_by_jsx_extension():
    from core.parser.engine import detect_language
    assert detect_language("var x = 1", filename="app.jsx") == Language.JAVASCRIPT


def test_detect_language_javascript_by_tsx_extension():
    from core.parser.engine import detect_language
    assert detect_language("var x = 1", filename="app.tsx") == Language.JAVASCRIPT


def test_detect_language_bash_by_sh_extension():
    from core.parser.engine import detect_language
    assert detect_language("echo hi", filename="run.sh") == Language.BASH


def test_detect_language_python_heuristic_def():
    from core.parser.engine import detect_language
    assert detect_language("def foo(): pass") == Language.PYTHON


def test_detect_language_javascript_heuristic_const():
    from core.parser.engine import detect_language
    assert detect_language("const x = 1;") == Language.JAVASCRIPT


def test_detect_language_javascript_heuristic_let():
    from core.parser.engine import detect_language
    assert detect_language("let y = 2;") == Language.JAVASCRIPT


def test_detect_language_javascript_heuristic_function():
    from core.parser.engine import detect_language
    assert detect_language("function greet() {}") == Language.JAVASCRIPT


def test_detect_language_javascript_heuristic_arrow():
    from core.parser.engine import detect_language
    assert detect_language("const f = x => x + 1;") == Language.JAVASCRIPT


def test_detect_language_bash_heuristic_shebang():
    from core.parser.engine import detect_language
    assert detect_language("#!/bin/bash\necho hello") == Language.BASH


def test_detect_language_unknown_for_unrecognised_code():
    from core.parser.engine import detect_language
    assert detect_language("x = 42; y = x + 1;") == Language.UNKNOWN


def test_detect_language_filename_overrides_heuristic():
    # Content looks like JavaScript but filename says Python
    from core.parser.engine import detect_language
    assert detect_language("const x = 1;", filename="module.py") == Language.PYTHON


# ─── parse_code: BASH / UNKNOWN branch ─────────────────────────────────────

def test_parse_code_bash_returns_not_implemented():
    result = parse_code("#!/bin/bash\necho hi")
    assert result.success is False
    assert result.language.value == "bash"
    assert any("not implemented" in e.message for e in result.errors)


def test_parse_code_unknown_returns_not_implemented():
    result = parse_code("x 42 z")
    assert result.success is False
    assert result.language.value == "unknown"


# ─── parse_python edge-cases ────────────────────────────────────────────────

def test_parse_python_empty_module_succeeds():
    result = parse_code("", filename="empty.py")
    assert result.success is True
    assert result.ast_data["body_count"] == 0


def test_parse_python_body_count_matches():
    result = parse_code("x = 1\ny = 2\nz = 3", filename="three.py")
    assert result.success is True
    assert result.ast_data["body_count"] == 3


# ─── parse_javascript when pyjsparser is absent ─────────────────────────────

def test_parse_javascript_no_pyjsparser(monkeypatch):
    monkeypatch.setattr("core.parser.engine._has_pyjsparser", False)
    result = parse_code("const x = 1;")
    assert result.success is False
    assert "not installed" in result.errors[0].message


# ─── parse_code: None filename passes through correctly ─────────────────────

def test_parse_code_none_filename_uses_heuristics():
    result = parse_code("def f(): pass", filename=None)
    assert result.language == Language.PYTHON
    assert result.success is True
