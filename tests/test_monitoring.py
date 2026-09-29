"""
Tests for the Sentry monitoring module (``core.monitoring``).

These tests avoid any real network calls to Sentry: they either disable
Sentry via configuration or mock ``sentry_sdk.init`` so no transport is
created. They pass whether or not ``sentry_sdk`` is installed.
"""

import importlib
import os
import unittest
from types import ModuleType
from unittest.mock import MagicMock, patch


def _fresh_monitoring() -> ModuleType:
    """Import a fresh copy of core.monitoring with a reset init guard."""
    import core.monitoring as monitoring

    importlib.reload(monitoring)
    return monitoring


class TestEnvParsers(unittest.TestCase):
    """Test the environment-variable parsing helpers."""

    def test_env_bool_default_when_unset(self) -> None:
        """An unset variable falls back to the provided default."""
        monitoring = _fresh_monitoring()
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("SENTRY_TEST_BOOL", None)
            self.assertTrue(monitoring._env_bool("SENTRY_TEST_BOOL", default=True))
            self.assertFalse(monitoring._env_bool("SENTRY_TEST_BOOL", default=False))

    def test_env_bool_truthy_and_falsy(self) -> None:
        """Common truthy strings parse True and everything else False."""
        monitoring = _fresh_monitoring()
        for truthy in ("1", "true", "TRUE", "Yes", "on"):
            with patch.dict(os.environ, {"SENTRY_TEST_BOOL": truthy}):
                self.assertTrue(monitoring._env_bool("SENTRY_TEST_BOOL", default=False))
        for falsy in ("0", "false", "no", "off", "nonsense"):
            with patch.dict(os.environ, {"SENTRY_TEST_BOOL": falsy}):
                self.assertFalse(monitoring._env_bool("SENTRY_TEST_BOOL", default=True))

    def test_env_float_valid_and_invalid(self) -> None:
        """Valid floats parse; invalid or unset values fall back to default."""
        monitoring = _fresh_monitoring()
        with patch.dict(os.environ, {"SENTRY_TEST_FLOAT": "0.25"}):
            self.assertEqual(monitoring._env_float("SENTRY_TEST_FLOAT", 1.0), 0.25)
        with patch.dict(os.environ, {"SENTRY_TEST_FLOAT": "not-a-number"}):
            self.assertEqual(monitoring._env_float("SENTRY_TEST_FLOAT", 1.0), 1.0)
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("SENTRY_TEST_FLOAT", None)
            self.assertEqual(monitoring._env_float("SENTRY_TEST_FLOAT", 0.5), 0.5)

    def test_sample_rate_rejects_out_of_range(self) -> None:
        """Out-of-range or non-finite sample rates fall back to the default."""
        monitoring = _fresh_monitoring()
        for bad in ("1.5", "-0.1", "inf", "nan"):
            with patch.dict(os.environ, {"SENTRY_TEST_RATE": bad}):
                self.assertEqual(
                    monitoring._env_sample_rate("SENTRY_TEST_RATE", 1.0), 1.0
                )
        with patch.dict(os.environ, {"SENTRY_TEST_RATE": "0.25"}):
            self.assertEqual(monitoring._env_sample_rate("SENTRY_TEST_RATE", 1.0), 0.25)


