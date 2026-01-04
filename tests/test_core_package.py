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
        self.assertEqual(__version__, "0.2.0")

    def test_cli_module_imports(self):
        """Test that CLI module can be imported"""
        from core.cli import configure_logging, main, parse_args

        self.assertTrue(callable(parse_args))
        self.assertTrue(callable(configure_logging))
        self.assertTrue(callable(main))

    def test_logging_module_imports(self):
        """Test that logging module can be imported"""
        from core.logging import StructuredFormatter, get_logger, setup_logging

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
        from core import __version__
        from core.cli import parse_args

        with self.assertRaises(SystemExit) as cm:
            parse_args(["--version"])

        self.assertEqual(cm.exception.code, 0)

    def test_logging_setup(self):
        """Test logging configuration"""
        import logging

        from core.logging import setup_logging

        # Setup with INFO level
        setup_logging("INFO")

        # Check root logger level
        root_logger = logging.getLogger()
        self.assertEqual(root_logger.level, logging.INFO)

    def test_logging_formatter(self):
        """Test structured formatter"""
        import logging

        from core.logging import StructuredFormatter

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


if __name__ == "__main__":
    unittest.main()
