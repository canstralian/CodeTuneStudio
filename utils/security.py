"""
Security utilities for CodeTuneStudio.

This module provides security utilities for input validation, sanitization,
and safe code execution patterns to prevent security vulnerabilities.
"""

import re
import html
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class InputValidator:
    """
    Validator for user inputs with comprehensive security checks.
    
    Prevents injection attacks, validates data types, and enforces
    reasonable constraints on input values.
    """
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """
        Sanitize string inputs by removing potentially dangerous characters.
        
        Args:
            value: Input string to sanitize
            max_length: Maximum allowed string length
            
        Returns:
            Sanitized string safe for database/display
            
        Raises:
            ValueError: If input is not a string or exceeds max length
        """
        if not isinstance(value, str):
            raise ValueError("Input must be a string")
        
        if len(value) > max_length:
            raise ValueError(f"Input exceeds maximum length of {max_length}")
        
        # Remove potentially dangerous characters while preserving alphanumerics,
        # spaces, and common safe punctuation
        sanitized = re.sub(r"[^\w\s\.\-_@,;:!?()'\"]", "", value.strip())
        
        return sanitized
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent directory traversal attacks.
        
        Args:
            filename: Original filename
            
        Returns:
            Safe filename without path components
            
        Raises:
            ValueError: If filename is invalid
        """
        if not isinstance(filename, str) or not filename:
            raise ValueError("Filename must be a non-empty string")
        
        # Remove path components and dangerous characters
        safe_name = re.sub(r"[^\w\.\-]", "_", filename)
        
        # Remove leading dots to prevent hidden files
        safe_name = safe_name.lstrip(".")
        
        # Prevent empty filename after sanitization
        if not safe_name:
            raise ValueError("Filename becomes empty after sanitization")
        
        return safe_name
    
    @staticmethod
    def validate_numeric_range(
        value: float,
        min_val: float,
        max_val: float,
        param_name: str = "parameter"
    ) -> List[str]:
        """
        Validate numeric parameter within acceptable range.
        
        Args:
            value: Value to validate
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            param_name: Parameter name for error messages
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        if not isinstance(value, (int, float)):
            errors.append(f"{param_name} must be numeric")
            return errors
        
        if value < min_val or value > max_val:
            errors.append(
                f"{param_name} must be between {min_val} and {max_val}"
            )
        
        return errors
    
    @staticmethod
    def validate_enum(
        value: str,
        allowed_values: List[str],
        param_name: str = "parameter"
    ) -> List[str]:
        """
        Validate that value is in allowed list.
        
        Args:
            value: Value to validate
            allowed_values: List of allowed values
            param_name: Parameter name for error messages
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        if value not in allowed_values:
            errors.append(
                f"{param_name} must be one of: {', '.join(allowed_values)}"
            )
        
        return errors


class OutputSanitizer:
    """Sanitizer for output data to prevent XSS and injection attacks."""
    
    @staticmethod
    def escape_html(data: str) -> str:
        """
        Escape HTML characters in output data.
        
        Args:
            data: String to escape
            
        Returns:
            HTML-escaped string
        """
        return html.escape(data, quote=True)
    
    @staticmethod
    def sanitize_error_message(error: Exception) -> str:
        """
        Sanitize error messages to prevent information disclosure.
        
        Args:
            error: Exception to sanitize
            
        Returns:
            Safe error message without internal details
        """
        # Log the full error internally
        logger.error(f"Error occurred: {error}", exc_info=True)
        
        # Return generic message to user
        if isinstance(error, ValueError):
            return "Invalid input provided"
        elif isinstance(error, PermissionError):
            return "Access denied"
        elif isinstance(error, FileNotFoundError):
            return "Resource not found"
        else:
            return "An internal error occurred"


class SecureCodeExecutor:
    """
    Secure code execution wrapper with sandboxing and timeout enforcement.
    
    This class provides a safe interface for executing code with proper
    security controls. It should be used instead of direct exec() calls.
    
    Note: This is a basic implementation. For production use, consider
    using more robust sandboxing solutions like:
    - RestrictedPython for Python code
    - Docker containers for complete isolation
    - VM-based sandboxes for maximum security
    """
    
    def __init__(self, timeout_seconds: int = 30):
        """
        Initialize secure code executor.
        
        Args:
            timeout_seconds: Maximum execution time allowed
        """
        self.timeout_seconds = timeout_seconds
    
    def validate_code(self, code: str) -> List[str]:
        """
        Validate code for dangerous patterns before execution.
        
        Args:
            code: Code string to validate
            
        Returns:
            List of security warnings/errors
        """
        warnings = []
        
        if not isinstance(code, str):
            warnings.append("Code must be a string")
            return warnings
        
        # Check for dangerous imports
        dangerous_imports = [
            "os", "sys", "subprocess", "socket", "eval", "exec",
            "compile", "__import__", "open", "file"
        ]
        
        for dangerous in dangerous_imports:
            if re.search(rf"\b{dangerous}\b", code):
                warnings.append(
                    f"Potentially dangerous operation detected: {dangerous}"
                )
        
        return warnings
    
    def execute_with_timeout(
        self,
        code: str,
        globals_dict: Optional[Dict[str, Any]] = None,
        locals_dict: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute code with timeout enforcement.
        
        WARNING: This is a simplified implementation for demonstration.
        Production code should use proper sandboxing solutions.
        
        Args:
            code: Code to execute
            globals_dict: Global namespace for execution
            locals_dict: Local namespace for execution
            
        Returns:
            Dictionary with execution results and any errors
            
        Raises:
            SecurityError: If code fails validation
        """
        # Validate code first
        warnings = self.validate_code(code)
        if warnings:
            raise SecurityError(
                f"Code validation failed: {', '.join(warnings)}"
            )
        
        # For production, this should use proper sandboxing
        # This is a placeholder that should NOT be used as-is
        return {
            "status": "error",
            "message": "Direct code execution is disabled for security. "
                      "Please use a proper sandboxing solution like "
                      "RestrictedPython or Docker containers."
        }


class SecurityError(Exception):
    """Custom exception for security-related errors."""
    pass


class RateLimiter:
    """
    Simple in-memory rate limiter for API endpoints.
    
    For production use, consider using Redis-backed rate limiting
    with Flask-Limiter or similar libraries.
    """
    
    def __init__(self):
        """Initialize rate limiter."""
        self._requests = {}
    
    def is_allowed(
        self,
        identifier: str,
        max_requests: int,
        window_seconds: int
    ) -> bool:
        """
        Check if request is allowed based on rate limit.
        
        Args:
            identifier: Unique identifier (IP, user ID, API key)
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
            
        Returns:
            True if request is allowed, False otherwise
        """
        import time
        
        current_time = time.time()
        
        if identifier not in self._requests:
            self._requests[identifier] = []
        
        # Remove old requests outside the window
        self._requests[identifier] = [
            timestamp for timestamp in self._requests[identifier]
            if current_time - timestamp < window_seconds
        ]
        
        # Check if limit exceeded
        if len(self._requests[identifier]) >= max_requests:
            return False
        
        # Record this request
        self._requests[identifier].append(current_time)
        return True


# Module-level exports
__all__ = [
    "InputValidator",
    "OutputSanitizer",
    "SecureCodeExecutor",
    "SecurityError",
    "RateLimiter",
]
