"""
Unit tests for security utilities.

Tests input validation, output sanitization, and secure code execution patterns.
"""

import unittest
from utils.security import (
    InputValidator,
    OutputSanitizer,
    SecureCodeExecutor,
    SecurityError,
    RateLimiter,
)


class TestInputValidator(unittest.TestCase):
    """Tests for InputValidator class."""
    
    def test_sanitize_string_valid(self):
        """Test sanitization of valid strings."""
        result = InputValidator.sanitize_string("Hello World!")
        self.assertEqual(result, "Hello World!")
    
    def test_sanitize_string_with_special_chars(self):
        """Test removal of dangerous characters."""
        result = InputValidator.sanitize_string("test<script>alert('xss')</script>")
        self.assertNotIn("<", result)
        self.assertNotIn(">", result)
    
    def test_sanitize_string_max_length(self):
        """Test max length enforcement."""
        with self.assertRaises(ValueError):
            InputValidator.sanitize_string("a" * 2000, max_length=1000)
    
    def test_sanitize_string_invalid_type(self):
        """Test rejection of non-string input."""
        with self.assertRaises(ValueError):
            InputValidator.sanitize_string(123)
    
    def test_sanitize_filename_valid(self):
        """Test sanitization of valid filenames."""
        result = InputValidator.sanitize_filename("test_file.txt")
        self.assertEqual(result, "test_file.txt")
    
    def test_sanitize_filename_path_traversal(self):
        """Test prevention of directory traversal."""
        result = InputValidator.sanitize_filename("../../../etc/passwd")
        self.assertNotIn("..", result)
        self.assertNotIn("/", result)
    
    def test_sanitize_filename_hidden_file(self):
        """Test removal of leading dots."""
        result = InputValidator.sanitize_filename(".hidden")
        self.assertFalse(result.startswith("."))
    
    def test_sanitize_filename_invalid(self):
        """Test rejection of invalid filenames."""
        with self.assertRaises(ValueError):
            InputValidator.sanitize_filename("")
        
        with self.assertRaises(ValueError):
            InputValidator.sanitize_filename(None)
    
    def test_validate_numeric_range_valid(self):
        """Test validation of valid numeric values."""
        errors = InputValidator.validate_numeric_range(5.0, 0.0, 10.0, "test")
        self.assertEqual(len(errors), 0)
    
    def test_validate_numeric_range_invalid_type(self):
        """Test rejection of non-numeric values."""
        errors = InputValidator.validate_numeric_range("5", 0.0, 10.0, "test")
        self.assertGreater(len(errors), 0)
        self.assertIn("numeric", errors[0].lower())
    
    def test_validate_numeric_range_out_of_bounds(self):
        """Test rejection of out-of-range values."""
        errors = InputValidator.validate_numeric_range(15.0, 0.0, 10.0, "test")
        self.assertGreater(len(errors), 0)
        self.assertIn("between", errors[0].lower())
    
    def test_validate_enum_valid(self):
        """Test validation of valid enum values."""
        errors = InputValidator.validate_enum("option1", ["option1", "option2"], "test")
        self.assertEqual(len(errors), 0)
    
    def test_validate_enum_invalid(self):
        """Test rejection of invalid enum values."""
        errors = InputValidator.validate_enum("invalid", ["option1", "option2"], "test")
        self.assertGreater(len(errors), 0)
        self.assertIn("must be one of", errors[0].lower())


class TestOutputSanitizer(unittest.TestCase):
    """Tests for OutputSanitizer class."""
    
    def test_escape_html(self):
        """Test HTML escaping."""
        result = OutputSanitizer.escape_html("<script>alert('xss')</script>")
        self.assertIn("&lt;", result)
        self.assertIn("&gt;", result)
        self.assertNotIn("<script>", result)
    
    def test_escape_html_quotes(self):
        """Test escaping of quotes."""
        result = OutputSanitizer.escape_html('test "quoted" text')
        self.assertIn("&quot;", result)
    
    def test_sanitize_error_message_value_error(self):
        """Test sanitization of ValueError."""
        error = ValueError("Internal database connection failed at host 192.168.1.1")
        result = OutputSanitizer.sanitize_error_message(error)
        self.assertEqual(result, "Invalid input provided")
        self.assertNotIn("192.168.1.1", result)
    
    def test_sanitize_error_message_permission_error(self):
        """Test sanitization of PermissionError."""
        error = PermissionError("Cannot access /etc/secret/file.conf")
        result = OutputSanitizer.sanitize_error_message(error)
        self.assertEqual(result, "Access denied")
        self.assertNotIn("/etc/secret", result)
    
    def test_sanitize_error_message_generic(self):
        """Test sanitization of generic errors."""
        error = RuntimeError("Internal error with stack trace")
        result = OutputSanitizer.sanitize_error_message(error)
        self.assertEqual(result, "An internal error occurred")


