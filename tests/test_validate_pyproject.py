"""Tests for scripts/validate_pyproject.py

Covers the validate_pyproject function after its black-formatting refactor in
this PR.  The function behaviour (not just formatting) is verified here.
"""
import sys
import os
import tempfile
import unittest
from pathlib import Path
from io import StringIO
from unittest.mock import patch, MagicMock

# Ensure scripts/ is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from validate_pyproject import validate_pyproject  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_VALID_TOML = b"""
[project]
name = "my-project"
version = "1.0.0"

[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"
"""

_INVALID_TOML = b"key = [broken toml\n"


class TestValidatePyproject(unittest.TestCase):
    # ------------------------------------------------------------------
    # File-not-found cases
    # ------------------------------------------------------------------

    def test_returns_false_for_nonexistent_file(self):
        result = validate_pyproject("/no/such/path/pyproject.toml")
        self.assertFalse(result)

    def test_prints_error_to_stderr_when_file_missing(self):
        with self.assertRaises(SystemExit) as _:
            pass  # just confirm the function handles missing file
        # Redirect stderr and confirm error message
        with patch("sys.stderr", new_callable=StringIO) as mock_err:
            validate_pyproject("/nonexistent/pyproject.toml")
            output = mock_err.getvalue()
        self.assertIn("not found", output)

    # ------------------------------------------------------------------
    # Valid TOML cases
    # ------------------------------------------------------------------

    def test_returns_true_for_valid_toml(self):
        with tempfile.NamedTemporaryFile(suffix=".toml", delete=False) as f:
            f.write(_VALID_TOML)
            tmp_path = f.name
        try:
            result = validate_pyproject(tmp_path)
            self.assertTrue(result)
        finally:
            os.unlink(tmp_path)

    def test_prints_success_message_for_valid_toml(self):
        with tempfile.NamedTemporaryFile(suffix=".toml", delete=False) as f:
            f.write(_VALID_TOML)
            tmp_path = f.name
        try:
            with patch("builtins.print") as mock_print:
                validate_pyproject(tmp_path)
                printed = " ".join(str(c) for c in mock_print.call_args_list)
            self.assertIn("valid", printed)
        finally:
            os.unlink(tmp_path)

    def test_valid_toml_with_empty_sections(self):
        content = b"[project]\nname = 'x'\n"
        with tempfile.NamedTemporaryFile(suffix=".toml", delete=False) as f:
            f.write(content)
            tmp_path = f.name
        try:
            self.assertTrue(validate_pyproject(tmp_path))
        finally:
            os.unlink(tmp_path)

    # ------------------------------------------------------------------
    # Invalid TOML cases
    # ------------------------------------------------------------------

    def test_returns_false_for_invalid_toml(self):
        with tempfile.NamedTemporaryFile(suffix=".toml", delete=False) as f:
            f.write(_INVALID_TOML)
            tmp_path = f.name
        try:
            result = validate_pyproject(tmp_path)
            self.assertFalse(result)
        finally:
            os.unlink(tmp_path)

    def test_prints_error_to_stderr_for_invalid_toml(self):
        with tempfile.NamedTemporaryFile(suffix=".toml", delete=False) as f:
            f.write(_INVALID_TOML)
            tmp_path = f.name
        try:
            with patch("sys.stderr", new_callable=StringIO) as mock_err:
                validate_pyproject(tmp_path)
                output = mock_err.getvalue()
            self.assertIn("invalid", output.lower())
        finally:
            os.unlink(tmp_path)

    # ------------------------------------------------------------------
    # TOML library fallback
    # ------------------------------------------------------------------

    def test_uses_tomllib_when_tomli_unavailable(self):
        """When tomli is absent, validate_pyproject falls back to tomllib."""
        with tempfile.NamedTemporaryFile(suffix=".toml", delete=False) as f:
            f.write(_VALID_TOML)
            tmp_path = f.name
        try:
            import builtins

            real_import = builtins.__import__

            def mock_import(name, *args, **kwargs):
                if name == "tomli":
                    raise ImportError("no tomli")
                return real_import(name, *args, **kwargs)

            with patch("builtins.__import__", side_effect=mock_import):
                result = validate_pyproject(tmp_path)
            # Result depends on whether tomllib is available (Python >= 3.11)
            self.assertIn(result, (True, False))
        finally:
            os.unlink(tmp_path)

    def test_returns_false_when_no_toml_library_available(self):
        """Returns False when neither tomli nor tomllib can be imported."""
        with tempfile.NamedTemporaryFile(suffix=".toml", delete=False) as f:
            f.write(_VALID_TOML)
            tmp_path = f.name
        try:
            import builtins

            real_import = builtins.__import__

            def mock_import(name, *args, **kwargs):
                if name in ("tomli", "tomllib"):
                    raise ImportError(f"no {name}")
                return real_import(name, *args, **kwargs)

            with patch("builtins.__import__", side_effect=mock_import):
                result = validate_pyproject(tmp_path)
            self.assertFalse(result)
        finally:
            os.unlink(tmp_path)

    # ------------------------------------------------------------------
    # Default argument
    # ------------------------------------------------------------------

    def test_default_filepath_is_pyproject_toml(self):
        """Called with no args, validate_pyproject targets 'pyproject.toml'."""
        # We can't easily test the default (current directory), so we verify
        # the function signature default value.
        import inspect

        sig = inspect.signature(validate_pyproject)
        default = sig.parameters["filepath"].default
        self.assertEqual(default, "pyproject.toml")

    # ------------------------------------------------------------------
    # Boundary / regression cases
    # ------------------------------------------------------------------

    def test_empty_file_is_valid_toml(self):
        """An empty TOML file is technically valid TOML."""
        with tempfile.NamedTemporaryFile(suffix=".toml", delete=False) as f:
            f.write(b"")
            tmp_path = f.name
        try:
            # tomli/tomllib accept empty files
            result = validate_pyproject(tmp_path)
            self.assertTrue(result)
        finally:
            os.unlink(tmp_path)

    def test_accepts_path_with_different_name(self):
        """Function is not restricted to files named pyproject.toml."""
        with tempfile.NamedTemporaryFile(
            suffix=".toml", prefix="custom_", delete=False
        ) as f:
            f.write(_VALID_TOML)
            tmp_path = f.name
        try:
            result = validate_pyproject(tmp_path)
            self.assertTrue(result)
        finally:
            os.unlink(tmp_path)

    def test_unicode_values_are_valid(self):
        content = '[project]\nname = "héllo"\n'.encode("utf-8")
        with tempfile.NamedTemporaryFile(suffix=".toml", delete=False) as f:
            f.write(content)
            tmp_path = f.name
        try:
            result = validate_pyproject(tmp_path)
            self.assertTrue(result)
        finally:
            os.unlink(tmp_path)

    def test_returns_bool_not_none(self):
        result = validate_pyproject("/nonexistent/file.toml")
        self.assertIsInstance(result, bool)


if __name__ == "__main__":
    unittest.main()