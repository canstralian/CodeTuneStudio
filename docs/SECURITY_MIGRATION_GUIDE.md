# Security Migration Guide

This guide helps migrate existing CodeTuneStudio code to use new security utilities.

## 🎯 Migration Overview

The security improvements provide utilities to prevent common vulnerabilities:
- SQL injection
- Cross-site scripting (XSS)
- Remote code execution (RCE)
- Denial of service (DoS)
- Information disclosure

## 📋 Migration Checklist

### For Each Python File:

- [ ] Replace direct `exec()` calls with validation
- [ ] Add input validation for user inputs
- [ ] Use parameterized queries (if database access)
- [ ] Add output sanitization for HTML content
- [ ] Add timeout enforcement for long operations
- [ ] Validate environment variables
- [ ] Add error handling with message sanitization

## 🔄 Common Migration Patterns

### Pattern 1: User Input Validation

**Before:**
```python
def process_request(request):
    name = request.form.get('name')
    value = request.form.get('value')
    # Direct use of inputs
    result = do_something(name, value)
    return result
```

**After:**
```python
from utils.security import InputValidator

def process_request(request):
    # Validate and sanitize inputs
    name = InputValidator.sanitize_string(
        request.form.get('name', ''),
        max_length=100
    )
    
    raw_value = request.form.get('value', 0)
    errors = InputValidator.validate_numeric_range(
        float(raw_value),
        min_val=0.0,
        max_val=100.0,
        param_name='value'
    )
    
    if errors:
        return {'error': errors[0]}, 400
    
    value = float(raw_value)
    result = do_something(name, value)
    return result
```

### Pattern 2: Database Queries

**Before:**
```python
def get_user(email):
    # String concatenation - SQL injection risk!
    query = f"SELECT * FROM users WHERE email = '{email}'"
    return db.execute(query)
```

**After:**
```python
def get_user(email):
    # Use ORM - safe from SQL injection
    return User.query.filter_by(email=email).first()

# Or with parameterized query:
def get_user(email):
    from sqlalchemy import text
    stmt = text("SELECT * FROM users WHERE email = :email")
    return db.session.execute(stmt, {"email": email}).first()
```

### Pattern 3: Code Execution

**Before:**
```python
def evaluate_code(code):
    # Direct execution - RCE vulnerability!
    exec(code)
    return "Executed"
```

**After:**
```python
from utils.security import SecureCodeExecutor, SecurityError

def evaluate_code(code):
    executor = SecureCodeExecutor(timeout_seconds=30)
    
    # Validate code first
    warnings = executor.validate_code(code)
    if warnings:
        return {
            'error': 'Code validation failed',
            'warnings': warnings
        }, 400
    
    # For production, use proper sandboxing:
    # - RestrictedPython for Python sandboxing
    # - Docker containers for isolation
    # - Don't use exec() at all if possible
    
    return {
        'message': 'Code validated but not executed for security'
    }, 200
```

### Pattern 4: Flask Endpoints

**Before:**
```python
@app.route('/api/endpoint', methods=['POST'])
def endpoint():
    data = request.get_json()
    # No validation or authentication
    result = process(data)
    return jsonify(result)
```

**After:**
```python
from utils.secure_flask import (
    require_api_key,
    validate_json_input,
    sanitize_request_data
)

@app.route('/api/endpoint', methods=['POST'])
@require_api_key
@validate_json_input(['param1', 'param2'])
def endpoint():
    try:
        # Get and sanitize data
        raw_data = request.get_json()
        data = sanitize_request_data(raw_data)
        
        # Process with validated data
        result = process(data)
        return jsonify(result), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
```

### Pattern 5: Error Handling

**Before:**
```python
@app.errorhandler(Exception)
def handle_error(error):
    # Exposes internal details
    return jsonify({'error': str(error)}), 500
```

**After:**
```python
from utils.security import OutputSanitizer
import logging

logger = logging.getLogger(__name__)

@app.errorhandler(Exception)
def handle_error(error):
    # Log detailed error internally
    logger.error(f"Error occurred: {error}", exc_info=True)
    
    # Return sanitized message to user
    safe_message = OutputSanitizer.sanitize_error_message(error)
    
    if isinstance(error, ValueError):
        return jsonify({'error': safe_message}), 400
    else:
        return jsonify({'error': safe_message}), 500
```

