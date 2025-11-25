#!/usr/bin/env python
"""
Demonstration of the enhanced logging system in CodeTune Studio.

This script shows various logging features including:
- JSON formatted output
- Request ID tracking
- Sensitive data sanitization
- Different log levels
- Structured logging with extra fields
"""

import sys
from pathlib import Path

# Add parent directory to path to import core modules
sys.path.insert(0, str(Path(__file__).parent.parent))

# noqa: E402 - imports must come after path modification
from core.logging import (  # noqa: E402
    generate_request_id,
    get_logger,
    sanitize_for_logging,
    set_request_id,
    setup_logging,
)


def demonstrate_basic_logging():
    """Demonstrate basic logging functionality."""
    print("\n" + "=" * 60)
    print("1. Basic Logging Examples")
    print("=" * 60)

    logger = get_logger(__name__)

    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")


def demonstrate_request_id_tracking():
    """Demonstrate request ID tracking."""
    print("\n" + "=" * 60)
    print("2. Request ID Tracking")
    print("=" * 60)

    logger = get_logger(__name__)

    # Simulate multiple requests
    for i in range(3):
        request_id = generate_request_id()
        set_request_id(request_id)

        logger.info(
            f"Processing request #{i + 1}",
            extra={"request_number": i + 1, "user_id": f"user_{i}"},
        )


def demonstrate_sensitive_data_sanitization():
    """Demonstrate automatic sensitive data sanitization."""
    print("\n" + "=" * 60)
    print("3. Sensitive Data Sanitization")
    print("=" * 60)

    logger = get_logger(__name__)

    # Sample data with sensitive information
    user_data = {
        "username": "john_doe",
        "email": "john@example.com",
        "password": "super_secret_password",
        "api_key": "sk-1234567890abcdef",
        "profile": {
            "name": "John Doe",
            "token": "bearer_token_xyz",
            "preferences": {"theme": "dark", "notifications": True},
        },
    }

    # ⚠️ WARNING: This is for demonstration purposes ONLY!
    # NEVER print or log unsanitized user data in production code!
    print("\nBefore sanitization (DO NOT DO THIS IN PRODUCTION):")
    # print(user_data)  # Commented out to prevent accidental sensitive data exposure
    print("(Sensitive data would be shown here if uncommented)")

    # Log with sanitization (recommended)
    print("\nAfter sanitization (RECOMMENDED):")
    sanitized = sanitize_for_logging(user_data)
    print(sanitized)

    logger.info("User data processed", extra={"user_data": sanitized})


def demonstrate_structured_logging():
    """Demonstrate structured logging with extra fields."""
    print("\n" + "=" * 60)
    print("4. Structured Logging with Extra Fields")
    print("=" * 60)

    logger = get_logger(__name__)

    # Simulate processing with metrics
    logger.info(
        "Training started",
        extra={
            "model_type": "CodeT5",
            "dataset": "python_code",
            "batch_size": 32,
            "learning_rate": 5e-5,
        },
    )

    logger.info(
        "Epoch completed",
        extra={
            "epoch": 1,
            "train_loss": 0.234,
            "eval_loss": 0.189,
            "duration_seconds": 123.45,
        },
    )


def demonstrate_error_logging():
    """Demonstrate error logging with exception information."""
    print("\n" + "=" * 60)
    print("5. Error Logging with Exception Information")
    print("=" * 60)

    logger = get_logger(__name__)

    try:
        # Simulate an error
        _ = 1 / 0  # noqa: F841
    except ZeroDivisionError as e:
        logger.error(
            f"Division error occurred: {e}",
            exc_info=True,
            extra={
                "operation": "division",
                "numerator": 1,
                "denominator": 0,
            },
        )


def demonstrate_json_output():
    """Demonstrate JSON formatted output."""
    print("\n" + "=" * 60)
    print("6. JSON Formatted Output")
    print("=" * 60)

    # Reconfigure logging with JSON format
    setup_logging(log_level="INFO", json_format=True)

    logger = get_logger(__name__)

    request_id = generate_request_id()
    set_request_id(request_id)

    logger.info(
        "Request processed successfully",
        extra={
            "method": "POST",
            "path": "/api/train",
            "status_code": 200,
            "duration_ms": 45.67,
        },
    )


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 60)
    print("CodeTune Studio - Enhanced Logging System Demo")
    print("=" * 60)

    # Start with human-readable format
    setup_logging(log_level="DEBUG", enable_color=True, json_format=False)

    # Run demonstrations
    demonstrate_basic_logging()
    demonstrate_request_id_tracking()
    demonstrate_sensitive_data_sanitization()
    demonstrate_structured_logging()
    demonstrate_error_logging()
    demonstrate_json_output()

    print("\n" + "=" * 60)
    print("Demo completed! Check the output above.")
    print("For more information, see LOGGING.md")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
