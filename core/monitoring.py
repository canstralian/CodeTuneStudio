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
import re

logger = logging.getLogger(__name__)

# Idempotency guard held in a mutable mapping so repeated calls within a
# single interpreter (e.g. CLI + app process) are cheap and safe.
_STATE: dict[str, bool] = {"initialized": False}

# Patterns for secrets that must never leave the host inside Sentry events or
# breadcrumbs. Defense-in-depth: even though known log sites are already
# sanitized, an unforeseen log line or exception message could still embed a
# credential, so every outbound string is scrubbed before it is sent.
_SECRET_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    # URL userinfo password: scheme://user:password@host -> scheme://user:***@host
    (re.compile(r"://([^:/?#@\s]+):[^@/?#\s]+@"), r"://\1:***@"),
    # key=value secrets in query strings / connection strings.
    (
        re.compile(r"(?i)\b(password|passwd|pwd|token|secret|api[_-]?key)=[^&\s;]+"),
        r"\1=***",
    ),
)

# Bound recursion when walking arbitrary Sentry event structures.
_MAX_SCRUB_DEPTH = 20


def _scrub_text(text: str) -> str:
    """Redact known credential patterns from a single string."""
    for pattern, replacement in _SECRET_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def _scrub_event_data(obj: object, _depth: int = 0) -> object:
    """
    Recursively redact secrets from a Sentry event or breadcrumb structure.

    Walks nested dicts and lists up to a bounded depth, applying
    :func:`_scrub_text` to every string leaf. Non-string, non-container values
    are returned unchanged.
    """
    if _depth > _MAX_SCRUB_DEPTH:
        return obj
    if isinstance(obj, str):
        return _scrub_text(obj)
    if isinstance(obj, dict):
        return {k: _scrub_event_data(v, _depth + 1) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_scrub_event_data(v, _depth + 1) for v in obj]
    if isinstance(obj, tuple):
        return tuple(_scrub_event_data(v, _depth + 1) for v in obj)
    return obj


def _before_send(event: object, _hint: object) -> object:
    """Sentry ``before_send`` hook: scrub secrets from outgoing events."""
    try:
        return _scrub_event_data(event)
    except Exception:
        logger.exception("Sentry event scrubbing failed; dropping event")
        return None


def _before_breadcrumb(crumb: object, _hint: object) -> object:
    """Sentry ``before_breadcrumb`` hook: scrub secrets from breadcrumbs."""
    try:
        return _scrub_event_data(crumb)
    except Exception:
        logger.exception("Sentry breadcrumb scrubbing failed; dropping breadcrumb")
        return None


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

    Outgoing events and breadcrumbs are passed through credential scrubbers
    (``before_send`` / ``before_breadcrumb``) so secrets such as database-URL
    passwords cannot leak even if an unrelated log line or exception embeds
    one.

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
            # Defense-in-depth: scrub credentials from every outgoing event and
            # breadcrumb so a stray log line or exception cannot leak secrets.
            before_send=_before_send,
            before_breadcrumb=_before_breadcrumb,
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
