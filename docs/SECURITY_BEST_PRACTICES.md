# Security Best Practices for CodeTuneStudio

This document outlines security best practices for CodeTuneStudio development and deployment.

## 🔒 Critical Security Rules

### 1. Never Execute Untrusted Code Directly

**❌ DANGEROUS - Never do this:**
```python
# Using exec() directly is a critical security vulnerability
user_code = request.json.get('code')
exec(user_code)  # DANGEROUS!
```

**✅ SAFE - Use sandboxing instead:**
```python
from utils.security import SecureCodeExecutor, SecurityError

executor = SecureCodeExecutor(timeout_seconds=30)

try:
    # Validate code before execution
    warnings = executor.validate_code(user_code)
    if warnings:
        return jsonify({'error': 'Code validation failed', 'warnings': warnings}), 400
    
    # For production, use proper sandboxing solutions:
    # - RestrictedPython for Python code sandboxing
    # - Docker containers for complete isolation
    # - VM-based sandboxes for maximum security
    
except SecurityError as e:
    logger.error(f"Security error: {e}")
    return jsonify({'error': 'Security validation failed'}), 403
```

### 2. Always Validate and Sanitize User Input

**✅ Required for all user inputs:**
```python
from utils.security import InputValidator

# Sanitize strings
safe_string = InputValidator.sanitize_string(user_input, max_length=1000)

# Validate numeric ranges
errors = InputValidator.validate_numeric_range(
    value=user_value,
    min_val=0.0,
    max_val=100.0,
    param_name="learning_rate"
)

# Validate enum values
errors = InputValidator.validate_enum(
    value=user_choice,
    allowed_values=['option1', 'option2', 'option3'],
    param_name="model_type"
)

# Sanitize filenames
safe_filename = InputValidator.sanitize_filename(uploaded_file.filename)
```

### 3. Use Parameterized Queries (Never String Concatenation)

**❌ DANGEROUS - SQL Injection vulnerability:**
```python
# Never concatenate SQL queries
query = f"SELECT * FROM users WHERE email = '{user_email}'"  # DANGEROUS!
db.session.execute(query)
```

**✅ SAFE - Use SQLAlchemy ORM or parameterized queries:**
```python
from sqlalchemy import text

# Method 1: SQLAlchemy ORM (preferred)
user = User.query.filter_by(email=user_email).first()

# Method 2: Parameterized query
stmt = text("SELECT * FROM users WHERE email = :email")
result = db.session.execute(stmt, {"email": user_email})
```

### 4. Protect API Endpoints

**✅ Implement authentication, validation, and rate limiting:**
```python
from utils.secure_flask import require_api_key, validate_json_input, sanitize_request_data

@app.route('/api/protected', methods=['POST'])
@require_api_key
@validate_json_input(['data', 'operation'])
def protected_endpoint():
    """Protected endpoint with proper security controls."""
    try:
        # Get and sanitize request data
        raw_data = request.get_json()
        data = sanitize_request_data(raw_data)
        
        # Process with validated data
        result = process_data(data)
        return jsonify(result), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
```

### 5. Never Hardcode Secrets

**❌ NEVER hardcode credentials:**
```python
# NEVER do this
API_KEY = "sk-1234567890abcdef"  # PROHIBITED!
DATABASE_URL = "postgresql://user:password@localhost/db"  # PROHIBITED!
```

**✅ ALWAYS use environment variables:**
```python
import os

# Load from environment with validation
API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///database.db")
```

## 🛡️ Security Implementation Guide

### Code Execution Sandboxing

When you need to execute user-provided code, use proper sandboxing:

```python
# For Python code sandboxing
from RestrictedPython import compile_restricted
from RestrictedPython.Guards import safe_builtins, safe_globals

def execute_user_python_code(code: str, timeout: int = 30):
    """
    Execute Python code in a restricted environment.
    
    This uses RestrictedPython to prevent dangerous operations.
    For even more security, run in a Docker container.
    """
    try:
        # Compile with restrictions
        byte_code = compile_restricted(
            code,
            filename='<user_code>',
            mode='exec'
        )
        
        # Check for compilation errors
        if byte_code.errors:
            return {'error': 'Code validation failed', 'details': byte_code.errors}
        
        # Execute with restricted globals
        restricted_globals = {
            '__builtins__': safe_builtins,
            '_getattr_': getattr,
        }
        
        exec(byte_code.code, restricted_globals)
        
        return {'status': 'success'}
        
    except Exception as e:
        logger.error(f"Code execution error: {e}")
        return {'error': 'Execution failed'}
```

### Timeout Enforcement

Always enforce timeouts to prevent denial-of-service:

