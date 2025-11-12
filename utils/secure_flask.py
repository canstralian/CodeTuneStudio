"""
Secure Flask API patterns and utilities.

This module provides secure patterns for Flask API endpoints including
authentication, rate limiting, and input validation.
"""

from functools import wraps
from flask import request, jsonify
import secrets
import os
import logging
from typing import Callable, Optional, Any, Dict

logger = logging.getLogger(__name__)


def require_api_key(f: Callable) -> Callable:
    """
    Decorator to require API key authentication for Flask endpoints.
    
    Expects API key in X-API-Key header. Compares against API_KEY
    environment variable using constant-time comparison.
    
    Usage:
        @app.route('/api/endpoint')
        @require_api_key
        def protected_endpoint():
            return jsonify({'data': 'protected'})
    
    Args:
        f: Flask route function to protect
        
    Returns:
        Decorated function with authentication
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        expected_key = os.environ.get('API_KEY')
        
        if not expected_key:
            logger.error("API_KEY environment variable not set")
            return jsonify({'error': 'Server configuration error'}), 500
        
        if not api_key:
            logger.warning("API request without API key")
            return jsonify({'error': 'API key required'}), 401
        
        # Use constant-time comparison to prevent timing attacks
        if not secrets.compare_digest(api_key, expected_key):
            logger.warning(f"Invalid API key attempted from {request.remote_addr}")
            return jsonify({'error': 'Invalid API key'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function


def validate_json_input(required_fields: list) -> Callable:
    """
    Decorator to validate JSON input for Flask endpoints.
    
    Ensures request contains valid JSON and all required fields are present.
    
    Usage:
        @app.route('/api/endpoint', methods=['POST'])
        @validate_json_input(['field1', 'field2'])
        def endpoint():
            data = request.get_json()
            # All required fields are guaranteed to exist
    
    Args:
        required_fields: List of required field names
        
    Returns:
        Decorator function
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({
                    'error': 'Content-Type must be application/json'
                }), 400
            
            try:
                data = request.get_json()
            except Exception as e:
                logger.warning(f"Invalid JSON in request: {e}")
                return jsonify({'error': 'Invalid JSON'}), 400
            
            missing_fields = [
                field for field in required_fields
                if field not in data
            ]
            
            if missing_fields:
                return jsonify({
                    'error': f'Missing required fields: {", ".join(missing_fields)}'
                }), 400
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator


def add_security_headers(response):
    """
    Add security headers to Flask response.
    
    Should be registered as an after_request handler:
        app.after_request(add_security_headers)
    
    Args:
        response: Flask response object
        
    Returns:
        Response with security headers added
    """
    # Prevent MIME type sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # Prevent clickjacking
    response.headers['X-Frame-Options'] = 'DENY'
    
    # Enable XSS protection
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Control referrer information
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Enforce HTTPS (in production)
    if not os.environ.get('FLASK_ENV') == 'development':
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    return response


def sanitize_request_data(data: Dict[str, Any], max_length: int = 10000) -> Dict[str, Any]:
    """
    Sanitize request data to prevent injection attacks.
    
    Args:
        data: Request data dictionary
        max_length: Maximum length for string values
        
    Returns:
        Sanitized data dictionary
        
    Raises:
        ValueError: If data validation fails
    """
    from utils.security import InputValidator
    
    sanitized = {}
    
    for key, value in data.items():
        # Sanitize keys
        safe_key = InputValidator.sanitize_string(key, max_length=100)
        
        # Sanitize values based on type
        if isinstance(value, str):
            if len(value) > max_length:
                raise ValueError(f"Field '{safe_key}' exceeds maximum length")
            sanitized[safe_key] = InputValidator.sanitize_string(value, max_length)
        elif isinstance(value, (int, float, bool)):
            sanitized[safe_key] = value
        elif isinstance(value, dict):
            sanitized[safe_key] = sanitize_request_data(value, max_length)
        elif isinstance(value, list):
            sanitized[safe_key] = [
                sanitize_request_data({'item': item}, max_length).get('item')
                if isinstance(item, dict)
                else InputValidator.sanitize_string(str(item), max_length)
                for item in value[:100]  # Limit list size
            ]
        else:
            # Convert other types to string and sanitize
            sanitized[safe_key] = InputValidator.sanitize_string(
                str(value), max_length
            )
    
    return sanitized


