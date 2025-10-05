# Development Guide - CodeTuneStudio

This guide covers development setup, testing, debugging, and automation for CodeTuneStudio.

---

## Table of Contents

1. [Development Setup](#development-setup)
2. [Testing](#testing)
3. [Debugging](#debugging)
4. [Code Quality](#code-quality)
5. [CI/CD Automation](#cicd-automation)
6. [Contributing](#contributing)

---

## Development Setup

### Prerequisites

- Python 3.11 or 3.12
- `uv` package manager (recommended) or `pip`
- Git
- VS Code (recommended) or PyCharm

### Installation

```bash
# Clone the repository
git clone https://github.com/canstralian/CodeTuneStudio.git
cd CodeTuneStudio

# Install with uv (recommended)
uv pip install -e ".[dev]"

# Or install with pip
pip install -e ".[dev]"
```

### Development Dependencies

The `[dev]` extra includes:
- **Testing**: pytest, pytest-cov, pytest-html, pytest-xdist, pytest-timeout
- **Linting**: ruff, flake8, flake8-docstrings, flake8-bugbear
- **Type Checking**: mypy
- **Security**: bandit, safety
- **Formatting**: autopep8
- **Validation**: pydantic
- **Hooks**: pre-commit

---

## Testing

### Running Tests

#### Quick Test Run
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_app.py

# Run specific test function
pytest tests/test_app.py::TestMLFineTuningApp::test_save_training_config_success
```

#### Test with Coverage
```bash
# Generate coverage report
pytest --cov=. --cov-report=html --cov-report=term-missing

# View HTML coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

#### Parallel Testing
```bash
# Run tests in parallel (faster)
pytest -n auto
```

#### Test Markers
```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"

# Run security tests
pytest -m security
```

### VS Code Testing

Tests are automatically discovered in VS Code. Use:
- **Test Explorer** sidebar
- **Run Test** CodeLens above test functions
- **Debug Test** to debug with breakpoints

### Debugging Configurations

Available debug configurations (`.vscode/launch.json`):

1. **Python: Current File** - Debug any Python file
2. **Python: Streamlit App** - Debug Streamlit application
3. **Python: Flask App** - Debug Flask backend
4. **Python: pytest (All Tests)** - Debug all tests
5. **Python: pytest (Current File)** - Debug tests in current file
6. **Python: pytest (Failed Tests)** - Re-run and debug failed tests
7. **Python: pytest (With Coverage)** - Debug with coverage collection
8. **Python: Debug Plugin** - Debug plugin system
9. **Python: Remote Attach** - Attach to remote debugger

### Writing Tests

#### Test Structure
```python
import pytest
from app import MLFineTuningApp

@pytest.fixture
def app():
    """Create test app instance."""
    return MLFineTuningApp()

def test_feature(app):
    """Test description."""
    # Arrange
    expected = "value"

    # Act
    result = app.some_method()

    # Assert
    assert result == expected
```

#### Test Markers
```python
@pytest.mark.unit
def test_unit_function():
    """Unit test."""
    pass

@pytest.mark.integration
def test_integration_feature():
    """Integration test."""
    pass

@pytest.mark.slow
def test_slow_operation():
    """Slow test (skipped in quick runs)."""
    pass

@pytest.mark.security
def test_security_validation():
    """Security-related test."""
    pass
```

---

## Debugging

### Streamlit App Debugging

```bash
# Option 1: VS Code Debug Configuration
# Select "Python: Streamlit App" from debug dropdown

# Option 2: CLI with debugpy
python -m debugpy --listen 5678 --wait-for-client -m streamlit run app.py
```

### Flask App Debugging

```bash
# Option 1: VS Code Debug Configuration
# Select "Python: Flask App" from debug dropdown

# Option 2: CLI
FLASK_APP=app.py FLASK_ENV=development flask run --debug
```

### Remote Debugging

```python
# Add to your code
import debugpy
debugpy.listen(5678)
debugpy.wait_for_client()  # Optional: wait for debugger to attach
```

Then use "Python: Remote Attach" configuration in VS Code.

### Debugging Tips

1. **Breakpoints**: Click left margin in editor
2. **Conditional Breakpoints**: Right-click breakpoint → Edit Breakpoint
3. **Logpoints**: Right-click breakpoint → Add Logpoint
4. **Watch Expressions**: Add variables to Watch panel
5. **Debug Console**: Execute code in current context

---

## Code Quality

### Linting

#### Ruff (Primary Linter - Fast)
```bash
# Check code
ruff check .

# Auto-fix issues
ruff check . --fix

# Check formatting
ruff format --check .

# Format code
ruff format .
```

#### Flake8 (Additional Checks)
```bash
# Critical errors only
flake8 . --select=E9,F63,F7,F82 --show-source

# Full check
flake8 .
```

### Type Checking

```bash
# Run mypy
mypy .

# Run mypy on specific file
mypy app.py

# Generate type stubs
stubgen -p mypackage -o stubs/
```

Configuration: `mypy.ini` and `pyproject.toml [tool.mypy]`

### Auto-formatting

#### Ruff (Recommended)
```bash
ruff format .
```

#### autopep8 (Alternative)
```bash
# Format current directory
autopep8 --in-place --recursive .

# Format specific file
autopep8 --in-place app.py

# Preview changes (dry run)
autopep8 --diff app.py
```

Configuration: `.autopep8`

### Security Scanning

```bash
# Bandit (security linter)
bandit -r . --exclude venv,tests

# Safety (dependency vulnerabilities)
safety check

# Combined security check
bandit -r . && safety check
```

### Pre-commit Hooks

```bash
# Install hooks
pre-commit install

# Run on all files
pre-commit run --all-files

# Run specific hook
pre-commit run ruff --all-files
```

---

## CI/CD Automation

### GitHub Actions Workflows

#### 1. **Pytest CI** (`.github/workflows/pytest.yml`)

**Triggers**: Push to main/develop, Pull Requests
**Jobs**:
- **Test Matrix**: Python 3.11 & 3.12
- **Coverage Reports**: HTML, XML, terminal
- **Artifacts**: Test results, coverage reports
- **Integration Tests**: PostgreSQL database
- **Security Scans**: Bandit, Safety
- **Code Quality**: Ruff, MyPy

**Features**:
- ✅ Parallel testing with pytest-xdist
- ✅ Coverage reporting to Codecov
- ✅ Test result publishing
- ✅ PR coverage comments
- ✅ Artifact retention (30 days)

#### 2. **CI Pipeline** (`.github/workflows/ci.yml`)

**Triggers**: Push to main, Pull Requests
**Jobs**:
- Linting (Ruff, Flake8)
- Security scanning (Bandit)
- Model validation (Pydantic)
- Type checking (MyPy)

#### Manual Trigger

```bash
# Trigger workflow manually
gh workflow run pytest.yml
```

### Local CI Emulation

```bash
# Run full CI suite locally
make test-all  # If Makefile exists

# Or manually:
ruff check .
mypy .
bandit -r .
safety check
pytest --cov=. --cov-report=html
```

---

## Project Structure

```
CodeTuneStudio/
├── .github/
│   └── workflows/
│       ├── ci.yml              # Main CI pipeline
│       ├── pytest.yml          # Pytest automation
│       ├── release.yml         # Release automation
│       └── huggingface-deploy.yml
├── .vscode/
│   ├── launch.json             # Debug configurations
│   └── settings.json           # VS Code settings
├── components/                 # Streamlit UI components
├── plugins/                    # Extensible plugin system
├── tests/                      # Test suite
├── utils/                      # Utility modules
├── .autopep8                   # autopep8 configuration
├── mypy.ini                    # MyPy type checking config
├── pytest.ini                  # Pytest configuration
├── pyproject.toml              # Project metadata & tool configs
├── DEVELOPMENT.md              # This file
└── README.md                   # User-facing documentation
```

---

## Contributing

### Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make Changes**
   - Write code
   - Add tests
   - Update documentation

3. **Run Quality Checks**
   ```bash
   ruff check . --fix
   ruff format .
   mypy .
   pytest --cov=.
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/my-feature
   gh pr create --title "Add new feature" --body "Description"
   ```

### Commit Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation only
- `style:` Code style (formatting, no logic change)
- `refactor:` Code refactoring
- `perf:` Performance improvement
- `test:` Adding/updating tests
- `chore:` Maintenance tasks
- `ci:` CI/CD changes

### Code Review Checklist

- [ ] Tests added/updated and passing
- [ ] Code formatted (Ruff)
- [ ] Type hints added (MyPy clean)
- [ ] Security scan passed (Bandit)
- [ ] Documentation updated
- [ ] CHANGELOG.md updated (for releases)
- [ ] No breaking changes (or documented)

---

## Troubleshooting

### Common Issues

#### pytest not finding tests
```bash
# Ensure PYTHONPATH is set
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or use pytest.ini (already configured)
pytest
```

#### Import errors in tests
```bash
# Install in editable mode
uv pip install -e ".[dev]"
```

#### MyPy import errors
```bash
# Install type stubs
mypy --install-types --non-interactive
```

#### Coverage not working
```bash
# Install pytest-cov
uv pip install pytest-cov

# Run without addopts (use CLI args)
pytest --cov=. --cov-report=html
```

### Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug("Debug message")
```

---

## Resources

- **Project Repository**: https://github.com/canstralian/CodeTuneStudio
- **Documentation**: [CLAUDE.md](CLAUDE.md)
- **Security**: [SECURITY_SCAN_REPORT_v0.1.1.md](SECURITY_SCAN_REPORT_v0.1.1.md)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)
- **Issues**: https://github.com/canstralian/CodeTuneStudio/issues

---

**Last Updated**: 2025-10-05
**Version**: 0.1.1
