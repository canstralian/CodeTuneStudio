# Security Quick Reference Guide

Quick reference for secure coding practices in CodeTuneStudio.

## 🔐 Import Security Utilities

```python
from utils.security import (
    InputValidator,
    OutputSanitizer,
    SecureCodeExecutor,
    SecurityError,
    RateLimiter,
)
from utils.secure_flask import (
    require_api_key,
    validate_json_input,
    sanitize_request_data,
)
```

## ✅ Input Validation

### String Sanitization
```python
# Sanitize user input
safe_string = InputValidator.sanitize_string(user_input, max_length=1000)
```

### Filename Sanitization
```python
# Prevent directory traversal
safe_filename = InputValidator.sanitize_filename(uploaded_file.filename)
```

### Numeric Validation
```python
# Validate ranges
errors = InputValidator.validate_numeric_range(
    value=learning_rate,
    min_val=0.0001,
    max_val=0.1,
    param_name="learning_rate"
)
if errors:
    return {"error": errors[0]}, 400
```

### Enum Validation
```python
# Validate against whitelist
errors = InputValidator.validate_enum(
    value=model_type,
    allowed_values=["bert", "gpt2", "t5"],
    param_name="model_type"
)
```

## 🛡️ Output Sanitization

```python
# Escape HTML in outputs
safe_output = OutputSanitizer.escape_html(user_content)

# Sanitize error messages
safe_error = OutputSanitizer.sanitize_error_message(exception)
```

## 🔒 Database Queries

### ✅ DO: Use ORM
```python
# SQLAlchemy ORM (safe)
user = User.query.filter_by(email=email).first()
configs = TrainingConfig.query.filter(
    TrainingConfig.model_type == model_type
).all()
```

### ✅ DO: Parameterized Queries
```python
from sqlalchemy import text

stmt = text("SELECT * FROM users WHERE email = :email")
result = db.session.execute(stmt, {"email": email})
```

### ❌ DON'T: String Concatenation
```python
# NEVER do this - SQL injection vulnerability
query = f"SELECT * FROM users WHERE email = '{email}'"  # DANGEROUS!
```

## 🌐 Secure Flask Endpoints

### Basic Secure Endpoint
```python
@app.route('/api/endpoint', methods=['POST'])
@require_api_key
@validate_json_input(['param1', 'param2'])
def secure_endpoint():
    try:
        data = sanitize_request_data(request.get_json())
        result = process_data(data)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
```

### Rate Limited Endpoint
```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=get_remote_address)

@app.route('/api/resource-intensive', methods=['POST'])
@limiter.limit("10 per hour")
@require_api_key
def resource_intensive():
    # Implementation
    pass
```

## 🚫 Code Execution (Avoid!)

### ❌ NEVER: Direct exec()
```python
# NEVER do this - Remote Code Execution vulnerability
exec(user_code)  # DANGEROUS!
```

### ✅ IF REQUIRED: Use Sandboxing
```python
from RestrictedPython import compile_restricted

# Compile with restrictions
byte_code = compile_restricted(code, '<user_code>', 'exec')

if byte_code.errors:
    return {'error': 'Invalid code'}

# Execute with limited globals
safe_globals = {'__builtins__': safe_builtins}
exec(byte_code.code, safe_globals)
```

### ✅ BETTER: Validate Only
```python
executor = SecureCodeExecutor()
warnings = executor.validate_code(user_code)

if warnings:
    return {'error': 'Code validation failed', 'warnings': warnings}

# Don't execute - just analyze or use in Docker container
```

## ⏱️ Timeout Enforcement

```python
from concurrent.futures import ThreadPoolExecutor, TimeoutError

def execute_with_timeout(func, timeout_sec, *args):
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func, *args)
        try:
            return future.result(timeout=timeout_sec)
        except TimeoutError:
            raise TimeoutError(f"Exceeded {timeout_sec}s")
```

## 🔑 Environment Variables

### ✅ DO: Use Environment Variables
```python
import os

API_KEY = os.environ.get("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY environment variable required")

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///default.db")
```

### ❌ DON'T: Hardcode Secrets
```python
# NEVER do this
API_KEY = "sk-1234567890"  # PROHIBITED!
```

## 📤 File Uploads

```python
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'txt', 'json', 'csv'}
MAX_SIZE = 10 * 1024 * 1024  # 10MB

def handle_upload(file):
    # Validate extension
    if not file.filename.endswith(tuple(ALLOWED_EXTENSIONS)):
        raise ValueError("Invalid file type")
    
    # Check size
    file.seek(0, os.SEEK_END)
    if file.tell() > MAX_SIZE:
        raise ValueError("File too large")
    file.seek(0)
    
    # Sanitize filename
    filename = InputValidator.sanitize_filename(file.filename)
    filepath = os.path.join(UPLOAD_DIR, filename)
    file.save(filepath)
    
    return filepath
```

## 🚨 Error Handling

```python
@app.errorhandler(Exception)
def handle_error(error):
    # Log internally with details
    logger.error(f"Error: {error}", exc_info=True)
    
    # Return generic message to user
    safe_msg = OutputSanitizer.sanitize_error_message(error)
    return jsonify({'error': safe_msg}), 500
```

## 🔍 Security Scanning

### Run Security Checks
```bash
# Scan for security issues
bandit -r . -f screen

# Check dependency vulnerabilities
safety check

# Run all tests
python -m unittest discover tests/
```

### Before Committing
```bash
# Check your code
flake8 your_file.py
bandit your_file.py

# Run tests
python -m unittest tests/test_your_feature.py
```

## 📋 Pre-Deployment Checklist

- [ ] No hardcoded secrets
- [ ] All inputs validated and sanitized
- [ ] Database queries use ORM or parameterized queries
- [ ] Outputs properly escaped
- [ ] Authentication on sensitive endpoints
- [ ] Rate limiting on resource-intensive endpoints
- [ ] Error handling doesn't expose internals
- [ ] Timeouts on long operations
- [ ] Security scans pass (bandit, safety)
- [ ] Tests pass
- [ ] Documentation updated

## 📚 More Information

- Full guide: `docs/SECURITY_BEST_PRACTICES.md`
- Security policy: `SECURITY.md`
- Report vulnerabilities: See `SECURITY.md`

---

*Keep this guide handy during development!*
