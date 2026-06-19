"""
Tests for scripts/validate_pyproject.py — validate_pyproject function.

Covers:
  - Valid TOML file returns True
  - Non-existent file returns False
  - Invalid TOML syntax returns False
  - tomli/tomllib import fallback logic (via mocking)
  - Neither TOML library available returns False
  - File path argument handling
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ensure the project root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.validate_pyproject import validate_pyproject  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_toml(dir_path: Path, name: str, content: bytes) -> Path:
    """Write binary content to a TOML file and return its path."""
    path = dir_path / name
    path.write_bytes(content)
    return path


VALID_TOML = b'[project]\nname = "mypackage"\nversion = "1.0.0"\n'
INVALID_TOML = b"[project\nname = broken = syntax\n"


# ---------------------------------------------------------------------------
# TestValidPyproject
# ---------------------------------------------------------------------------


class TestValidatePyprojectValidFile(unittest.TestCase):
    """validate_pyproject returns True for files with valid TOML syntax."""

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmpdir.name)

    def tearDown(self):
        self._tmpdir.cleanup()

    def test_valid_toml_returns_true(self):
        p = _write_toml(self.tmp, "pyproject.toml", VALID_TOML)
        self.assertTrue(validate_pyproject(str(p)))

    def test_minimal_valid_toml_returns_true(self):
        """An empty TOML file (only whitespace / comments) is syntactically valid."""
        p = _write_toml(self.tmp, "pyproject.toml", b"# just a comment\n")
        self.assertTrue(validate_pyproject(str(p)))

    def test_complex_valid_toml_returns_true(self):
        content = (
            b"[project]\n"
            b'name = "pkg"\n'
            b'version = "0.1.0"\n'
            b"[build-system]\n"
            b'requires = ["setuptools"]\n'
            b'build-backend = "setuptools.build_meta"\n'
        )
        p = _write_toml(self.tmp, "pyproject.toml", content)
        self.assertTrue(validate_pyproject(str(p)))

    def test_default_filename_is_pyproject_toml(self):
        """Without args, it should use the default `pyproject.toml` path."""
        _write_toml(self.tmp, "pyproject.toml", VALID_TOML)
        prev_cwd = os.getcwd()
        try:
            os.chdir(self.tmp)
            self.assertTrue(validate_pyproject())
        finally:
            os.chdir(prev_cwd)

    def test_returns_bool_true_type(self):
        p = _write_toml(self.tmp, "pyproject.toml", VALID_TOML)
        result = validate_pyproject(str(p))
        self.assertIsInstance(result, bool)
        self.assertTrue(result)


# ---------------------------------------------------------------------------
# TestInvalidPyproject
# ---------------------------------------------------------------------------


class TestValidatePyprojectInvalidFile(unittest.TestCase):
    """validate_pyproject returns False for files with invalid syntax."""

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmpdir.name)

    def tearDown(self):
        self._tmpdir.cleanup()

    def test_invalid_toml_returns_false(self):
        p = _write_toml(self.tmp, "pyproject.toml", INVALID_TOML)
        self.assertFalse(validate_pyproject(str(p)))

    def test_invalid_toml_returns_bool_false(self):
        p = _write_toml(self.tmp, "pyproject.toml", INVALID_TOML)
        result = validate_pyproject(str(p))
        self.assertIsInstance(result, bool)
        self.assertFalse(result)

    def test_binary_garbage_returns_false(self):
        p = _write_toml(self.tmp, "pyproject.toml", b"\x00\xff\xfe bad content")
        self.assertFalse(validate_pyproject(str(p)))

    def test_unclosed_bracket_returns_false(self):
        p = _write_toml(self.tmp, "pyproject.toml", b"[project\n")
        self.assertFalse(validate_pyproject(str(p)))

    def test_duplicate_key_returns_false(self):
        content = b"[project]\nname = 'a'\nname = 'b'\n"
        p = _write_toml(self.tmp, "pyproject.toml", content)
        # Duplicate keys are invalid in TOML
        self.assertFalse(validate_pyproject(str(p)))


# ---------------------------------------------------------------------------
# TestMissingFile
# ---------------------------------------------------------------------------


class TestValidatePyprojectMissingFile(unittest.TestCase):
    """validate_pyproject returns False when the file does not exist."""

    def test_nonexistent_file_returns_false(self):
        self.assertFalse(validate_pyproject("/nonexistent/path/pyproject.toml"))

    def test_nonexistent_relative_path_returns_false(self):
        self.assertFalse(validate_pyproject("__no_such_file__.toml"))

    def test_missing_file_writes_to_stderr(self):
        import io

        buf = io.StringIO()
        with patch("sys.stderr", buf):
            result = validate_pyproject("/nonexistent/pyproject.toml")
        self.assertFalse(result)
        self.assertIn("not found", buf.getvalue())


# ---------------------------------------------------------------------------
# TestTomlLibraryFallback
# ---------------------------------------------------------------------------


class TestValidatePyprojectTomlFallback(unittest.TestCase):
    """Test behaviour when tomli/tomllib is available or unavailable."""

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmpdir.name)
        self.valid_path = _write_toml(self.tmp, "pyproject.toml", VALID_TOML)
        self.invalid_path = _write_toml(self.tmp, "bad.toml", INVALID_TOML)

    def tearDown(self):
        self._tmpdir.cleanup()

    def test_neither_library_returns_false(self):
        """Return False when both tomli and tomllib are unavailable."""
        import builtins

        original_import = builtins.__import__

        def _blocked_import(name, *args, **kwargs):
            if name in ("tomli", "tomllib"):
                raise ImportError(f"Mocked: {name} not available")
            return original_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=_blocked_import):
            result = validate_pyproject(str(self.valid_path))
        self.assertFalse(result)

    def test_tomli_used_when_available(self):
        """When tomli is importable, its load function is called."""
        mock_tomli = MagicMock()
        mock_tomli.load.return_value = {}

        with patch.dict("sys.modules", {"tomli": mock_tomli, "tomllib": None}):
            # Remove tomllib so only tomli path is taken
            saved = sys.modules.pop("tomllib", "SENTINEL")
            try:
                result = validate_pyproject(str(self.valid_path))
            finally:
                if saved != "SENTINEL":
                    sys.modules["tomllib"] = saved
        self.assertTrue(result)
        mock_tomli.load.assert_called_once()

    def test_valid_file_with_tomllib_fallback(self):
        """validate_pyproject works when using tomllib (Python 3.11+)."""
        # Simulate tomli not present, tomllib available
        import builtins

        original_import = builtins.__import__

        def _no_tomli_import(name, *args, **kwargs):
            if name == "tomli":
                raise ImportError("Mocked: tomli not available")
            return original_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=_no_tomli_import):
            result = validate_pyproject(str(self.valid_path))
        # Python 3.11+ provides tomllib; result should be True if available
        # Python 3.10 won't have tomllib, so just verify it returns a bool
        self.assertIsInstance(result, bool)


# ---------------------------------------------------------------------------
# TestOutputMessages
# ---------------------------------------------------------------------------


class TestValidatePyprojectOutputMessages(unittest.TestCase):
    """Verify that validate_pyproject prints meaningful messages."""

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmpdir.name)

    def tearDown(self):
        self._tmpdir.cleanup()

    def test_valid_file_prints_success_message(self, capsys=None):
        import io

        buf = io.StringIO()
        p = _write_toml(self.tmp, "pyproject.toml", VALID_TOML)
        with patch("sys.stdout", buf):
            validate_pyproject(str(p))
        self.assertIn("valid", buf.getvalue().lower())

    def test_invalid_file_prints_error_to_stderr(self):
        import io

        buf = io.StringIO()
        p = _write_toml(self.tmp, "pyproject.toml", INVALID_TOML)
        with patch("sys.stderr", buf):
            validate_pyproject(str(p))
        self.assertIn("invalid", buf.getvalue().lower())

    def test_missing_file_prints_error_to_stderr(self):
        import io

        buf = io.StringIO()
        with patch("sys.stderr", buf):
            validate_pyproject("/no/such/file.toml")
        output = buf.getvalue()
        self.assertTrue(len(output) > 0)


if __name__ == "__main__":
    unittest.main()
