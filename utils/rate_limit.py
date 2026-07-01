# SPDX-License-Identifier: MIT
"""
Flask rate-limiting via flask-limiter.

Environment variables:
  RATELIMIT_DEFAULT      — default limit string (default: "200 per day;50 per hour")
  RATELIMIT_STORAGE_URI  — storage backend URI (default: "memory://" for single-process;
                           set to a Redis URL for distributed deployments)

Usage:
    from utils.rate_limit import init_limiter, get_limiter

    # In app initialisation:
    init_limiter(flask_app)

    # On a specific Flask route:
    from flask import Blueprint
    from utils.rate_limit import get_limiter

    bp = Blueprint("api", __name__)

    @bp.route("/train")
    @get_limiter().limit("10 per minute")
    def train():
        ...
"""

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

_limiter: object | None = None


def init_limiter(app: Any) -> object | None:
    """Attach flask-limiter to *app*; return Limiter or None on failure."""
    global _limiter  # noqa: PLW0603

    raw = os.environ.get("RATELIMIT_DEFAULT", "200 per day;50 per hour")
    default_limits = [limit.strip() for limit in raw.split(";") if limit.strip()]
    storage_uri = os.environ.get("RATELIMIT_STORAGE_URI", "memory://")

    try:
        from flask_limiter import Limiter  # noqa: PLC0415
        from flask_limiter.util import get_remote_address  # noqa: PLC0415

        _limiter = Limiter(
            app=app,
            key_func=get_remote_address,
            default_limits=default_limits,
            storage_uri=storage_uri,
            strategy="fixed-window",
        )
        logger.info("Rate limiter initialised (storage=%s)", storage_uri)
    except ImportError:
        logger.warning("flask-limiter not installed; run: pip install flask-limiter")
        return None
    except Exception:
        logger.exception("Failed to initialise rate limiter")
        return None
    else:
        return _limiter


def get_limiter() -> object | None:
    """Return the initialised Limiter instance, or None if not yet initialised."""
    return _limiter
