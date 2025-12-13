# GitHub Copilot & AI Code Generation Guide for CodeTuneStudio

## Purpose and Scope

This guide provides comprehensive guidance for developers using GitHub Copilot, Codex, or other AI code generation tools when contributing to the CodeTuneStudio repository. It ensures consistency, security, and quality across all AI-assisted code contributions.

**Important:** All contributors using AI code generation tools **must** review, test, and validate all generated code before merging. AI suggestions are starting points, not finished products.

For official GitHub Copilot best practices, see: https://gh.io/copilot-coding-agent-tips

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
Always document required environment variables in `.env.example`:

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

## 🐍 Python Development Standards

### Code Style

**PEP 8 Compliance:**
- Max line length: 88 characters (Black formatter compatible)
- Use type hints for all function signatures
- Follow snake_case for functions/variables
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

### Database Security

**⛔ NEVER use raw SQL or string concatenation:**

```python
# ❌ WRONG - SQL Injection Vulnerability
user_id = request.args.get('id')
query = f"SELECT * FROM users WHERE id = {user_id}"  # DANGEROUS
```

**✅ CORRECT - Use SQLAlchemy ORM or parameterized queries:**

```python
from sqlalchemy import text
from utils.database import db, TrainingConfig

# Method 1: SQLAlchemy ORM (PREFERRED)
def get_training_config(config_id: int) -> Optional[TrainingConfig]:
    """Retrieve training config using ORM (safe from SQL injection)."""
    return TrainingConfig.query.filter_by(id=config_id).first()

# Method 2: Parameterized queries
def get_configs_by_model(model_type: str) -> List[TrainingConfig]:
    """Retrieve configs with parameterized query."""
    stmt = text("SELECT * FROM training_config WHERE model_type = :model_type")
    result = db.session.execute(stmt, {"model_type": model_type})
    return result.fetchall()
```

---

## 🧪 Testing Requirements

### Test Coverage
- All code changes **must** include unit tests
- Integration tests required for API endpoints and database operations
- Use `pytest` as the testing framework
- Maintain or improve existing test coverage

### Test Structure
```python
import pytest
from your_module import your_function

def test_your_function_with_valid_input():
    """Test function with valid input."""
    result = your_function(valid_input)
    assert result == expected_output

def test_your_function_with_invalid_input():
    """Test function handles invalid input correctly."""
    with pytest.raises(ValueError):
        your_function(invalid_input)

@pytest.fixture
def sample_config():
    """Provide sample configuration for tests."""
    return {
        'model_type': 'CodeT5',
        'batch_size': 32,
        'learning_rate': 5e-5
    }
```

### Running Tests
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=core --cov=utils --cov=components tests/

# Run specific test file
pytest tests/test_database.py

# Run with verbose output
pytest -v tests/
```

---

## 📝 Documentation Requirements

### Docstrings (Required for All Functions)

Use comprehensive docstrings following Google/NumPy style:

```python
def train_model(
    config: Dict[str, Any],
    dataset_path: str,
    checkpoint_dir: Optional[str] = None
) -> Dict[str, float]:
    """
    Train a machine learning model with the given configuration.
    
    This function handles the complete training pipeline including data loading,
    model initialization, training loop, and checkpoint saving.
    
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

---

## 🔧 Code Quality Tools

### Linting and Formatting

**Required Tools:**
- `black` - Code formatting (88 character line length)
- `flake8` - Linting and PEP 8 compliance
- `mypy` - Static type checking (optional but recommended)

**Running Quality Checks:**
```bash
# Format code
black .

# Check linting
flake8 .

# Type checking
mypy core/ utils/ components/

# Run all checks
black . && flake8 . && pytest tests/
```

### Pre-commit Hooks

Set up pre-commit hooks for automatic checking:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

---

## 👥 AI Code Generation Best Practices

### Before Using AI Code Generation

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

# Run tests
python -m unittest discover -s tests

# Security scanning
bandit -r . -f json -o bandit-report.json
safety check
```

### When to NOT Use AI Generation

**Avoid AI generation for:**
- Security-critical code (authentication, encryption, access control)
- Complex business logic requiring deep domain knowledge
- Database migrations
- Production configuration files
- Cryptographic implementations

---

## 🚀 CI/CD Integration

### GitHub Workflows

CodeTuneStudio uses GitHub Actions for CI/CD:

- **ci.yml**: Main CI pipeline (linting, testing)
- **python-style-checks.yml**: Code style validation
- **huggingface-deploy.yml**: Model deployment
- **security-and-deps.yml**: Security scanning

### Quality Gates

All PRs must pass:
- Code formatting checks (Black)
- Linting (Flake8)
- Unit tests (pytest)
- Security scans (where applicable)

---

## 📚 Additional Resources

### Official Documentation
- GitHub Copilot Best Practices: https://gh.io/copilot-coding-agent-tips
- Flask Security: https://flask.palletsprojects.com/en/latest/security/
- SQLAlchemy Security: https://docs.sqlalchemy.org/en/latest/core/security.html
- OWASP Top 10: https://owasp.org/www-project-top-ten/

### Project-Specific Documentation
- [Architecture Guide](ARCHITECTURE.md) - System design and component overview
- [Plugin Development Guide](PLUGIN_GUIDE.md) - Create custom code analysis plugins
- [Contributing Guidelines](../CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Guidelines](CONTRIBUTING_CODE_QUALITY.md) - Detailed code quality standards

---

## 📝 Summary

**Key Principles:**
1. **Security First**: Never compromise on security practices
2. **Validate Everything**: All inputs, outputs, and configurations
3. **Use Safe APIs**: Parameterized queries, ORM, escape functions
4. **Protect Secrets**: Environment variables, never in code
5. **Document Thoroughly**: Docstrings, comments, type hints
6. **Test Extensively**: Before merging any code
7. **Review Carefully**: Human review is mandatory for all AI-generated code

**Remember:** AI-generated code is a starting point, not a finished product. Always review, test, and validate before merging.

---

*For questions or concerns, please open an issue on GitHub.*
*Last Updated: 2024-12-13*
