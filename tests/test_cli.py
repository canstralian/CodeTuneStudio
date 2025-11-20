"""
Tests for the CodeTuneStudio CLI module.
"""

import unittest
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest

from codetunestudio import __version__
from codetunestudio.cli import (
    check_database,
    main,
    run_streamlit,
    show_version,
)


class TestCLI(unittest.TestCase):
    """Test suite for CLI functionality."""

    def test_version_import(self) -> None:
        """Test that version can be imported."""
        assert __version__ is not None
        assert isinstance(__version__, str)
        assert len(__version__) > 0

    def test_show_version(self) -> None:
        """Test show_version function."""
        args = MagicMock()
        result = show_version(args)
        assert result == 0

    @patch("subprocess.run")
    def test_run_streamlit_default_args(self, mock_run: MagicMock) -> None:
        """Test run_streamlit with default arguments."""
        args = MagicMock()
        args.port = 7860
        args.host = "0.0.0.0"
        args.headless = False

        mock_run.return_value = MagicMock(returncode=0)
        result = run_streamlit(args)

        assert result == 0
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert "streamlit" in call_args
        assert "run" in call_args
        assert "app.py" in call_args

    @patch("subprocess.run")
    def test_run_streamlit_custom_port(self, mock_run: MagicMock) -> None:
        """Test run_streamlit with custom port."""
        args = MagicMock()
        args.port = 8080
        args.host = "localhost"
        args.headless = True

        mock_run.return_value = MagicMock(returncode=0)
        result = run_streamlit(args)

        assert result == 0
        call_args = mock_run.call_args[0][0]
        assert "8080" in str(call_args)
        assert "localhost" in call_args

    @patch("subprocess.run")
    def test_run_streamlit_failure(self, mock_run: MagicMock) -> None:
        """Test run_streamlit handles failures."""
        args = MagicMock()
        args.port = 7860
        args.host = "0.0.0.0"
        args.headless = False

        mock_run.side_effect = Exception("Test error")
        result = run_streamlit(args)

        assert result == 1

    def test_check_database_success(self) -> None:
        """Test check_database with successful connection."""
        # Mock the import and function call inside check_database
        with patch("builtins.__import__") as mock_import:
            mock_db_check = MagicMock()
            mock_db_check.check_database.return_value = True
            mock_import.return_value = mock_db_check

            args = MagicMock()
            result = check_database(args)
            assert result == 0

    def test_check_database_failure(self) -> None:
        """Test check_database with failed connection."""
        with patch("builtins.__import__") as mock_import:
            mock_db_check = MagicMock()
            mock_db_check.check_database.return_value = False
            mock_import.return_value = mock_db_check

            args = MagicMock()
            result = check_database(args)
            assert result == 1

    def test_check_database_exception(self) -> None:
        """Test check_database handles exceptions."""
        args = MagicMock()
        # Test the exception handling path by catching import errors
        with patch("builtins.__import__", side_effect=ImportError("Test error")):
            result = check_database(args)
            assert result == 1

    def test_main_no_args(self) -> None:
        """Test main with no arguments (should default to streamlit)."""
        with patch("codetunestudio.cli.run_streamlit") as mock_streamlit:
            mock_streamlit.return_value = 0
            result = main([])
            assert result == 0

    def test_main_version_command(self) -> None:
        """Test main with version command."""
        result = main(["version"])
        assert result == 0

    def test_main_help(self) -> None:
        """Test main with help flag."""
        with patch("sys.stdout", new=StringIO()):
            try:
                main(["--help"])
            except SystemExit as e:
                assert e.code == 0

    @patch("codetunestudio.cli.run_streamlit")
    def test_main_streamlit_command(self, mock_streamlit: MagicMock) -> None:
        """Test main with streamlit command."""
        mock_streamlit.return_value = 0
        result = main(["streamlit", "--port", "8080"])
        assert result == 0
        mock_streamlit.assert_called_once()

    @patch("codetunestudio.cli.check_database")
    def test_main_db_check(self, mock_check: MagicMock) -> None:
        """Test main with db check command."""
        mock_check.return_value = 0
        result = main(["db", "check"])
        assert result == 0
        mock_check.assert_called_once()

    @patch("codetunestudio.cli.init_database")
    def test_main_db_init(self, mock_init: MagicMock) -> None:
        """Test main with db init command."""
        mock_init.return_value = 0
        result = main(["db", "init"])
        assert result == 0
        mock_init.assert_called_once()

    def test_main_invalid_command(self) -> None:
        """Test main with invalid command."""
        with patch("sys.stderr", new=StringIO()):
            with pytest.raises(SystemExit):
                main(["invalid_command"])


class TestCLIIntegration(unittest.TestCase):
    """Integration tests for CLI."""

    @patch("sys.argv", ["codetune-studio", "--version"])
    def test_version_flag(self) -> None:
        """Test --version flag."""
        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            try:
                main()
            except SystemExit as e:
                assert e.code == 0
                output = mock_stdout.getvalue()
                assert __version__ in output

    @patch("codetunestudio.cli.run_streamlit")
    def test_default_behavior(self, mock_streamlit: MagicMock) -> None:
        """Test default behavior (no command)."""
        mock_streamlit.return_value = 0
        result = main([])
        assert result == 0
        # Should call streamlit with defaults
        args = mock_streamlit.call_args[0][0]
        assert args.port == 7860
        assert args.host == "0.0.0.0"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
