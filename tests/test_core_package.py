"""
Tests for the core package structure and entry points.

These tests verify that the package can be imported and the basic
structure is correct without requiring external dependencies like
Streamlit or database connections.
"""

import os
import unittest
from unittest.mock import patch


class TestCorePackage(unittest.TestCase):
    """Test core package imports and structure"""

    def test_version_import(self):
        """Test that version can be imported"""
        from core import __version__

        self.assertIsInstance(__version__, str)
        self.assertRegex(__version__, r"^\d+\.\d+\.\d+$")
        self.assertEqual(__version__, "0.2.1")

    def test_cli_module_imports(self):
        """Test that CLI module can be imported"""
        from core.cli import parse_args, configure_logging, main

        self.assertTrue(callable(parse_args))
        self.assertTrue(callable(configure_logging))
        self.assertTrue(callable(main))

    def test_logging_module_imports(self):
        """Test that logging module can be imported"""
        from core.logging import setup_logging, get_logger, StructuredFormatter

        self.assertTrue(callable(setup_logging))
        self.assertTrue(callable(get_logger))
        self.assertTrue(hasattr(StructuredFormatter, "format"))

    def test_cli_parse_args_defaults(self):
        """Test CLI argument parsing with defaults"""
        from core.cli import parse_args

        args = parse_args([])

        # Check default values
        self.assertEqual(args.host, os.environ.get("HOST", "localhost"))
        self.assertEqual(args.port, int(os.environ.get("PORT", "7860")))
        self.assertEqual(args.log_level, os.environ.get("LOG_LEVEL", "INFO"))
        self.assertFalse(args.no_browser)

    def test_cli_parse_args_custom(self):
        """Test CLI argument parsing with custom values"""
        from core.cli import parse_args

        args = parse_args(
            [
                "--host",
                "0.0.0.0",
                "--port",
                "8501",
                "--log-level",
                "DEBUG",
                "--no-browser",
            ]
        )

        self.assertEqual(args.host, "0.0.0.0")
        self.assertEqual(args.port, 8501)
        self.assertEqual(args.log_level, "DEBUG")
        self.assertTrue(args.no_browser)

    def test_cli_version_flag(self):
        """Test that version flag works"""
        from core.cli import parse_args
        from core import __version__

        with self.assertRaises(SystemExit) as cm:
            parse_args(["--version"])

        self.assertEqual(cm.exception.code, 0)

    def test_logging_setup(self):
        """Test logging configuration"""
        from core.logging import setup_logging
        import logging

        # Setup with INFO level
        setup_logging("INFO")

        # Check root logger level
        root_logger = logging.getLogger()
        self.assertEqual(root_logger.level, logging.INFO)

    def test_logging_formatter(self):
        """Test structured formatter"""
        from core.logging import StructuredFormatter
        import logging

        formatter = StructuredFormatter(
            use_color=False, fmt="%(levelname)s - %(message)s"
        )
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        formatted = formatter.format(record)
        self.assertIn("Test message", formatted)

    def test_app_file_exists(self):
        """Test that app.py exists for backward compatibility"""
        import os

        app_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app.py")
        self.assertTrue(os.path.exists(app_path))

        # Verify it imports from core.server
        with open(app_path) as f:
            content = f.read()
            self.assertIn("from core.server import run_app", content)

    @patch.dict(os.environ, {"LOG_LEVEL": "DEBUG"}, clear=False)
    def test_environment_variable_integration(self):
        """Test that environment variables are respected"""
        from core.cli import parse_args

        args = parse_args([])
        self.assertEqual(args.log_level, "DEBUG")


class TestPackageMetadata(unittest.TestCase):
    """Test package metadata and configuration"""

    def test_pyproject_toml_exists(self):
        """Test that pyproject.toml exists and is readable"""
        import os

        pyproject_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "pyproject.toml"
        )
        self.assertTrue(os.path.exists(pyproject_path))

    def test_readme_exists(self):
        """Test that README.md exists"""
        import os

        readme_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "README.md"
        )
        self.assertTrue(os.path.exists(readme_path))

    def test_changelog_exists(self):
        """Test that CHANGELOG.md exists"""
        import os

        changelog_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "CHANGELOG.md"
        )
        self.assertTrue(os.path.exists(changelog_path))

    def test_core_package_structure(self):
        """Test that core package has expected structure"""
        import os

        core_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "core")

        self.assertTrue(os.path.exists(core_path))
        self.assertTrue(os.path.exists(os.path.join(core_path, "__init__.py")))
        self.assertTrue(os.path.exists(os.path.join(core_path, "cli.py")))
        self.assertTrue(os.path.exists(os.path.join(core_path, "server.py")))
        self.assertTrue(os.path.exists(os.path.join(core_path, "logging.py")))



