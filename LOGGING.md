# 📝 Logging Guide for CodeTune Studio

This guide explains how to use the enhanced logging system in CodeTune Studio, which provides structured JSON logging with request ID tracking for improved observability and debugging.

## 🎯 Overview

CodeTune Studio uses a sophisticated logging system that provides:

- **JSON-formatted logs** for structured data and easy parsing
- **Unique request IDs** for tracing requests through the system
- **Automatic sensitive data sanitization** to prevent accidental logging of secrets
- **Color-coded console output** for better readability during development
- **File-based logging** with automatic rotation
- **Flask middleware integration** for automatic request/response logging

## 🚀 Quick Start

### Basic Usage

The logging system is automatically configured when the application starts. You can use it like standard Python logging:

```python
from core.logging import get_logger

logger = get_logger(__name__)

logger.info("Processing user request")
logger.warning("Cache miss detected")
logger.error("Failed to connect to database", exc_info=True)
```

### Environment Variables

Configure logging behavior using environment variables in your `.env` file:

```bash
# Set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Enable JSON formatted output (recommended for production)
LOG_JSON=true

# Specify log file path (optional)
LOG_FILE=/var/log/codetune-studio/app.log
```

## 📊 Log Format

### JSON Format (Production)

When `LOG_JSON=true`, logs are output in JSON format:

```json
{
  "timestamp": "2024-06-11T10:30:45.123456+00:00",
  "level": "INFO",
  "logger": "core.server",
  "message": "Request completed: GET /api/config - Status: 200",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "location": {
    "file": "/app/core/server.py",
    "line": 142,
    "function": "handle_request"
  },
  "extras": {
    "method": "GET",
    "path": "/api/config",
    "status_code": 200,
    "duration_ms": 45.67
  }
}
```

### Human-Readable Format (Development)

When `LOG_JSON=false` (default), logs use colored, human-readable format:

```
2024-06-11 10:30:45 - core.server - INFO - Request completed: GET /api/config - Status: 200
```

## 🔐 Security Features

### Automatic Sensitive Data Sanitization

The logging system automatically redacts sensitive information to prevent accidental exposure:

```python
from core.logging import sanitize_for_logging

# Input data with sensitive information
user_data = {
    "username": "john_doe",
    "password": "secret123",
    "api_key": "sk-1234567890",
    "email": "john@example.com"
}

# Sanitized output
sanitized = sanitize_for_logging(user_data)
# Result: {
#   "username": "john_doe",
#   "password": "***REDACTED***",
#   "api_key": "***REDACTED***",
#   "email": "john@example.com"
# }
```

**Sensitive keywords automatically redacted:**
- `password`, `passwd`, `pwd`
- `secret`, `api_key`, `apikey`
- `token`, `auth`, `authorization`
- `session`, `cookie`, `csrf`
- `private_key`, `access_token`, `refresh_token`

### Best Practices

1. **Never log raw user input** without sanitization
2. **Use structured logging** with extra fields instead of string formatting
3. **Avoid logging entire request/response bodies** unless necessary
4. **Review logs periodically** to ensure no sensitive data leakage
5. **⚠️ Never include sensitive data directly in log message strings**

### Important Security Note

The `sanitize_for_logging()` function only sanitizes data passed via the `extra` parameter. **It does NOT sanitize the log message string itself.** 

**DON'T DO THIS:**
```python
# ❌ UNSAFE - password will be logged in plain text!
logger.info(f"User authenticated with password: {password}")
logger.info(f"API key used: {api_key}")
```

**DO THIS INSTEAD:**
```python
# ✅ SAFE - sensitive data is passed via extra and will be sanitized
logger.info("User authenticated", extra={"password": password})
logger.info("API request made", extra={"api_key": api_key})
```

Always pass sensitive data via the `extra` parameter where automatic sanitization will redact it.

## 🆔 Request ID Tracking

Every HTTP request is automatically assigned a unique request ID that is:

1. **Generated automatically** by the middleware
2. **Propagated throughout** the request lifecycle
3. **Included in all log entries** made during request processing
4. **Returned in response headers** as `X-Request-ID`

### Manual Request ID Management

```python
from core.logging import generate_request_id, set_request_id, get_request_id

# Generate a new request ID
request_id = generate_request_id()  # Returns UUID string

# Set request ID in current context
set_request_id(request_id)

# Get current request ID
current_id = get_request_id()  # Returns request ID or None

# All logs after this will include the request ID
logger.info("Processing task")  # Automatically includes request_id
```

### Tracking Requests Across Services

When making external API calls, propagate the request ID:

```python
import requests
from core.logging import get_request_id

# Forward request ID to downstream services
request_id = get_request_id()
headers = {"X-Request-ID": request_id} if request_id else {}

response = requests.get(
    "https://api.example.com/data",
    headers=headers
)
```

## 🔧 Advanced Configuration

### Programmatic Setup

You can configure logging programmatically in your code:

```python
from core.logging import setup_logging

# Configure with custom settings
setup_logging(
    log_level="DEBUG",
    log_file="/var/log/app/debug.log",
    enable_color=True,
    json_format=False
)
```

### Flask Middleware Integration

The request logging middleware is automatically initialized in the Flask app. You can customize it:

```python
from flask import Flask
from core.middleware import RequestLoggingMiddleware

app = Flask(__name__)

# Custom middleware with different request ID header
middleware = RequestLoggingMiddleware(
    app,
    request_id_header="X-Correlation-ID"
)
```

### Function-Level Logging Decorator

Use the decorator to automatically log function entry/exit:

```python
from core.middleware import with_request_logging

@with_request_logging(log_args=True, log_result=True)
def process_data(data: dict) -> dict:
    """Process some data with automatic logging."""
    # Function implementation
    return processed_data

# Logs:
# DEBUG - Entering process_data - args: (...) kwargs: {...}
# DEBUG - Exiting process_data - result: {...}
```

## 📈 Log Analysis

### Querying JSON Logs

JSON logs can be easily parsed and analyzed:

```bash
# Find all errors for a specific request
jq 'select(.request_id == "a1b2c3d4-e5f6-7890-abcd-ef1234567890" and .level == "ERROR")' app.log

# Count requests by status code
jq -s 'group_by(.extras.status_code) | map({status: .[0].extras.status_code, count: length})' app.log

# Find slow requests (> 1 second)
jq 'select(.extras.duration_ms > 1000)' app.log
```

### Integration with Log Aggregators

JSON logs work seamlessly with log aggregation services:

- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Splunk**
- **Datadog**
- **CloudWatch Logs Insights**
- **Grafana Loki**

Example Logstash configuration:

```ruby
input {
  file {
    path => "/var/log/codetune-studio/app.log"
    codec => "json"
  }
}

filter {
  # Parse timestamp
  date {
    match => ["timestamp", "ISO8601"]
  }
  
  # Add tags based on log level
  if [level] == "ERROR" {
    mutate { add_tag => ["error"] }
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "codetune-logs-%{+YYYY.MM.dd}"
  }
}
```

## 🐛 Debugging Tips

### Enable Debug Logging

```bash
# In .env file
LOG_LEVEL=DEBUG

# Or via environment variable
export LOG_LEVEL=DEBUG
python app.py
```

### Trace a Specific Request

1. Extract the request ID from the response header:
   ```bash
   curl -i http://localhost:7860/api/config
   # Look for: X-Request-ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890
   ```

2. Filter logs by request ID:
   ```bash
   # JSON logs
   grep "a1b2c3d4-e5f6-7890-abcd-ef1234567890" app.log | jq .
   
   # Human-readable logs
   grep "a1b2c3d4-e5f6-7890-abcd-ef1234567890" app.log
   ```

### Common Issues

**Issue: Logs not appearing in file**
- Check file permissions: `ls -la /var/log/codetune-studio/`
- Verify LOG_FILE environment variable is set correctly
- Check disk space: `df -h`

