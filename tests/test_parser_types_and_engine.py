"""
Tests for core/parser/types.py and core/parser/engine.py.

Covers:
  - Language enum
  - ParseError dataclass
  - ParseResult dataclass
  - detect_language()
  - parse_python()
  - parse_javascript()
  - parse_code()
"""

import unittest

from core.parser import engine as _engine_mod
from core.parser.engine import (
    detect_language,
    parse_python,
    parse_javascript,
    parse_code,
)
from core.parser.types import Language, ParseError, ParseResult


# ===========================================================================
# Tests for core/parser/types.py
# ===========================================================================


class TestLanguageEnum(unittest.TestCase):
    """Tests for the Language enum defined in core/parser/types.py."""

    def test_python_value(self):
        self.assertEqual(Language.PYTHON.value, "python")

    def test_javascript_value(self):
        self.assertEqual(Language.JAVASCRIPT.value, "javascript")

    def test_bash_value(self):
        self.assertEqual(Language.BASH.value, "bash")

    def test_unknown_value(self):
        self.assertEqual(Language.UNKNOWN.value, "unknown")

    def test_has_four_members(self):
        self.assertEqual(len(Language), 4)

    def test_members_accessible_by_name(self):
        self.assertIs(Language["PYTHON"], Language.PYTHON)
        self.assertIs(Language["JAVASCRIPT"], Language.JAVASCRIPT)

    def test_members_accessible_by_value(self):
        self.assertIs(Language("python"), Language.PYTHON)
        self.assertIs(Language("javascript"), Language.JAVASCRIPT)

    def test_invalid_value_raises(self):
        with self.assertRaises(ValueError):
            Language("ruby")


class TestParseError(unittest.TestCase):
    """Tests for the ParseError dataclass."""

    def _make(self, message="err", line=1, column=2, source="src"):
        return ParseError(message=message, line=line, column=column, source=source)

    def test_fields_stored(self):
        err = self._make("oops", 5, 10, "def foo(")
        self.assertEqual(err.message, "oops")
        self.assertEqual(err.line, 5)
        self.assertEqual(err.column, 10)
        self.assertEqual(err.source, "def foo(")

    def test_equality(self):
        self.assertEqual(self._make(), self._make())

    def test_inequality_different_message(self):
        self.assertNotEqual(self._make("a"), self._make("b"))

    def test_zero_line_and_column(self):
        err = ParseError(message="x", line=0, column=0, source="")
        self.assertEqual(err.line, 0)
        self.assertEqual(err.column, 0)

    def test_repr_contains_message(self):
        err = self._make("my error")
        self.assertIn("my error", repr(err))


class TestParseResult(unittest.TestCase):
    """Tests for the ParseResult dataclass."""

    def test_defaults(self):
        result = ParseResult(language=Language.PYTHON, ast_data={})
        self.assertEqual(result.errors, [])
        self.assertTrue(result.success)

    def test_explicit_values(self):
        err = ParseError("bad", 1, 0, "x")
        result = ParseResult(
            language=Language.JAVASCRIPT,
            ast_data={"type": "Program"},
            errors=[err],
            success=False,
        )
        self.assertIs(result.language, Language.JAVASCRIPT)
        self.assertEqual(result.ast_data, {"type": "Program"})
        self.assertEqual(result.errors, [err])
        self.assertFalse(result.success)

    def test_errors_list_is_independent_per_instance(self):
        r1 = ParseResult(language=Language.PYTHON, ast_data={})
        r2 = ParseResult(language=Language.PYTHON, ast_data={})
        r1.errors.append(ParseError("x", 1, 0, ""))
        self.assertEqual(r2.errors, [])

    def test_equality(self):
        r1 = ParseResult(language=Language.BASH, ast_data={"k": "v"})
        r2 = ParseResult(language=Language.BASH, ast_data={"k": "v"})
        self.assertEqual(r1, r2)


# ===========================================================================
# Tests for core/parser/engine.py
# ===========================================================================


class TestDetectLanguageByFilename(unittest.TestCase):
    """detect_language uses file extension when a filename is supplied."""

    def test_py_extension_returns_python(self):
        self.assertIs(detect_language("", "main.py"), Language.PYTHON)

    def test_js_extension_returns_javascript(self):
        self.assertIs(detect_language("", "app.js"), Language.JAVASCRIPT)

    def test_jsx_extension_returns_javascript(self):
        self.assertIs(detect_language("", "App.jsx"), Language.JAVASCRIPT)

    def test_ts_extension_returns_javascript(self):
        self.assertIs(detect_language("", "index.ts"), Language.JAVASCRIPT)

    def test_tsx_extension_returns_javascript(self):
        self.assertIs(detect_language("", "Component.tsx"), Language.JAVASCRIPT)

    def test_sh_extension_returns_bash(self):
        self.assertIs(detect_language("", "setup.sh"), Language.BASH)

    def test_unknown_extension_falls_through_to_heuristics(self):
        # No heuristic matches empty content → falls back
        result = detect_language("", "file.rb")
        # Should not be PYTHON, JAVASCRIPT, or BASH for empty content with .rb
        self.assertNotIn(result, [Language.PYTHON, Language.JAVASCRIPT, Language.BASH])


