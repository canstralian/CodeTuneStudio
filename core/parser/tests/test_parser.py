from core.parser.engine import parse_code, Language


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