class SecureFlaskConfig:
    """
    Secure configuration for Flask applications.
    
    Usage:
        app.config.from_object(SecureFlaskConfig)
    """
    
    # Security settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    
    # Session security
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') != 'development'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Database security
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 1800,  # Recycle connections every 30 minutes
        'pool_pre_ping': True,  # Verify connections before use
        'max_overflow': 20,
        'pool_timeout': 30
    }
    
    # CSRF protection (requires Flask-WTF)
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None  # Or set appropriate timeout
    
    # Rate limiting (requires Flask-Limiter)
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'memory://')
    RATELIMIT_STRATEGY = 'fixed-window'


def create_secure_flask_app():
    """
    Create a Flask app with security best practices enabled.
    
    Returns:
        Configured Flask application
    """
    from flask import Flask
    
    app = Flask(__name__)
    app.config.from_object(SecureFlaskConfig)
    
    # Add security headers to all responses
    app.after_request(add_security_headers)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Error handlers
    @app.errorhandler(Exception)
    def handle_error(error):
        """Handle errors without exposing internal details."""
        from utils.security import OutputSanitizer
        
        safe_message = OutputSanitizer.sanitize_error_message(error)
        
        if isinstance(error, ValueError):
            return jsonify({'error': safe_message}), 400
        elif isinstance(error, PermissionError):
            return jsonify({'error': safe_message}), 403
        elif isinstance(error, FileNotFoundError):
            return jsonify({'error': safe_message}), 404
        else:
            return jsonify({'error': safe_message}), 500
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        """Handle rate limit errors."""
        return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429
    
    return app


# Example secure endpoint implementation
def create_example_secure_endpoint(app):
    """
    Example of a secure API endpoint implementation.
    
    This demonstrates proper use of authentication, validation,
    rate limiting, and error handling.
    
    Args:
        app: Flask application instance
    """
    @app.route('/api/example', methods=['POST'])
    @require_api_key
    @validate_json_input(['data', 'operation'])
    def secure_endpoint():
        """
        Example secure endpoint with proper validation.
        
        Expected JSON body:
        {
            "data": "user data",
            "operation": "operation_type"
        }
        """
        try:
            # Get and sanitize request data
            raw_data = request.get_json()
            data = sanitize_request_data(raw_data)
            
            # Validate operation type
            from utils.security import InputValidator
            
            allowed_operations = ['analyze', 'transform', 'validate']
            errors = InputValidator.validate_enum(
                data['operation'],
                allowed_operations,
                'operation'
            )
            
            if errors:
                return jsonify({'error': errors[0]}), 400
            
            # Process request (with proper error handling)
            result = process_secure_operation(data)
            
            return jsonify(result), 200
            
        except ValueError as e:
            logger.warning(f"ValueError in secure endpoint: {e}", exc_info=True)
            return jsonify({'error': 'Invalid request data'}), 400
        except Exception as e:
            logger.error(f"Error in secure endpoint: {e}", exc_info=True)
            return jsonify({'error': 'An internal error occurred'}), 500


def process_secure_operation(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Example of secure data processing.
    
    Args:
        data: Validated and sanitized request data
        
    Returns:
        Processing results
    """
    # Implement actual processing logic here
    return {
        'status': 'success',
        'message': f"Processed operation: {data['operation']}",
        'data': data['data']
    }


# Module-level exports
__all__ = [
    'require_api_key',
    'validate_json_input',
    'add_security_headers',
    'sanitize_request_data',
    'SecureFlaskConfig',
    'create_secure_flask_app',
    'create_example_secure_endpoint',
]
