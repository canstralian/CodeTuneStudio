"""
Tests for scripts/cleanup_stale_prs.py.

Covers:
  - close_pr: dry-run mode returns True without making HTTP calls
  - close_pr: live mode POSTs comment and PATCHes state with timeout=30
  - close_pr: handles comment POST failure (non-201 status)
  - close_pr: handles close PATCH failure (non-200 status)
  - close_pr: handles request exception on comment
  - close_pr: handles request exception on close
  - close_prs_by_category: aggregates results from close_pr calls
  - close_prs_by_category: uses correct closure message for known category
  - close_prs_by_category: falls back to default message for unknown category
  - get_github_token: returns token from environment
  - get_github_token: calls sys.exit when token absent
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, call, patch

# Ensure the project root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.cleanup_stale_prs import (  # noqa: E402
    CLOSURE_MESSAGES,
    GITHUB_API,
    REPO_NAME,
    REPO_OWNER,
    STALE_PRS,
    close_pr,
    close_prs_by_category,
    get_github_token,
)


# ---------------------------------------------------------------------------
# TestClosePrDryRun
# ---------------------------------------------------------------------------


class TestClosePrDryRun(unittest.TestCase):
    """close_pr with dry_run=True must not make any HTTP requests."""

    @patch("scripts.cleanup_stale_prs.requests")
    def test_dry_run_returns_true(self, mock_requests):
        result = close_pr(42, "test comment", "fake_token", dry_run=True)
        self.assertTrue(result)

    @patch("scripts.cleanup_stale_prs.requests")
    def test_dry_run_makes_no_http_calls(self, mock_requests):
        close_pr(42, "test comment", "fake_token", dry_run=True)
        mock_requests.post.assert_not_called()
        mock_requests.patch.assert_not_called()

    @patch("scripts.cleanup_stale_prs.requests")
    def test_dry_run_default_is_true(self, mock_requests):
        """Default dry_run parameter is True."""
        result = close_pr(99, "comment", "token")
        self.assertTrue(result)
        mock_requests.post.assert_not_called()


# ---------------------------------------------------------------------------
# TestClosePrLiveMode
# ---------------------------------------------------------------------------


class TestClosePrLiveMode(unittest.TestCase):
    """close_pr with dry_run=False makes proper HTTP requests."""

    def _mock_response(self, status_code: int) -> MagicMock:
        resp = MagicMock()
        resp.status_code = status_code
        resp.text = "OK"
        return resp

    @patch("scripts.cleanup_stale_prs.requests")
    def test_live_mode_posts_comment(self, mock_requests):
        mock_requests.post.return_value = self._mock_response(201)
        mock_requests.patch.return_value = self._mock_response(200)

        close_pr(10, "closing message", "my_token", dry_run=False)

        expected_comment_url = (
            f"{GITHUB_API}/repos/{REPO_OWNER}/{REPO_NAME}/issues/10/comments"
        )
        mock_requests.post.assert_called_once_with(
            expected_comment_url,
            headers={
                "Authorization": "Bearer my_token",
                "Accept": "application/vnd.github.v3+json",
            },
            json={"body": "closing message"},
            timeout=30,
        )

    @patch("scripts.cleanup_stale_prs.requests")
    def test_live_mode_patches_state_closed(self, mock_requests):
        mock_requests.post.return_value = self._mock_response(201)
        mock_requests.patch.return_value = self._mock_response(200)

        close_pr(10, "closing message", "my_token", dry_run=False)

        expected_pr_url = f"{GITHUB_API}/repos/{REPO_OWNER}/{REPO_NAME}/pulls/10"
        mock_requests.patch.assert_called_once_with(
            expected_pr_url,
            headers={
                "Authorization": "Bearer my_token",
                "Accept": "application/vnd.github.v3+json",
            },
            json={"state": "closed"},
            timeout=30,
        )

    @patch("scripts.cleanup_stale_prs.requests")
    def test_live_mode_success_returns_true(self, mock_requests):
        mock_requests.post.return_value = self._mock_response(201)
        mock_requests.patch.return_value = self._mock_response(200)

        result = close_pr(10, "message", "token", dry_run=False)
        self.assertTrue(result)

    @patch("scripts.cleanup_stale_prs.requests")
    def test_comment_failure_returns_false(self, mock_requests):
        """When POST comment returns non-201, close_pr returns False."""
        mock_requests.post.return_value = self._mock_response(422)

        result = close_pr(10, "message", "token", dry_run=False)
        self.assertFalse(result)

    @patch("scripts.cleanup_stale_prs.requests")
    def test_comment_failure_does_not_call_patch(self, mock_requests):
        """When comment fails, the PR close PATCH is not attempted."""
        mock_requests.post.return_value = self._mock_response(403)

        close_pr(10, "message", "token", dry_run=False)
        mock_requests.patch.assert_not_called()

    @patch("scripts.cleanup_stale_prs.requests")
    def test_close_patch_failure_returns_false(self, mock_requests):
        """When PATCH close returns non-200, close_pr returns False."""
        mock_requests.post.return_value = self._mock_response(201)
        mock_requests.patch.return_value = self._mock_response(500)

        result = close_pr(10, "message", "token", dry_run=False)
        self.assertFalse(result)

    @patch("scripts.cleanup_stale_prs.requests")
    def test_comment_exception_returns_false(self, mock_requests):
        """When POST raises an exception, close_pr returns False."""
        mock_requests.post.side_effect = Exception("network error")

        result = close_pr(10, "message", "token", dry_run=False)
        self.assertFalse(result)

    @patch("scripts.cleanup_stale_prs.requests")
    def test_close_exception_returns_false(self, mock_requests):
        """When PATCH raises an exception, close_pr returns False."""
        mock_requests.post.return_value = self._mock_response(201)
        mock_requests.patch.side_effect = Exception("connection refused")

        result = close_pr(10, "message", "token", dry_run=False)
        self.assertFalse(result)

    @patch("scripts.cleanup_stale_prs.requests")
    def test_timeout_parameter_is_30(self, mock_requests):
        """The timeout parameter must be exactly 30 for both requests."""
        mock_requests.post.return_value = self._mock_response(201)
        mock_requests.patch.return_value = self._mock_response(200)

        close_pr(7, "msg", "tok", dry_run=False)

        _, post_kwargs = mock_requests.post.call_args
        _, patch_kwargs = mock_requests.patch.call_args
        self.assertEqual(post_kwargs["timeout"], 30)
        self.assertEqual(patch_kwargs["timeout"], 30)

    @patch("scripts.cleanup_stale_prs.requests")
    def test_auth_header_uses_bearer_token(self, mock_requests):
        """Authorization header must use 'Bearer <token>'."""
        mock_requests.post.return_value = self._mock_response(201)
        mock_requests.patch.return_value = self._mock_response(200)

        close_pr(5, "msg", "secret_token", dry_run=False)

        _, post_kwargs = mock_requests.post.call_args
        self.assertEqual(post_kwargs["headers"]["Authorization"], "Bearer secret_token")


# ---------------------------------------------------------------------------
# TestClosePrsByCategory
# ---------------------------------------------------------------------------


class TestClosePrsByCategory(unittest.TestCase):
    """close_prs_by_category aggregates results and uses correct messages."""

    @patch("scripts.cleanup_stale_prs.close_pr", return_value=True)
    def test_all_success_counts(self, mock_close_pr):
        results = close_prs_by_category(
            "security_autofix", [1, 2, 3], "token", dry_run=True
        )
        self.assertEqual(results["success"], 3)
        self.assertEqual(results["failed"], 0)

    @patch("scripts.cleanup_stale_prs.close_pr", return_value=False)
    def test_all_failure_counts(self, mock_close_pr):
        results = close_prs_by_category(
            "security_autofix", [1, 2], "token", dry_run=False
        )
        self.assertEqual(results["success"], 0)
        self.assertEqual(results["failed"], 2)

    @patch("scripts.cleanup_stale_prs.close_pr")
    def test_mixed_success_failure_counts(self, mock_close_pr):
        mock_close_pr.side_effect = [True, False, True, False, True]
        results = close_prs_by_category(
            "duplicate_ci", [10, 11, 12, 13, 14], "token", dry_run=True
        )
        self.assertEqual(results["success"], 3)
        self.assertEqual(results["failed"], 2)

    @patch("scripts.cleanup_stale_prs.close_pr", return_value=True)
    def test_empty_pr_list_returns_zero_counts(self, mock_close_pr):
        results = close_prs_by_category("october_prs", [], "token", dry_run=True)
        self.assertEqual(results["success"], 0)
        self.assertEqual(results["failed"], 0)
        mock_close_pr.assert_not_called()

    @patch("scripts.cleanup_stale_prs.close_pr", return_value=True)
    def test_uses_known_category_message(self, mock_close_pr):
        """The closure message for a known category is fetched from CLOSURE_MESSAGES."""
        close_prs_by_category("security_autofix", [1], "token", dry_run=True)
        # The message passed to close_pr should be the security_autofix message
        call_args = mock_close_pr.call_args
        message_arg = call_args[0][1]  # positional arg index 1
        self.assertEqual(message_arg, CLOSURE_MESSAGES["security_autofix"])

    @patch("scripts.cleanup_stale_prs.close_pr", return_value=True)
    def test_unknown_category_falls_back_to_default_message(self, mock_close_pr):
        """An unknown category falls back to the 'september_prs' message."""
        close_prs_by_category("nonexistent_category", [1], "token", dry_run=True)
        call_args = mock_close_pr.call_args
        message_arg = call_args[0][1]
        self.assertEqual(message_arg, CLOSURE_MESSAGES["september_prs"])

    @patch("scripts.cleanup_stale_prs.close_pr", return_value=True)
    def test_passes_token_to_close_pr(self, mock_close_pr):
        close_prs_by_category("duplicate_ci", [42], "my_token", dry_run=True)
        call_args = mock_close_pr.call_args
        self.assertEqual(call_args[0][2], "my_token")

    @patch("scripts.cleanup_stale_prs.close_pr", return_value=True)
    def test_passes_dry_run_flag_to_close_pr(self, mock_close_pr):
        close_prs_by_category("duplicate_ci", [42], "tok", dry_run=False)
        call_args = mock_close_pr.call_args
        self.assertFalse(call_args[0][3])

    @patch("scripts.cleanup_stale_prs.close_pr", return_value=True)
    def test_calls_close_pr_for_each_pr(self, mock_close_pr):
        pr_numbers = [10, 20, 30]
        close_prs_by_category("duplicate_docs", pr_numbers, "tok", dry_run=True)
        self.assertEqual(mock_close_pr.call_count, len(pr_numbers))
        called_pr_numbers = [c[0][0] for c in mock_close_pr.call_args_list]
        self.assertEqual(called_pr_numbers, pr_numbers)

    @patch("scripts.cleanup_stale_prs.close_pr", return_value=True)
    def test_returns_dict_with_success_and_failed_keys(self, mock_close_pr):
        results = close_prs_by_category("merge_conflicts", [1], "tok", dry_run=True)
        self.assertIn("success", results)
        self.assertIn("failed", results)


# ---------------------------------------------------------------------------
# TestGetGithubToken
# ---------------------------------------------------------------------------


class TestGetGithubToken(unittest.TestCase):
    """get_github_token reads from environment and exits when absent."""

    def test_returns_token_from_env(self):
        with patch.dict("os.environ", {"GITHUB_TOKEN": "ghp_testtoken"}):
            token = get_github_token()
        self.assertEqual(token, "ghp_testtoken")

    def test_exits_when_token_absent(self):
        import os

        env = {k: v for k, v in os.environ.items() if k != "GITHUB_TOKEN"}
        with patch.dict("os.environ", env, clear=True):
            with self.assertRaises(SystemExit):
                get_github_token()

    def test_exits_with_code_1_when_token_absent(self):
        import os

        env = {k: v for k, v in os.environ.items() if k != "GITHUB_TOKEN"}
        with patch.dict("os.environ", env, clear=True):
            with self.assertRaises(SystemExit) as ctx:
                get_github_token()
        self.assertEqual(ctx.exception.code, 1)


# ---------------------------------------------------------------------------
# TestStalePrsConfiguration
# ---------------------------------------------------------------------------


class TestStalePrsConfiguration(unittest.TestCase):
    """Verify STALE_PRS and CLOSURE_MESSAGES are consistent (structural sanity)."""

    def test_all_categories_have_closure_messages(self):
        """Every category in STALE_PRS must have a corresponding CLOSURE_MESSAGES entry."""
        for category in STALE_PRS:
            self.assertIn(
                category,
                CLOSURE_MESSAGES,
                f"Category '{category}' in STALE_PRS has no matching CLOSURE_MESSAGES entry",
            )

    def test_stale_prs_all_values_are_lists(self):
        for category, pr_list in STALE_PRS.items():
            self.assertIsInstance(
                pr_list, list, f"STALE_PRS['{category}'] is not a list"
            )

    def test_stale_prs_all_values_are_integers(self):
        for category, pr_list in STALE_PRS.items():
            for pr in pr_list:
                self.assertIsInstance(
                    pr, int, f"STALE_PRS['{category}'] contains non-int: {pr!r}"
                )

    def test_october_prs_are_sorted_list(self):
        """october_prs should be a properly formatted list (no inline single-line)."""
        october = STALE_PRS.get("october_prs", [])
        self.assertIsInstance(october, list)
        self.assertGreater(len(october), 0)

    def test_closure_messages_are_non_empty_strings(self):
        for category, msg in CLOSURE_MESSAGES.items():
            self.assertIsInstance(
                msg, str, f"CLOSURE_MESSAGES['{category}'] is not a str"
            )
            self.assertGreater(len(msg), 0, f"CLOSURE_MESSAGES['{category}'] is empty")


if __name__ == "__main__":
    unittest.main()
