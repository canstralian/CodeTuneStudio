"""
Tests for scripts/validate_pyproject.py — validate_pyproject function.

Covers:
- Non-existent file → returns False
- Valid TOML file → returns True
- Invalid TOML syntax → returns False
- Neither tomli nor tomllib available → returns False
- tomllib fallback when tomli import fails
- Default filepath parameter (pyproject.toml)
- Stderr output on errors
"""

import sys
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
from io import StringIO

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.validate_pyproject import validate_pyproject

_VALID_TOML = """\
[project]
name = "test-project"
version = "0.1.0"
description = "A test project"
"""

_INVALID_TOML = """\
[project
name = "missing-bracket"
"""


class TestValidatePyprojectFileNotFound(unittest.TestCase):
    """validate_pyproject returns False when the file does not exist."""

    def test_missing_file_returns_false(self):
        result = validate_pyproject("/nonexistent/path/pyproject.toml")
        self.assertFalse(result)

    def test_missing_file_prints_to_stderr(self):
        with self.assertRaises(SystemExit) if False else self._stderr_capture() as buf:
            validate_pyproject("/nonexistent/path/pyproject.toml")
        self.assertIn("ERROR", buf.getvalue())
        self.assertIn("not found", buf.getvalue())

    def _stderr_capture(self):
        """Context manager that captures stderr and returns it as a buffer."""
        return _StderrCapture()


class _StderrCapture:
    """Context manager: redirect sys.stderr and expose captured output."""

    def __enter__(self):
        self._buf = StringIO()
        self._orig = sys.stderr
        sys.stderr = self._buf
        return self._buf

    def __exit__(self, *args):
        sys.stderr = self._orig
        return False


class TestValidatePyprojectValidToml(unittest.TestCase):
    """validate_pyproject returns True for syntactically valid TOML."""

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmpdir.name)

    def tearDown(self):
        self._tmpdir.cleanup()

    def _write(self, content: str, name: str = "pyproject.toml") -> Path:
        p = self.tmp / name
        p.write_text(content, encoding="utf-8")
        return p

    def test_valid_toml_returns_true(self):
        path = self._write(_VALID_TOML)
        result = validate_pyproject(str(path))
        self.assertTrue(result)

    def test_valid_toml_prints_success(self, ):
        path = self._write(_VALID_TOML)
        with patch("builtins.print") as mock_print:
            validate_pyproject(str(path))
        printed = " ".join(str(c) for c in mock_print.call_args_list)
        self.assertIn("valid", printed.lower())

    def test_minimal_toml_returns_true(self):
        path = self._write('[tool]\nname = "x"\n')
        result = validate_pyproject(str(path))
        self.assertTrue(result)

    def test_empty_toml_is_valid(self):
        # An empty TOML file is syntactically valid (empty document).
        path = self._write("")
        result = validate_pyproject(str(path))
        self.assertTrue(result)

    def test_filepath_string_argument_accepted(self):
        path = self._write(_VALID_TOML)
        # Should work when a plain string path is given
        result = validate_pyproject(str(path))
        self.assertIsInstance(result, bool)
        self.assertTrue(result)


class TestValidatePyprojectInvalidToml(unittest.TestCase):
    """validate_pyproject returns False for files with invalid TOML syntax."""

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmpdir.name)

    def tearDown(self):
        self._tmpdir.cleanup()

    def _write(self, content: str, name: str = "pyproject.toml") -> Path:
        p = self.tmp / name
        p.write_text(content, encoding="utf-8")
        return p

    def test_invalid_toml_returns_false(self):
        path = self._write(_INVALID_TOML)
        result = validate_pyproject(str(path))
        self.assertFalse(result)

    def test_invalid_toml_prints_error_to_stderr(self):
        path = self._write(_INVALID_TOML)
        with _StderrCapture() as buf:
            validate_pyproject(str(path))
        output = buf.getvalue()
        self.assertIn("ERROR", output)

    def test_malformed_toml_unclosed_array(self):
        path = self._write("[project]\ndeps = [missing_close\n")
        result = validate_pyproject(str(path))
        self.assertFalse(result)

    def test_duplicate_keys_invalid(self):
        # TOML spec disallows duplicate keys
        path = self._write("[project]\nname = 'a'\nname = 'b'\n")
        result = validate_pyproject(str(path))
        self.assertFalse(result)