**Issue: Request ID is None in logs**
- Ensure middleware is properly initialized
- Check that you're using Flask request context
- Verify the middleware is registered before other middleware

**Issue: Sensitive data appearing in logs**
- Review custom logging calls that bypass sanitization
- Add custom sensitive keywords to `SENSITIVE_KEYS` in `core/logging.py`
- Use `sanitize_for_logging()` before logging user data

## 📚 API Reference

### Core Functions

#### `get_logger(name: str) -> logging.Logger`
Get a logger instance with the specified name.

```python
logger = get_logger(__name__)
```

#### `setup_logging(log_level, log_file, enable_color, json_format)`
Configure application-wide logging.

**Parameters:**
- `log_level` (str, optional): Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `log_file` (str, optional): Path to log file
- `enable_color` (bool): Enable colored console output (default: True)
- `json_format` (bool, optional): Use JSON format (default: from LOG_JSON env var)

#### `generate_request_id() -> str`
Generate a unique UUID-based request ID.

#### `set_request_id(request_id: str)`
Set the request ID in the current context.

#### `get_request_id() -> Optional[str]`
Get the current request ID from context.

#### `sanitize_for_logging(data: Any, max_depth: int = 5) -> Any`
Sanitize data to prevent logging sensitive information.

**Parameters:**
- `data`: Data to sanitize (dict, list, or primitive)
- `max_depth` (int): Maximum recursion depth (default: 5)

**Returns:** Sanitized copy of data with sensitive values replaced.

### Middleware Classes

#### `RequestLoggingMiddleware`
Flask middleware for automatic request/response logging.

**Methods:**
- `__init__(app, request_id_header="X-Request-ID")`
- `init_app(app)`

#### Decorator: `@with_request_logging(log_args=False, log_result=False)`
Decorator for logging function calls with request context.

**Parameters:**
- `log_args` (bool): Log function arguments (default: False)
- `log_result` (bool): Log function return value (default: False)

## 🔄 Migration Guide

### Migrating from Basic Logging

**Before:**
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Processing request")
```

**After:**
```python
from core.logging import get_logger, setup_logging

setup_logging()  # Called once at startup
logger = get_logger(__name__)

logger.info("Processing request")  # Now includes request ID and structured data
```

### Updating Existing Flask Apps

Add middleware to your Flask application:

```python
from flask import Flask
from core.middleware import setup_request_logging

app = Flask(__name__)

# Add this line after creating the Flask app
setup_request_logging(app)
```

## 🤝 Contributing

When contributing to CodeTune Studio, follow these logging guidelines:

1. **Use structured logging** with extra fields:
   ```python
   logger.info(
       "User action completed",
       extra={
           "user_id": user_id,
           "action": "update_profile",
           "duration_ms": elapsed_time
       }
   )
   ```

2. **Choose appropriate log levels:**
   - `DEBUG`: Detailed diagnostic information
   - `INFO`: General informational messages
   - `WARNING`: Warning messages for potentially harmful situations
   - `ERROR`: Error messages for failures
   - `CRITICAL`: Critical issues requiring immediate attention

3. **Include context in error logs:**
   ```python
   try:
       result = dangerous_operation()
   except Exception as e:
       logger.error(
           f"Operation failed: {e}",
           exc_info=True,  # Include full traceback
           extra={
               "operation": "dangerous_operation",
               "input_data": sanitize_for_logging(data)
           }
       )
       raise
   ```

4. **Test logging in your changes:**
   - Verify sensitive data is sanitized
   - Check that request IDs are propagated
   - Ensure JSON logs are valid JSON

## 📞 Support

For questions or issues related to logging:

1. Check this documentation first
2. Search existing issues on GitHub
3. Create a new issue with the `logging` label
4. Include relevant log samples (with sensitive data removed)

## 📝 License

This logging system is part of CodeTune Studio and is licensed under the MIT License.

---

*Last Updated: 2024-06-11*
*Version: 1.0.0*
