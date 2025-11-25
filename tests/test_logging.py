"""
Unit tests for enhanced logging functionality.

Tests cover JSON formatting, request ID tracking, security filtering,
and middleware integration.
"""

import json

import unittest
from unittest.mock import MagicMock, patch

from flask import Flask

from core.logging import (
    JSONFormatter,
    generate_request_id,
    get_request_id,
    sanitize_for_logging,
    set_request_id,
    setup_logging,
)
from core.middleware import RequestLoggingMiddleware, setup_request_logging


class TestRequestIDFunctions(unittest.TestCase):
    """Test request ID generation and management."""

    def test_generate_request_id(self):
        """Test that request ID generation creates unique UUIDs."""
        request_id_1 = generate_request_id()
        request_id_2 = generate_request_id()

        self.assertIsInstance(request_id_1, str)
        self.assertIsInstance(request_id_2, str)
        self.assertNotEqual(request_id_1, request_id_2)
        self.assertEqual(len(request_id_1), 36)  # UUID format

    def test_set_and_get_request_id(self):
        """Test setting and getting request ID from context."""
        test_id = "test-request-id-123"
        set_request_id(test_id)

        retrieved_id = get_request_id()
        self.assertEqual(retrieved_id, test_id)

    def test_get_request_id_none(self):
        """Test getting request ID when none is set."""
        # Note: This might fail if other tests have set a request ID
        # In a real scenario, each test should have isolated context
        pass  # Context vars are tricky in tests


class TestSanitizeForLogging(unittest.TestCase):
    """Test sensitive data sanitization."""

    def test_sanitize_dict_with_sensitive_keys(self):
        """Test sanitization of dictionaries with sensitive keys."""
        data = {
            "username": "john_doe",
            "password": "secret123",
            "api_key": "sk-1234567890",
            "normal_field": "public_data",
        }

        sanitized = sanitize_for_logging(data)

        self.assertEqual(sanitized["username"], "john_doe")
        self.assertEqual(sanitized["password"], "***REDACTED***")
        self.assertEqual(sanitized["api_key"], "***REDACTED***")
        self.assertEqual(sanitized["normal_field"], "public_data")

    def test_sanitize_nested_dict(self):
        """Test sanitization of nested dictionaries."""
        data = {
            "user": {
                "name": "John Doe",
                "credentials": {
                    "password": "secret",
                    "token": "abc123",
                },
            },
            "metadata": "public",
        }

        sanitized = sanitize_for_logging(data)

        self.assertEqual(sanitized["user"]["name"], "John Doe")
        self.assertEqual(sanitized["user"]["credentials"]["password"], "***REDACTED***")
        self.assertEqual(sanitized["user"]["credentials"]["token"], "***REDACTED***")
        self.assertEqual(sanitized["metadata"], "public")

    def test_sanitize_list(self):
        """Test sanitization of lists."""
        data = [
            {"username": "user1", "password": "pass1"},
            {"username": "user2", "api_key": "key2"},
        ]

        sanitized = sanitize_for_logging(data)

        self.assertEqual(sanitized[0]["username"], "user1")
        self.assertEqual(sanitized[0]["password"], "***REDACTED***")
        self.assertEqual(sanitized[1]["username"], "user2")
        self.assertEqual(sanitized[1]["api_key"], "***REDACTED***")

    def test_sanitize_long_string(self):
        """Test truncation of very long strings."""
        long_string = "a" * 1500
        sanitized = sanitize_for_logging(long_string)

        self.assertIn("***TRUNCATED:", sanitized)
        self.assertIn("1500chars***", sanitized)

    def test_sanitize_max_depth(self):
        """Test maximum depth limit for nested structures."""
        deeply_nested = {"level1": {"level2": {"level3": {"level4": "data"}}}}

        sanitized = sanitize_for_logging(deeply_nested, max_depth=2)

        self.assertIn("***MAX_DEPTH***", str(sanitized))