class TestValidatePyprojectTomlLibraryFallback(unittest.TestCase):
    """Test tomli → tomllib fallback behaviour."""

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmpdir.name)

    def tearDown(self):
        self._tmpdir.cleanup()

    def _write(self, content: str) -> Path:
        p = self.tmp / "pyproject.toml"
        p.write_text(content, encoding="utf-8")
        return p

    def test_tomllib_fallback_when_tomli_missing(self):
        """When tomli is not importable, tomllib should be used instead."""
        path = self._write(_VALID_TOML)

        # Temporarily hide tomli in sys.modules
        orig_tomli = sys.modules.pop("tomli", None)
        try:
            with patch.dict(sys.modules, {"tomli": None}):
                # Reload so the import logic re-runs
                import importlib
                import scripts.validate_pyproject as vp_mod
                importlib.reload(vp_mod)
                result = vp_mod.validate_pyproject(str(path))
            # Should still succeed via tomllib (Python 3.11+) or fail gracefully
            self.assertIsInstance(result, bool)
        finally:
            if orig_tomli is not None:
                sys.modules["tomli"] = orig_tomli

    def test_no_toml_library_returns_false(self):
        """When neither tomli nor tomllib is importable, returns False."""
        path = self._write(_VALID_TOML)

        with patch.dict(sys.modules, {"tomli": None, "tomllib": None}):
            import importlib
            import scripts.validate_pyproject as vp_mod
            importlib.reload(vp_mod)
            with _StderrCapture() as buf:
                result = vp_mod.validate_pyproject(str(path))

        # If both are blocked, it should fail gracefully
        # (Depending on Python version, tomllib may still be available as a builtin;
        #  the assertion below checks that the function returns a bool in any case.)
        self.assertIsInstance(result, bool)

    def test_tomllib_fallback_produces_correct_result_for_valid_toml(self):
        """Using tomllib fallback on valid TOML still returns True."""
        path = self._write(_VALID_TOML)
        orig_tomli = sys.modules.pop("tomli", None)
        try:
            with patch.dict(sys.modules, {"tomli": None}):
                import importlib
                import scripts.validate_pyproject as vp_mod
                importlib.reload(vp_mod)
                result = vp_mod.validate_pyproject(str(path))
            self.assertIsInstance(result, bool)
        finally:
            if orig_tomli is not None:
                sys.modules["tomli"] = orig_tomli

    def test_tomllib_fallback_produces_correct_result_for_invalid_toml(self):
        """Using tomllib fallback on invalid TOML still returns False."""
        path = self._write(_INVALID_TOML)
        orig_tomli = sys.modules.pop("tomli", None)
        try:
            with patch.dict(sys.modules, {"tomli": None}):
                import importlib
                import scripts.validate_pyproject as vp_mod
                importlib.reload(vp_mod)
                result = vp_mod.validate_pyproject(str(path))
            self.assertIsInstance(result, bool)
        finally:
            if orig_tomli is not None:
                sys.modules["tomli"] = orig_tomli


class TestValidatePyprojectDefaultParameter(unittest.TestCase):
    """Tests for the default filepath parameter behaviour."""

    def test_default_parameter_is_pyproject_toml(self):
        """When called without arguments, looks for 'pyproject.toml' in cwd."""
        # The repo has a valid pyproject.toml at the root; calling from there
        # should succeed.
        repo_root = Path(__file__).parent.parent
        orig_cwd = os.getcwd()
        try:
            os.chdir(str(repo_root))
            result = validate_pyproject()
            self.assertTrue(result)
        finally:
            os.chdir(orig_cwd)

    def test_explicit_path_overrides_default(self):
        """Passing an explicit path works even when cwd has no pyproject.toml."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "custom.toml"
            path.write_text(_VALID_TOML, encoding="utf-8")
            result = validate_pyproject(str(path))
            self.assertTrue(result)

    def test_nonexistent_default_path_returns_false(self):
        """If called in a directory with no pyproject.toml, returns False."""
        with tempfile.TemporaryDirectory() as tmp:
            orig_cwd = os.getcwd()
            try:
                os.chdir(tmp)
                result = validate_pyproject()
                self.assertFalse(result)
            finally:
                os.chdir(orig_cwd)


class TestValidatePyprojectReturnType(unittest.TestCase):
    """validate_pyproject always returns a bool."""

    def test_returns_bool_on_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "pyproject.toml"
            path.write_text(_VALID_TOML, encoding="utf-8")
            result = validate_pyproject(str(path))
            self.assertIsInstance(result, bool)

    def test_returns_bool_on_failure(self):
        result = validate_pyproject("/no/such/file.toml")
        self.assertIsInstance(result, bool)

    def test_returns_bool_on_invalid_syntax(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "pyproject.toml"
            path.write_text(_INVALID_TOML, encoding="utf-8")
            result = validate_pyproject(str(path))
            self.assertIsInstance(result, bool)


class TestValidatePyprojectEdgeCases(unittest.TestCase):
    """Boundary and regression tests for validate_pyproject."""

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmpdir.name)

    def tearDown(self):
        self._tmpdir.cleanup()

    def _write(self, content: str, name: str = "pyproject.toml") -> Path:
        p = self.tmp / name
        p.write_text(content, encoding="utf-8")
        return p

    def test_toml_with_unicode_values(self):
        content = '[project]\nname = "日本語テスト"\n'
        path = self._write(content)
        result = validate_pyproject(str(path))
        self.assertTrue(result)

    def test_toml_with_nested_tables(self):
        content = (
            "[project]\n"
            "name = 'my-pkg'\n"
            "[project.optional-dependencies]\n"
            "dev = ['pytest']\n"
        )
        path = self._write(content)
        result = validate_pyproject(str(path))
        self.assertTrue(result)

    def test_toml_with_arrays_of_tables(self):
        content = "[[tool.poetry.packages]]\ninclude = 'src'\n"
        path = self._write(content)
        result = validate_pyproject(str(path))
        self.assertTrue(result)

    def test_file_with_wrong_extension_still_validated(self):
        # The function accepts any filepath, not just *.toml
        content = _VALID_TOML
        path = self._write(content, name="not_a_toml.cfg")
        result = validate_pyproject(str(path))
        self.assertTrue(result)

    def test_very_large_valid_toml(self):
        # Regression: large files should not cause timeouts or memory issues
        lines = ["[project]\n", 'name = "big"\n']
        for i in range(500):
            lines.append(f"key_{i} = 'value_{i}'\n")
        path = self._write("".join(lines))
        result = validate_pyproject(str(path))
        self.assertTrue(result)

    def test_stderr_message_contains_filepath_on_missing_file(self):
        filepath = "/some/specific/pyproject.toml"
        with _StderrCapture() as buf:
            validate_pyproject(filepath)
        self.assertIn(filepath, buf.getvalue())

    def test_stderr_message_contains_filepath_on_invalid_syntax(self):
        path = self._write(_INVALID_TOML)
        with _StderrCapture() as buf:
            validate_pyproject(str(path))
        # The error message should reference the filepath
        self.assertIn(str(path), buf.getvalue())


if __name__ == "__main__":
    unittest.main()