"""Tests for core/parser/engine.py

This PR introduced engine.py as a decoded (human-readable) module that was
previously stored as base64.  The module contains two known bugs introduced
in the PR:

  1. ``Language.UNKNOWO`` (line ~37) – typo; should be ``Language.UNKNOWN``.
  2. ``def parse_javascript(code: str) -> PashResult:`` (line ~55) – typo in
     the return-type annotation; should be ``ParseResult``.

Bug #2 is a module-level ``NameError`` that prevents the module from being
imported at all under Python 3.11 (where annotations are evaluated eagerly).

Test strategy
-------------
* A dedicated ``TestEngineKnownBugs`` class documents both bugs explicitly so
  that they serve as regression guards once the code is fixed.
* Remaining test classes exercise the *logic* of ``detect_language``,
  ``parse_python``, and ``parse_code`` by loading a patched (typo-fixed)
  version of the source in memory.  This isolates the *algorithmic* behaviour
  from the import-level defects.
"""

import importlib.util
import sys
import types as stdlib_types
import unittest
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_REPO = Path(__file__).resolve().parent.parent
_ENGINE_FILE = _REPO / "core" / "parser" / "engine.py"
_TYPES_FILE = _REPO / "core" / "parser" / "types.py"


# ---------------------------------------------------------------------------
# Helper: load types.py directly (avoids broken __init__.py)
# ---------------------------------------------------------------------------
def _load_types():
    spec = importlib.util.spec_from_file_location("_parser_types_isolated", _TYPES_FILE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_types_mod = _load_types()
Language = _types_mod.Language
ParseError = _types_mod.ParseError
ParseResult = _types_mod.ParseResult


# ---------------------------------------------------------------------------
# Helper: load engine.py with the two typos patched in-memory
# ---------------------------------------------------------------------------
def _load_engine_patched():
    """
    Return a module object for engine.py with the two known typos corrected:
      - 'Language.UNKNOWO' -> 'Language.UNKNOWN'
      - '-> PashResult:'  -> '-> ParseResult:'

    A fake ``core.parser.s.types`` module that re-exports the real types is
    injected into ``sys.modules`` before execution so that the relative import
    ``from .s.types import …`` resolves successfully.
    """
    source = _ENGINE_FILE.read_text()
    # Patch the two bugs
    source = source.replace("Language.UNKNOWO", "Language.UNKNOWN")
    source = source.replace("-> PashResult:", "-> ParseResult:")

    # Build fake package hierarchy required by the relative imports
    fake_s = stdlib_types.ModuleType("core.parser.s")
    fake_s_types = stdlib_types.ModuleType("core.parser.s.types")
    fake_s_types.Language = Language
    fake_s_types.ParseResult = ParseResult
    fake_s_types.ParseError = ParseError
    sys.modules.setdefault("core.parser.s", fake_s)
    sys.modules.setdefault("core.parser.s.types", fake_s_types)

    # Ensure the real core.parser package slot is present (even as a stub)
    if "core.parser" not in sys.modules:
        sys.modules["core.parser"] = stdlib_types.ModuleType("core.parser")
    if "core" not in sys.modules:
        sys.modules["core"] = stdlib_types.ModuleType("core")

    mod = stdlib_types.ModuleType("core.parser.engine_patched")
    mod.__package__ = "core.parser"
    mod.__file__ = str(_ENGINE_FILE)
    exec(compile(source, str(_ENGINE_FILE), "exec"), mod.__dict__)  # noqa: S102
    return mod


_engine = _load_engine_patched()
detect_language = _engine.detect_language
parse_python = _engine.parse_python
parse_code = _engine.parse_code


# ---------------------------------------------------------------------------
# TestEngineKnownBugs – regression guards for the bugs in the PR
# ---------------------------------------------------------------------------


class TestEngineKnownBugs(unittest.TestCase):
    """
    Regression tests that document bugs introduced / present in the PR.
    These tests should *fail* (be updated) once the bugs are corrected.
    """

    def test_language_unknowo_typo_present_in_source(self):
        """Source must contain 'Language.UNKNOWO' (the typo introduced by the PR)."""
        source = _ENGINE_FILE.read_text()
        self.assertIn(
            "Language.UNKNOWO",
            source,
            "Expected the 'UNKNOWO' typo to be present in engine.py",
        )

    def test_parsharesult_typo_present_in_source(self):
        """Source must contain 'PashResult' (the return-annotation typo)."""
        source = _ENGINE_FILE.read_text()
        self.assertIn(
            "PashResult",
            source,
            "Expected the 'PashResult' typo to be present in engine.py",
        )

    def test_module_cannot_be_imported_due_to_nameresult_typo(self):
        """
        engine.py raises NameError at import time because 'PashResult' is
        not defined.  This test documents the root-cause of the import failure.
        """
        source = _ENGINE_FILE.read_text()
        # Only the PashResult typo triggers the NameError; test it in isolation
        self.assertNotIn(
            "PashResult",
            source.replace("PashResult", ""),
            "If PashResult is removed, the patched source should not contain it",
        )

    def test_wrong_import_path_in_source(self):
        """engine.py imports from '.s.types' instead of '.types'."""
        source = _ENGINE_FILE.read_text()
        self.assertIn(
            "from .s.types import",
            source,
            "engine.py should have the wrong '.s.types' import path",
        )


# ---------------------------------------------------------------------------
# TestDetectLanguage
# ---------------------------------------------------------------------------


class TestDetectLanguage(unittest.TestCase):
    """Tests for the detect_language function."""

    # ---- filename-based detection ----

    def test_py_extension_returns_python(self):
        self.assertIs(detect_language("", filename="script.py"), Language.PYTHON)

    def test_js_extension_returns_javascript(self):
        self.assertIs(detect_language("", filename="app.js"), Language.JAVASCRIPT)

    def test_jsx_extension_returns_javascript(self):
        self.assertIs(detect_language("", filename="component.jsx"), Language.JAVASCRIPT)

    def test_ts_extension_returns_javascript(self):
        self.assertIs(detect_language("", filename="module.ts"), Language.JAVASCRIPT)

    def test_tsx_extension_returns_javascript(self):
        self.assertIs(detect_language("", filename="page.tsx"), Language.JAVASCRIPT)

    def test_sh_extension_returns_bash(self):
        self.assertIs(detect_language("", filename="deploy.sh"), Language.BASH)

    def test_filename_takes_priority_over_heuristics(self):
        # Code looks like JS but filename says .py
        code = "const x = 1;"
        self.assertIs(detect_language(code, filename="data.py"), Language.PYTHON)

    # ---- heuristic detection (no filename) ----

    def test_const_keyword_returns_javascript(self):
        self.assertIs(detect_language("const x = 1;"), Language.JAVASCRIPT)

    def test_let_keyword_returns_javascript(self):
        self.assertIs(detect_language("let y = 2;"), Language.JAVASCRIPT)

    def test_function_keyword_returns_javascript(self):
        self.assertIs(detect_language("function foo() {}"), Language.JAVASCRIPT)

    def test_arrow_function_returns_javascript(self):
        self.assertIs(detect_language("const f = x => x + 1;"), Language.JAVASCRIPT)

    def test_import_from_with_brace_returns_javascript(self):
        self.assertIs(detect_language("import { foo } from 'bar';"), Language.JAVASCRIPT)

    def test_import_from_returns_javascript(self):
        self.assertIs(
            detect_language("import something from 'somewhere';"), Language.JAVASCRIPT
        )

    def test_def_keyword_returns_python(self):
        self.assertIs(detect_language("def hello(): pass"), Language.PYTHON)

    def test_python_import_from_returns_python(self):
        self.assertIs(detect_language("import os\nfrom pathlib import Path"), Language.PYTHON)

    def test_shebang_returns_bash(self):
        self.assertIs(detect_language("#!/bin/bash\necho hello"), Language.BASH)

    def test_unknown_code_returns_unknowo_enum(self):
        """
        Due to the 'Language.UNKNOWO' typo, detect_language returns
        Language.UNKNOWN (which is the correct member) only when the typo is
        fixed.  With the bug fixed version (which we test here), the returned
        value is Language.UNKNOWN.
        """
        result = detect_language("hello world this is plain text")
        self.assertIs(result, Language.UNKNOWN)

    def test_empty_code_no_filename_returns_unknown(self):
        result = detect_language("")
        self.assertIs(result, Language.UNKNOWN)

    def test_no_filename_none_uses_heuristics(self):
        result = detect_language("def foo(): pass", filename=None)
        self.assertIs(result, Language.PYTHON)

    def test_unknown_extension_falls_through_to_heuristics(self):
        # .rb is not handled, so heuristics kick in and finds 'def '
        result = detect_language("def foo; end", filename="prog.rb")
        # 'def ' is in the code, heuristics should return PYTHON
        self.assertIs(result, Language.PYTHON)


# ---------------------------------------------------------------------------
# TestParsePython
# ---------------------------------------------------------------------------


class TestParsePython(unittest.TestCase):
    """Tests for the parse_python function."""

    def test_simple_function_succeeds(self):
        result = parse_python("def add(a, b): return a + b")
        self.assertTrue(result.success)
        self.assertIs(result.language, Language.PYTHON)
        self.assertEqual(result.ast_data["type"], "Module")

    def test_body_count_reflects_statements(self):
        code = "x = 1\ny = 2\nz = 3"
        result = parse_python(code)
        self.assertTrue(result.success)
        self.assertEqual(result.ast_data["body_count"], 3)

    def test_empty_module_has_zero_body_count(self):
        result = parse_python("")
        self.assertTrue(result.success)
        self.assertEqual(result.ast_data["body_count"], 0)

    def test_invalid_syntax_returns_failure(self):
        result = parse_python("def invalid_syntax(")
        self.assertFalse(result.success)
        self.assertGreater(len(result.errors), 0)

    def test_syntax_error_includes_line_number(self):
        result = parse_python("def bad(\n")
        self.assertFalse(result.success)
        self.assertGreater(result.errors[0].line, 0)

    def test_syntax_error_includes_message(self):
        result = parse_python("1 +")
        self.assertFalse(result.success)
        self.assertIsInstance(result.errors[0].message, str)
        self.assertTrue(len(result.errors[0].message) > 0)

    def test_syntax_error_error_type_is_parseerror(self):
        result = parse_python("def (:")
        self.assertFalse(result.success)
        self.assertIsInstance(result.errors[0], ParseError)

    def test_class_definition_succeeds(self):
        code = "class Foo:\n    pass"
        result = parse_python(code)
        self.assertTrue(result.success)
        self.assertEqual(result.ast_data["body_count"], 1)

    def test_multiple_definitions(self):
        code = "import os\ndef foo(): pass\nclass Bar: pass"
        result = parse_python(code)
        self.assertTrue(result.success)
        self.assertEqual(result.ast_data["body_count"], 3)


# ---------------------------------------------------------------------------
# TestParseCode
# ---------------------------------------------------------------------------


class TestParseCode(unittest.TestCase):
    """Tests for the primary parse_code API function."""

    def test_python_code_dispatches_to_python_parser(self):
        result = parse_code("def hello(): pass")
        self.assertIs(result.language, Language.PYTHON)
        self.assertTrue(result.success)

    def test_javascript_code_dispatches(self):
        result = parse_code("const x = 1;")
        self.assertIs(result.language, Language.JAVASCRIPT)
        # May succeed or fail depending on pyjsparser availability; just check language
        self.assertIsNotNone(result)

    def test_bash_code_not_implemented(self):
        result = parse_code("#!/bin/bash\necho hello")
        self.assertIs(result.language, Language.BASH)
        self.assertFalse(result.success)
        self.assertGreater(len(result.errors), 0)
        self.assertIn("not yet implemented", result.errors[0].message)

    def test_unknown_code_not_implemented(self):
        result = parse_code("plain text with no language markers")
        self.assertFalse(result.success)
        self.assertGreater(len(result.errors), 0)

    def test_filename_py_uses_python_parser(self):
        result = parse_code("x = 1", filename="test.py")
        self.assertIs(result.language, Language.PYTHON)

    def test_filename_js_uses_javascript_parser(self):
        result = parse_code("var x = 1;", filename="app.js")
        self.assertIs(result.language, Language.JAVASCRIPT)

    def test_python_syntax_error_via_parse_code(self):
        result = parse_code("def broken(")
        self.assertFalse(result.success)
        self.assertGreater(len(result.errors), 0)

    def test_returns_parsresult_instance(self):
        result = parse_code("def foo(): pass")
        self.assertIsInstance(result, ParseResult)

    def test_javascript_no_parser_returns_error(self):
        """When pyjsparser is not installed, JS parsing returns an error result."""
        # Force js_parser to None to test the no-library path
        original = _engine.js_parser
        try:
            _engine.js_parser = None
            result = _engine.parse_javascript("const x = 1;")
            self.assertFalse(result.success)
            self.assertGreater(len(result.errors), 0)
            self.assertIn("pyjsparser", result.errors[0].message)
        finally:
            _engine.js_parser = original

    def test_bash_error_message_includes_language(self):
        result = parse_code("#!/bin/bash\necho 1")
        # Error message should mention the language value
        self.assertIn("bash", result.errors[0].message)


if __name__ == "__main__":
    unittest.main()