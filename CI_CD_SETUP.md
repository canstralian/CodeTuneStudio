# CI/CD Pipeline Setup Guide

This document explains the comprehensive CI/CD pipeline configured for CodeTuneStudio, including all quality and security tools.

## 🛠️ Tools Integrated

### Code Quality Tools

1. **Ruff** - Fast Python linter and formatter (10-100x faster than Flake8)
   - Comprehensive rule sets (Pyflakes, pycodestyle, isort, pep8-naming, etc.)
   - Auto-fixing capabilities
   - Configuration: `pyproject.toml` → `[tool.ruff]`

2. **Flake8** - Additional Python linting for extra coverage
   - Complements Ruff with different rule interpretations
   - Plugins: flake8-docstrings, flake8-bugbear
   - Configuration: `.flake8`

3. **MyPy** - Static type checking (optional, can be added to CI)
   - Configuration: `pyproject.toml` → `[tool.mypy]`

### Security Tools

4. **Bandit** - Python security linter
   - Scans for common security issues
   - Generates JSON and text reports
   - Configuration: `pyproject.toml` → `[tool.bandit]`

### Testing Tools

5. **Pytest** - Modern testing framework
   - Replaces unittest with better features
   - Integrated with coverage reporting
   - Configuration: `pyproject.toml` → `[tool.pytest.ini_options]`

6. **Coverage.py** - Code coverage analysis
   - Tracks which code is tested
   - Generates XML, HTML, and terminal reports
   - Configuration: `pyproject.toml` → `[tool.coverage]`

### Code Analysis Platform

7. **Codacy** - Automated code review and quality platform
   - Receives coverage reports
   - Performs static analysis
   - Tracks code quality over time
   - Requires: `CODACY_PROJECT_TOKEN` secret

### Data Validation

8. **Pydantic** - Data validation using Python type annotations
   - Runtime validation step in CI
   - Validates all Pydantic models in the codebase
   - Ensures data integrity

## 🔧 GitHub Actions Workflow

### Workflow File

Location: `.github/workflows/ci.yml`

### Workflow Steps

1. **Checkout Code** - Fetches repository with full history
2. **Set up Python** - Installs Python 3.11
3. **Cache Dependencies** - Speeds up subsequent runs
4. **Install uv** - Fast dependency manager
5. **Install Dependencies** - Installs all dev dependencies
6. **Security Scan (Bandit)** - Identifies security issues
7. **Lint (Ruff)** - Fast comprehensive linting
8. **Lint (Flake8)** - Additional linting coverage
9. **Validate Pydantic** - Runtime model validation
10. **Test (Pytest)** - Run tests with coverage
11. **Upload Coverage (Codacy)** - Send coverage data
12. **Run Codacy Analysis** - Static code analysis
13. **Upload Artifacts** - Preserve reports for review

### Triggers

- **Push** to `main` branch
- **Pull requests** targeting `main` branch

## 🔐 Required Secrets

Configure these in GitHub Settings → Secrets and variables → Actions:

### Required

- `CODACY_PROJECT_TOKEN` - For Codacy integration
  - Get from: https://app.codacy.com/project-settings/integrations

### Optional (for full functionality)

- `OPENAI_API_KEY` - For OpenAI plugin tests
- `ANTHROPIC_API_KEY` - For Anthropic plugin tests
- `HF_TOKEN` - For Hugging Face integration tests

## 📊 Reports and Artifacts

### Generated Reports

1. **Coverage Reports**
   - `coverage.xml` - Machine-readable coverage data
   - `htmlcov/` - Interactive HTML coverage report
   - Terminal output - Summary in CI logs

2. **Security Reports**
   - `bandit-report.json` - Detailed security findings
   - Text output in CI logs

3. **Test Reports**
   - Pytest verbose output
   - Test duration and status

### Accessing Reports

- **In CI logs**: Click on workflow run → Expand step
- **Artifacts**: Download from workflow run page (retained 30 days)
- **Codacy Dashboard**: https://app.codacy.com

## 🚀 Local Development

### Run All Checks Locally

```bash
# Install dev dependencies
uv pip install -e ".[dev]"

# Security scan
bandit -r . -f txt

# Lint with Ruff
ruff check .
ruff format --check .

# Lint with Flake8
flake8 .

# Type checking (optional)
mypy .

# Run tests with coverage
pytest tests/ -v --cov=. --cov-report=term --cov-report=html

# Open coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Pre-commit Hooks

Install pre-commit hooks to run checks automatically before commits:

```bash
pre-commit install
```

This runs:
- Ruff linting and formatting
- Bandit security checks
- File formatting checks
- YAML validation

## 📝 Configuration Files

### Main Configuration: `pyproject.toml`

Contains configuration for:
- Project metadata
- Dependencies
- Ruff (linting & formatting)
- Pytest (testing)
- Coverage (coverage reporting)
- Bandit (security)
- MyPy (type checking)

### Additional Configurations

- `.flake8` - Flake8-specific settings
- `.pre-commit-config.yaml` - Pre-commit hook configuration
- `.github/workflows/ci.yml` - CI/CD pipeline definition

## 🎯 Quality Standards

### Minimum Requirements

- **Test Coverage**: 60%+ (target: 80%+)
- **Ruff**: All checks must pass
- **Flake8**: Critical errors (E9, F63, F7, F82) must pass
- **Bandit**: No high-severity security issues
- **Pytest**: All tests must pass

### Best Practices

1. **Write tests** for all new features
2. **Run checks locally** before pushing
3. **Fix security issues** immediately
4. **Maintain coverage** - don't decrease it
5. **Document complex code** with docstrings
6. **Use type hints** for better code quality

## 🔄 Continuous Improvement

### Adding New Checks

To add a new check to CI:

1. Add dependency to `pyproject.toml` → `[project.optional-dependencies].dev`
2. Add step to `.github/workflows/ci.yml`
3. Add configuration to `pyproject.toml` or separate config file
4. Test locally first
5. Update this documentation

### Example: Adding Black Formatter

```toml
# In pyproject.toml
[project.optional-dependencies]
dev = [
    # ... existing dependencies
    "black>=24.0.0",
]

[tool.black]
line-length = 88
target-version = ['py311']
```

```yaml
# In .github/workflows/ci.yml
- name: Format check with Black
  run: |
    black --check .
```

## 🐛 Troubleshooting

### Common Issues

**Issue**: Codacy upload fails
- **Solution**: Check `CODACY_PROJECT_TOKEN` secret is set correctly
- **Note**: Codacy steps are `continue-on-error: true`, so they won't fail the build

**Issue**: Tests fail locally but pass in CI (or vice versa)
- **Solution**: Ensure same Python version (3.11)
- **Solution**: Clear cache: `rm -rf .pytest_cache __pycache__`
- **Solution**: Check environment variables in `.env`

**Issue**: Bandit reports false positives
- **Solution**: Add skip codes to `pyproject.toml` → `[tool.bandit].skips`
- **Solution**: Use `# nosec` comment for specific lines (use sparingly)

**Issue**: Coverage decreases unexpectedly
- **Solution**: Add tests for new code
- **Solution**: Check `[tool.coverage.run].omit` for excluded files

## 📚 Additional Resources

- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Bandit Documentation](https://bandit.readthedocs.io/)
- [Codacy Documentation](https://docs.codacy.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/canstralian/CodeTuneStudio/issues)
- **Discussions**: [GitHub Discussions](https://github.com/canstralian/CodeTuneStudio/discussions)
- **Documentation**: [CLAUDE.md](CLAUDE.md)

---

**Last Updated**: 2025-10-01
**CI/CD Version**: 2.0
