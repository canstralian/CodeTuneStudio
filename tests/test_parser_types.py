"""Tests for core/parser/types.py

The core.parser package __init__.py is currently broken (contains raw base64 text
as Python code), so we load types.py directly via importlib to avoid that error.
"""
import importlib.util
import sys
import types as stdlib_types
import unittest
from pathlib import Path

# ---------------------------------------------------------------------------
# Bootstrap: load core/parser/types.py without triggering the broken __init__.py
# ---------------------------------------------------------------------------
_TYPES_FILE = Path(__file__).resolve().parent.parent / "core" / "parser" / "types.py"

_types_spec = importlib.util.spec_from_file_location("core.parser.types", _TYPES_FILE)
_types_mod = importlib.util.module_from_spec(_types_spec)
_types_spec.loader.exec_module(_types_mod)

Language = _types_mod.Language
ParseError = _types_mod.ParseError
ParseResult = _types_mod.ParseResult


# ---------------------------------------------------------------------------
# Language enum tests
# ---------------------------------------------------------------------------


class TestLanguageEnum(unittest.TestCase):
    """Tests for the Language enum added in this PR."""

    def test_python_value(self):
        self.assertEqual(Language.PYTHON.value, "python")

    def test_javascript_value(self):
        self.assertEqual(Language.JAVASCRIPT.value, "javascript")

    def test_bash_value(self):
        self.assertEqual(Language.BASH.value, "bash")

    def test_unknown_value(self):
        self.assertEqual(Language.UNKNOWN.value, "unknown")

    def test_enum_members_count(self):
        """Exactly four language variants should be defined."""
        self.assertEqual(len(Language), 4)

    def test_enum_from_value_python(self):
        self.assertIs(Language("python"), Language.PYTHON)

    def test_enum_from_value_javascript(self):
        self.assertIs(Language("javascript"), Language.JAVASCRIPT)

    def test_enum_from_value_bash(self):
        self.assertIs(Language("bash"), Language.BASH)

    def test_enum_from_value_unknown(self):
        self.assertIs(Language("unknown"), Language.UNKNOWN)

    def test_enum_invalid_value_raises(self):
        with self.assertRaises(ValueError):
            Language("ruby")

    def test_enum_identity(self):
        """Accessing the same member twice yields the same object."""
        self.assertIs(Language.PYTHON, Language.PYTHON)


# ---------------------------------------------------------------------------
# ParseError dataclass tests
# ---------------------------------------------------------------------------


class TestParseError(unittest.TestCase):
    """Tests for the ParseError dataclass added in this PR."""

    def _make(self, message="err", line=1, column=0, source=""):
        return ParseError(message=message, line=line, column=column, source=source)

    def test_fields_stored_correctly(self):
        err = self._make(message="bad token", line=3, column=5, source="bad code here")
        self.assertEqual(err.message, "bad token")
        self.assertEqual(err.line, 3)
        self.assertEqual(err.column, 5)
        self.assertEqual(err.source, "bad code here")

    def test_zero_line_allowed(self):
        err = self._make(line=0)
        self.assertEqual(err.line, 0)

    def test_empty_source_allowed(self):
        err = self._make(source="")
        self.assertEqual(err.source, "")

    def test_equality(self):
        a = ParseError(message="x", line=1, column=2, source="s")
        b = ParseError(message="x", line=1, column=2, source="s")
        self.assertEqual(a, b)

    def test_inequality_on_line(self):
        a = ParseError(message="x", line=1, column=0, source="")
        b = ParseError(message="x", line=2, column=0, source="")
        self.assertNotEqual(a, b)

    def test_is_dataclass(self):
        import dataclasses

        self.assertTrue(dataclasses.is_dataclass(ParseError))


# ---------------------------------------------------------------------------
# ParseResult dataclass tests
# ---------------------------------------------------------------------------


class TestParseResult(unittest.TestCase):
    """Tests for the ParseResult dataclass added in this PR."""

    def test_defaults(self):
        result = ParseResult(language=Language.PYTHON, ast_data={"type": "Module"})
        self.assertEqual(result.language, Language.PYTHON)
        self.assertEqual(result.ast_data, {"type": "Module"})
        self.assertEqual(result.errors, [])
        self.assertTrue(result.success)

    def test_success_defaults_to_true(self):
        result = ParseResult(language=Language.BASH, ast_data={})
        self.assertTrue(result.success)

    def test_errors_default_is_independent_per_instance(self):
        """Mutable default via field(default_factory=list) must not be shared."""
        r1 = ParseResult(language=Language.PYTHON, ast_data={})
        r2 = ParseResult(language=Language.PYTHON, ast_data={})
        r1.errors.append(ParseError("e", 1, 0, ""))
        self.assertEqual(len(r2.errors), 0)

    def test_explicit_errors(self):
        err = ParseError("syntax error", 5, 3, "bad code")
        result = ParseResult(
            language=Language.PYTHON, ast_data={}, errors=[err], success=False
        )
        self.assertFalse(result.success)
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(result.errors[0].message, "syntax error")

    def test_language_javascript(self):
        result = ParseResult(language=Language.JAVASCRIPT, ast_data={"body": []})
        self.assertIs(result.language, Language.JAVASCRIPT)

    def test_is_dataclass(self):
        import dataclasses

        self.assertTrue(dataclasses.is_dataclass(ParseResult))

    def test_equality(self):
        r1 = ParseResult(language=Language.BASH, ast_data={})
        r2 = ParseResult(language=Language.BASH, ast_data={})
        self.assertEqual(r1, r2)

    def test_ast_data_preserved(self):
        data = {"type": "Module", "body_count": 3}
        result = ParseResult(language=Language.PYTHON, ast_data=data)
        self.assertEqual(result.ast_data["body_count"], 3)


if __name__ == "__main__":
    unittest.main()