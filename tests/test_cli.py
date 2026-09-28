"""
Tests for CLI helpers in ``core.cli``.

These tests exercise the pure helper functions only; they do not launch the
Streamlit subprocess or touch the network.
"""

import unittest

from core.cli import _safe_database_url


class TestSafeDatabaseUrl(unittest.TestCase):
    """Test that database URLs are summarized without leaking credentials."""

    def test_strips_userinfo_password(self) -> None:
        """A ``user:password@`` userinfo component is removed entirely."""
        result = _safe_database_url("postgresql://user:secret@localhost:5432/db")
        self.assertEqual(result, "postgresql://localhost:5432/db")
        self.assertNotIn("secret", result)
        self.assertNotIn("user", result)

    def test_strips_query_string_password(self) -> None:
        """A password carried in the query string is dropped, not logged."""
        result = _safe_database_url("postgresql://user@host/db?password=secret")
        self.assertEqual(result, "postgresql://host/db")
        self.assertNotIn("secret", result)

    def test_preserves_credential_free_url(self) -> None:
        """A URL with no credentials keeps its scheme, host, and path."""
        self.assertEqual(
            _safe_database_url("postgresql://localhost/db"),
            "postgresql://localhost/db",
        )

    def test_sqlite_url_unchanged(self) -> None:
        """A local SQLite URL (no host/credentials) is returned intact."""
        self.assertEqual(
            _safe_database_url("sqlite:///database.db"),
            "sqlite:///database.db",
        )

    def test_unparseable_url_falls_back(self) -> None:
        """An invalid URL (e.g. a bad port) yields a safe placeholder."""
        self.assertEqual(
            _safe_database_url("postgresql://host:notaport/db"), "<database>"
        )


if __name__ == "__main__":
    unittest.main()
