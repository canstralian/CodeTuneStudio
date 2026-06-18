"""
Tests for core/parser/engine.py.

Covers:
  - detect_language: filename-based detection (.py, .js, .jsx, .ts, .tsx, .sh)
  - detect_language: heuristic-based detection (const/let/function/=>, import, def)
  - detect_language: falls back to Language.UNKNOWN for unrecognised code
  - parse_python: valid code, invalid syntax, body_count, error fields
  - parse_javascript: no pyjsparser fallback behaviour
  - parse_code: dispatcher to python/javascript/unsupported language
"""

import unittest
from unittest.mock import MagicMock

from core.parser.engine import (
    detect_language,
    parse_python,
    parse_javascript,
    parse_code,
)
from core.parser.types import Language


# ---------------------------------------------------------------------------
# detect_language: filename-based detection
# ---------------------------------------------------------------------------


class TestDetectLanguageByFilename(unittest.TestCase):
    def test_py_extension_returns_python(self):
        self.assertEqual(detect_language("", filename="script.py"), Language.PYTHON)

    def test_js_extension_returns_javascript(self):
        self.assertEqual(detect_language("", filename="app.js"), Language.JAVASCRIPT)

    def test_jsx_extension_returns_javascript(self):
        self.assertEqual(detect_language("", filename="comp.jsx"), Language.JAVASCRIPT)

    def test_ts_extension_returns_javascript(self):
        self.assertEqual(detect_language("", filename="app.ts"), Language.JAVASCRIPT)

    def test_tsx_extension_returns_javascript(self):
        self.assertEqual(detect_language("", filename="comp.tsx"), Language.JAVASCRIPT)

    def test_sh_extension_returns_bash(self):
        self.assertEqual(detect_language("", filename="run.sh"), Language.BASH)

    def test_unknown_extension_falls_through_to_heuristics(self):
        # An unrecognised extension falls through to heuristic detection.
        # Code containing "def " should be identified as Python.
        result = detect_language("def foo(): pass", filename="script.rb")
        self.assertEqual(result, Language.PYTHON)

    def test_filename_takes_priority_over_content_heuristics(self):
        # Even if content looks like JavaScript, .py extension wins.
        result = detect_language("const x = 1;", filename="script.py")
        self.assertEqual(result, Language.PYTHON)


# ---------------------------------------------------------------------------
# detect_language: heuristic-based detection (no filename)
# ---------------------------------------------------------------------------


class TestDetectLanguageHeuristics(unittest.TestCase):
    def test_const_keyword_returns_javascript(self):
        self.assertEqual(detect_language("const x = 1;"), Language.JAVASCRIPT)

    def test_let_keyword_returns_javascript(self):
        self.assertEqual(detect_language("let y = 2;"), Language.JAVASCRIPT)

    def test_function_keyword_returns_javascript(self):
        self.assertEqual(detect_language("function foo() {}"), Language.JAVASCRIPT)

    def test_arrow_function_returns_javascript(self):
        self.assertEqual(detect_language("const f = x => x + 1;"), Language.JAVASCRIPT)

    def test_import_with_from_returns_javascript(self):
        # "import ... from" with braces → JS
        self.assertEqual(
            detect_language("import { useState } from 'react';"), Language.JAVASCRIPT
        )

    def test_import_with_braces_returns_javascript(self):
        self.assertEqual(
            detect_language("import {Component} from './comp'"), Language.JAVASCRIPT
        )

    def test_def_keyword_returns_python(self):
        self.assertEqual(detect_language("def hello(): pass"), Language.PYTHON)

    def test_python_import_from_returns_python(self):
        self.assertEqual(
            detect_language("import os\nfrom pathlib import Path"), Language.PYTHON
        )

    def test_shebang_returns_bash(self):
        self.assertEqual(detect_language("#!/bin/bash\necho hi"), Language.BASH)

    def test_shebang_env_bash_returns_bash(self):
        self.assertEqual(detect_language("#!/usr/bin/env bash\nls"), Language.BASH)

    def test_unknown_code_returns_unknown_language(self):
        result = detect_language("some random text without any keywords")
        self.assertEqual(result, Language.UNKNOWN)

    def test_plain_assignment_returns_unknown_language(self):
        result = detect_language("x = 1")  # no 'const', 'let', 'def', 'import', '#!'
        self.assertEqual(result, Language.UNKNOWN)

    def test_js_heuristic_takes_priority_over_python(self):
        # Code with both JS and Python indicators should prefer JS (checked first).
        code = "const x = 1; def foo(): pass"
        self.assertEqual(detect_language(code), Language.JAVASCRIPT)


