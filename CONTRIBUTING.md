# Contributing to CodeTuneStudio

Thank you for your interest in contributing to CodeTuneStudio! 🎉

We welcome contributions of all kinds: bug reports, feature requests, documentation improvements, and code contributions.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Testing](#testing)
- [Documentation](#documentation)

## 📜 Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## 🤝 How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the issue
- **Expected behavior** vs **actual behavior**
- **Screenshots** (if applicable)
- **Environment details** (OS, Python version, dependencies)
- **Error messages** and stack traces

**Bug Report Template:**

```markdown
**Description:**
A clear description of the bug.

**Steps to Reproduce:**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior:**
What you expected to happen.

**Actual Behavior:**
What actually happened.

**Environment:**
- OS: [e.g., Ubuntu 22.04]
- Python: [e.g., 3.11.5]
- CodeTuneStudio: [e.g., 0.1.0]

**Additional Context:**
Any other relevant information.
```

### Suggesting Features

Feature requests are welcome! Please provide:

- **Clear use case** for the feature
- **Why it would be useful** to most users
- **Possible implementation** approach (optional)
- **Examples** from other projects (if applicable)

### Improving Documentation

Documentation improvements are always appreciated:

- Fix typos or clarify existing docs
- Add missing documentation
- Create tutorials or examples
- Improve API documentation
- Translate documentation

## 🛠️ Development Setup

### Prerequisites

- Python 3.11 or higher
- uv (recommended) or pip
- Git

### Setup Steps

1. **Fork and clone the repository:**

   ```bash
   git clone https://github.com/YOUR_USERNAME/CodeTuneStudio.git
   cd CodeTuneStudio
   ```

2. **Install uv (recommended):**

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Create a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install dependencies:**

   ```bash
   uv pip install -e ".[dev]"
   # Or with pip:
   # pip install -e ".[dev]"
   ```

5. **Set up environment:**

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

6. **Install pre-commit hooks:**

   ```bash
   pre-commit install
   ```

7. **Verify installation:**

   ```bash
   python -m unittest discover -s tests
   ruff check .
   ```

## 📝 Coding Standards

### Code Style

We use **Ruff** for linting and formatting:

```bash
# Check code
ruff check .

# Format code
ruff format .

# Fix auto-fixable issues
ruff check --fix .
```

### Code Guidelines

1. **Python Version**: Target Python 3.11+
2. **Type Hints**: Use type hints for all function signatures
3. **Docstrings**: Use Google-style docstrings
4. **Line Length**: Maximum 88 characters (Black compatible)
5. **Imports**: Organize with isort (handled by Ruff)
6. **Naming Conventions**:
   - Functions/variables: `snake_case`
   - Classes: `PascalCase`
   - Constants: `UPPER_SNAKE_CASE`
   - Private members: `_leading_underscore`

### Example Code

```python
"""Module docstring describing the module purpose."""

import logging
from typing import Optional

from utils.config import Config

logger = logging.getLogger(__name__)


class MyFeature:
    """Class docstring describing the class purpose.

    Attributes:
        config: Configuration instance
        enabled: Whether feature is enabled
    """

    def __init__(self, config: Config) -> None:
        """Initialize MyFeature.

        Args:
            config: Configuration instance
        """
        self.config = config
        self.enabled = True

    def process_data(self, data: str) -> Optional[str]:
        """Process the provided data.

        Args:
            data: Input data to process

        Returns:
            Processed data or None if processing fails

        Raises:
            ValueError: If data is invalid
        """
        if not data:
            raise ValueError("Data cannot be empty")

        try:
            result = data.upper()
            logger.info(f"Processed data: {len(result)} characters")
            return result
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            return None
```

## 💬 Commit Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/):

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Build process or auxiliary tool changes
- `ci`: CI/CD configuration changes

### Examples

```bash
feat(plugins): add support for custom LLM providers

Add plugin base class for integrating custom LLM providers.
Includes validation and error handling.

Closes #123
```

```bash
fix(database): prevent crash on missing DATABASE_URL

Add fallback to sqlite:///database.db when DATABASE_URL
environment variable is not set.

Fixes #456
```

## 🔄 Pull Request Process

### Before Submitting

1. **Update your fork:**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run tests:**
   ```bash
   python -m unittest discover -s tests
   ```

3. **Check code quality:**
   ```bash
   ruff check .
   ruff format .
   ```

4. **Update documentation** if needed

5. **Add tests** for new features

### Submitting

1. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request** on GitHub

3. **Fill in the PR template:**

   ```markdown
   ## Description
   Brief description of changes

   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update

   ## Testing
   Describe tests performed

   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Self-reviewed code
   - [ ] Commented complex code
   - [ ] Updated documentation
   - [ ] Added tests
   - [ ] All tests pass
   - [ ] No new warnings
   ```

### Review Process

1. **Automated checks** must pass (CI/CD)
2. **Code review** by maintainers
3. **Address feedback** if requested
4. **Squash commits** if asked
5. **Merge** once approved

## 🧪 Testing

### Running Tests

```bash
# All tests
python -m unittest discover -s tests

# Specific test file
python -m unittest tests.test_app

# With coverage
pytest --cov=. --cov-report=html
```

### Writing Tests

```python
import unittest
from utils.config import Config


class TestConfig(unittest.TestCase):
    """Test configuration management."""

    def test_default_database_url(self):
        """Test default DATABASE_URL value."""
        self.assertEqual(Config.DATABASE_URL, "sqlite:///database.db")

    def test_config_validation(self):
        """Test configuration validation."""
        errors = Config.validate()
        self.assertIsInstance(errors, list)


if __name__ == "__main__":
    unittest.main()
```

### Test Guidelines

- Write tests for all new features
- Maintain or improve code coverage
- Test edge cases and error conditions
- Use descriptive test names
- Keep tests independent and isolated

## 📚 Documentation

### Docstring Style

Use **Google-style** docstrings:

```python
def function_name(param1: str, param2: int = 0) -> bool:
    """Short description.

    Longer description if needed. Can span multiple
    lines and include examples.

    Args:
        param1: Description of param1
        param2: Description of param2 (default: 0)

    Returns:
        Description of return value

    Raises:
        ValueError: When param1 is empty
        RuntimeError: When operation fails

    Example:
        >>> result = function_name("test", 5)
        >>> print(result)
        True
    """
```

### Documentation Updates

When making changes:

1. Update relevant docstrings
2. Update CLAUDE.md if architecture changes
3. Update README.md if user-facing changes
4. Add entry to CHANGELOG.md
5. Update examples if API changes

## 🎯 Development Workflow

### Branch Naming

- Features: `feature/description`
- Bug fixes: `fix/description`
- Documentation: `docs/description`
- Refactoring: `refactor/description`

### Development Cycle

1. Create issue for feature/bug
2. Create branch from `main`
3. Implement changes
4. Write tests
5. Update documentation
6. Submit PR
7. Address review feedback
8. Merge when approved

## 🐛 Debugging

### Logging

Use the centralized logging system:

```python
import logging

logger = logging.getLogger(__name__)

logger.debug("Detailed debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical error")
```

### Common Issues

**Import errors:**
- Ensure all `__init__.py` files exist
- Check PYTHONPATH
- Verify package installation

**Database errors:**
- Check DATABASE_URL in `.env`
- Run migrations: `python manage.py db upgrade`
- Check database permissions

**Plugin not loading:**
- Verify API keys in `.env`
- Check plugin file location
- Review logs: `tail -f codetunestudio.log`

## 📞 Getting Help

- 💬 [GitHub Discussions](https://github.com/canstralian/CodeTuneStudio/discussions)
- 🐛 [GitHub Issues](https://github.com/canstralian/CodeTuneStudio/issues)
- 📖 [Documentation](CLAUDE.md)

## 🎉 Recognition

Contributors will be recognized in:
- README.md acknowledgements section
- Release notes
- GitHub contributors page

Thank you for contributing to CodeTuneStudio! 🚀
