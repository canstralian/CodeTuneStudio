# GitHub Copilot Coding Agent Instructions

This document provides comprehensive guidance for the GitHub Copilot Coding Agent when working with the CodeTuneStudio repository. All contributors using Copilot or other AI code generation tools should review, test, and validate all generated code before merging.

For official best practices, see: https://gh.io/copilot-coding-agent-tips

---

## 🎯 Project Context

CodeTuneStudio is a Streamlit/Flask hybrid application for ML model fine-tuning with:
- Parameter-efficient training (PEFT/LoRA)
- Plugin architecture for extensible code analysis tools
- PostgreSQL/SQLite database backend for experiment tracking
- Flask API backend with SQLAlchemy ORM
- Streamlit interactive web UI (port 7860)

**Development Environments:** VS Code, Kali Linux, Replit, GitHub Codespaces

---

## 🔒 Security-First Requirements

### Critical Security Rules

**⛔ PROHIBITED PRACTICES:**
1. **NEVER** hardcode secrets, API keys, tokens, passwords, or credentials in code
2. **NEVER** commit sensitive data to version control
3. **NEVER** use raw SQL queries or string concatenation for database operations
4. **NEVER** trust user input without validation and sanitization
5. **NEVER** expose internal system details in error messages to end users

### Required Security Practices

#### 1. Secrets Management
- ✅ **ALWAYS** use environment variables for sensitive data
- ✅ Store all secrets in `.env` files (excluded from git via `.gitignore`)
- ✅ Use `os.environ.get()` or `os.getenv()` with safe defaults
- ✅ Document required environment variables in README or `.env.example`
- ✅ Use secret management services (AWS Secrets Manager, Azure Key Vault, etc.) in production

**Example - Correct Usage:**
```python
import os

# Load from environment with fallback
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///database.db")
API_KEY = os.getenv("OPENAI_API_KEY")  # Required, validated before use

if not API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")
```

**Example - INCORRECT (DO NOT USE):**
```python
# ❌ NEVER DO THIS
API_KEY = "sk-1234567890abcdef"  # PROHIBITED
DATABASE_URL = "postgresql://user:password123@localhost/db"  # PROHIBITED
```

#### 2. Environment Variable Documentation
Always document required environment variables:

```bash
# .env.example (commit this template)
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
HF_TOKEN=your_huggingface_token_here
SQL_DEBUG=False
SPACE_ID=your_space_id
```

---

## 🐍 Python/Flask API Development

### Code Style Standards

**PEP 8 Compliance:**
- Max line length: 88 characters (Black formatter compatible)
- Use type hints for all function signatures
- Follow existing naming conventions (snake_case for functions/variables)
- Use descriptive variable names

**Example:**
```python
from typing import Dict, List, Optional, Any

def validate_training_config(
    config: Dict[str, Any],
    dataset_name: Optional[str] = None
) -> List[str]:
    """
    Validate training configuration parameters.
    
    Args:
        config: Dictionary containing training parameters
        dataset_name: Optional dataset identifier
        
    Returns:
        List of validation error messages (empty if valid)
        
    Raises:
        ValueError: If config is None or invalid type
    """
    errors: List[str] = []
    # Implementation
    return errors
```

### Input Validation & Sanitization

**ALWAYS validate and sanitize ALL user inputs:**

```python
import re
from typing import Any

def sanitize_string(value: str) -> str:
    """
    Sanitize string inputs by removing special characters.
    
    Args:
        value: Input string to sanitize
        
    Returns:
        Sanitized string safe for database/display
        
    Raises:
        ValueError: If input is not a string
    """
    if not isinstance(value, str):
        raise ValueError("Input must be a string")
    
    # Remove potentially dangerous characters
    return re.sub(r"[^a-zA-Z0-9_\-\.]", "", value.strip())

def validate_numeric_range(
    value: float,
    min_val: float,
    max_val: float,
    param_name: str
) -> List[str]:
    """Validate numeric parameter within acceptable range."""
    errors = []
    
    if not isinstance(value, (int, float)):
        errors.append(f"{param_name} must be numeric")
        return errors
        
    if value < min_val or value > max_val:
        errors.append(
            f"{param_name} must be between {min_val} and {max_val}"
        )
    
    return errors
```

