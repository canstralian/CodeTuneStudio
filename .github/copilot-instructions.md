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

> **Note:** This document contains **agent behavioral rules** for GitHub Copilot Coding Agent. For **developer workflow documentation** (tool installation, CI/CD setup, troubleshooting), see [`docs/ai-assistant-guide.md`](../docs/ai-assistant-guide.md).

---

## 🤖 Agent Behavioral Template

The following conceptual YAML template defines the behavioral constraints and expectations for AI agents working on CodeTuneStudio:

```yaml
copilot:
  role: "pair-programmer with strict guardrails"
  project_name: "CodeTuneStudio"
  must_do:
    - follow CodeTuneStudio repository coding standards and async guidelines
    - suggest tests and lint checks for any code change
    - minimize external calls; use mocks in tests
    - keep prompts and completions free of secrets
    - use parameterized SQL queries exclusively (SQLAlchemy ORM preferred)
    - emit structured logs with correlation IDs
    - validate all inputs at service boundaries
    - use type hints for all function signatures
  must_not_do:
    - generate untyped code when the module requires types
    - auto-create large refactors without explicit request
    - bypass code review or CI requirements
    - hardcode secrets, API keys, or credentials
    - use raw SQL queries or string concatenation
    - block the event loop with synchronous I/O in async contexts
    - expose internal system details in error messages
  reviewer_notes:
    - highlight missing tests, logging, or security validations
    - flag blocking operations inside async flows
    - call out missing input validation or output sanitization
    - identify opportunities for better error handling

codex:
  role: "automation copilot for CI/CD and maintenance"
  project_name: "CodeTuneStudio"
  must_do:
    - enforce quality gates (lint, type-check, test) on code diffs
    - ignore documentation-only changes for heavy test runs
    - recommend dependency and security updates regularly
    - pin third-party GitHub Actions to commit SHAs
    - scope coverage targets to core/, components/, utils/, plugins/
  must_not_do:
    - push releases without passing quality gates
    - downgrade security settings for speed
    - use || true to mask test failures
    - run MyPy on root directory (use specific packages)
```

This template guides agent behavior to align with CodeTuneStudio's architecture, security requirements, and development practices.

---

## 🔄 Async Pattern Mandates

### Required Async Patterns

**ALL asynchronous code in CodeTuneStudio MUST follow these patterns:**

#### 1. Use `asyncio` Primitives

```python
import asyncio
from typing import Optional

async def fetch_data(url: str, timeout: float = 5.0) -> Optional[dict]:
    """
    Fetch data from API with timeout and proper error handling.
    
    Args:
        url: API endpoint URL
        timeout: Request timeout in seconds
        
    Returns:
        Parsed JSON response or None on failure
    """
    try:
        async with asyncio.timeout(timeout):  # Python 3.11+
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    return await response.json()
    except asyncio.TimeoutError:
        logger.error(f"Timeout fetching {url}", extra={"url": url})
        return None
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}", exc_info=True)
        return None
```

#### 2. Use `async with` for Resource Management

```python
# ✅ CORRECT - Automatic cleanup with async context manager
async with aiofiles.open('file.txt', 'w') as f:
    await f.write(data)

# ❌ WRONG - No automatic cleanup
f = await aiofiles.open('file.txt', 'w')
await f.write(data)
await f.close()  # Easy to forget
```

#### 3. Cancel Tasks Cleanly

```python
async def supervised_task():
    """Run task with proper cancellation handling."""
    task = asyncio.create_task(long_running_operation())
    
    try:
        result = await task
        return result
    except asyncio.CancelledError:
        logger.info("Task cancelled, cleaning up...")
        # Perform cleanup
        raise  # Re-raise to propagate cancellation
```

#### 4. NEVER Block the Event Loop

**❌ PROHIBITED:**
```python
async def bad_async_function():
    # NEVER do synchronous I/O in async context
    with open('file.txt') as f:  # BLOCKS EVENT LOOP
        data = f.read()
    
    time.sleep(5)  # BLOCKS EVENT LOOP
    
    requests.get(url)  # BLOCKS EVENT LOOP
```

**✅ REQUIRED:**
```python
async def good_async_function():
    # Use async file I/O
    async with aiofiles.open('file.txt') as f:
        data = await f.read()
    
    # Use async sleep
    await asyncio.sleep(5)
    
    # Use async HTTP client
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.text()
```

#### 5. Use Timeouts and Semaphores

```python
from asyncio import Semaphore

# Limit concurrent operations
semaphore = Semaphore(10)

async def rate_limited_operation(item):
    """Execute operation with concurrency limit."""
    async with semaphore:
        return await process_item(item)

# Timeout for long operations
async def with_timeout():
    """Execute with timeout protection."""
    try:
        async with asyncio.timeout(30):
            return await expensive_operation()
    except asyncio.TimeoutError:
        logger.error("Operation timed out after 30s")
        raise
```

---

## 🔐 Security Defaults (Expanded)

### Mandatory Security Requirements

#### 1. No Secrets in Logs

**❌ PROHIBITED:**
```python
logger.info(f"Connecting with API key: {api_key}")
logger.debug(f"User password: {password}")
```