# ---------------------------------------------------------------------------
# parse_python
# ---------------------------------------------------------------------------


class TestParsePython(unittest.TestCase):
    def test_valid_function_succeeds(self):
        result = parse_python("def add(a, b): return a + b")
        self.assertTrue(result.success)
        self.assertEqual(result.language, Language.PYTHON)
        self.assertEqual(result.ast_data["type"], "Module")
        self.assertGreaterEqual(result.ast_data["body_count"], 1)

    def test_valid_empty_module(self):
        result = parse_python("")
        self.assertTrue(result.success)
        self.assertEqual(result.ast_data["body_count"], 0)

    def test_valid_class_definition(self):
        code = "class Foo:\n    pass\n"
        result = parse_python(code)
        self.assertTrue(result.success)
        self.assertEqual(result.ast_data["body_count"], 1)

    def test_valid_multiple_statements(self):
        code = "x = 1\ny = 2\nz = x + y\n"
        result = parse_python(code)
        self.assertTrue(result.success)
        self.assertEqual(result.ast_data["body_count"], 3)

    def test_invalid_syntax_returns_failure(self):
        result = parse_python("def invalid_syntax(")
        self.assertFalse(result.success)
        self.assertEqual(result.language, Language.PYTHON)
        self.assertGreater(len(result.errors), 0)

    def test_invalid_syntax_error_has_line_number(self):
        result = parse_python("def invalid_syntax(")
        self.assertFalse(result.success)
        self.assertGreater(result.errors[0].line, 0)

    def test_invalid_syntax_error_has_message(self):
        result = parse_python("def invalid_syntax(")
        self.assertIsInstance(result.errors[0].message, str)
        self.assertGreater(len(result.errors[0].message), 0)

    def test_invalid_syntax_error_column(self):
        result = parse_python("def f(\n")
        self.assertFalse(result.success)
        # Column may be 0 or positive
        self.assertGreaterEqual(result.errors[0].column, 0)

    def test_invalid_syntax_ast_data_empty(self):
        result = parse_python("::::")
        self.assertFalse(result.success)
        self.assertEqual(result.ast_data, {})

    def test_valid_import_statement(self):
        result = parse_python("import os\nfrom pathlib import Path\n")
        self.assertTrue(result.success)
        self.assertEqual(result.ast_data["body_count"], 2)

    def test_valid_code_no_errors(self):
        result = parse_python("x = 42")
        self.assertEqual(result.errors, [])

    def test_indentation_error_returns_failure(self):
        code = "if True:\npass\n"  # incorrect indentation
        result = parse_python(code)
        self.assertFalse(result.success)

    def test_multiline_valid_code(self):
        code = (
            "def greet(name):\n"
            "    return f'Hello, {name}'\n\n"
            "result = greet('World')\n"
        )
        result = parse_python(code)
        self.assertTrue(result.success)
        self.assertEqual(result.ast_data["body_count"], 2)


# ---------------------------------------------------------------------------
# parse_javascript
# ---------------------------------------------------------------------------


