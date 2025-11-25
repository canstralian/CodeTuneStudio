"""
Flask middleware for request tracking and logging.

This module provides middleware components for Flask applications to handle
request ID generation, propagation, and logging of HTTP requests/responses.
"""

import time
from functools import wraps
from typing import Any, Callable, Dict, Optional

from flask import Flask, Response, g, request

from core.logging import (
    generate_request_id,
    get_logger,
    sanitize_for_logging,
    set_request_id,
)

logger = get_logger(__name__)


class RequestLoggingMiddleware:
    """
    Middleware for logging HTTP requests and responses with request IDs.

    This middleware automatically generates a unique request ID for each
    incoming request, logs request/response details, and ensures the request
    ID is propagated throughout the application context.
    """

    def __init__(
        self,
        app: Optional[Flask] = None,
        request_id_header: str = "X-Request-ID",
    ):
        """
        Initialize the request logging middleware.

        Args:
            app: Flask application instance (optional, can be set via init_app).
            request_id_header: HTTP header name for request ID.
        """
        self.request_id_header = request_id_header
        if app:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """
        Initialize the middleware with a Flask application.

        Args:
            app: Flask application instance.
        """
        app.before_request(self._before_request)
        app.after_request(self._after_request)
        app.teardown_request(self._teardown_request)

    def _before_request(self) -> None:
        """
        Handle request initialization before processing.

        Generates or extracts request ID, stores it in context,
        and logs the incoming request.
        """
        # Get or generate request ID
        request_id = request.headers.get(self.request_id_header)
        if not request_id:
            request_id = generate_request_id()

        # Store in context for the current request
        g.request_id = request_id
        set_request_id(request_id)

        # Store request start time
        g.request_start_time = time.time()

        # Log incoming request
        logger.info(
            f"Incoming request: {request.method} {request.path}",
            extra={
                "method": request.method,
                "path": request.path,
                "remote_addr": request.remote_addr,
                "user_agent": request.headers.get("User-Agent"),
            },
        )

    def _after_request(self, response: Response) -> Response:
        """
        Handle request finalization after processing.

        Adds request ID to response headers and logs the response.

        Args:
            response: Flask response object.

        Returns:
            Modified response with request ID header.
        """
        # Add request ID to response headers
        request_id = getattr(g, "request_id", None)
        if request_id:
            response.headers[self.request_id_header] = request_id

        # Calculate request duration
        start_time = getattr(g, "request_start_time", None)
        duration = time.time() - start_time if start_time else None

        # Log response
        logger.info(
            f"Request completed: {request.method} {request.path} - "
            f"Status: {response.status_code}",
            extra={
                "method": request.method,
                "path": request.path,
                "status_code": response.status_code,
                "duration_ms": round(duration * 1000, 2) if duration else None,
            },
        )

        return response

    def _teardown_request(self, exception: Optional[Exception] = None) -> None:
        """
        Handle request teardown and cleanup.

        Logs any exceptions that occurred during request processing.

        Args:
            exception: Exception that occurred during request processing, if any.
        """
        if exception:
            logger.error(
                f"Request failed with exception: {exception}",
                exc_info=True,
                extra={
                    "method": request.method,
                    "path": request.path,
                },
            )


def with_request_logging(
    log_args: bool = False,
    log_result: bool = False,
) -> Callable:
    """
    Decorator for logging function calls with request context.

    This decorator logs function entry and exit, optionally including
    arguments and return values, with the current request ID.

    Note: When log_args or log_result is True, the data is automatically
    sanitized using sanitize_for_logging() to prevent accidental exposure
    of sensitive information like passwords, API keys, or tokens.

    Args:
        log_args: Whether to log function arguments (default: False).
        log_result: Whether to log function return value (default: False).

    Returns:
        Decorated function with logging.

    Example:
        @with_request_logging(log_args=True)
        def process_data(data: dict) -> dict:
            # Process data
            return processed_data
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            func_name = f"{func.__module__}.{func.__qualname__}"

            extra_info: Dict[str, Any] = {"function": func_name}
            if log_args:
                # Sanitize args and kwargs to prevent logging sensitive data
                extra_info["args"] = sanitize_for_logging(args)
                extra_info["kwargs"] = sanitize_for_logging(kwargs)

            logger.debug(f"Entering {func_name}", extra=extra_info)

            try:
                result = func(*args, **kwargs)

                if log_result:
                    # Sanitize result to prevent logging sensitive data
                    extra_info["result"] = sanitize_for_logging(result)

                logger.debug(f"Exiting {func_name}", extra=extra_info)

                return result
            except Exception as e:
                logger.error(
                    f"Exception in {func_name}: {e}",
                    exc_info=True,
                    extra=extra_info,
                )
                raise

        return wrapper

    return decorator


def setup_request_logging(app: Flask) -> None:
    """
    Set up request logging middleware for a Flask application.

    This is a convenience function that initializes the RequestLoggingMiddleware
    with default settings.

    Args:
        app: Flask application instance.

    Example:
        app = Flask(__name__)
        setup_request_logging(app)
    """
    middleware = RequestLoggingMiddleware(request_id_header="X-Request-ID")
    middleware.init_app(app)

    logger.info("Request logging middleware initialized")
