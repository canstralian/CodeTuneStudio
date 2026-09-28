"""
Sentry monitoring and performance tracing for CodeTune Studio.

This module centralizes Sentry SDK initialization so that error monitoring
and performance tracing (Tracing) are configured consistently across the
Streamlit UI, Flask backend, and CLI entrypoints.

Sentry is **opt-in**: it initializes only when ``SENTRY_DSN`` is explicitly
set to a non-empty value, so a default install sends no telemetry to any
third party. Initialization is also lazy and defensive: if the ``sentry_sdk``
package is not installed, initialization is skipped without raising. This
keeps Sentry an optional dependency and preserves the CPU-only,
network-restricted runtime contract of the project.
"""

from __future__ import annotations

import logging
import math
import os

logger = logging.getLogger(__name__)

# Idempotency guard held in a mutable mapping so repeated calls within a
# single interpreter (e.g. CLI + app process) are cheap and safe.
_STATE: dict[str, bool] = {"initialized": False}


def _env_bool(name: str, *, default: bool) -> bool:
    """
    Parse a boolean environment variable.

    Args:
        name: Environment variable name to read.
        default: Value returned when the variable is unset.

    Returns:
        ``True`` for ``"1"``, ``"true"``, ``"yes"`` or ``"on"``
        (case-insensitive), ``False`` for any other set value, and
        ``default`` when the variable is unset.
    """
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


def _env_float(name: str, default: float) -> float:
    """
    Parse a float environment variable.

    Args:
        name: Environment variable name to read.
        default: Value returned when the variable is unset or not a valid
            float.

    Returns:
        The parsed float, or ``default`` when the variable is unset, empty,
        or cannot be parsed as a float.
    """
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return default
    try:
        return float(raw)
    except ValueError:
        logger.warning("Invalid float for %s=%r; using default %s", name, raw, default)
        return default


def _env_sample_rate(name: str, default: float) -> float:
    """
    Parse a Sentry sample-rate environment variable.

    A sample rate must be a finite float in the inclusive range
    ``[0.0, 1.0]``; anything else (including a value such as ``1.5`` that the
    SDK would silently treat as "sample nothing") falls back to ``default``.

    Args:
        name: Environment variable name to read.
        default: Value returned when the variable is unset, non-numeric, or
            outside the valid range.

    Returns:
        The parsed rate when valid, otherwise ``default``.
    """
    value = _env_float(name, default)
    if not math.isfinite(value) or not 0.0 <= value <= 1.0:
        logger.warning(
            "%s=%r is outside the valid range [0.0, 1.0]; using default %s",
            name,
            os.environ.get(name),
            default,
        )
        return default
    return value


def setup_sentry() -> bool:
    """
    Initialize the Sentry SDK with performance tracing enabled.

    Sentry is opt-in: it initializes only when ``SENTRY_DSN`` is set to a
    non-empty value, so a default install sends no telemetry. Configuration
    is read from environment variables:

    - ``SENTRY_DSN``: Project DSN. Unset or empty disables Sentry entirely.
    - ``SENTRY_TRACES_SAMPLE_RATE``: Fraction of transactions to trace
      (``0.0``-``1.0``, default ``1.0``). Lower this for high-traffic
      deployments. Non-numeric or out-of-range values fall back to the
      default.
    - ``SENTRY_SEND_DEFAULT_PII``: Whether to attach request headers and IP
      addresses (default ``false``). Set to ``true`` to opt in to collecting
      this personally identifiable information.
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

    dsn = os.environ.get("SENTRY_DSN", "").strip()
    if not dsn:
        logger.info("SENTRY_DSN not set; Sentry monitoring is disabled")
        return False

    try:
        import sentry_sdk  # noqa: PLC0415 - optional dependency, imported lazily
    except ImportError:
        logger.warning(
            "sentry_sdk is not installed; skipping Sentry initialization. "
            "Install with `pip install 'sentry-sdk[flask]'` to enable monitoring."
        )
        return False

    traces_sample_rate = _env_sample_rate("SENTRY_TRACES_SAMPLE_RATE", 1.0)
    send_default_pii = _env_bool("SENTRY_SEND_DEFAULT_PII", default=False)
    environment = os.environ.get(
        "SENTRY_ENVIRONMENT", os.environ.get("APP_ENV", "development")
    )

    try:
        sentry_sdk.init(
            dsn=dsn,
            environment=environment,
            # Attach request headers and IP addresses only when explicitly
            # opted in via SENTRY_SEND_DEFAULT_PII=true.
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
