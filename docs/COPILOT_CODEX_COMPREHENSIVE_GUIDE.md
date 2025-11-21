# GitHub Copilot & Codex Comprehensive Configuration Guide

> **Version:** 1.0.0  
> **Last Updated:** 2025-11-21  
> **Scope:** CodeTuneStudio & Trading Bot Swarm Ecosystem

---

## Table of Contents

- [Purpose and Scope](#purpose-and-scope)
- [Configuration Overview](#configuration-overview)
- [Copilot as a Disciplined Pair Programmer](#copilot-as-a-disciplined-pair-programmer)
- [Testing and Linting Automation](#testing-and-linting-automation)
- [Code Style Standards](#code-style-standards)
- [Security Scanning Methodologies](#security-scanning-methodologies)
- [Semantic Release Processes](#semantic-release-processes)
- [CI/CD Integration](#cicd-integration)
- [Contributor Expectations](#contributor-expectations)
- [Maintenance Workflows](#maintenance-workflows)
- [Troubleshooting Guide](#troubleshooting-guide)
- [Best Practices Summary](#best-practices-summary)

---

## Purpose and Scope

This guide establishes operational standards for integrating GitHub Copilot and
Codex within the CodeTuneStudio and Trading Bot Swarm ecosystem. It ensures
that AI-assisted development maintains the highest standards of:

- **Code Quality**: PEP 8 compliance, type safety, and maintainability
- **Security**: Vulnerability scanning, secrets management, and secure defaults
- **Testing**: Comprehensive test coverage and automated validation
- **Automation**: CI/CD pipelines, semantic versioning, and release management
- **Observability**: Structured logging, metrics, and tracing

### Target Audience

- Software engineers contributing to the codebase
- Code reviewers and maintainers
- DevOps engineers managing CI/CD pipelines
- Security teams implementing scanning policies

### Related Documentation

- [GitHub Copilot Instructions](.github/copilot-instructions.md)
- [Architecture Guide](docs/ARCHITECTURE.md)
- [Contributing Guidelines](docs/CONTRIBUTING_CODE_QUALITY.md)
- [Security Policy](SECURITY.md)

---

## Configuration Overview

### Core Principles

GitHub Copilot and Codex function as disciplined pair programmers who:

1. **Propose Minimal Changes**: Suggest incremental, auditable modifications
2. **Preserve Safety Controls**: Never bypass security, authentication, or
   authorization mechanisms
3. **Require Testing**: Include test requirements with every code suggestion
4. **Follow Standards**: Adhere to project formatters, type hints, and async
   patterns
5. **Respect Architecture**: Align with existing design patterns and
   conventions

### Behavioral Constraints

**ALWAYS:**
- Mention required tests and linters for proposed changes
- Provide context-aware suggestions referencing relevant modules
- Use structured logging with correlation IDs
- Default to defensive error handling and explicit timeouts
- Surface test commands and note when tests are skipped

**NEVER:**
- Suggest code that bypasses security policies or secrets management
- Propose documentation-only edits unless explicitly requested
- Invent APIs, data sources, or environment variables without references
- Use print debugging (use project logging helpers instead)
- Suggest hard-coded secrets or PII in code

---

## Copilot as a Disciplined Pair Programmer

### Custom Instructions Configuration

The `.github/copilot-instructions.md` file defines Copilot's behavior:

```yaml
copilot:
  role: "Disciplined pair programmer for Trading Bot Swarm"
  rules:
    - "Use minimal diffs; preserve safety and compliance controls"
    - "Require tests/linters for code changes"
    - "Follow project formatters and typing standards"
    - "Propose structured async with timeouts and cancellation"
    - "Never suggest hard-coded secrets or PII"
    - "Use structured logging; avoid print statements"
    - "State test commands in suggestions"
    - "Ask for clarification when requirements are ambiguous"
  
codex:
  role: "Automation assistant enforcing quality gates"
  rules:
    - "Run linters and tests before merge"
    - "Reject suggestions that reduce security posture"
    - "Align with CI/CD workflows and release policies"
```

### Interaction Patterns

#### Requesting Code Suggestions

**Good Request:**
```
Create a function to validate user input for the trading bot configuration.
Requirements:
- Type hints for all parameters
- Validate numeric ranges (0.0 to 1.0 for confidence threshold)
- Return tuple of (is_valid: bool, errors: List[str])
- Include unit tests with pytest
```

**Poor Request:**
```
Make a function to check input
```

#### Reviewing Copilot Suggestions

1. **Verify Security**: No hardcoded secrets, proper input validation
2. **Check Tests**: Ensure test coverage for new logic
3. **Validate Style**: PEP 8 compliance, type hints present
4. **Review Dependencies**: No unnecessary new packages
5. **Test Locally**: Run linters and tests before committing

---

## Testing and Linting Automation

### Testing Standards

#### Test Framework

- **Python**: pytest with coverage reporting
- **JavaScript/TypeScript**: jest or equivalent

#### Test Requirements

All code changes **MUST** include:

1. **Unit Tests**: Test individual functions/methods in isolation
2. **Integration Tests**: Test component interactions
3. **Edge Cases**: Boundary conditions, error scenarios
4. **Coverage Target**: Minimum 80% code coverage

#### Running Tests

```bash
# Run all tests with coverage
pytest -v --cov=. --cov-report=xml --cov-report=term

# Run specific test file
pytest tests/test_specific.py -v

# Run tests matching pattern
pytest -k "test_validation" -v

# Run with maximum verbosity and stop on first failure
pytest -vv --maxfail=1

# Run tests in parallel (requires pytest-xdist)
pytest -n auto
```

### Linting Standards

#### Primary Linters

**Python:**
- **flake8**: PEP 8 compliance (enforced in CI)
- **ruff**: Fast linting (optional for local development)
- **black**: Code formatting (88 character line length)
- **mypy**: Static type checking

**JavaScript/TypeScript:**
- **eslint**: Code quality and style
- **prettier**: Code formatting

#### Running Linters

```bash
# Python - Critical errors only (CI requirement)
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

# Python - Full check with complexity analysis
flake8 . --count --max-complexity=10 --max-line-length=88 --statistics

# Python - Format check with Black
black --check --line-length=88 .

# Python - Auto-format with Black
black --line-length=88 .

# Python - Type checking
mypy core/ --ignore-missing-imports

# Ruff (fast alternative for local dev)
ruff check .
ruff check . --fix  # Auto-fix issues
```

#### Pre-commit Hooks

Install pre-commit hooks to automatically run linters:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks from .pre-commit-config.yaml
pre-commit install

# Run against all files
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files
```

### Automated Quality Gates

The CI pipeline enforces quality standards on every pull request:

**Quality Gate Steps:**
1. Checkout code with full history
2. Set up Python 3.10+ and Node.js 20+
3. Install dependencies with caching
4. Run linters (fail on critical errors)
5. Run type checkers (mypy for Python)
6. Run tests with coverage reporting
7. Upload coverage artifacts
8. Block merge if any check fails

---

## Code Style Standards

### Python (PEP 8 Compliance)

#### General Standards

- **Line Length**: 88 characters (Black formatter compatible)
- **Indentation**: 4 spaces (never tabs)
- **Imports**: Organized (stdlib, third-party, local)
- **Naming**: snake_case for functions/variables, PascalCase for classes
- **Type Hints**: Required for all function signatures

#### Example

```python
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


def validate_training_config(
    config: Dict[str, Any],
    dataset_name: Optional[str] = None
) -> tuple[bool, List[str]]:
    """
    Validate training configuration parameters.
    
    Args:
        config: Dictionary containing training parameters
        dataset_name: Optional dataset identifier
        
    Returns:
        Tuple of (is_valid, errors) where errors is list of messages
        
    Raises:
        ValueError: If config is None or invalid type
    """
    if not isinstance(config, dict):
        raise ValueError("config must be a dictionary")
    
    errors: List[str] = []
    
    # Validate required fields
    required_fields = ["model_type", "batch_size", "learning_rate"]
    for field in required_fields:
        if field not in config:
            errors.append(f"Missing required field: {field}")
    
    # Validate numeric ranges
    if "learning_rate" in config:
        lr = config["learning_rate"]
        if not isinstance(lr, (int, float)) or lr <= 0 or lr >= 1:
            errors.append("learning_rate must be between 0 and 1")
    
    is_valid = len(errors) == 0
    if is_valid:
        logger.info("Configuration validated successfully")
    else:
        logger.warning(f"Configuration validation failed: {errors}")
    
    return is_valid, errors
```

### Async/Await Patterns

#### Best Practices

1. **Structured Concurrency**: Use asyncio.gather() or TaskGroup
2. **Timeout Handling**: Always include timeouts for network operations
3. **Cancellation**: Support graceful cancellation via asyncio.CancelledError
4. **Bounded Retries**: Implement exponential backoff with max attempts

#### Example

```python
import asyncio
from typing import List, Optional


async def fetch_market_data(
    symbol: str,
    timeout: float = 30.0
) -> Optional[Dict[str, Any]]:
    """
    Fetch market data with timeout and error handling.
    
    Args:
        symbol: Trading symbol (e.g., "BTC/USD")
        timeout: Maximum time to wait in seconds
        
    Returns:
        Market data dictionary or None on failure
    """
    try:
        async with asyncio.timeout(timeout):
            # Simulated API call
            await asyncio.sleep(0.1)
            return {"symbol": symbol, "price": 50000.0}
    except asyncio.TimeoutError:
        logger.error(f"Timeout fetching data for {symbol}")
        return None
    except asyncio.CancelledError:
        logger.info(f"Cancelled fetching data for {symbol}")
        raise
    except Exception as e:
        logger.exception(f"Error fetching data for {symbol}: {e}")
        return None


async def fetch_multiple_symbols(
    symbols: List[str],
    timeout: float = 30.0
) -> Dict[str, Optional[Dict[str, Any]]]:
    """
    Fetch data for multiple symbols concurrently.
    
    Args:
        symbols: List of trading symbols
        timeout: Timeout per symbol
        
    Returns:
        Dictionary mapping symbols to their data
    """
    tasks = [fetch_market_data(symbol, timeout) for symbol in symbols]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return {
        symbol: result if not isinstance(result, Exception) else None
        for symbol, result in zip(symbols, results)
    }
```

### Logging and Observability

#### Structured Logging

```python
import logging
from typing import Any, Dict

# Use project logging module
from core.logging import get_logger

logger = get_logger(__name__)


def process_trade(
    trade_id: str,
    amount: float,
    correlation_id: str
) -> bool:
    """
    Process a trade with structured logging.
    
    Args:
        trade_id: Unique trade identifier
        amount: Trade amount
        correlation_id: Request correlation ID for tracing
        
    Returns:
        True if successful, False otherwise
    """
    logger.info(
        "Processing trade",
        extra={
            "trade_id": trade_id,
            "amount": amount,
            "correlation_id": correlation_id,
        }
    )
    
    try:
        # Process trade logic
        result = True
        
        logger.info(
            "Trade processed successfully",
            extra={
                "trade_id": trade_id,
                "correlation_id": correlation_id,
                "result": result,
            }
        )
        return result
    except Exception as e:
        logger.error(
            "Trade processing failed",
            extra={
                "trade_id": trade_id,
                "correlation_id": correlation_id,
                "error": str(e),
            },
            exc_info=True
        )
        return False
```

---

## Security Scanning Methodologies

### Security Principles

1. **Defense in Depth**: Multiple security layers
2. **Least Privilege**: Minimal permissions for all components
3. **Secrets Management**: Never hardcode credentials
4. **Input Validation**: Sanitize and validate all inputs
5. **Dependency Scanning**: Regular vulnerability checks

### Secrets Management

#### Environment Variables

**Always** use environment variables for sensitive data:

```python
import os

# Correct: Load from environment
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///database.db")
API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable required")

# Never do this:
# API_KEY = "sk-1234567890abcdef"  # PROHIBITED
```

#### .env.example Template

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# API Keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
HF_TOKEN=your_huggingface_token_here

# Security
SECRET_KEY=your_secret_key_here

# Observability
SQL_DEBUG=False
LOG_LEVEL=INFO

# Application
SPACE_ID=your_space_id
HOST=localhost
PORT=7860
```

### Dependency Scanning

#### Python Dependencies

```bash
# Install security scanning tools
pip install safety pip-audit bandit

# Scan dependencies for known vulnerabilities
safety check --json

# Audit dependencies (checks PyPI advisories)
pip-audit --requirement requirements.txt

# Security linting (SAST)
bandit -r . -f json -o bandit-report.json
```

#### Automated Security Workflow

The security scanning workflow runs:
- **Schedule**: Weekly on Mondays at 3 AM UTC
- **Triggers**: Pull requests to main branch
- **Tools**: pip-audit, Trivy, CodeQL

```yaml
name: Security Scan

on:
  schedule:
    - cron: "0 3 * * 1"  # Weekly on Monday
  pull_request:
    branches: [main]
  workflow_dispatch:

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Python Dependency Audit
        run: |
          pipx run pip-audit --requirement requirements.txt
      
      - name: Trivy Filesystem Scan
        uses: aquasecurity/trivy-action@v0.24.0
        with:
          scan-type: fs
          format: sarif
          output: trivy-results.sarif
          severity: HIGH,CRITICAL
      
      - name: CodeQL Analysis
        uses: github/codeql-action/analyze@v3
        with:
          languages: python,javascript
      
      - name: Upload Security Findings
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: security-findings
          path: trivy-results.sarif
```

### Input Validation and Sanitization

#### Validation Example

```python
import re
from typing import Any, List


def sanitize_string(value: str, max_length: int = 255) -> str:
    """
    Sanitize string input by removing dangerous characters.
    
    Args:
        value: Input string to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string safe for database/display
        
    Raises:
        ValueError: If input is invalid
    """
    if not isinstance(value, str):
        raise ValueError("Input must be a string")
    
    if len(value) > max_length:
        raise ValueError(f"Input exceeds {max_length} characters")
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r"[^a-zA-Z0-9_\-\.\s]", "", value.strip())
    
    return sanitized


def validate_numeric_range(
    value: float,
    min_val: float,
    max_val: float,
    param_name: str
) -> List[str]:
    """
    Validate numeric parameter within acceptable range.
    
    Args:
        value: Numeric value to validate
        min_val: Minimum acceptable value
        max_val: Maximum acceptable value
        param_name: Parameter name for error messages
        
    Returns:
        List of validation errors (empty if valid)
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
```

### Database Security

#### Parameterized Queries (Required)

**Never** use string concatenation for SQL queries:

```python
from sqlalchemy import text
from utils.database import db, TrainingConfig

# CORRECT: SQLAlchemy ORM (preferred)
def get_training_config(config_id: int) -> Optional[TrainingConfig]:
    """Retrieve training config using ORM (safe)."""
    return TrainingConfig.query.filter_by(id=config_id).first()

# CORRECT: Parameterized query
def get_configs_by_model(model_type: str) -> List[TrainingConfig]:
    """Retrieve configs with parameterized query."""
    stmt = text(
        "SELECT * FROM training_config WHERE model_type = :model_type"
    )
    result = db.session.execute(stmt, {"model_type": model_type})
    return result.fetchall()

# WRONG: SQL injection vulnerability
# query = f"SELECT * FROM users WHERE id = {user_id}"  # NEVER DO THIS
```

---

## Semantic Release Processes

### Conventional Commits

Use conventional commit messages to drive automated versioning:

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### Types

- **feat**: New feature (minor version bump)
- **fix**: Bug fix (patch version bump)
- **docs**: Documentation changes
- **style**: Code style changes (formatting)
- **refactor**: Code refactoring
- **perf**: Performance improvements
- **test**: Adding or updating tests
- **build**: Build system changes
- **ci**: CI configuration changes
- **chore**: Other changes (dependencies, etc.)

#### Breaking Changes

Add `BREAKING CHANGE:` in footer for major version bump:

```
feat(api): change response format for training endpoints

BREAKING CHANGE: The API response format has changed from array to object.
```

### Release Workflow

The semantic release workflow:

1. Analyzes commit messages since last release
2. Determines version bump (major, minor, patch)
3. Generates changelog
4. Creates git tag
5. Publishes GitHub release
6. (Optional) Publishes to PyPI

#### Workflow Configuration

```yaml
name: Semantic Release

on:
  push:
    branches: [main]

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      issues: write
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          token: ${{ secrets.GITHUB_TOKEN }}
      
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      
      - name: Install dependencies
        run: npm ci
      
      - name: Semantic Release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: npx semantic-release
```

### Manual Release Process

For manual releases:

```bash
# 1. Update version in core/__init__.py
__version__ = "0.3.0"

# 2. Update CHANGELOG.md
# Add release notes under new version section

# 3. Commit changes
git add core/__init__.py CHANGELOG.md
git commit -m "chore(release): bump version to 0.3.0"

# 4. Create and push tag
git tag -a v0.3.0 -m "Release version 0.3.0"
git push origin main --tags

# 5. Trigger release workflow
# The workflow will build and publish to PyPI
```

---

## CI/CD Integration

### Branch Protection

Enforce quality standards with branch protection rules:

**Required Settings:**
- Require pull request before merging
- Require status checks to pass:
  - `lint` (Python style checks)
  - `test` (Unit and integration tests)
  - `type-check` (Static type checking)
  - `security` (Dependency scanning)
- Require conversation resolution
- Require signed commits (recommended)
- Include administrators (enforce for all)

### CI Pipeline Overview

#### Quality Gate Workflow (`ci.yml`)

**Triggers:**
- Pull requests to `main`
- Pushes to `main`
- Ignores documentation-only changes

**Jobs:**
1. **Lint**: flake8, black, ruff
2. **Type Check**: mypy static analysis
3. **Test**: pytest with coverage (Python 3.10, 3.11)
4. **Build**: Package build validation

#### Style Checks Workflow (`python-style-checks.yml`)

**Additional Checks:**
- Black formatting verification
- Flake8 complexity analysis
- Pre-commit hook validation

#### Hugging Face Deploy Workflow (`huggingface-deploy.yml`)

**Triggers:**
- Pushes to `main` branch (after tests pass)

**Actions:**
- Deploys model to Hugging Face Hub
- Updates Space metadata

### Local Development Workflow

```bash
# 1. Create feature branch
git checkout -b feature/add-validation

# 2. Make changes with Copilot assistance

# 3. Run linters locally
flake8 . --select=E9,F63,F7,F82
black --check .

# 4. Run tests locally
pytest -v --cov=. --cov-report=term

# 5. Commit with conventional commit message
git add .
git commit -m "feat(validation): add input validation for config"

# 6. Push and create PR
git push origin feature/add-validation

# 7. Wait for CI checks to pass
# 8. Request review from maintainers
# 9. Address review comments
# 10. Squash and merge after approval
```

---

## Contributor Expectations

### Before Contributing

1. **Read Documentation**:
   - [Contributing Guidelines](docs/CONTRIBUTING_CODE_QUALITY.md)
   - [Architecture Guide](docs/ARCHITECTURE.md)
   - [Security Policy](SECURITY.md)

2. **Set Up Development Environment**:
   ```bash
   # Clone repository
   git clone https://github.com/canstralian/CodeTuneStudio.git
   cd CodeTuneStudio
   
   # Install dependencies
   pip install -r requirements.txt
   pip install -e ".[dev]"
   
   # Install pre-commit hooks
   pre-commit install
   ```

3. **Understand Project Context**:
   - CodeTuneStudio architecture
   - Plugin system design
   - Database schema
   - Testing patterns

### Contribution Workflow

#### 1. Open an Issue

Before implementing changes:

- **Describe**: Clearly state the problem or feature
- **Context**: Provide use cases and examples
- **Risk**: Assess potential impact on existing features
- **Testing**: Outline testing approach
- **Security**: Note any security considerations

#### 2. Implement Changes

- **Branch Naming**: `feature/<ticket-id>-<summary>` or `fix/<issue-number>`
- **Small Commits**: Atomic, logical changesets
- **Conventional Commits**: Follow commit message format
- **Documentation**: Update relevant docs

#### 3. Testing Requirements

**Must Include:**
- Unit tests for new functions/methods
- Integration tests for component interactions
- Edge case coverage
- Minimum 80% code coverage for changed files

**Test Checklist:**
```bash
# Run full test suite
pytest -v --cov=. --cov-report=term

# Check specific coverage
pytest --cov=components/new_feature --cov-report=html

# Run with all warnings
pytest -v -W error
```

#### 4. Quality Checks

Run all checks before submitting PR:

```bash
# Linting
flake8 . --select=E9,F63,F7,F82
black --check .
ruff check .

# Type checking
mypy core/

# Security checks (recommended)
bandit -r . -ll

# Pre-commit hooks
pre-commit run --all-files
```

#### 5. Pull Request

**PR Template:**

```markdown
## Description
Brief description of changes

## Related Issue
Fixes #123

## Changes Made
- [ ] Added validation for user input
- [ ] Updated tests
- [ ] Updated documentation

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed

## Security Considerations
- [ ] No hardcoded secrets
- [ ] Input validation implemented
- [ ] No SQL injection vulnerabilities

## Checklist
- [ ] Code follows PEP 8 style guide
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] Commit messages follow conventional format
```

### Code Review Criteria

Reviewers will check:

1. **Functionality**: Code works as intended
2. **Security**: No vulnerabilities introduced
3. **Testing**: Adequate test coverage
4. **Style**: PEP 8 compliance
5. **Documentation**: Clear docstrings and comments
6. **Performance**: No obvious bottlenecks
7. **Architecture**: Fits project design patterns

### Merge Requirements

**Before Merge:**
- [ ] All CI checks pass
- [ ] Code review approved by maintainer
- [ ] Conversations resolved
- [ ] Commits squashed (if multiple)
- [ ] Changelog updated (for features)

---

## Maintenance Workflows

### Quarterly Reviews

**Schedule**: Every 3 months or after major releases

**Review Checklist:**
- [ ] Update this guide with new practices
- [ ] Review and update CI/CD workflows
- [ ] Audit dependency versions
- [ ] Review security scan results
- [ ] Update contributor guidelines
- [ ] Archive outdated documentation

### Dependency Updates

**Monthly Tasks:**

```bash
# Check for outdated packages
pip list --outdated

# Update dependencies (test thoroughly)
pip install --upgrade <package>

# Update requirements.txt
pip freeze > requirements.txt

# Run full test suite
pytest -v

# Check for vulnerabilities
pip-audit
safety check
```

### Security Audits

**Weekly Automated:**
- Dependency scanning (pip-audit, safety)
- SAST scanning (bandit, CodeQL)
- Container scanning (Trivy)

**Monthly Manual:**
- Review security findings
- Update security policies
- Rotate API keys and tokens
- Review access permissions

### Documentation Maintenance

**Continuous:**
- Update docs with code changes
- Keep examples current
- Fix broken links
- Update version numbers

**Quarterly:**
- Review entire documentation
- Update screenshots
- Refresh tutorials
- Archive outdated guides

---

## Troubleshooting Guide

### Common Issues

#### Copilot Suggests Insecure Code

**Problem**: Copilot suggests hardcoded secrets or unsafe patterns

**Solution**:
1. Regenerate with stronger security prompt
2. Add security requirements to comments
3. Review `.github/copilot-instructions.md`
4. Report persistent issues to maintainers

**Example Prompt**:
```
Create a function to fetch API data with:
- Environment variable for API key
- Input validation and sanitization
- Error handling with logging
- Type hints
- Unit tests
```

#### Flaky Tests

**Problem**: Tests pass/fail inconsistently

**Solutions**:

1. **Add Timeouts**:
   ```python
   @pytest.mark.timeout(10)
   def test_api_call():
       # Test code
   ```

2. **Use Deterministic Seeds**:
   ```python
   import random
   random.seed(42)
   ```

3. **Mock External Dependencies**:
   ```python
   from unittest.mock import patch
   
   @patch('requests.get')
   def test_api(mock_get):
       mock_get.return_value.json.return_value = {"data": "test"}
   ```

4. **Increase Wait Times**:
   ```python
   import time
   time.sleep(0.1)  # Allow async operations to complete
   ```

#### Lint Failures

**Problem**: Linter reports errors

**Common Issues**:

1. **Line Too Long**:
   ```python
   # Bad
   result = some_function(arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8)
   
   # Good
   result = some_function(
       arg1, arg2, arg3, arg4,
       arg5, arg6, arg7, arg8
   )
   ```

2. **Missing Type Hints**:
   ```python
   # Bad
   def process(data):
       return data * 2
   
   # Good
   def process(data: int) -> int:
       return data * 2
   ```

3. **Import Order**:
   ```python
   # Bad
   from mymodule import something
   import sys
   import os
   
   # Good
   import os
   import sys
   
   from mymodule import something
   ```

**Auto-fix**:
```bash
# Format with Black
black .

# Fix import order
isort .

# Auto-fix with Ruff
ruff check . --fix
```

#### CI Timeouts

**Problem**: CI jobs exceed time limits

**Solutions**:

1. **Cache Dependencies**:
   ```yaml
   - uses: actions/setup-python@v5
     with:
       python-version: '3.10'
       cache: 'pip'
   ```

2. **Parallelize Tests**:
   ```yaml
   - name: Run tests
     run: pytest -n auto
   ```

3. **Shard Test Suites**:
   ```yaml
   strategy:
     matrix:
       shard: [1, 2, 3, 4]
   steps:
     - run: pytest --shard=${{ matrix.shard }}/4
   ```

#### Merge Conflicts

**Problem**: Branch has conflicts with main

**Solution**:
```bash
# Update main branch
git checkout main
git pull origin main

# Rebase feature branch
git checkout feature/my-feature
git rebase main

# Resolve conflicts in editor
# After resolving:
git add .
git rebase --continue

# Force push (only on feature branches)
git push --force-with-lease
```

---

## Best Practices Summary

### Code Quality

✅ **DO:**
- Follow PEP 8 style guide
- Use type hints for all functions
- Write comprehensive docstrings
- Keep functions small and focused
- Use meaningful variable names
- Handle errors gracefully

❌ **DON'T:**
- Hardcode secrets or credentials
- Use global variables
- Write functions over 50 lines
- Ignore linter warnings
- Skip tests for "simple" changes
- Use print() for debugging

### Security

✅ **DO:**
- Use environment variables for secrets
- Validate and sanitize all inputs
- Use parameterized queries
- Log security events
- Scan dependencies regularly
- Follow principle of least privilege

❌ **DON'T:**
- Commit secrets to version control
- Trust user input without validation
- Use string concatenation for SQL
- Expose internal errors to users
- Disable security scans
- Grant excessive permissions

### Testing

✅ **DO:**
- Write tests before or with code (TDD)
- Test edge cases and errors
- Mock external dependencies
- Aim for 80%+ coverage
- Use descriptive test names
- Keep tests independent

❌ **DON'T:**
- Skip tests for bug fixes
- Test implementation details
- Create flaky tests
- Ignore test failures
- Write tests that depend on order
- Test private methods directly

### Automation

✅ **DO:**
- Use conventional commits
- Let CI validate changes
- Automate repetitive tasks
- Document automation workflows
- Monitor CI job performance
- Keep workflows up to date

❌ **DON'T:**
- Bypass CI checks
- Merge without approval
- Ignore failing tests
- Commit generated files
- Manually run what can be automated
- Push directly to main

### Collaboration

✅ **DO:**
- Communicate changes clearly
- Review code thoroughly
- Provide constructive feedback
- Ask questions when unsure
- Document decisions
- Share knowledge

❌ **DON'T:**
- Make large, undocumented changes
- Rubber-stamp reviews
- Take feedback personally
- Work in isolation
- Assume others understand context
- Hoard knowledge

---

## Conclusion

This comprehensive guide establishes standards for AI-assisted development in
the CodeTuneStudio and Trading Bot Swarm ecosystem. By following these
practices, we ensure:

- **High Code Quality**: Maintainable, well-tested code
- **Strong Security**: Protected against vulnerabilities
- **Efficient Automation**: Streamlined development workflows
- **Clear Communication**: Documented processes and decisions
- **Continuous Improvement**: Regular reviews and updates

### Quick Reference

**Before Every Commit:**
```bash
flake8 . --select=E9,F63,F7,F82  # Critical errors
black --check .                   # Format check
pytest -v --cov=.                 # Tests with coverage
```

**Before Every PR:**
- [ ] Tests pass locally
- [ ] Linters pass
- [ ] Documentation updated
- [ ] Conventional commit messages
- [ ] Security considerations reviewed

**Resources:**
- [GitHub Copilot Docs](https://docs.github.com/en/copilot)
- [PEP 8 Style Guide](https://peps.python.org/pep-0008/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)

---

**Version History:**
- **1.0.0** (2025-11-21): Initial comprehensive guide

**Maintainers:**
- [@canstralian](https://github.com/canstralian)

**Last Review:** 2025-11-21  
**Next Review Due:** 2026-02-21