**Input Validation Checklist:**
- ✅ Validate data types (str, int, float, bool)
- ✅ Check value ranges (min/max)
- ✅ Sanitize string inputs (remove special chars, SQL injection patterns)
- ✅ Validate enum values against whitelists
- ✅ Check file paths for directory traversal attacks
- ✅ Validate file uploads (type, size, content)

### Output Sanitization

**Prevent XSS and injection attacks:**

```python
import html
from markupsafe import escape

def sanitize_output(data: str) -> str:
    """Escape HTML characters in output data."""
    return html.escape(data, quote=True)

# For Streamlit UI (handles escaping by default)
import streamlit as st
st.text(user_input)  # Automatically escaped

# When using unsafe_allow_html=True, manually sanitize:
sanitized_html = escape(user_provided_html)
st.markdown(sanitized_html, unsafe_allow_html=True)
```

---

## 🗄️ Database Security (PostgreSQL/SQLite)

### Parameterized Queries - REQUIRED

**⛔ NEVER use raw SQL or string concatenation:**

```python
# ❌ WRONG - SQL Injection Vulnerability
user_id = request.args.get('id')
query = f"SELECT * FROM users WHERE id = {user_id}"  # DANGEROUS
db.session.execute(query)

# ❌ WRONG - String concatenation
query = "SELECT * FROM users WHERE email = '" + email + "'"  # DANGEROUS
```

**✅ CORRECT - Use SQLAlchemy ORM or parameterized queries:**

```python
from sqlalchemy import text
from utils.database import db, TrainingConfig

# Method 1: SQLAlchemy ORM (PREFERRED)
def get_training_config(config_id: int) -> Optional[TrainingConfig]:
    """Retrieve training config using ORM (safe from SQL injection)."""
    return TrainingConfig.query.filter_by(id=config_id).first()

# Method 2: Parameterized queries with SQLAlchemy
def get_configs_by_model(model_type: str) -> List[TrainingConfig]:
    """Retrieve configs with parameterized query."""
    stmt = text("SELECT * FROM training_config WHERE model_type = :model_type")
    result = db.session.execute(stmt, {"model_type": model_type})
    return result.fetchall()

# Method 3: ORM filters (RECOMMENDED)
def search_configs(
    model_type: Optional[str] = None,
    min_epochs: Optional[int] = None
) -> List[TrainingConfig]:
    """Search configs with multiple filters (safe)."""
    query = TrainingConfig.query
    
    if model_type:
        query = query.filter(TrainingConfig.model_type == model_type)
    if min_epochs:
        query = query.filter(TrainingConfig.epochs >= min_epochs)
    
    return query.all()
```

### Database Session Management

**Always use context managers for database operations:**

```python
from contextlib import contextmanager
from sqlalchemy.exc import SQLAlchemyError

@contextmanager
def session_scope():
    """
    Provide a transactional scope for database operations.
    
    Yields:
        Database session with automatic commit/rollback
        
    Raises:
        SQLAlchemyError: On database operation failures
    """
    session = db.session
    try:
        yield session
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Database error: {e}", exc_info=True)
        raise
    finally:
        session.close()

# Usage:
def save_training_config(config_data: Dict[str, Any]) -> int:
    """Save config with proper transaction management."""
    with session_scope() as session:
        config = TrainingConfig(**config_data)
        session.add(config)
        session.flush()  # Get ID before commit
        return config.id
```

### Database Connection Security

```python
# Configure secure connection pooling
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'pool_recycle': 1800,  # Recycle connections every 30 minutes
    'pool_pre_ping': True,  # Verify connections before use
    'max_overflow': 20,
    'pool_timeout': 30
}
```

---

## 🔐 Secure API Design

### Authentication & Authorization

**Implement proper authentication for API endpoints:**

```python
from functools import wraps
from flask import request, jsonify
import secrets

def require_api_key(f):
    """Decorator to require API key authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        expected_key = os.environ.get('API_KEY')
        
        if not api_key or not secrets.compare_digest(api_key, expected_key):
            return jsonify({'error': 'Invalid or missing API key'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/config', methods=['POST'])
@require_api_key
def create_config():
    """Protected endpoint requiring API key."""
    # Implementation
    pass
```

### CSRF Protection

**For Flask forms, use Flask-WTF:**

