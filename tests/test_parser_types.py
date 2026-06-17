"""
Tests for core/parser/types.py.

Covers:
- Language enum (values, membership, iteration)
- ParseError dataclass (construction, field access)
- ParseResult dataclass (construction, defaults, field access)
"""

import unittest

from core.parser.types import Language, ParseError, ParseResult


# ---------------------------------------------------------------------------
# Language enum tests
# ---------------------------------------------------------------------------


class TestLanguageEnum(unittest.TestCase):
    def test_python_value(self):
        self.assertEqual(Language.PYTHON.value, "python")

    def test_javascript_value(self):
        self.assertEqual(Language.JAVASCRIPT.value, "javascript")

    def test_bash_value(self):
        self.assertEqual(Language.BASH.value, "bash")

    def test_unknown_value(self):
        self.assertEqual(Language.UNKNOWN.value, "unknown")

    def test_all_members_present(self):
        names = {m.name for m in Language}
        self.assertIn("PYTHON", names)
        self.assertIn("JAVASCRIPT", names)
        self.assertIn("BASH", names)
        self.assertIn("UNKNOWN", names)

    def test_exactly_four_members(self):
        self.assertEqual(len(list(Language)), 4)

    def test_lookup_by_value(self):
        self.assertEqual(Language("python"), Language.PYTHON)
        self.assertEqual(Language("javascript"), Language.JAVASCRIPT)
        self.assertEqual(Language("bash"), Language.BASH)
        self.assertEqual(Language("unknown"), Language.UNKNOWN)

    def test_invalid_value_raises(self):
        with self.assertRaises(ValueError):
            Language("ruby")

    def test_members_are_comparable(self):
        self.assertEqual(Language.PYTHON, Language.PYTHON)
        self.assertNotEqual(Language.PYTHON, Language.JAVASCRIPT)

    def test_members_are_enum_instances(self):
        from enum import Enum

        self.assertIsInstance(Language.PYTHON, Enum)


# ---------------------------------------------------------------------------
# ParseError dataclass tests
# ---------------------------------------------------------------------------


class TestParseError(unittest.TestCase):
    def test_construction_with_all_fields(self):
        err = ParseError(message="syntax error", line=10, column=5, source="def foo(")
        self.assertEqual(err.message, "syntax error")
        self.assertEqual(err.line, 10)
        self.assertEqual(err.column, 5)
        self.assertEqual(err.source, "def foo(")

    def test_zero_line_and_column(self):
        err = ParseError(message="lib missing", line=0, column=0, source="")
        self.assertEqual(err.line, 0)
        self.assertEqual(err.column, 0)
        self.assertEqual(err.source, "")

    def test_message_is_string(self):
        err = ParseError(message="err", line=1, column=1, source="x")
        self.assertIsInstance(err.message, str)

    def test_equality(self):
        err1 = ParseError(message="err", line=1, column=2, source="x")
        err2 = ParseError(message="err", line=1, column=2, source="x")
        self.assertEqual(err1, err2)

    def test_inequality_different_message(self):
        err1 = ParseError(message="err1", line=1, column=2, source="x")
        err2 = ParseError(message="err2", line=1, column=2, source="x")
        self.assertNotEqual(err1, err2)

    def test_inequality_different_line(self):
        err1 = ParseError(message="err", line=1, column=2, source="x")
        err2 = ParseError(message="err", line=3, column=2, source="x")
        self.assertNotEqual(err1, err2)

    def test_repr_contains_fields(self):
        err = ParseError(message="oops", line=7, column=3, source="bad code")
        r = repr(err)
        self.assertIn("oops", r)
        self.assertIn("7", r)

    def test_multiline_source(self):
        err = ParseError(message="err", line=2, column=0, source="line1\nline2")
        self.assertIn("\n", err.source)

    def test_long_message(self):
        long_msg = "x" * 1000
        err = ParseError(message=long_msg, line=1, column=0, source="")
        self.assertEqual(len(err.message), 1000)


# ---------------------------------------------------------------------------
# ParseResult dataclass tests
# ---------------------------------------------------------------------------


class TestParseResult(unittest.TestCase):
    def test_minimal_construction(self):
        result = ParseResult(language=Language.PYTHON, ast_data={})
        self.assertEqual(result.language, Language.PYTHON)
        self.assertEqual(result.ast_data, {})
        self.assertEqual(result.errors, [])
        self.assertTrue(result.success)

    def test_explicit_success_false(self):
        result = ParseResult(language=Language.PYTHON, ast_data={}, success=False)
        self.assertFalse(result.success)

    def test_errors_default_is_empty_list(self):
        r1 = ParseResult(language=Language.PYTHON, ast_data={})
        r2 = ParseResult(language=Language.JAVASCRIPT, ast_data={})
        # Each instance should have its own list (not shared)
        r1.errors.append(ParseError("e", 1, 0, ""))
        self.assertEqual(r2.errors, [])

    def test_with_errors(self):
        err = ParseError(message="SyntaxError", line=3, column=0, source="bad")
        result = ParseResult(
            language=Language.PYTHON, ast_data={}, errors=[err], success=False
        )
        self.assertEqual(len(result.errors), 1)
        self.assertIs(result.errors[0], err)
        self.assertFalse(result.success)

    def test_ast_data_preserved(self):
        data = {"type": "Module", "body_count": 5}
        result = ParseResult(language=Language.PYTHON, ast_data=data)
        self.assertEqual(result.ast_data["type"], "Module")
        self.assertEqual(result.ast_data["body_count"], 5)

    def test_javascript_language(self):
        result = ParseResult(language=Language.JAVASCRIPT, ast_data={"type": "Program"})
        self.assertEqual(result.language, Language.JAVASCRIPT)

    def test_bash_language(self):
        result = ParseResult(language=Language.BASH, ast_data={})
        self.assertEqual(result.language, Language.BASH)

    def test_unknown_language(self):
        result = ParseResult(language=Language.UNKNOWN, ast_data={})
        self.assertEqual(result.language, Language.UNKNOWN)

    def test_equality_same_values(self):
        r1 = ParseResult(language=Language.PYTHON, ast_data={"k": "v"})
        r2 = ParseResult(language=Language.PYTHON, ast_data={"k": "v"})
        self.assertEqual(r1, r2)

    def test_inequality_different_language(self):
        r1 = ParseResult(language=Language.PYTHON, ast_data={})
        r2 = ParseResult(language=Language.JAVASCRIPT, ast_data={})
        self.assertNotEqual(r1, r2)

    def test_multiple_errors(self):
        errors = [
            ParseError("err1", 1, 0, ""),
            ParseError("err2", 2, 3, "source"),
        ]
        result = ParseResult(
            language=Language.PYTHON, ast_data={}, errors=errors, success=False
        )
        self.assertEqual(len(result.errors), 2)

    def test_success_true_is_default(self):
        result = ParseResult(language=Language.PYTHON, ast_data={})
        self.assertIs(result.success, True)

    def test_empty_ast_data(self):
        result = ParseResult(language=Language.UNKNOWN, ast_data={})
        self.assertEqual(result.ast_data, {})

    def test_ast_data_with_nested_structure(self):
        data = {"type": "Module", "body": [{"type": "FunctionDef", "name": "foo"}]}
        result = ParseResult(language=Language.PYTHON, ast_data=data)
        self.assertEqual(result.ast_data["body"][0]["name"], "foo")


if __name__ == "__main__":
    unittest.main()
