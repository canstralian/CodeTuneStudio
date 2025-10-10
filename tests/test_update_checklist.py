"""
Unit tests for scripts/update_checklist.py

Tests the secure implementation of the checklist update script,
including environment variable handling and error cases.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, mock_open, patch

# Add parent directory to path to import scripts module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import after path modification (noqa to suppress flake8 warning)
from scripts.update_checklist import (  # noqa: E402
    fetch_closed_prs,
    load_environment,
    read_checklist_file,
    update_checklist_lines,
    validate_github_token,
    write_checklist_file,
)


class TestLoadEnvironment(unittest.TestCase):
    """Test cases for load_environment function."""

    @patch('scripts.update_checklist.load_dotenv')
    def test_load_environment_calls_load_dotenv(self, mock_load_dotenv):
        """Test that load_environment calls load_dotenv."""
        load_environment()
        mock_load_dotenv.assert_called_once()


class TestValidateGitHubToken(unittest.TestCase):
    """Test cases for validate_github_token function."""

    @patch.dict(os.environ, {"GITHUB_TOKEN": "ghp_test123"})
    def test_valid_token_returns_token(self):
        """Test that a valid token is returned correctly."""
        token = validate_github_token()
        self.assertEqual(token, "ghp_test123")

    @patch.dict(os.environ, {}, clear=True)
    def test_missing_token_exits_with_error(self):
        """Test that missing token causes system exit."""
        with self.assertRaises(SystemExit) as cm:
            validate_github_token()
        self.assertEqual(cm.exception.code, 1)

    @patch.dict(os.environ, {"GITHUB_TOKEN": ""})
    def test_empty_token_exits_with_error(self):
        """Test that empty token causes system exit."""
        with self.assertRaises(SystemExit) as cm:
            validate_github_token()
        self.assertEqual(cm.exception.code, 1)

    @patch.dict(os.environ, {"GITHUB_TOKEN": "   "})
    def test_whitespace_token_exits_with_error(self):
        """Test that whitespace-only token causes system exit."""
        with self.assertRaises(SystemExit) as cm:
            validate_github_token()
        self.assertEqual(cm.exception.code, 1)


class TestFetchClosedPRs(unittest.TestCase):
    """Test cases for fetch_closed_prs function."""

    @patch('scripts.update_checklist.requests.get')
    def test_successful_fetch(self, mock_get):
        """Test successful PR fetching from GitHub API."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"number": 1, "merged_at": "2024-01-01"},
            {"number": 2, "merged_at": None}
        ]
        mock_get.return_value = mock_response

        prs = fetch_closed_prs("owner/repo", "token123")

        self.assertEqual(len(prs), 2)
        self.assertEqual(prs[0]["number"], 1)
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertIn("Authorization", kwargs["headers"])
        self.assertEqual(kwargs["headers"]["Authorization"], "token token123")

    @patch('scripts.update_checklist.requests.get')
    def test_api_error_exits(self, mock_get):
        """Test that API errors cause system exit."""
        import requests
        mock_get.side_effect = requests.exceptions.RequestException("API Error")

        with self.assertRaises(SystemExit) as cm:
            fetch_closed_prs("owner/repo", "token123")
        self.assertEqual(cm.exception.code, 1)


class TestReadChecklistFile(unittest.TestCase):
    """Test cases for read_checklist_file function."""

    @patch('builtins.open', new_callable=mock_open,
           read_data="- [ ] PR #1\n- [ ] PR #2\n")
    def test_successful_read(self, mock_file):
        """Test successful checklist file reading."""
        lines = read_checklist_file("checklist.md")

        self.assertEqual(len(lines), 2)
        self.assertIn("PR #1", lines[0])
        mock_file.assert_called_once_with("checklist.md", "r", encoding="utf-8")

    @patch('builtins.open', side_effect=FileNotFoundError())
    def test_file_not_found_exits(self, mock_file):
        """Test that missing file causes system exit."""
        with self.assertRaises(SystemExit) as cm:
            read_checklist_file("nonexistent.md")
        self.assertEqual(cm.exception.code, 1)

    @patch('builtins.open', side_effect=OSError("Permission denied"))
    def test_os_error_exits(self, mock_file):
        """Test that OS errors cause system exit."""
        with self.assertRaises(SystemExit) as cm:
            read_checklist_file("checklist.md")
        self.assertEqual(cm.exception.code, 1)


