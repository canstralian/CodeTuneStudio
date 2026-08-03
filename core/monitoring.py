"""
Sentry monitoring and performance tracing for CodeTune Studio.

This module centralizes Sentry SDK initialization so that error monitoring
and performance tracing (Tracing) are configured consistently across the
Streamlit UI, Flask backend, and CLI entrypoints.

Sentry is initialized lazily and defensively: if the ``sentry_sdk`` package
is not installed, or no DSN is configured, initialization is skipped without
raising. This keeps Sentry an optional dependency and preserves the CPU-only,
network-restricted runtime contract of the project.
"""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)

# Default DSN for the CodeTune Studio Sentry project. A Sentry DSN is a
# client-side ingestion key (safe to distribute, unlike an auth token);
# override it per environment with the ``SENTRY_DSN`` environment variable,
# or set ``SENTRY_DSN=""`` to disable Sentry entirely.
DEFAULT_SENTRY_DSN = (
    "https://01891c0e1b4212dd8e7e0240af53af50@"
    "o4510152912863232.ingest.us.sentry.io/4510152912994305"
)

# Idempotency guard held in a mutable mapping so repeated calls within a
# single interpreter (e.g. CLI + app process) are cheap and safe.
_STATE: dict[str, bool] = {"initialized": False}


def _env_bool(name: str, *, default: bool) -> bool:
    """Parse a boolean environment variable, falling back to ``default``."""
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


def _env_float(name: str, default: float) -> float:
    """Parse a float environment variable, falling back to ``default``."""
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return default
    try:
        return float(raw)
    except ValueError:
        logger.warning(
            "Invalid float for %s=%r; using default %s", name, raw, default
        )
        return default


def setup_sentry() -> bool:
    """
    Initialize the Sentry SDK with performance tracing enabled.

    Configuration is read from environment variables:

    - ``SENTRY_DSN``: Project DSN (defaults to the CodeTune Studio project).
      Set to an empty string to disable Sentry entirely.
    - ``SENTRY_TRACES_SAMPLE_RATE``: Fraction of transactions to trace
      (``0.0``-``1.0``, default ``1.0``). Lower this for high-traffic
      deployments to keep overhead acceptable.
    - ``SENTRY_SEND_DEFAULT_PII``: Whether to attach request headers and IP
      addresses (default ``true``). Set to ``false`` to avoid collecting
      personally identifiable information.
    - ``SENTRY_ENVIRONMENT``: Environment name reported to Sentry
      (defaults to ``APP_ENV`` or ``"development"``).

    The call is idempotent within a process and never raises: any failure
    (missing package, bad DSN, network restriction) is logged and swallowed
    so monitoring can never take down the application.

    Returns:
        ``True`` if Sentry was initialized, ``False`` if it was skipped
        (missing DSN, missing ``sentry_sdk``, already initialized, or error).
    """
    if _STATE["initialized"]:
        return False

    dsn = os.environ.get("SENTRY_DSN", DEFAULT_SENTRY_DSN).strip()
    if not dsn:
        logger.info("Sentry DSN not configured; skipping Sentry initialization")
        return False

    try:
        import sentry_sdk
    except ImportError:
        logger.warning(
            "sentry_sdk is not installed; skipping Sentry initialization. "
            "Install with `pip install 'sentry-sdk[flask]'` to enable monitoring."
        )
        return False

    traces_sample_rate = _env_float("SENTRY_TRACES_SAMPLE_RATE", 1.0)
    send_default_pii = _env_bool("SENTRY_SEND_DEFAULT_PII", default=True)
    environment = os.environ.get(
        "SENTRY_ENVIRONMENT", os.environ.get("APP_ENV", "development")
    )

    try:
        sentry_sdk.init(
            dsn=dsn,
            environment=environment,
            # Capture request headers and IP addresses. Disable via
            # SENTRY_SEND_DEFAULT_PII=false to avoid collecting PII.
            send_default_pii=send_default_pii,
            # Fraction of transactions sampled for performance tracing.
            # 1.0 traces every transaction; lower it for high-traffic apps.
            traces_sample_rate=traces_sample_rate,
        )
    except Exception:
        logger.exception("Failed to initialize Sentry")
        return False

    _STATE["initialized"] = True
    logger.info(
        "Sentry initialized (environment=%s, traces_sample_rate=%s, "
        "send_default_pii=%s)",
        environment,
        traces_sample_rate,
        send_default_pii,
    )
    return True
