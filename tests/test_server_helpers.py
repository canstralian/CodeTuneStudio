"""Tests for core.server helper functions: _env_flag and _redact_url_password."""

import pytest

from core.server import _env_flag, _redact_url_password


# ---------------------------------------------------------------------------
# _env_flag tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("1", True),
        ("true", True),
        ("TRUE", True),
        ("True", True),
        (" yes ", True),
        ("t", True),
        ("y", True),
        ("on", True),
        ("ON", True),
        ("0", False),
        ("false", False),
        ("False", False),
        ("FALSE", False),
        ("", False),
        ("no", False),
        ("off", False),
        ("2", False),
        ("random", False),
    ],
)
def test_env_flag_parsing(monkeypatch, value: str, expected: bool) -> None:
    monkeypatch.setenv("SQL_DEBUG", value)
    assert _env_flag("SQL_DEBUG", default=False) is expected


def test_env_flag_missing_returns_default_false(monkeypatch) -> None:
    monkeypatch.delenv("SQL_DEBUG", raising=False)
    assert _env_flag("SQL_DEBUG", default=False) is False


def test_env_flag_missing_returns_default_true(monkeypatch) -> None:
    monkeypatch.delenv("SQL_DEBUG", raising=False)
    assert _env_flag("SQL_DEBUG", default=True) is True


# ---------------------------------------------------------------------------
# _redact_url_password tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        # SQLite — no credentials
        ("sqlite:///database.db", "sqlite:///database.db"),
        # PostgreSQL with password
        (
            "postgresql://user:pass@localhost:5432/db",
            "postgresql://user:***@localhost:5432/db",
        ),
        # PostgreSQL without port
        (
            "postgresql://user:secret@db.example.com/mydb",
            "postgresql://user:***@db.example.com/mydb",
        ),
        # MySQL with password
        (
            "mysql://admin:hunter2@db.example.com/prod",
            "mysql://admin:***@db.example.com/prod",
        ),
        # PostgreSQL without password — unchanged
        ("postgresql://localhost/db", "postgresql://localhost/db"),
        # URL with username but no password — unchanged
        ("postgresql://user@localhost/db", "postgresql://user@localhost/db"),
    ],
)
def test_redact_url_password(url: str, expected: str) -> None:
    assert _redact_url_password(url) == expected