### Pattern 6: File Uploads

**Before:**
```python
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    # Direct save - security risks!
    file.save(f'/uploads/{file.filename}')
    return "Uploaded"
```

**After:**
```python
from utils.security import InputValidator
from werkzeug.utils import secure_filename
import os

ALLOWED_EXTENSIONS = {'txt', 'json', 'csv'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    
    if not file or file.filename == '':
        return jsonify({'error': 'No file provided'}), 400
    
    # Validate extension
    if not file.filename.endswith(tuple(ALLOWED_EXTENSIONS)):
        return jsonify({'error': 'Invalid file type'}), 400
    
    # Check size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        return jsonify({'error': 'File too large'}), 400
    
    # Sanitize filename
    filename = InputValidator.sanitize_filename(file.filename)
    upload_dir = '/uploads'
    os.makedirs(upload_dir, exist_ok=True)
    
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)
    
    return jsonify({'message': 'Uploaded', 'filename': filename}), 200
```

### Pattern 7: Environment Variables

**Before:**
```python
# Hardcoded secrets
API_KEY = "sk-1234567890"
DATABASE_URL = "postgresql://user:pass@localhost/db"
```

**After:**
```python
import os

# Load from environment
API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "sqlite:///database.db"  # Safe default
)
```

## 🔍 Finding Code to Migrate

### Search for Vulnerable Patterns

```bash
# Find direct exec() calls
grep -r "exec(" --include="*.py" .

# Find string concatenation in SQL
grep -r "f\".*SELECT" --include="*.py" .
grep -r "\".*SELECT.*{" --include="*.py" .

# Find hardcoded secrets (examples)
grep -r "api_key\s*=\s*['\"]" --include="*.py" .
grep -r "password\s*=\s*['\"]" --include="*.py" .

# Find error handlers that might leak info
grep -r "str(error)" --include="*.py" .
```

## 📊 Priority Migration Order

1. **Critical (Migrate First)**
   - Direct `exec()` or `eval()` calls
   - SQL string concatenation
   - Hardcoded secrets
   - Unvalidated file operations

2. **High Priority**
   - API endpoints without authentication
   - Missing input validation
   - Error handlers exposing details
   - File uploads without validation

3. **Medium Priority**
   - Missing rate limiting
   - No timeout enforcement
   - Missing output sanitization
   - Weak session configuration

4. **Low Priority**
   - Adding security headers
   - Improving logging
   - Documentation updates

## ✅ Testing After Migration

### 1. Run Security Scans
```bash
# Check for security issues
bandit -r . -f screen

# Check dependencies
safety check
```

### 2. Run Unit Tests
```bash
# Run all tests
python -m unittest discover tests/

# Run security tests specifically
python -m unittest tests.test_security
```

### 3. Manual Testing
- Test with malicious inputs (XSS, SQL injection attempts)
- Test file upload with dangerous filenames
- Test rate limiting
- Test timeout enforcement
- Test error handling

### 4. Code Review Checklist
- [ ] No hardcoded secrets
- [ ] All inputs validated
- [ ] Database queries parameterized
- [ ] Outputs sanitized
- [ ] Authentication on sensitive endpoints
- [ ] Rate limiting on resource-intensive endpoints
- [ ] Proper error handling
- [ ] Tests pass
- [ ] Security scans pass

## 🆘 Getting Help

If you need help with migration:

1. **Documentation**
   - [Security Best Practices](SECURITY_BEST_PRACTICES.md)
   - [Security Quick Reference](SECURITY_QUICK_REFERENCE.md)

2. **Examples**
   - Check `utils/secure_flask.py` for secure endpoint examples
   - Check `tests/test_security.py` for usage examples

3. **Questions**
   - Open an issue with "security" label
   - Reference this migration guide

## 📝 Migration Log Template

Keep track of your migration progress:

```markdown
# Security Migration Log

## Completed
- [ ] File: `module1.py` - Added input validation
- [ ] File: `module2.py` - Migrated database queries
- [ ] File: `api.py` - Added authentication

## In Progress
- [ ] File: `legacy.py` - Needs refactoring

## Blocked
- [ ] File: `old_code.py` - Awaiting specification

## Notes
- Discovered additional vulnerability in X, created issue #123
```

---

*Last Updated: 2024-10-10*