class TestDetectLanguageByHeuristics(unittest.TestCase):
    """detect_language uses code content when no filename is given."""

    def test_const_keyword_is_javascript(self):
        self.assertIs(detect_language("const x = 1;"), Language.JAVASCRIPT)

    def test_let_keyword_is_javascript(self):
        self.assertIs(detect_language("let y = 2;"), Language.JAVASCRIPT)

    def test_function_keyword_is_javascript(self):
        self.assertIs(detect_language("function foo() {}"), Language.JAVASCRIPT)

    def test_arrow_function_is_javascript(self):
        self.assertIs(detect_language("const f = x => x + 1;"), Language.JAVASCRIPT)

    def test_import_from_with_brace_is_javascript(self):
        self.assertIs(
            detect_language("import { foo } from 'bar';"), Language.JAVASCRIPT
        )

    def test_def_keyword_is_python(self):
        self.assertIs(detect_language("def hello(): pass"), Language.PYTHON)

    def test_import_from_is_python(self):
        self.assertIs(
            detect_language("import os\nfrom pathlib import Path"), Language.PYTHON
        )

    def test_shebang_is_bash(self):
        self.assertIs(detect_language("#!/bin/bash\necho hello"), Language.BASH)

    def test_empty_string_is_not_python_or_js_or_bash(self):
        result = detect_language("")
        self.assertNotIn(result, [Language.PYTHON, Language.JAVASCRIPT, Language.BASH])

    def test_plain_prose_is_not_python_or_js_or_bash(self):
        result = detect_language("Hello, world! This is plain text.")
        self.assertNotIn(result, [Language.PYTHON, Language.JAVASCRIPT, Language.BASH])


class TestParsePython(unittest.TestCase):
    """Tests for parse_python()."""

    def test_valid_code_success(self):
        result = parse_python("def add(a, b): return a + b")
        self.assertTrue(result.success)
        self.assertIs(result.language, Language.PYTHON)

    def test_valid_code_has_module_type(self):
        result = parse_python("x = 1")
        self.assertEqual(result.ast_data.get("type"), "Module")

    def test_valid_code_body_count(self):
        result = parse_python("x = 1\ny = 2\nz = 3")
        self.assertEqual(result.ast_data.get("body_count"), 3)

    def test_valid_code_empty_errors(self):
        result = parse_python("pass")
        self.assertEqual(result.errors, [])

    def test_syntax_error_sets_success_false(self):
        result = parse_python("def invalid_syntax(")
        self.assertFalse(result.success)

    def test_syntax_error_has_errors(self):
        result = parse_python("def bad(")
        self.assertGreater(len(result.errors), 0)

    def test_syntax_error_has_positive_line(self):
        result = parse_python("def bad(")
        self.assertGreater(result.errors[0].line, 0)

    def test_syntax_error_has_message(self):
        result = parse_python("(")
        self.assertIsInstance(result.errors[0].message, str)
        self.assertGreater(len(result.errors[0].message), 0)

    def test_syntax_error_language_is_python(self):
        result = parse_python("def bad(")
        self.assertIs(result.language, Language.PYTHON)

    def test_empty_string_is_valid(self):
        result = parse_python("")
        self.assertTrue(result.success)
        self.assertEqual(result.ast_data.get("body_count"), 0)

    def test_multiline_valid_code(self):
        code = "class Foo:\n    def bar(self):\n        return 42\n"
        result = parse_python(code)
        self.assertTrue(result.success)


class TestParseJavascript(unittest.TestCase):
    """Tests for parse_javascript() — focused on the no-parser path."""

    def test_no_js_parser_returns_error_result(self):
        """When js_parser is None (pyjsparser not installed), expect error."""
        if _engine_mod.js_parser is not None:
            self.skipTest("pyjsparser is installed; skipping no-parser path")
        result = parse_javascript("const x = 1;")
        self.assertFalse(result.success)
        self.assertIs(result.language, Language.JAVASCRIPT)
        self.assertGreater(len(result.errors), 0)

    def test_no_js_parser_error_message_mentions_library(self):
        if _engine_mod.js_parser is not None:
            self.skipTest("pyjsparser is installed")
        result = parse_javascript("const x = 1;")
        msg = result.errors[0].message.lower()
        self.assertIn("pyjsparser", msg)

    def test_with_mock_js_parser_success(self):
        """When js_parser is present and succeeds, result should be success."""
        import unittest.mock as mock

        fake_ast = {"type": "Program"}
        fake_parser = mock.MagicMock()
        fake_parser.parse.return_value = fake_ast

        original = _engine_mod.js_parser
        try:
            _engine_mod.js_parser = fake_parser
            result = parse_javascript("const x = 1;")
            self.assertTrue(result.success)
            self.assertIs(result.language, Language.JAVASCRIPT)
            self.assertEqual(result.ast_data, fake_ast)
        finally:
            _engine_mod.js_parser = original

    def test_with_mock_js_parser_exception_returns_error(self):
        """When js_parser.parse raises, result should capture the error."""
        import unittest.mock as mock

        fake_parser = mock.MagicMock()
        fake_parser.parse.side_effect = RuntimeError("parse failure")

        original = _engine_mod.js_parser
        try:
            _engine_mod.js_parser = fake_parser
            result = parse_javascript("bad js {{")
            self.assertFalse(result.success)
            self.assertIn("parse failure", result.errors[0].message)
        finally:
            _engine_mod.js_parser = original


