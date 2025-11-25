#!/usr/bin/env python
"""
Flask application demonstrating request logging middleware.

This demo shows how the logging middleware automatically:
- Generates unique request IDs
- Logs incoming requests
- Logs responses with duration
- Propagates request IDs through the system
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# noqa: E402 - imports must come after path modification
from flask import Flask, jsonify  # noqa: E402

from core.logging import get_logger, setup_logging  # noqa: E402
from core.middleware import setup_request_logging  # noqa: E402

# Configure logging
setup_logging(log_level="INFO", json_format=False)

# Create Flask app
app = Flask(__name__)

# Setup request logging middleware
setup_request_logging(app)

# Get logger
logger = get_logger(__name__)


@app.route("/")
def index():
    """Home endpoint."""
    logger.info("Home page accessed")
    return jsonify({"message": "Welcome to CodeTune Studio Logging Demo!"})


@app.route("/api/data")
def get_data():
    """Sample API endpoint."""
    logger.info("Fetching data")
    data = {"items": [1, 2, 3, 4, 5], "count": 5}
    logger.debug(f"Returning {data['count']} items")
    return jsonify(data)


@app.route("/api/error")
def trigger_error():
    """Endpoint that demonstrates error logging."""
    logger.warning("About to trigger an error")
    try:
        _ = 1 / 0
    except ZeroDivisionError as e:
        logger.error(f"Error occurred: {e}", exc_info=True)
        return jsonify({"error": "Division by zero"}), 500


@app.route("/api/user/<user_id>")
def get_user(user_id):
    """User endpoint demonstrating structured logging."""
    logger.info("Fetching user data", extra={"user_id": user_id})

    # Simulate user data (with sensitive information)
    user_data = {
        "id": user_id,
        "username": f"user_{user_id}",
        "email": f"user_{user_id}@example.com",
    }

    logger.info("User data retrieved", extra={"user_id": user_id})
    return jsonify(user_data)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Flask Logging Demo - Starting Server")
    print("=" * 60)
    print("Visit the following endpoints to see logging in action:")
    print("  - http://127.0.0.1:5001/")
    print("  - http://127.0.0.1:5001/api/data")
    print("  - http://127.0.0.1:5001/api/user/123")
    print("  - http://127.0.0.1:5001/api/error")
    print("\nWatch the console for logs with request IDs!")
    print("=" * 60 + "\n")

    app.run(host="127.0.0.1", port=5001, debug=False)