class TestRedactUrl(unittest.TestCase):
    """Tests for core.logging.redact_url added in 0.2.1."""

    def _redact(self, value):
        from core.logging import redact_url
        return redact_url(value)

    # ── falsy / no-netloc inputs ────────────────────────────────────────────

    def test_empty_string_returned_unchanged(self):
        self.assertEqual(self._redact(""), "")

    def test_none_returned_unchanged(self):
        # redact_url is specified to return the input if it is falsy
        self.assertIsNone(self._redact(None))

    def test_plain_string_without_scheme_returned_unchanged(self):
        # No netloc → no redaction
        self.assertEqual(self._redact("not_a_url"), "not_a_url")

    def test_path_only_string_returned_unchanged(self):
        self.assertEqual(self._redact("/etc/passwd"), "/etc/passwd")

    # ── URLs without credentials ────────────────────────────────────────────

    def test_url_without_credentials_unchanged(self):
        url = "postgresql://localhost/mydb"
        self.assertEqual(self._redact(url), url)

    def test_url_with_host_and_port_no_credentials_unchanged(self):
        url = "postgresql://db.example.com:5432/mydb"
        self.assertEqual(self._redact(url), url)

    # ── credential masking ──────────────────────────────────────────────────

    def test_username_and_password_are_masked(self):
        url = "postgresql://alice:s3cr3t@localhost/mydb"
        result = self._redact(url)
        self.assertIn("***:***@", result)
        self.assertNotIn("alice", result)
        self.assertNotIn("s3cr3t", result)

    def test_scheme_is_preserved_after_redaction(self):
        url = "postgresql://user:pass@db.example.com/prod"
        result = self._redact(url)
        self.assertTrue(result.startswith("postgresql://"))

    def test_host_is_preserved_after_redaction(self):
        url = "postgresql://user:pass@db.example.com/prod"
        result = self._redact(url)
        self.assertIn("db.example.com", result)

    def test_path_is_preserved_after_redaction(self):
        url = "postgresql://user:pass@db.example.com/prod"
        result = self._redact(url)
        self.assertTrue(result.endswith("/prod"))

    def test_port_is_preserved_after_redaction(self):
        url = "postgresql://user:pass@db.example.com:5432/prod"
        result = self._redact(url)
        self.assertIn(":5432", result)
        self.assertIn("***:***@", result)

    def test_username_only_is_masked(self):
        # urllib.parse parses "user@host" as username="user", password=None
        url = "postgresql://user@localhost/mydb"
        result = self._redact(url)
        self.assertIn("***:***@", result)
        self.assertNotIn("user@", result)

    def test_query_string_preserved(self):
        url = "https://user:pass@example.com/path?a=1&b=2"
        result = self._redact(url)
        self.assertIn("?a=1&b=2", result)
        self.assertNotIn("user", result)

    def test_fragment_preserved(self):
        url = "https://user:pass@example.com/path?q=x#frag"
        result = self._redact(url)
        self.assertIn("#frag", result)
        self.assertNotIn("pass", result)

    def test_mysql_connection_string(self):
        url = "mysql://root:hunter2@127.0.0.1:3306/testdb"
        result = self._redact(url)
        self.assertNotIn("root", result)
        self.assertNotIn("hunter2", result)
        self.assertIn("127.0.0.1", result)
        self.assertIn("3306", result)

    def test_redis_url_with_password_only(self):
        # Redis often omits the username: "redis://:password@host"
        url = "redis://:secrettoken@cache.internal:6379/0"
        result = self._redact(url)
        self.assertNotIn("secrettoken", result)
        self.assertIn("***:***@", result)

    def test_ipv6_host_with_credentials(self):
        url = "postgresql://user:pass@[::1]:5432/mydb"
        result = self._redact(url)
        self.assertIn("***:***@", result)
        self.assertNotIn("user", result)
        self.assertNotIn("pass", result)
        # IPv6 address must still be present
        self.assertIn("::1", result)

    def test_username_not_in_cleartext_regression(self):
        """Regression: v0.2.0 leaked the username in clear text; v0.2.1 must not."""
        url = "postgresql://dbuser:dbpass@prod-db:5432/appdb"
        result = self._redact(url)
        self.assertNotIn("dbuser", result)
        self.assertNotIn("dbpass", result)

    def test_masked_marker_format(self):
        """The redaction marker must be exactly ***:***@host."""
        url = "https://u:p@example.com/"
        result = self._redact(url)
        self.assertIn("***:***@example.com", result)


if __name__ == "__main__":
    unittest.main()