```python
import signal
from contextlib import contextmanager

@contextmanager
def timeout(seconds: int):
    """
    Context manager to enforce timeout on operations.
    
    Usage:
        with timeout(30):
            long_running_operation()
    """
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Operation exceeded {seconds} seconds")
    
    # Set the signal handler
    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)


# For thread-based timeout (works on Windows)
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

def execute_with_timeout(func, timeout_seconds: int, *args, **kwargs):
    """
    Execute function with timeout using thread pool.
    
    Args:
        func: Function to execute
        timeout_seconds: Maximum execution time
        *args, **kwargs: Arguments for func
        
    Returns:
        Function result
        
    Raises:
        TimeoutError: If execution exceeds timeout
    """
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func, *args, **kwargs)
        try:
            return future.result(timeout=timeout_seconds)
        except FutureTimeoutError:
            raise TimeoutError(f"Execution exceeded {timeout_seconds} seconds")
```

### File Upload Security

Secure file upload handling:

```python
import os
from werkzeug.utils import secure_filename
from utils.security import InputValidator

ALLOWED_EXTENSIONS = {'txt', 'json', 'csv', 'py'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def secure_file_upload(file, upload_folder: str) -> Optional[str]:
    """
    Handle file upload securely.
    
    Args:
        file: Uploaded file object
        upload_folder: Directory to save files
        
    Returns:
        Path to saved file or None if validation fails
    """
    if not file or file.filename == '':
        logger.warning("Empty file upload attempted")
        return None
    
    if not allowed_file(file.filename):
        logger.warning(f"Invalid file type: {file.filename}")
        return None
    
    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        logger.warning(f"File too large: {file_size} bytes")
        return None
    
    # Sanitize filename
    filename = InputValidator.sanitize_filename(file.filename)
    filepath = os.path.join(upload_folder, filename)
    
    # Ensure upload directory exists
    os.makedirs(upload_folder, exist_ok=True)
    
    # Save file
    file.save(filepath)
    logger.info(f"File uploaded successfully: {filename}")
    
    return filepath
```

### Rate Limiting

Implement rate limiting to prevent abuse:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=os.environ.get("REDIS_URL", "memory://")
)

# Apply to specific endpoints
@app.route('/api/expensive-operation', methods=['POST'])
@limiter.limit("10 per hour")
@require_api_key
def expensive_operation():
    """Rate-limited endpoint."""
    # Implementation
    pass
```

### Secure Session Management

Configure secure sessions:

```python
from flask import Flask, session
import secrets

app = Flask(__name__)

# Secure session configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour
```

### Error Handling

Never expose internal details in error messages:

```python
from utils.security import OutputSanitizer

@app.errorhandler(Exception)
def handle_error(error):
    """Handle errors securely."""
    # Log detailed error internally
    logger.error(f"Error occurred: {error}", exc_info=True)
    
    # Return sanitized error to user
    safe_message = OutputSanitizer.sanitize_error_message(error)
    
    if isinstance(error, ValueError):
        return jsonify({'error': safe_message}), 400
    else:
        return jsonify({'error': 'An internal error occurred'}), 500
```

## 🔍 Security Testing

### Run Security Scans

```bash
# Install security scanning tools
pip install bandit safety

# Scan Python code for security issues
bandit -r . -f json -o bandit-report.json

# Check dependencies for known vulnerabilities
safety check --json

# Run type checking
mypy app.py utils/ components/
```

### Security Testing Checklist

- [ ] No hardcoded secrets in code
- [ ] All database queries use parameterized queries or ORM
- [ ] User input is validated and sanitized
- [ ] Output is properly escaped
- [ ] Error messages don't expose internal details
- [ ] Authentication and authorization properly implemented
- [ ] CSRF protection enabled for forms
- [ ] Rate limiting implemented for API endpoints
- [ ] Dependencies are up-to-date and vulnerability-free
- [ ] Logging doesn't expose sensitive information
- [ ] Timeouts enforced on long-running operations
- [ ] File uploads properly validated and sanitized
- [ ] Code execution (if any) properly sandboxed

## 📚 Additional Resources

### Security Tools
- **bandit**: Security linter for Python code
- **safety**: Scan dependencies for vulnerabilities
- **Flask-Limiter**: Rate limiting for Flask
- **Flask-Talisman**: Security headers for Flask
- **RestrictedPython**: Sandboxed Python execution
- **Docker**: Container-based isolation

### Documentation
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/latest/security/)
- [SQLAlchemy Security](https://docs.sqlalchemy.org/en/latest/core/security.html)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)

## 🚨 Incident Response

If you discover a security vulnerability:

1. **Do NOT commit the fix to a public branch immediately**
2. Report it privately to the maintainers
3. Document the vulnerability and its impact
4. Wait for security advisory before public disclosure
5. Apply the fix after coordinated disclosure

## 📝 Security Review Process

All code changes must pass security review:

1. Automated security scanning (bandit, safety)
2. Manual code review focusing on:
   - Input validation
   - Output sanitization
   - Authentication/authorization
   - Database queries
   - Error handling
   - Secret management
3. Security testing for new features
4. Update documentation as needed

---

*Last Updated: 2024-10-10*
*For security concerns, please contact the maintainers privately.*