class TestParseCode(unittest.TestCase):
    """Tests for parse_code() — the primary API."""

    def test_python_filename_routes_to_python(self):
        result = parse_code("def f(): pass", "script.py")
        self.assertIs(result.language, Language.PYTHON)

    def test_js_filename_routes_to_javascript(self):
        result = parse_code("const x = 1;", "app.js")
        self.assertIs(result.language, Language.JAVASCRIPT)

    def test_python_heuristic_routes_to_python(self):
        result = parse_code("def hello(): pass")
        self.assertIs(result.language, Language.PYTHON)

    def test_javascript_heuristic_routes_to_javascript(self):
        result = parse_code("const x = 1;")
        self.assertIs(result.language, Language.JAVASCRIPT)

    def test_bash_shebang_returns_unimplemented_error(self):
        result = parse_code("#!/bin/bash\necho hi")
        self.assertFalse(result.success)
        self.assertIs(result.language, Language.BASH)
        self.assertGreater(len(result.errors), 0)

    def test_unknown_language_returns_error_result(self):
        result = parse_code("")  # no heuristics match
        self.assertFalse(result.success)
        self.assertGreater(len(result.errors), 0)

    def test_python_parse_success_via_filename(self):
        result = parse_code("x = 1 + 2", "calc.py")
        self.assertTrue(result.success)
        self.assertEqual(result.ast_data["type"], "Module")

    def test_python_parse_failure_via_filename(self):
        result = parse_code("def broken(", "broken.py")
        self.assertFalse(result.success)
        self.assertGreater(len(result.errors), 0)

    def test_no_filename_bash_shebang(self):
        result = parse_code("#!/usr/bin/env bash\nls -la")
        # Bash parser is not implemented; should return error
        self.assertFalse(result.success)
        self.assertIs(result.language, Language.BASH)

    def test_unimplemented_language_error_message_contains_language(self):
        result = parse_code("#!/bin/bash\necho hi")
        err_msg = result.errors[0].message
        self.assertIn("bash", err_msg.lower())

    # ------------------------------------------------------------------
    # Type validation (new in this PR)
    # ------------------------------------------------------------------

    def test_non_string_code_returns_error_result(self):
        """parse_code rejects non-string code with an error ParseResult."""
        result = parse_code(42)
        self.assertFalse(result.success)
        self.assertIs(result.language, Language.UNKNOWN)
        self.assertGreater(len(result.errors), 0)

    def test_none_code_returns_error_result(self):
        result = parse_code(None)
        self.assertFalse(result.success)
        self.assertIs(result.language, Language.UNKNOWN)

    def test_non_string_filename_returns_error_result(self):
        result = parse_code("def foo(): pass", 123)
        self.assertFalse(result.success)
        self.assertIs(result.language, Language.UNKNOWN)

    def test_none_filename_is_valid(self):
        """filename=None is explicitly permitted."""
        result = parse_code("def foo(): pass", None)
        self.assertTrue(result.success)

    def test_type_error_message_mentions_strings(self):
        result = parse_code(0)
        error_text = " ".join(e.message for e in result.errors).lower()
        self.assertIn("string", error_text)


class TestDetectLanguageShebangSubtypes(unittest.TestCase):
    """Shebang sub-type detection paths added in this PR."""

    def test_shebang_python_returns_python(self):
        self.assertIs(
            detect_language("#!/usr/bin/python\nprint('hi')"), Language.PYTHON
        )

    def test_shebang_env_python_returns_python(self):
        self.assertIs(
            detect_language("#!/usr/bin/env python\nprint('hi')"), Language.PYTHON
        )

    def test_shebang_node_returns_javascript(self):
        self.assertIs(
            detect_language("#!/usr/bin/node\nconsole.log(1);"), Language.JAVASCRIPT
        )

    def test_shebang_env_node_returns_javascript(self):
        self.assertIs(
            detect_language("#!/usr/bin/env node\nprocess.exit(0);"),
            Language.JAVASCRIPT,
        )

    def test_shebang_deno_returns_javascript(self):
        self.assertIs(
            detect_language("#!/usr/bin/deno run\nconsole.log('hi');"),
            Language.JAVASCRIPT,
        )

    def test_shebang_sh_returns_bash(self):
        self.assertIs(detect_language("#!/bin/sh\nls"), Language.BASH)

    def test_shebang_unknown_interpreter_returns_unknown(self):
        result = detect_language("#!/usr/bin/ruby\nputs 'hi'")
        self.assertIs(result, Language.UNKNOWN)


if __name__ == "__main__":
    unittest.main()