class TestUpdateChecklistLines(unittest.TestCase):
    """Test cases for update_checklist_lines function."""

    def test_update_merged_prs(self):
        """Test that merged PRs are marked as completed."""
        lines = [
            "- [ ] PR #123 Feature A\n",
            "- [ ] PR #456 Feature B\n",
            "- [ ] PR #789 Feature C\n"
        ]
        prs = [
            {"number": 123, "merged_at": "2024-01-01"},
            {"number": 456, "merged_at": "2024-01-02"},
            {"number": 999, "merged_at": "2024-01-03"}  # Not in checklist
        ]

        updated = update_checklist_lines(lines, prs)

        self.assertIn("[x]", updated[0])
        self.assertIn("PR #123", updated[0])
        self.assertIn("[x]", updated[1])
        self.assertIn("PR #456", updated[1])
        self.assertIn("[ ]", updated[2])  # Not merged
        self.assertIn("PR #789", updated[2])

    def test_skip_unmerged_prs(self):
        """Test that unmerged PRs are not marked as completed."""
        lines = ["- [ ] PR #123 Feature A\n"]
        prs = [{"number": 123, "merged_at": None}]

        updated = update_checklist_lines(lines, prs)

        self.assertIn("[ ]", updated[0])
        self.assertNotIn("[x]", updated[0])

    def test_empty_lines(self):
        """Test handling of empty checklist."""
        lines = []
        prs = [{"number": 123, "merged_at": "2024-01-01"}]

        updated = update_checklist_lines(lines, prs)

        self.assertEqual(len(updated), 0)

    def test_empty_prs(self):
        """Test handling of empty PR list."""
        lines = ["- [ ] PR #123 Feature A\n"]
        prs = []

        updated = update_checklist_lines(lines, prs)

        self.assertIn("[ ]", updated[0])

    def test_original_lines_not_modified(self):
        """Test that original lines list is not modified."""
        lines = ["- [ ] PR #123 Feature A\n"]
        prs = [{"number": 123, "merged_at": "2024-01-01"}]
        original_lines = lines.copy()

        update_checklist_lines(lines, prs)

        self.assertEqual(lines, original_lines)


class TestWriteChecklistFile(unittest.TestCase):
    """Test cases for write_checklist_file function."""

    @patch('builtins.open', new_callable=mock_open)
    def test_successful_write(self, mock_file):
        """Test successful checklist file writing."""
        lines = ["- [x] PR #1\n", "- [ ] PR #2\n"]

        write_checklist_file("checklist.md", lines)

        mock_file.assert_called_once_with("checklist.md", "w", encoding="utf-8")
        handle = mock_file()
        handle.writelines.assert_called_once_with(lines)

    @patch('builtins.open', side_effect=IOError("Write error"))
    def test_io_error_exits(self, mock_file):
        """Test that IO errors cause system exit."""
        lines = ["- [x] PR #1\n"]

        with self.assertRaises(SystemExit) as cm:
            write_checklist_file("checklist.md", lines)
        self.assertEqual(cm.exception.code, 1)

    @patch('builtins.open', side_effect=OSError("Permission denied"))
    def test_os_error_exits(self, mock_file):
        """Test that OS errors cause system exit."""
        lines = ["- [x] PR #1\n"]

        with self.assertRaises(SystemExit) as cm:
            write_checklist_file("checklist.md", lines)
        self.assertEqual(cm.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