class TestParseJavascript(unittest.TestCase):
    def test_without_pyjsparser_returns_error(self):
        """When pyjsparser is not installed, parse_javascript returns an error."""
        import core.parser.engine as engine_mod

        original = engine_mod.js_parser
        try:
            engine_mod.js_parser = None
            result = parse_javascript("const x = 1;")
            self.assertFalse(result.success)
            self.assertEqual(result.language, Language.JAVASCRIPT)
            self.assertGreater(len(result.errors), 0)
            self.assertIn("pyjsparser", result.errors[0].message)
        finally:
            engine_mod.js_parser = original

    def test_without_pyjsparser_error_line_zero(self):
        import core.parser.engine as engine_mod

        original = engine_mod.js_parser
        try:
            engine_mod.js_parser = None
            result = parse_javascript("const x = 1;")
            self.assertEqual(result.errors[0].line, 0)
            self.assertEqual(result.errors[0].column, 0)
        finally:
            engine_mod.js_parser = original

    def test_with_working_pyjsparser(self):
        """When pyjsparser is available, a successful parse returns success."""
        import core.parser.engine as engine_mod

        mock_parser = MagicMock()
        mock_parser.parse.return_value = {"type": "Program"}
        original = engine_mod.js_parser
        try:
            engine_mod.js_parser = mock_parser
            result = parse_javascript("const x = 1;")
            self.assertTrue(result.success)
            self.assertEqual(result.language, Language.JAVASCRIPT)
            self.assertEqual(result.ast_data, {"type": "Program"})
        finally:
            engine_mod.js_parser = original

    def test_with_pyjsparser_exception_returns_failure(self):
        """When pyjsparser raises, parse_javascript returns an error result."""
        import core.parser.engine as engine_mod

        mock_parser = MagicMock()
        mock_parser.parse.side_effect = Exception("JS parse error")
        original = engine_mod.js_parser
        try:
            engine_mod.js_parser = mock_parser
            result = parse_javascript("bad js code %%")
            self.assertFalse(result.success)
            self.assertIn("JS parse error", result.errors[0].message)
        finally:
            engine_mod.js_parser = original


# ---------------------------------------------------------------------------
# parse_code: dispatcher
# ---------------------------------------------------------------------------


class TestParseCode(unittest.TestCase):
    def test_python_code_dispatches_to_parse_python(self):
        result = parse_code("def foo(): pass")
        self.assertEqual(result.language, Language.PYTHON)
        self.assertTrue(result.success)

    def test_python_file_by_filename(self):
        result = parse_code("x = 1", filename="script.py")
        self.assertEqual(result.language, Language.PYTHON)

    def test_javascript_code_dispatches_to_parse_javascript(self):
        import core.parser.engine as engine_mod

        original = engine_mod.js_parser
        try:
            engine_mod.js_parser = None
            result = parse_code("const x = 1;")
            self.assertEqual(result.language, Language.JAVASCRIPT)
            self.assertFalse(result.success)
        finally:
            engine_mod.js_parser = original

    def test_javascript_file_by_filename(self):
        result = parse_code("var x = 1;", filename="app.js")
        self.assertEqual(result.language, Language.JAVASCRIPT)

    def test_bash_file_by_filename_returns_unsupported(self):
        result = parse_code("echo hello", filename="run.sh")
        # detect_language returns BASH; no parser for BASH → error result
        self.assertFalse(result.success)
        self.assertEqual(result.language, Language.BASH)
        self.assertTrue(
            any("not yet implemented" in e.message for e in result.errors),
            f"Errors: {result.errors}",
        )

    def test_shebang_bash_returns_unsupported(self):
        result = parse_code("#!/bin/bash\necho hi")
        self.assertFalse(result.success)
        self.assertEqual(result.language, Language.BASH)

    def test_python_invalid_syntax_error_propagated(self):
        result = parse_code("def bad(")
        self.assertFalse(result.success)
        self.assertEqual(result.language, Language.PYTHON)
        self.assertGreater(len(result.errors), 0)

    def test_python_valid_ast_data_structure(self):
        result = parse_code("import sys\nprint(sys.argv)")
        self.assertTrue(result.success)
        self.assertEqual(result.ast_data["type"], "Module")
        self.assertIn("body_count", result.ast_data)

    def test_no_filename_uses_heuristics(self):
        # "def " heuristic → Python
        result = parse_code("def hello(): return 42")
        self.assertEqual(result.language, Language.PYTHON)

    def test_unknown_code_without_filename_returns_unknown_language(self):
        result = parse_code("totally unrecognised content 12345")
        self.assertFalse(result.success)
        self.assertEqual(result.language, Language.UNKNOWN)

    def test_tsx_file_treated_as_javascript(self):
        result = parse_code("const C = () => <div />;", filename="comp.tsx")
        self.assertEqual(result.language, Language.JAVASCRIPT)

    def test_typescript_file_treated_as_javascript(self):
        result = parse_code("const x: number = 1;", filename="app.ts")
        self.assertEqual(result.language, Language.JAVASCRIPT)

    def test_bash_unsupported_error_message_contains_bash(self):
        result = parse_code("ls -la", filename="run.sh")
        self.assertFalse(result.success)
        error_messages = [e.message for e in result.errors]
        self.assertTrue(
            any("bash" in m.lower() for m in error_messages),
            f"Error messages: {error_messages}",
        )