class TestSecureCodeExecutor(unittest.TestCase):
    """Tests for SecureCodeExecutor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.executor = SecureCodeExecutor(timeout_seconds=30)
    
    def test_validate_code_safe(self):
        """Test validation of safe code."""
        code = "x = 1 + 2\nprint(x)"
        warnings = self.executor.validate_code(code)
        self.assertEqual(len(warnings), 0)
    
    def test_validate_code_dangerous_import(self):
        """Test detection of dangerous imports."""
        code = "import os\nos.system('rm -rf /')"
        warnings = self.executor.validate_code(code)
        self.assertGreater(len(warnings), 0)
        self.assertTrue(any("os" in w for w in warnings))
    
    def test_validate_code_eval(self):
        """Test detection of eval()."""
        code = "eval('malicious code')"
        warnings = self.executor.validate_code(code)
        self.assertGreater(len(warnings), 0)
        self.assertTrue(any("eval" in w for w in warnings))
    
    def test_validate_code_exec(self):
        """Test detection of exec()."""
        code = "exec('malicious code')"
        warnings = self.executor.validate_code(code)
        self.assertGreater(len(warnings), 0)
        self.assertTrue(any("exec" in w for w in warnings))
    
    def test_validate_code_subprocess(self):
        """Test detection of subprocess."""
        code = "import subprocess\nsubprocess.call(['ls'])"
        warnings = self.executor.validate_code(code)
        self.assertGreater(len(warnings), 0)
    
    def test_validate_code_invalid_type(self):
        """Test rejection of non-string code."""
        warnings = self.executor.validate_code(123)
        self.assertGreater(len(warnings), 0)
        self.assertIn("string", warnings[0].lower())
    
    def test_execute_with_timeout_disabled(self):
        """Test that direct execution is disabled."""
        code = "x = 1 + 2"
        result = self.executor.execute_with_timeout(code)
        self.assertEqual(result["status"], "error")
        self.assertIn("disabled", result["message"].lower())
    
    def test_execute_validation_failure(self):
        """Test that validation failures raise SecurityError."""
        code = "import os\nos.system('ls')"
        with self.assertRaises(SecurityError):
            self.executor.execute_with_timeout(code)


class TestRateLimiter(unittest.TestCase):
    """Tests for RateLimiter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.limiter = RateLimiter()
    
    def test_is_allowed_first_request(self):
        """Test that first request is allowed."""
        result = self.limiter.is_allowed("user1", max_requests=5, window_seconds=60)
        self.assertTrue(result)
    
    def test_is_allowed_within_limit(self):
        """Test that requests within limit are allowed."""
        identifier = "user2"
        for i in range(5):
            result = self.limiter.is_allowed(identifier, max_requests=5, window_seconds=60)
            self.assertTrue(result)
    
    def test_is_allowed_exceeds_limit(self):
        """Test that exceeding limit is blocked."""
        identifier = "user3"
        max_requests = 3
        
        # Use up the limit
        for i in range(max_requests):
            self.limiter.is_allowed(identifier, max_requests=max_requests, window_seconds=60)
        
        # Next request should be blocked
        result = self.limiter.is_allowed(identifier, max_requests=max_requests, window_seconds=60)
        self.assertFalse(result)
    
    def test_is_allowed_different_identifiers(self):
        """Test that different identifiers are tracked separately."""
        self.limiter.is_allowed("user4", max_requests=1, window_seconds=60)
        
        # Different user should still be allowed
        result = self.limiter.is_allowed("user5", max_requests=1, window_seconds=60)
        self.assertTrue(result)
    
    def test_is_allowed_window_expiry(self):
        """Test that old requests are removed after window expires."""
        import time
        
        identifier = "user6"
        window_seconds = 1
        
        # Make request
        self.limiter.is_allowed(identifier, max_requests=1, window_seconds=window_seconds)
        
        # Wait for window to expire
        time.sleep(window_seconds + 0.1)
        
        # Should be allowed again
        result = self.limiter.is_allowed(identifier, max_requests=1, window_seconds=window_seconds)
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
