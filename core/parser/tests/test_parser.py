from core.parser.engine import Language, parse_code


def test_language_detection() -> None:
    assert parse_code("def hello(): pass").language == Language.PYTHON
    assert parse_code("const x = 1;").language == Language.JAVASCRIPT
    assert parse_code("#!/bin/bash\necho 1").language == Language.BASH


def test_python_parsing_success() -> None:
    code = "def add(a, b): return a + b"
    result = parse_code(code)
    assert result.success is True
    assert result.language == Language.PYTHON
    assert result.ast_data["type"] == "Module"


def test_python_parsing_failure() -> None:
    code = "def invalid_syntax("
    result = parse_code(code)
    assert result.success is False
    assert len(result.errors) > 0
    assert result.errors[0].line > 0
