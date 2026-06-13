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
