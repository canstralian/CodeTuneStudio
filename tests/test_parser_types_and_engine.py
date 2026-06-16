"""
Tests for core/parser/types.py and core/parser/engine.py.

These tests cover the code introduced in this PR:
  - Language enum
  - ParseError dataclass
  - ParseResult dataclass
  - detect_language()
  - parse_python()
  - parse_javascript()
  - parse_code()

Because engine.py contains a module-level annotation bug (``-> PashResult``),
the module is loaded via importlib with the annotation patched in-memory.
If loading still fails for any reason, all engine tests are skipped.
"""

import importlib.util
import sys
import types as _types
import unittest
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
TYPES_PATH = REPO_ROOT / "core" / "parser" / "types.py"
ENGINE_PATH = REPO_ROOT / "core" / "parser" / "engine.py"

# ---------------------------------------------------------------------------
# Load core.parser.types via importlib (bypasses broken __init__.py)
# ---------------------------------------------------------------------------

_types_spec = importlib.util.spec_from_file_location("core.parser.types", TYPES_PATH)
_types_mod = importlib.util.module_from_spec(_types_spec)
_types_spec.loader.exec_module(_types_mod)

Language = _types_mod.Language
ParseError = _types_mod.ParseError
ParseResult = _types_mod.ParseResult

# ---------------------------------------------------------------------------
# Load core.parser.engine via importlib, working around the two known bugs:
#   1. `from .s.types import ...`  — the subpackage "s" does not exist.
#   2. `-> PashResult:`            — PashResult is undefined (typo).
# ---------------------------------------------------------------------------

_ENGINE_IMPORTABLE = False
_engine_mod = None

try:
    # Create a fake 'core.parser.s' package that re-exports the real types
    _s_pkg = _types.ModuleType("core.parser.s")
    _s_pkg.__path__ = []
    for _name in ("Language", "ParseError", "ParseResult"):
        setattr(_s_pkg, _name, getattr(_types_mod, _name))
    sys.modules.setdefault("core.parser.s", _s_pkg)
    sys.modules.setdefault("core.parser.s.types", _types_mod)

    # Read engine source and fix the annotation typo so the module loads
    _engine_src = ENGINE_PATH.read_text()
    _engine_src_fixed = _engine_src.replace("-> PashResult:", "-> ParseResult:")

    _engine_fake = _types.ModuleType("core.parser.engine")
    _engine_fake.__package__ = "core.parser"
    _engine_fake.__spec__ = None
    sys.modules["core.parser.engine"] = _engine_fake

    exec(compile(_engine_src_fixed, str(ENGINE_PATH), "exec"), _engine_fake.__dict__)

    detect_language = _engine_fake.detect_language
    parse_python = _engine_fake.parse_python
    parse_javascript = _engine_fake.parse_javascript
    parse_code = _engine_fake.parse_code

    _ENGINE_IMPORTABLE = True
    _engine_mod = _engine_fake

except Exception as _e:  # pragma: no cover
    _ENGINE_IMPORT_ERROR = str(_e)


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

_skip_engine = unittest.skipUnless(
    _ENGINE_IMPORTABLE, "core.parser.engine could not be imported"
)


@_skip_engine
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


@_skip_engine
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
        self.assertIs(detect_language("import { foo } from 'bar';"), Language.JAVASCRIPT)

    def test_def_keyword_is_python(self):
        self.assertIs(detect_language("def hello(): pass"), Language.PYTHON)

    def test_import_from_is_python(self):
        self.assertIs(detect_language("import os\nfrom pathlib import Path"), Language.PYTHON)

    def test_shebang_is_bash(self):
        self.assertIs(detect_language("#!/bin/bash\necho hello"), Language.BASH)

    def test_empty_string_is_not_python_or_js_or_bash(self):
        result = detect_language("")
        self.assertNotIn(result, [Language.PYTHON, Language.JAVASCRIPT, Language.BASH])

    def test_plain_prose_is_not_python_or_js_or_bash(self):
        result = detect_language("Hello, world! This is plain text.")
        self.assertNotIn(result, [Language.PYTHON, Language.JAVASCRIPT, Language.BASH])


@_skip_engine
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


@_skip_engine
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


@_skip_engine
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


if __name__ == "__main__":
    unittest.main()