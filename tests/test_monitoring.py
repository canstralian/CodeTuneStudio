"""
Tests for the Sentry monitoring module (``core.monitoring``).

These tests avoid any real network calls to Sentry: they either disable
Sentry via configuration or mock ``sentry_sdk.init`` so no transport is
created. They pass whether or not ``sentry_sdk`` is installed.
"""

import importlib
import os
import unittest
from unittest.mock import MagicMock, patch


def _fresh_monitoring():
    """Import a fresh copy of core.monitoring with a reset init guard."""
    import core.monitoring as monitoring

    importlib.reload(monitoring)
    return monitoring


class TestEnvParsers(unittest.TestCase):
    """Test the environment-variable parsing helpers."""

    def test_env_bool_default_when_unset(self):
        monitoring = _fresh_monitoring()
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("SENTRY_TEST_BOOL", None)
            self.assertTrue(monitoring._env_bool("SENTRY_TEST_BOOL", default=True))
            self.assertFalse(monitoring._env_bool("SENTRY_TEST_BOOL", default=False))

    def test_env_bool_truthy_and_falsy(self):
        monitoring = _fresh_monitoring()
        for truthy in ("1", "true", "TRUE", "Yes", "on"):
            with patch.dict(os.environ, {"SENTRY_TEST_BOOL": truthy}):
                self.assertTrue(monitoring._env_bool("SENTRY_TEST_BOOL", default=False))
        for falsy in ("0", "false", "no", "off", "nonsense"):
            with patch.dict(os.environ, {"SENTRY_TEST_BOOL": falsy}):
                self.assertFalse(monitoring._env_bool("SENTRY_TEST_BOOL", default=True))

    def test_env_float_valid_and_invalid(self):
        monitoring = _fresh_monitoring()
        with patch.dict(os.environ, {"SENTRY_TEST_FLOAT": "0.25"}):
            self.assertEqual(monitoring._env_float("SENTRY_TEST_FLOAT", 1.0), 0.25)
        with patch.dict(os.environ, {"SENTRY_TEST_FLOAT": "not-a-number"}):
            self.assertEqual(monitoring._env_float("SENTRY_TEST_FLOAT", 1.0), 1.0)
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("SENTRY_TEST_FLOAT", None)
            self.assertEqual(monitoring._env_float("SENTRY_TEST_FLOAT", 0.5), 0.5)


class TestSetupSentry(unittest.TestCase):
    """Test the setup_sentry entry point."""

    def test_disabled_when_dsn_empty(self):
        monitoring = _fresh_monitoring()
        with patch.dict(os.environ, {"SENTRY_DSN": ""}):
            self.assertFalse(monitoring.setup_sentry())

    def test_idempotent(self):
        monitoring = _fresh_monitoring()
        fake_sdk = MagicMock()
        with (
            patch.dict(os.environ, {"SENTRY_DSN": "https://k@example.test/1"}),
            patch.dict("sys.modules", {"sentry_sdk": fake_sdk}),
        ):
            self.assertTrue(monitoring.setup_sentry())
            # Second call is a no-op because init already happened.
            self.assertFalse(monitoring.setup_sentry())
        fake_sdk.init.assert_called_once()

    def test_init_receives_tracing_config(self):
        monitoring = _fresh_monitoring()
        fake_sdk = MagicMock()
        env = {
            "SENTRY_DSN": "https://k@example.test/1",
            "SENTRY_TRACES_SAMPLE_RATE": "0.3",
            "SENTRY_SEND_DEFAULT_PII": "false",
            "SENTRY_ENVIRONMENT": "staging",
        }
        with (
            patch.dict(os.environ, env),
            patch.dict("sys.modules", {"sentry_sdk": fake_sdk}),
        ):
            self.assertTrue(monitoring.setup_sentry())

        _, kwargs = fake_sdk.init.call_args
        self.assertEqual(kwargs["dsn"], "https://k@example.test/1")
        self.assertEqual(kwargs["traces_sample_rate"], 0.3)
        self.assertFalse(kwargs["send_default_pii"])
        self.assertEqual(kwargs["environment"], "staging")

    def test_swallows_init_errors(self):
        monitoring = _fresh_monitoring()
        fake_sdk = MagicMock()
        fake_sdk.init.side_effect = RuntimeError("boom")
        with (
            patch.dict(os.environ, {"SENTRY_DSN": "https://k@example.test/1"}),
            patch.dict("sys.modules", {"sentry_sdk": fake_sdk}),
        ):
            # Failure must not propagate; returns False instead.
            self.assertFalse(monitoring.setup_sentry())


if __name__ == "__main__":
    unittest.main()
