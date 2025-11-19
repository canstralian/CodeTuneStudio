# Code Quality Guidelines

This document outlines the code quality standards and tools used in the CodeTuneStudio project.

## Overview

We maintain high code quality standards through:
- **Black**: Automated code formatting
- **Flake8**: Style guide enforcement and linting
- **Pre-commit hooks**: Automated checks before commits

## Quick Start

### 1. Install Pre-commit Hooks

Run the setup script to install all necessary tools:

```bash
./scripts/setup-pre-commit.sh
```

This script will:
- Install pre-commit
- Install black and flake8
- Configure pre-commit hooks
- Run initial validation

### 2. Manual Installation (Alternative)

If you prefer manual installation:

```bash
# Install dependencies
pip install pre-commit black flake8

# Install pre-commit hooks
pre-commit install

# Run hooks on all files
pre-commit run --all-files
```

## Code Formatting with Black

Black is an opinionated code formatter that ensures consistent code style.

### Configuration

- **Line length**: 88 characters (Black's default)
- **Configuration file**: `pyproject.toml`

### Usage

```bash
# Format all Python files
black .

# Check formatting without making changes
black --check .

# Show diff of changes
black --diff .

# Format specific files
black path/to/file.py
```

### IDE Integration

#### VS Code
Add to `.vscode/settings.json`:
```json
{
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "python.formatting.blackArgs": ["--line-length=88"]
}
```

#### PyCharm
1. Go to Settings → Tools → Black
2. Enable "On save"
3. Set line length to 88

## Linting with Flake8

Flake8 enforces PEP 8 style guidelines and catches common errors.

### Configuration

Configuration is in `.flake8`:
```ini
[flake8]
max-line-length = 88
extend-ignore = E203
exclude = .git,__pycache__,build,dist,venv,ENV,env,.venv,app.py,index.html
per-file-ignores =
    __init__.py:F401
```

### Usage

```bash
# Check all files
flake8 .

# Check with statistics
flake8 . --statistics

# Show source code for errors
flake8 . --show-source
```

### Common Error Codes

- **E501**: Line too long (> 88 characters)
- **F401**: Module imported but unused
- **F821**: Undefined name
- **W293**: Blank line contains whitespace
- **E302**: Expected 2 blank lines
- **E305**: Expected 2 blank lines after class or function definition

## Pre-commit Hooks

Pre-commit hooks automatically run checks before each commit.

### Configuration

Hooks are configured in `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.2
    hooks:
      - id: ruff
        args: [ --fix ]
      - id: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

### Usage

```bash
# Run all hooks manually
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files

# Skip hooks for a commit (use sparingly!)
git commit --no-verify

# Update hook versions
pre-commit autoupdate
```

## CI/CD Integration

Our GitHub Actions workflow automatically checks code quality on every pull request.

### Workflow Steps

1. **Black Formatting Check**: Ensures code is properly formatted
2. **Flake8 Linting**: Checks for style violations and errors
3. **Pre-commit Validation**: Runs all configured hooks

### Workflow File

Located at `.github/workflows/python-style-checks.yml`

## Troubleshooting

### Black Fails on HTML Files

**Problem**: Black tries to format `app.py` which is actually an HTML file.

**Solution**: The `.flake8` config excludes `app.py`. Black will skip it 
automatically when run via pre-commit hooks.

### Import Statement Errors

**Problem**: Flake8 reports unused imports (F401).

**Solution**: Remove unused imports or add them to `per-file-ignores` in 
`.flake8` if they're required for type checking or exports.

### Line Too Long Errors

**Problem**: Lines exceed 88 characters (E501).

**Solutions**:
- Break long strings across multiple lines using parentheses
- Use implicit string concatenation
- For docstrings, break at logical points

Example:
```python
# Bad
error_message = "This is a very long error message that exceeds the maximum line length allowed"

# Good
error_message = (
    "This is a very long error message that exceeds the maximum "
    "line length allowed"
)
```

### Pre-commit Hooks Fail

**Problem**: Pre-commit hooks fail on commit.

**Solutions**:
1. Check the error message to identify the issue
2. Run `pre-commit run --all-files` to see all failures
3. Fix the issues manually or let the hooks auto-fix them
4. Stage the fixed files and commit again

### Skipping Hooks in Emergency

If you absolutely must skip hooks (e.g., emergency hotfix):

```bash
git commit --no-verify -m "Emergency fix"
```

**Note**: This should be rare. The CI will still check your code.

## Best Practices

1. **Run checks before pushing**: `pre-commit run --all-files`
2. **Keep commits small**: Easier to fix issues
3. **Fix issues immediately**: Don't accumulate technical debt
4. **Use IDE integration**: Catch issues as you type
5. **Read error messages**: They usually tell you exactly what's wrong

## Additional Resources

- [Black Documentation](https://black.readthedocs.io/)
- [Flake8 Documentation](https://flake8.pycqa.org/)
- [Pre-commit Documentation](https://pre-commit.com/)
- [PEP 8 Style Guide](https://pep8.org/)
- [Python Code Quality Authority](https://github.com/PyCQA)

## Getting Help

If you encounter issues with code quality tools:

1. Check this documentation
2. Search existing GitHub issues
3. Create a new issue with:
   - Error message
   - Steps to reproduce
   - Your environment (OS, Python version)

## Updating This Guide

This guide should be updated when:
- New tools are added
- Configuration changes
- New best practices emerge
- Common issues are discovered

Please submit a pull request with your improvements!