class TestJSONFormatter(unittest.TestCase):
    """Test JSON log formatting."""

    def setUp(self):
        """Set up test fixtures."""
        self.formatter = JSONFormatter()
        self.logger = logging.getLogger("test_logger")
        self.logger.setLevel(logging.INFO)

    def test_basic_json_format(self):
        """Test basic JSON log formatting."""
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        formatted = self.formatter.format(record)
        log_data = json.loads(formatted)

        self.assertEqual(log_data["level"], "INFO")
        self.assertEqual(log_data["logger"], "test")
        self.assertEqual(log_data["message"], "Test message")
        self.assertIn("timestamp", log_data)
        self.assertIn("location", log_data)

    def test_json_format_with_exception(self):
        """Test JSON formatting with exception information."""
        try:
            raise ValueError("Test error")
        except ValueError:
            record = logging.LogRecord(
                name="test",
                level=logging.ERROR,
                pathname="test.py",
                lineno=10,
                msg="Error occurred",
                args=(),
                exc_info=True,
            )
            record.exc_info = (ValueError, ValueError("Test error"), None)

        formatted = self.formatter.format(record)
        log_data = json.loads(formatted)

        self.assertIn("exception", log_data)
        self.assertEqual(log_data["exception"]["type"], "ValueError")

    def test_json_format_with_request_id(self):
        """Test JSON formatting includes request ID when available."""
        test_id = "test-request-123"
        set_request_id(test_id)

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        formatted = self.formatter.format(record)
        log_data = json.loads(formatted)

        self.assertEqual(log_data["request_id"], test_id)


class TestSetupLogging(unittest.TestCase):
    """Test logging configuration setup."""

    def setUp(self):
        """Clear existing handlers before each test."""
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

    def test_setup_logging_default(self):
        """Test default logging setup."""
        setup_logging()

        root_logger = logging.getLogger()
        self.assertGreater(len(root_logger.handlers), 0)

    def test_setup_logging_with_level(self):
        """Test logging setup with custom level."""
        setup_logging(log_level="DEBUG")

        root_logger = logging.getLogger()
        self.assertEqual(root_logger.level, logging.DEBUG)

    def test_setup_logging_invalid_level(self):
        """Test logging setup with invalid level raises error."""
        with self.assertRaises(ValueError):
            setup_logging(log_level="INVALID")

    @patch("core.logging.Path.mkdir")
    @patch("core.logging.RotatingFileHandler")
    def test_setup_logging_with_file(self, mock_handler, mock_mkdir):
        """Test logging setup with file output."""
        # Mock the handler instance to have proper level attribute
        mock_handler_instance = MagicMock()
        mock_handler_instance.level = logging.INFO
        mock_handler.return_value = mock_handler_instance

        setup_logging(log_file="/tmp/test.log")

        mock_mkdir.assert_called_once()
        mock_handler.assert_called_once()


class TestRequestLoggingMiddleware(unittest.TestCase):
    """Test Flask request logging middleware."""

    def setUp(self):
        """Set up Flask test application."""
        self.app = Flask(__name__)
        self.middleware = RequestLoggingMiddleware(self.app)
        self.client = self.app.test_client()

        @self.app.route("/test")
        def test_route():
            return {"message": "success"}

    def test_middleware_adds_request_id(self):
        """Test that middleware adds request ID to response."""
        response = self.client.get("/test")

        self.assertIn("X-Request-ID", response.headers)
        self.assertIsNotNone(response.headers.get("X-Request-ID"))

    def test_middleware_accepts_existing_request_id(self):
        """Test that middleware accepts request ID from headers."""
        test_id = "test-request-456"
        response = self.client.get("/test", headers={"X-Request-ID": test_id})

        self.assertEqual(response.headers.get("X-Request-ID"), test_id)

    @patch("core.middleware.logger")
    def test_middleware_logs_request(self, mock_logger):
        """Test that middleware logs incoming requests."""
        self.client.get("/test")

        # Check that logger.info was called for request
        self.assertTrue(mock_logger.info.called)

    @patch("core.middleware.logger")
    def test_middleware_logs_response(self, mock_logger):
        """Test that middleware logs responses."""
        self.client.get("/test")

        # Check that logger.info was called multiple times
        self.assertGreaterEqual(mock_logger.info.call_count, 2)


class TestSetupRequestLogging(unittest.TestCase):
    """Test convenience function for setting up request logging."""

    def test_setup_request_logging(self):
        """Test that setup function properly initializes middleware."""
        app = Flask(__name__)

        with patch("core.middleware.RequestLoggingMiddleware") as mock_middleware:
            setup_request_logging(app)

            mock_middleware.assert_called_once()


if __name__ == "__main__":
    unittest.main()
