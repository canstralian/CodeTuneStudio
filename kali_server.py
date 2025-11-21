"""Kali Linux Tools API server entrypoint.

This module configures the Flask application used to surface automation
endpoints for the Trading Bot Swarm integration tests. It mirrors the
expected behavior from the upstream repository while enforcing safe
network binding defaults.
"""
from __future__ import annotations

import argparse
import logging
import os
from typing import Any

from flask import Flask, jsonify

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("kali_server")

API_PORT = int(os.environ.get("API_PORT", "5000"))
DEBUG_MODE = os.environ.get("DEBUG_MODE", "0") == "1"


def parse_args() -> argparse.Namespace:
    """Parse command line arguments for the server entrypoint."""

    parser = argparse.ArgumentParser(description="Kali Linux Tools API Server")
    parser.add_argument(
        "--ip",
        default=os.environ.get("API_HOST", "127.0.0.1"),
        help="IP address to bind the API server",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=API_PORT,
        help="Port for the API server",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=DEBUG_MODE,
        help="Run the server in debug mode",
    )
    return parser.parse_args()


@app.get("/health")
def healthcheck() -> Any:
    """Simple health endpoint for monitoring."""

    return jsonify(status="ok")


if __name__ == "__main__":
    args = parse_args()

    # Set configuration from command line arguments
    if args.debug:
        DEBUG_MODE = True
        os.environ["DEBUG_MODE"] = "1"
        logger.setLevel(logging.DEBUG)

    if args.port != API_PORT:
        API_PORT = args.port

    logger.info(f"Starting Kali Linux Tools API Server on {args.ip}:{API_PORT}")
    app.run(host=args.ip, port=API_PORT, debug=DEBUG_MODE)