```python
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()
csrf.init_app(app)

# Configure CSRF for API endpoints
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_TIME_LIMIT'] = None  # Or set appropriate timeout
```

### Rate Limiting

**Implement rate limiting to prevent abuse:**

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=os.environ.get("REDIS_URL", "memory://")
)

@app.route('/api/train', methods=['POST'])
@limiter.limit("10 per hour")
def start_training():
    """Rate-limited training endpoint."""
    # Implementation
    pass
```

### Secure Headers

**Add security headers to all responses:**

```python
from flask import Flask
from flask_talisman import Talisman

app = Flask(__name__)

# Configure security headers
Talisman(app, 
    force_https=True,
    strict_transport_security=True,
    content_security_policy={
        'default-src': "'self'",
        'script-src': ["'self'", "'unsafe-inline'"],  # Minimize unsafe-inline
        'style-src': ["'self'", "'unsafe-inline'"],
    }
)

@app.after_request
def set_security_headers(response):
    """Add additional security headers."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response
```

### Error Handling

**Never expose sensitive information in errors:**

```python
import logging

logger = logging.getLogger(__name__)

@app.errorhandler(Exception)
def handle_error(error):
    """Handle errors without exposing internal details."""
    # Log detailed error internally
    logger.error(f"Error occurred: {error}", exc_info=True)
    
    # Return generic message to user
    if isinstance(error, ValueError):
        return jsonify({'error': 'Invalid input provided'}), 400
    
    # Generic error for unexpected issues
    return jsonify({'error': 'An internal error occurred'}), 500
```

---

## ⚛️ React/Frontend Security

### Functional Components (Required)

**Always use functional components with hooks:**

```javascript
// ✅ CORRECT - Functional component
import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';

const TrainingDashboard = ({ configId, onComplete }) => {
  const [metrics, setMetrics] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetchMetrics(configId);
  }, [configId]);
  
  const fetchMetrics = async (id) => {
    try {
      const response = await fetch(`/api/metrics/${id}`);
      if (!response.ok) throw new Error('Failed to fetch');
      const data = await response.json();
      setMetrics(data);
    } catch (error) {
      console.error('Error fetching metrics:', error);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="dashboard">
      {loading ? <Spinner /> : <MetricsChart data={metrics} />}
    </div>
  );
};

TrainingDashboard.propTypes = {
  configId: PropTypes.number.isRequired,
  onComplete: PropTypes.func.isRequired
};

export default TrainingDashboard;
```

**❌ AVOID - Class components:**

```javascript
// ❌ Avoid class components - use functional components instead
class TrainingDashboard extends React.Component {
  // Old pattern - avoid in new code
}
```

### PropTypes & TypeScript

**Use PropTypes for JavaScript or TypeScript for type safety:**

```typescript
// TypeScript (preferred for new components)
interface TrainingConfig {
  id: number;
  modelType: string;
  batchSize: number;
  learningRate: number;
}

interface TrainingFormProps {
  config?: TrainingConfig;
  onSubmit: (config: TrainingConfig) => Promise<void>;
  onCancel: () => void;
}

const TrainingForm: React.FC<TrainingFormProps> = ({
  config,
  onSubmit,
  onCancel
}) => {
  // Implementation with full type safety
  return <form>{/* ... */}</form>;
};

export default TrainingForm;
```

### XSS Prevention

**Escape user content and use safe API calls:**

```javascript
import DOMPurify from 'dompurify';

// Sanitize HTML content
const SafeContent = ({ htmlContent }) => {
  const sanitized = DOMPurify.sanitize(htmlContent, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'p', 'br'],
    ALLOWED_ATTR: []
  });
  
  return <div dangerouslySetInnerHTML={{ __html: sanitized }} />;
};

// Escape text content (React does this by default)
const UserComment = ({ comment }) => {
  return <p>{comment}</p>  // Automatically escaped
};
```

### Secure API Calls

**Always validate responses and handle errors:**

```javascript
const secureFetch = async (url, options = {}) => {
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': process.env.REACT_APP_API_KEY,
        ...options.headers
      },
      credentials: 'same-origin'  // Don't send credentials cross-origin
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const contentType = response.headers.get('content-type');
    if (!contentType || !contentType.includes('application/json')) {
      throw new Error('Invalid response type');
    }
    
    return await response.json();
  } catch (error) {
    console.error('API call failed:', error);
    throw error;
  }
};
```

---

## 📝 Documentation Requirements

### Docstrings (Required for All Functions)

**Use comprehensive docstrings following Google/NumPy style:**

```python
def train_model(
    config: Dict[str, Any],
    dataset_path: str,
    checkpoint_dir: Optional[str] = None
) -> Dict[str, float]:
    """
    Train a machine learning model with the given configuration.
    
    This function handles the complete training pipeline including data loading,
    model initialization, training loop, and checkpoint saving. It supports
    distributed training and automatic mixed precision.
    
    Args:
        config: Training configuration dictionary containing:
            - model_type (str): Model architecture identifier
            - batch_size (int): Training batch size
            - learning_rate (float): Initial learning rate
            - epochs (int): Number of training epochs
        dataset_path: Absolute path to training dataset
        checkpoint_dir: Optional directory for saving checkpoints.
                       Defaults to './checkpoints' if None.
    
    Returns:
        Dictionary containing final metrics:
            - train_loss (float): Final training loss
            - eval_loss (float): Final evaluation loss
            - training_time (float): Total training time in seconds
    
    Raises:
        ValueError: If config validation fails
        FileNotFoundError: If dataset_path does not exist
        RuntimeError: If training fails after max retries
    
    Example:
        >>> config = {
        ...     'model_type': 'CodeT5',
        ...     'batch_size': 32,
        ...     'learning_rate': 5e-5,
        ...     'epochs': 3
        ... }
        >>> metrics = train_model(config, '/data/train.json')
        >>> print(f"Final loss: {metrics['train_loss']:.4f}")
    """
    # Implementation
    pass
```

### Code Comments

**Add comments for complex logic only (code should be self-documenting):**

```python
def calculate_learning_rate(
    base_lr: float,
    step: int,
    warmup_steps: int,
    total_steps: int
) -> float:
    """Calculate learning rate with linear warmup and cosine decay."""
    
    # Linear warmup phase
    if step < warmup_steps:
        return base_lr * (step / warmup_steps)
    
    # Cosine decay phase
    progress = (step - warmup_steps) / (total_steps - warmup_steps)
    cosine_decay = 0.5 * (1 + math.cos(math.pi * progress))
    return base_lr * cosine_decay
```

### VS Code Compatibility

**Format code for optimal VS Code experience:**

```python
# Use type hints for IntelliSense
from typing import List, Dict, Optional, Union, Tuple, Any

# Structure for easy navigation (VS Code outline)
class ModelTrainer:
    """Main class for model training operations."""
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize trainer with configuration."""
        self.config = config
        
    def train(self) -> Dict[str, float]:
        """Execute training pipeline."""
        pass
    
    def evaluate(self) -> Dict[str, float]:
        """Evaluate model performance."""
        pass