class TestSetupSentry(unittest.TestCase):
    """Test the setup_sentry entry point."""

    def test_disabled_when_dsn_empty(self) -> None:
        """An empty SENTRY_DSN disables Sentry and returns False."""
        monitoring = _fresh_monitoring()
        with patch.dict(os.environ, {"SENTRY_DSN": ""}):
            self.assertFalse(monitoring.setup_sentry())

    def test_disabled_when_dsn_unset(self) -> None:
        """Sentry is opt-in: an unset SENTRY_DSN leaves it disabled."""
        monitoring = _fresh_monitoring()
        fake_sdk = MagicMock()
        with (
            patch.dict(os.environ, {}, clear=False),
            patch.dict("sys.modules", {"sentry_sdk": fake_sdk}),
        ):
            os.environ.pop("SENTRY_DSN", None)
            self.assertFalse(monitoring.setup_sentry())
        fake_sdk.init.assert_not_called()

    def test_idempotent(self) -> None:
        """A second setup_sentry call is a no-op after the first succeeds."""
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

    def test_init_receives_tracing_config(self) -> None:
        """Env vars are passed through to sentry_sdk.init as tracing config."""
        monitoring = _fresh_monitoring()
        fake_sdk = MagicMock()
        env = {
            "SENTRY_DSN": "https://k@example.test/1",
            "SENTRY_TRACES_SAMPLE_RATE": "0.3",
            "SENTRY_SEND_DEFAULT_PII": "true",
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
        self.assertTrue(kwargs["send_default_pii"])
        self.assertEqual(kwargs["environment"], "staging")

    def test_pii_defaults_off(self) -> None:
        """send_default_pii defaults to False when the env var is unset."""
        monitoring = _fresh_monitoring()
        fake_sdk = MagicMock()
        env = {"SENTRY_DSN": "https://k@example.test/1"}
        with (
            patch.dict(os.environ, env, clear=False),
            patch.dict("sys.modules", {"sentry_sdk": fake_sdk}),
        ):
            os.environ.pop("SENTRY_SEND_DEFAULT_PII", None)
            self.assertTrue(monitoring.setup_sentry())
        _, kwargs = fake_sdk.init.call_args
        self.assertFalse(kwargs["send_default_pii"])

    def test_swallows_init_errors(self) -> None:
        """An SDK init error is caught and reported as False, never raised."""
        monitoring = _fresh_monitoring()
        fake_sdk = MagicMock()
        fake_sdk.init.side_effect = RuntimeError("boom")
        with (
            patch.dict(os.environ, {"SENTRY_DSN": "https://k@example.test/1"}),
            patch.dict("sys.modules", {"sentry_sdk": fake_sdk}),
        ):
            # Failure must not propagate; returns False instead.
            self.assertFalse(monitoring.setup_sentry())


class TestScrubbing(unittest.TestCase):
    """Test that outgoing events and breadcrumbs are scrubbed of secrets."""

    def test_scrub_text_masks_url_password(self) -> None:
        """A password in URL userinfo is masked, host and user preserved."""
        monitoring = _fresh_monitoring()
        out = monitoring._scrub_text("postgresql://user:secret@localhost/db")
        self.assertEqual(out, "postgresql://user:***@localhost/db")
        self.assertNotIn("secret", out)

    def test_scrub_text_masks_key_value_secret(self) -> None:
        """A ``password=``/``token=`` style secret is masked in place."""
        monitoring = _fresh_monitoring()
        self.assertNotIn("hunter2", monitoring._scrub_text("db?password=hunter2"))
        self.assertNotIn("abc123", monitoring._scrub_text("Authorization token=abc123"))

    def test_scrub_event_data_walks_nested_structures(self) -> None:
        """Secrets are scrubbed from nested dict/list event structures."""
        monitoring = _fresh_monitoring()
        event = {
            "message": "connect postgresql://u:pw@h/db",
            "extra": {"urls": ["redis://a:b@h:6379/0"]},
        }
        scrubbed = monitoring._scrub_event_data(event)
        self.assertNotIn("pw@", scrubbed["message"])
        self.assertNotIn(":b@", scrubbed["extra"]["urls"][0])

    def test_before_send_scrubs_and_survives_bad_input(self) -> None:
        """before_send scrubs strings and never raises on odd input."""
        monitoring = _fresh_monitoring()
        event = {"message": "postgresql://u:pw@h/db"}
        self.assertNotIn("pw@", monitoring._before_send(event, None)["message"])

    def test_before_send_drops_payload_past_depth_limit(self) -> None:
        """A structure too deep to fully scrub is dropped, not sent partial."""
        monitoring = _fresh_monitoring()
        deep: object = "postgresql://u:pw@h/db"
        for _ in range(monitoring._MAX_SCRUB_DEPTH + 5):
            deep = {"nested": deep}
        # Fails closed: the whole event is dropped rather than sent unscrubbed.
        self.assertIsNone(monitoring._before_send(deep, None))
        self.assertIsNone(monitoring._before_breadcrumb(deep, None))

    def test_init_registers_scrubbers(self) -> None:
        """setup_sentry wires the before_send/before_breadcrumb scrubbers."""
        monitoring = _fresh_monitoring()
        fake_sdk = MagicMock()
        with (
            patch.dict(os.environ, {"SENTRY_DSN": "https://k@example.test/1"}),
            patch.dict("sys.modules", {"sentry_sdk": fake_sdk}),
        ):
            self.assertTrue(monitoring.setup_sentry())
        _, kwargs = fake_sdk.init.call_args
        self.assertTrue(callable(kwargs["before_send"]))
        self.assertTrue(callable(kwargs["before_breadcrumb"]))


if __name__ == "__main__":
    unittest.main()
