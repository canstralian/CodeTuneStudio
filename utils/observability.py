# SPDX-License-Identifier: MIT
"""
Observability initialisation — Sentry error tracking + Prometheus metrics.

Environment variables:
  SENTRY_DSN              — Sentry project DSN (leave unset to disable)
  SENTRY_ENVIRONMENT      — deployment environment tag (default: "production")
  SENTRY_RELEASE          — release identifier forwarded to Sentry
  SENTRY_SAMPLE_RATE      — traces_sample_rate float (default: "0.1")
  PROMETHEUS_PORT         — port for the Prometheus metrics HTTP server;
                            set to "0" or leave unset to disable (default: disabled)

All functions are no-ops when the relevant env var / optional dependency is absent.
Metric globals are always callable via the NoOpMetric fallback.
"""

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


class NoOpMetric:
    """Drop-in replacement used when prometheus-client is absent or disabled."""

    def labels(self, *args: Any, **kwargs: Any) -> "NoOpMetric":
        return self

    def inc(self, *args: Any, **kwargs: Any) -> None:
        pass

    def dec(self, *args: Any, **kwargs: Any) -> None:
        pass

    def observe(self, *args: Any, **kwargs: Any) -> None:
        pass

    def set(self, *args: Any, **kwargs: Any) -> None:
        pass

    def time(self) -> "NoOpMetric":
        return self

    def __enter__(self) -> "NoOpMetric":
        return self

    def __exit__(self, *args: Any) -> None:
        pass


# Module-level metrics — always callable (real counters replaced by init_prometheus)
training_runs_total: Any = NoOpMetric()
training_duration_seconds: Any = NoOpMetric()
db_errors_total: Any = NoOpMetric()


def init_sentry(flask_app: Any | None = None) -> bool:
    """Initialise Sentry SDK if SENTRY_DSN is set. Returns True on success."""
    dsn = os.environ.get("SENTRY_DSN", "")
    if not dsn:
        return False

    try:
        import sentry_sdk  # noqa: PLC0415
        from sentry_sdk.integrations.logging import (  # noqa: PLC0415
            LoggingIntegration,
        )
        from sentry_sdk.integrations.sqlalchemy import (  # noqa: PLC0415
            SqlalchemyIntegration,
        )

        integrations = [
            LoggingIntegration(level=logging.INFO, event_level=logging.ERROR),
            SqlalchemyIntegration(),
        ]

        if flask_app is not None:
            from sentry_sdk.integrations.flask import FlaskIntegration  # noqa: PLC0415

            integrations.append(FlaskIntegration())

        sentry_sdk.init(
            dsn=dsn,
            environment=os.environ.get("SENTRY_ENVIRONMENT", "production"),
            release=os.environ.get("SENTRY_RELEASE"),
            traces_sample_rate=float(os.environ.get("SENTRY_SAMPLE_RATE", "0.1")),
            integrations=integrations,
            send_default_pii=False,
        )
        env = os.environ.get("SENTRY_ENVIRONMENT", "production")
        logger.info("Sentry initialised (environment=%s)", env)
        return True
    except ImportError:
        logger.warning(
            "sentry-sdk not installed; run: pip install 'sentry-sdk[flask,sqlalchemy]'"
        )
        return False
    except Exception:
        logger.exception("Failed to initialise Sentry")
        return False


def init_prometheus(port: int | None = None) -> bool:
    """Start Prometheus metrics HTTP server if PROMETHEUS_PORT is set."""
    global training_runs_total, training_duration_seconds, db_errors_total  # noqa: PLW0603

    # Defensive port resolution — ignore non-integer env values
    if port is not None:
        resolved_port = port
    else:
        port_env = os.environ.get("PROMETHEUS_PORT", "0").strip()
        resolved_port = int(port_env) if port_env.isdigit() else 0

    if resolved_port <= 0:
        return False

    try:
        from prometheus_client import (  # noqa: PLC0415
            Counter,
            Histogram,
            start_http_server,
        )

        training_runs_total = Counter(
            "codetune_training_runs_total",
            "Total number of training runs",
            ["model_type", "status"],
        )
        training_duration_seconds = Histogram(
            "codetune_training_duration_seconds",
            "Training run duration in seconds",
            ["model_type"],
            buckets=[30, 60, 120, 300, 600, 1800, 3600],
        )
        db_errors_total = Counter(
            "codetune_db_errors_total",
            "Total database operation errors",
            ["operation"],
        )

        start_http_server(resolved_port)
        logger.info("Prometheus metrics server started on port %d", resolved_port)
    except ImportError:
        logger.warning(
            "prometheus-client not installed; run: pip install prometheus-client"
        )
        return False
    except Exception:
        logger.exception("Failed to start Prometheus metrics server")
        return False
    else:
        return True


def init_observability(flask_app: Any | None = None) -> None:
    """Convenience wrapper — initialise Sentry and Prometheus."""
    init_sentry(flask_app=flask_app)
    init_prometheus()