```

---

## 🛡️ Cybersecurity Best Practices

### Defense in Depth

Implement multiple layers of security:

1. **Input Layer**: Validate and sanitize all inputs
2. **Processing Layer**: Use parameterized queries, safe APIs
3. **Output Layer**: Escape/sanitize all outputs
4. **Infrastructure**: Use HTTPS, secure headers, rate limiting
5. **Monitoring**: Log security events, monitor for anomalies

### Secure Logging

**Log security events without exposing sensitive data:**

```python
import logging
from typing import Any, Dict

# Configure secure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def secure_log_request(request_data: Dict[str, Any]) -> None:
    """Log request data without exposing secrets."""
    # Create sanitized copy
    safe_data = request_data.copy()
    
    # Remove sensitive fields
    sensitive_fields = ['password', 'api_key', 'token', 'secret']
    for field in sensitive_fields:
        if field in safe_data:
            safe_data[field] = '***REDACTED***'
    
    logger.info(f"Request received: {safe_data}")
```

### Dependency Security

**Keep dependencies updated and scan for vulnerabilities:**

```bash
# Check for security vulnerabilities
pip install safety
safety check --json

# Update dependencies regularly
pip list --outdated
pip install --upgrade package_name

# Use requirements.txt with pinned versions
pip freeze > requirements.txt
```

### File Upload Security

**Validate file uploads thoroughly:**

```python
import os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'txt', 'json', 'csv'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def secure_file_upload(file) -> Optional[str]:
    """
    Handle file upload securely.
    
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
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    file.save(filepath)
    logger.info(f"File uploaded successfully: {filename}")
    return filepath
```

---

## 👥 Contributor Guidelines for AI Code Generation

### Before Using Code Generation Tools

1. **Understand the Context**: Read existing code and documentation
2. **Define Requirements**: Clearly specify what you need
3. **Review Architecture**: Ensure generated code fits project structure

### After Generating Code

**⚠️ CRITICAL: Never merge AI-generated code without thorough review**

#### Review Checklist:
- [ ] **Security**: No hardcoded secrets, proper input validation, safe queries
- [ ] **Correctness**: Code logic is correct and handles edge cases
- [ ] **Testing**: Write tests, run existing tests, verify functionality
- [ ] **Style**: Follows PEP 8, has proper docstrings and type hints
- [ ] **Dependencies**: No unnecessary new dependencies
- [ ] **Documentation**: Update docs if behavior changes
- [ ] **Performance**: No obvious performance issues
- [ ] **Error Handling**: Proper exception handling and logging

#### Testing Generated Code:

```bash
# Run linters
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics

# Run tests
python -m unittest discover -s tests

# Type checking (if using mypy)
mypy app.py utils/ components/

# Security scanning
bandit -r . -f json -o bandit-report.json
safety check
```

#### Manual Validation:

```bash
# Test the application
python app.py

# Test specific functionality
python -c "from utils.config_validator import validate_config; \
           print(validate_config({'model_type': 'CodeT5', 'batch_size': 32}))"

# Test database operations
DATABASE_URL="sqlite:///test.db" python -c "from app import MLFineTuningApp; \
                                            app = MLFineTuningApp()"
```

### When to NOT Use AI Generation

**Avoid AI generation for:**
- Security-critical code (authentication, encryption, access control)
- Complex business logic requiring deep domain knowledge
- Database migrations
- Production configuration files
- Cryptographic implementations

### Reporting Issues with AI-Generated Code

If you discover issues in AI-generated code:

1. **Document the problem** clearly
2. **Create a minimal reproduction** example
3. **File an issue** with "AI-generated" tag
4. **Do not merge** until resolved

---

## 🔍 Code Review Standards

### Security Review Checklist

When reviewing code (AI-generated or human-written):

- [ ] No hardcoded credentials or sensitive data
- [ ] All database queries use parameterized queries or ORM
- [ ] User input is validated and sanitized
- [ ] Output is properly escaped
- [ ] Error messages don't expose internal details
- [ ] Authentication and authorization are properly implemented
- [ ] CSRF protection is enabled for forms
- [ ] Rate limiting is implemented for API endpoints
- [ ] Dependencies are up-to-date and vulnerability-free
- [ ] Logging doesn't expose sensitive information

### Quality Review Checklist

- [ ] Code follows PEP 8 style guidelines
- [ ] All functions have comprehensive docstrings
- [ ] Type hints are used consistently
- [ ] Error handling is appropriate
- [ ] Tests cover new functionality
- [ ] Documentation is updated
- [ ] No unnecessary dependencies added
- [ ] Performance is acceptable

---

## 📚 Additional Resources

### Official Documentation
- GitHub Copilot Best Practices: https://gh.io/copilot-coding-agent-tips
- Flask Security: https://flask.palletsprojects.com/en/latest/security/
- SQLAlchemy Security: https://docs.sqlalchemy.org/en/latest/core/security.html
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- Python Security Best Practices: https://python.readthedocs.io/en/stable/library/security_warnings.html

### Project-Specific Documentation
- See `CLAUDE.md` for detailed architecture and development commands
- See `README.md` for project overview and setup instructions
- See `.github/workflows/` for CI/CD pipeline configuration

### Security Tools
- `safety`: Scan Python dependencies for vulnerabilities
- `bandit`: Security linter for Python code
- `flake8`: Python linting and style checking
- `mypy`: Static type checking
- `pytest`: Testing framework with security test support

---

## 🤖 AI Agent Behavioral Rules

### Conceptual YAML Behavioral Template

This section defines how GitHub Copilot and other AI coding assistants should behave when working with CodeTuneStudio. These rules ensure consistency, security, and quality across all AI-generated contributions.

```yaml
copilot:
  role: "pair-programmer with strict guardrails for CodeTuneStudio"
  context:
    project: "CodeTuneStudio - ML model fine-tuning platform"
    stack:
      backend: ["Flask", "Streamlit"]
      database: ["PostgreSQL", "SQLite"]
      ml_framework: ["PyTorch", "Transformers", "PEFT/LoRA"]
    directories: ["core/", "models/", "utils/", "plugins/", "components/"]
  
  must_do:
    - follow repository coding standards and PEP 8 guidelines
    - use async/await patterns for I/O operations; never block the event loop
    - suggest tests and lint checks for any code change
    - use parameterized queries (SQLAlchemy ORM) for all database operations
    - validate and sanitize all user inputs before processing
    - use structured logging with correlation IDs for observability
    - keep secrets in environment variables; never hardcode credentials
    - scope test coverage to core/models/utils/plugins/components directories
    - emit security-conscious code (input validation, output sanitization)
  
  must_not_do:
    - generate untyped code; always include type hints
    - use raw SQL queries or string concatenation for database access
    - bypass code quality gates (Black, Flake8, Ruff, MyPy)
    - commit secrets, API keys, or sensitive data
    - use continue-on-error or || true to mask failures
    - use overly broad test coverage (--cov=.)
    - create large refactors without explicit request
    - expose internal errors or stack traces to end users
  
  code_style:
    formatter: "Black (88 char line length)"
    linters: ["Flake8", "Ruff"]
    type_checker: "MyPy"
    async_patterns: "asyncio with proper cleanup and timeouts"
  
  security_defaults:
    secrets_management: "environment variables via .env files"
    input_validation: "mandatory for all user inputs"
    sql_queries: "parameterized queries or ORM only"
    logging: "structured logs without sensitive data"
    dependency_scanning: "pip-audit and TruffleHog in CI"
  
  ci_integration:
    quality_gates:
      - "Black formatting check"
      - "Flake8 linting"
      - "Ruff additional checks"
      - "MyPy type checking"
      - "Pytest with 80% coverage threshold"
    security_gates:
      - "TruffleHog secret scanning"
      - "pip-audit dependency audit"
      - "SBOM generation (CycloneDX)"
    enforcement: "blocking - all checks must pass before merge"
  
  reviewer_notes:
    highlight:
      - missing tests or insufficient coverage
      - missing type hints or docstrings
      - security vulnerabilities (injection, XSS, secrets)
      - blocking operations inside async flows
      - missing input validation or output sanitization
    suggest:
      - breaking large functions into smaller, testable units
      - adding correlation IDs for request tracking
      - using context managers for resource management

codex:
  role: "automation assistant for CI/CD and maintenance"
  must_do:
    - enforce quality and security gates on all code changes
    - recommend dependency updates with security context
    - validate workflow configurations before deployment
  must_not_do:
    - push releases without passing all quality gates
    - downgrade security settings for convenience
    - skip tests for "minor" changes
```

### Workflow Integration

All code changes to CodeTuneStudio must pass the following automated checks:

**Quality Checks** (`.github/workflows/quality.yml`):
- **Style**: Black, Flake8, Ruff on `core/ models/ utils/ plugins/ components/`
- **Types**: MyPy type checking on same directories
- **Tests**: Pytest with 80% coverage threshold

**Security Checks** (`.github/workflows/security.yml`):
- **Secrets**: TruffleHog with `--only-verified` flag
- **Dependencies**: pip-audit vulnerability scanning
- **SBOM**: Anchore SBOM generation (CycloneDX JSON)

See `docs/ai-assistant-guide.md` for complete developer workflow documentation.

---

## 📝 Summary

**Key Principles:**
1. **Security First**: Never compromise on security practices
2. **Validate Everything**: All inputs, outputs, and configurations
3. **Use Safe APIs**: Parameterized queries, ORM, escape functions
4. **Protect Secrets**: Environment variables, never in code
5. **Document Thoroughly**: Docstrings, comments, type hints
6. **Test Extensively**: Before merging any code
7. **Review Carefully**: Human review is mandatory

**Remember:** AI-generated code is a starting point, not a finished product. Always review, test, and validate before merging.

---

*Last Updated: 2025-12-13*
*For questions or concerns, please open an issue on GitHub.*