# ---------------------------------------------------------------------------
# detect_language: shebang sub-type detection (new in this PR)
# ---------------------------------------------------------------------------


class TestDetectLanguageShebangSubtypes(unittest.TestCase):
    """detect_language identifies Python, JS and Bash from shebang first-line."""

    def test_shebang_python_returns_python(self):
        self.assertEqual(
            detect_language("#!/usr/bin/python\nprint('hi')"), Language.PYTHON
        )

    def test_shebang_usr_bin_env_python_returns_python(self):
        self.assertEqual(
            detect_language("#!/usr/bin/env python\nprint('hi')"), Language.PYTHON
        )

    def test_shebang_python3_returns_python(self):
        self.assertEqual(
            detect_language("#!/usr/bin/python3\nprint('hi')"), Language.PYTHON
        )

    def test_shebang_node_returns_javascript(self):
        self.assertEqual(
            detect_language("#!/usr/bin/node\nconsole.log(1);"), Language.JAVASCRIPT
        )

    def test_shebang_env_node_returns_javascript(self):
        self.assertEqual(
            detect_language("#!/usr/bin/env node\nprocess.exit(0);"), Language.JAVASCRIPT
        )

    def test_shebang_deno_returns_javascript(self):
        self.assertEqual(
            detect_language("#!/usr/bin/deno run\nconsole.log('hi');"),
            Language.JAVASCRIPT,
        )

    def test_shebang_sh_returns_bash(self):
        self.assertEqual(
            detect_language("#!/bin/sh\nls"), Language.BASH
        )

    def test_shebang_env_bash_returns_bash(self):
        self.assertEqual(
            detect_language("#!/usr/bin/env bash\necho hello"), Language.BASH
        )

    def test_shebang_unknown_interpreter_returns_unknown(self):
        # A shebang with an unrecognised interpreter falls through to UNKNOWN
        result = detect_language("#!/usr/bin/ruby\nputs 'hi'")
        self.assertEqual(result, Language.UNKNOWN)


# ---------------------------------------------------------------------------
# parse_code: type validation (new in this PR)
# ---------------------------------------------------------------------------


class TestParseCodeTypeValidation(unittest.TestCase):
    """parse_code validates that code and filename are strings."""

    def test_non_string_code_returns_error(self):
        result = parse_code(42)
        self.assertFalse(result.success)
        self.assertEqual(result.language, Language.UNKNOWN)
        self.assertGreater(len(result.errors), 0)

    def test_none_code_returns_error(self):
        result = parse_code(None)
        self.assertFalse(result.success)
        self.assertEqual(result.language, Language.UNKNOWN)

    def test_list_code_returns_error(self):
        result = parse_code(["def foo(): pass"])
        self.assertFalse(result.success)

    def test_non_string_filename_returns_error(self):
        result = parse_code("def foo(): pass", filename=42)
        self.assertFalse(result.success)
        self.assertEqual(result.language, Language.UNKNOWN)

    def test_none_filename_is_allowed(self):
        """None filename is explicitly allowed (default)."""
        result = parse_code("def foo(): pass", filename=None)
        self.assertTrue(result.success)
        self.assertEqual(result.language, Language.PYTHON)

    def test_type_error_message_mentions_strings(self):
        result = parse_code(42)
        self.assertTrue(
            any("string" in e.message.lower() for e in result.errors),
            f"Error messages: {[e.message for e in result.errors]}",
        )

    def test_type_error_ast_data_is_empty(self):
        result = parse_code(42)
        self.assertEqual(result.ast_data, {})

    def test_empty_string_code_is_valid(self):
        """An empty string is a valid code argument."""
        result = parse_code("")
        # Empty string → UNKNOWN language (no heuristics match)
        self.assertFalse(result.success)
        # But the failure is due to unknown language, not type error
        self.assertNotIn(
            "must be strings",
            " ".join(e.message for e in result.errors),
        )


if __name__ == "__main__":
    unittest.main()