**✅ REQUIRED:**
```python
# Sanitize before logging
def sanitize_for_logging(data: dict) -> dict:
    """Remove sensitive fields from logging data."""
    sensitive_keys = {'password', 'api_key', 'token', 'secret', 'credential'}
    return {
        k: '***REDACTED***' if k.lower() in sensitive_keys else v
        for k, v in data.items()
    }

logger.info("User login", extra=sanitize_for_logging(request_data))
```

#### 2. Parameterized SQL (Mandatory)

**ALL database queries MUST use parameterized queries or SQLAlchemy ORM.**

See [Database Security section](#-database-security-postgresqlsqlite) for detailed examples.

#### 3. Input Validation at Boundaries

**Every external input MUST be validated before processing:**

```python
from pydantic import BaseModel, validator, Field

class TrainingConfigInput(BaseModel):
    """Validated training configuration."""
    model_type: str = Field(..., regex="^(CodeT5|CodeBERT|GPT2)$")
    batch_size: int = Field(..., ge=1, le=512)
    learning_rate: float = Field(..., gt=0, le=1.0)
    epochs: int = Field(..., ge=1, le=100)
    
    @validator('model_type')
    def validate_model_type(cls, v):
        """Ensure model type is supported."""
        allowed = {'CodeT5', 'CodeBERT', 'GPT2'}
        if v not in allowed:
            raise ValueError(f"Model type must be one of {allowed}")
        return v

# Usage in API endpoint
@app.route('/api/train', methods=['POST'])
def start_training():
    """Start training with validated input."""
    try:
        config = TrainingConfigInput(**request.json)
        result = train_model(config.dict())
        return jsonify(result), 200
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
```

---

## 📊 Logging Standards

### Structured Logging Requirements

**ALL log entries MUST use structured logging with correlation IDs:**

```python
import logging
import uuid
from contextvars import ContextVar

# Context variable for correlation IDs
correlation_id: ContextVar[str] = ContextVar('correlation_id', default='')

class CorrelationFilter(logging.Filter):
    """Add correlation ID to log records."""
    
    def filter(self, record):
        record.correlation_id = correlation_id.get() or 'N/A'
        return True

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(correlation_id)s] - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)

# Add filter to all loggers
for handler in logging.root.handlers:
    handler.addFilter(CorrelationFilter())

logger = logging.getLogger(__name__)

# Usage in request handlers
@app.before_request
def set_correlation_id():
    """Set correlation ID for request tracking."""
    request_id = request.headers.get('X-Request-ID') or str(uuid.uuid4())
    correlation_id.set(request_id)
    g.correlation_id = request_id

@app.after_request
def add_correlation_header(response):
    """Add correlation ID to response."""
    response.headers['X-Correlation-ID'] = g.get('correlation_id', 'N/A')
    return response

# Structured logging with extra context
logger.info(
    "Training job started",
    extra={
        'job_id': job.id,
        'model_type': config.model_type,
        'batch_size': config.batch_size
    }
)
```

### Log Level Guidelines

**Use consistent log levels:**

- **`DEBUG`**: Verbose diagnostic information (disabled in production)
- **`INFO`**: General informational messages (state changes, milestones)
- **`WARNING`**: Recoverable issues that don't stop execution
- **`ERROR`**: Errors requiring attention but system continues
- **`CRITICAL`**: Fatal errors requiring immediate intervention

```python
# Examples
logger.debug(f"Processing item {item_id}")  # Verbose trace
logger.info(f"Training started for job {job_id}")  # State change
logger.warning(f"Retry attempt {attempt}/3")  # Recoverable issue
logger.error(f"Failed to load model: {error}")  # Error occurred
logger.critical(f"Database connection lost")  # System failure
```

---

## 🎨 Code Style Enforcement (Expanded)

### Mandatory Style Requirements

#### 1. PEP 8 Compliance

**ALL Python code MUST follow PEP 8:**

- Line length: 88 characters (Black formatter compatible)
- Indentation: 4 spaces (no tabs)
- Imports: Grouped and sorted (stdlib, third-party, local)
- Naming: `snake_case` for functions/variables, `PascalCase` for classes
- Docstrings: Required for all public functions/classes

#### 2. Type Hints (Mandatory)

**ALL function signatures MUST include type hints:**

```python
from typing import Dict, List, Optional, Union, Any

# ✅ CORRECT
def process_data(
    items: List[Dict[str, Any]],
    config: Optional[Dict[str, Union[str, int]]] = None
) -> Dict[str, float]:
    """Process data items with optional configuration."""
    # Implementation
    return results

# ❌ WRONG - Missing type hints
def process_data(items, config=None):
    # Implementation
    return results
```

#### 3. Import Organization

**Use `isort` for consistent import ordering:**

```python
# Standard library imports
import os
import sys
from typing import Dict, List

# Third-party imports
import numpy as np
import pandas as pd
from flask import Flask, request

# Local imports
from core.models import TrainingConfig
from utils.validators import validate_input
```

#### 4. Docstring Requirements

**ALL public functions MUST have comprehensive docstrings:**

See [Documentation Requirements section](#-documentation-requirements) for detailed examples.

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

*Last Updated: 2024-06-11*
*For questions or concerns, please open an issue on GitHub.*
