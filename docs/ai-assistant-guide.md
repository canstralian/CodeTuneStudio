# AI Assistant Developer Workflow Guide

## Purpose and Scope

This guide provides **human developers** with comprehensive instructions for configuring AI-powered development tools and workflows in the **CodeTuneStudio** project. This includes GitHub Copilot, IDE integration, pre-commit hooks, CI/CD pipelines, and troubleshooting common issues.

> **Note:** For AI agent behavioral rules and code generation guidelines, see **[`.github/copilot-instructions.md`](../.github/copilot-instructions.md)**. This separation ensures clarity:
> - **This document** = developer workflow (tool installation, repository configuration, CI/CD setup)
> - **`.github/copilot-instructions.md`** = agent rules (behavioral constraints for Copilot Coding Agent)

---

## Table of Contents

1. [Tool Installation](#tool-installation)
2. [Repository Configuration](#repository-configuration)
3. [Pre-Commit Hooks](#pre-commit-hooks)
4. [CI/CD Workflows](#cicd-workflows)
5. [Troubleshooting](#troubleshooting)
6. [Best Practices](#best-practices)

---

## Tool Installation

### GitHub Copilot Subscriptions

**GitHub Copilot** provides AI-powered code suggestions directly in your IDE.

**Subscription Options:**
- **Individual**: $10/month or $100/year
- **Business**: $19/user/month (includes organization-wide policy management)
- **Enterprise**: Contact GitHub Sales for custom pricing

**How to Subscribe:**
1. Visit https://github.com/features/copilot
2. Click "Start free trial" or "Buy now"
3. Follow the setup wizard
4. Activate Copilot in your IDE (see below)

### IDE Plugin Installation

#### Visual Studio Code (Recommended)
1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X / Cmd+Shift+X)
3. Search for "GitHub Copilot"
4. Install both:
   - **GitHub Copilot** (code completions)
   - **GitHub Copilot Chat** (conversational AI assistance)
5. Sign in with your GitHub account
6. Verify activation with a test file

**VS Code Settings (`.vscode/settings.json`):**
```json
{
  "github.copilot.enable": {
    "*": true,
    "yaml": true,
    "plaintext": false,
    "markdown": true
  },
  "github.copilot.editor.enableAutoCompletions": true,
  "editor.inlineSuggest.enabled": true,
  "editor.quickSuggestions": {
    "other": true,
    "comments": false,
    "strings": true
  }
}
```

#### JetBrains IDEs (PyCharm, IntelliJ IDEA)
1. Open Settings/Preferences
2. Go to Plugins → Marketplace
3. Search "GitHub Copilot"
4. Install and restart IDE
5. Sign in via Tools → GitHub Copilot → Login

#### GitHub Codespaces
- Copilot is pre-installed in Codespaces
- Ensure your subscription is active
- Configure via Settings → Extensions

#### Replit Integration
- CodeTuneStudio supports Replit deployments
- Copilot is available via Replit's native AI features
- Use Replit AI for code generation and debugging

---

## Repository Configuration

### Branch Protection Rules

Protect the `main` branch with these settings:

1. Navigate to **Settings → Branches → Branch protection rules**
2. Add rule for `main`:
   - ✅ Require pull request reviews before merging (1+ approvals)
   - ✅ Require status checks to pass before merging:
     - `lint` (Linting & Code Quality)
     - `type-check` (Type Checking)
     - `test` (Tests)
     - `build` (Build Package)
   - ✅ Require conversation resolution before merging
   - ✅ Require linear history (rebase/squash, no merge commits)
   - ✅ Do not allow bypassing the above settings

### Required Status Checks

Configure these checks in `.github/workflows/ci.yml`:
- **Linting**: Ruff, Flake8, Black formatting
- **Type Checking**: MyPy on `core/` module
- **Tests**: Pytest with coverage reporting
- **Build**: Package build verification

### Security Settings

**Enable in Settings → Security:**
- ✅ Dependabot alerts
- ✅ Dependabot security updates
- ✅ Code scanning (CodeQL)
- ✅ Secret scanning
- ✅ Push protection (prevent committing secrets)

**Environment Variables (`.env.example`):**
```bash
# Required for CodeTuneStudio
DATABASE_URL=postgresql://user:password@localhost:5432/codetunedb
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
HF_TOKEN=your_huggingface_token_here
SQL_DEBUG=False
SPACE_ID=your_huggingface_space_id
```

**Never commit the actual `.env` file** (excluded via `.gitignore`).

---

## Pre-Commit Hooks

### Current Configuration

CodeTuneStudio uses **pre-commit** to enforce code quality automatically before commits.

**Existing `.pre-commit-config.yaml`:**
```yaml
# See https://pre-commit.com for more information
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.2
    hooks:
      # Run the linter
      - id: ruff
        args: [ --fix ]
      # Run the formatter
      - id: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

### Installation and Usage

**Install pre-commit:**
```bash
pip install pre-commit
```

**Activate hooks:**
```bash
cd /path/to/CodeTuneStudio
pre-commit install
```

**Run manually:**
```bash
# Run on all files
pre-commit run --all-files

# Run on staged files only
pre-commit run

# Update hook versions
pre-commit autoupdate
```

### Recommended Additional Hooks

For enhanced security and quality, consider adding:

```yaml
  # Security scanning
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: ['-c', 'pyproject.toml']
        additional_dependencies: ['bandit[toml]']

  # Type checking (if mypy is configured)
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.0
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]
        args: [--config-file=mypy.ini]
```

---

## CI/CD Workflows

### Overview

CodeTuneStudio uses GitHub Actions for automated quality gates. Workflows are defined in `.github/workflows/`.

### Security Best Practices

#### 1. Pin Third-Party Actions to Commit SHAs

**❌ WRONG (mutable tags can be hijacked):**
```yaml
- uses: actions/checkout@v3
```

**✅ CORRECT (immutable commit SHA with comment for readability):**
```yaml
- uses: actions/checkout@f43a0e5ff2bd294095638e18286ca9a3d1956744  # v3.6.0
```

**Why?** Tags can be moved to malicious commits; SHAs are immutable.

**How to Find SHAs:**
1. Visit the action's GitHub repo (e.g., https://github.com/actions/checkout)
2. Navigate to Releases → find the tag (e.g., v3.6.0)
3. Copy the commit SHA
4. Add a comment with the version for human readability

#### 2. Avoid `|| true` to Mask Failures

**❌ WRONG (silently ignores errors):**
```yaml
- name: Run linter
  run: ruff check . || true
```

**✅ CORRECT (fail fast or conditionally install):**
```yaml
- name: Run linter
  run: ruff check .

# For optional dependencies:
- name: Install optional dependencies
  run: |
    if [ -f requirements-optional.txt ]; then
      pip install -r requirements-optional.txt
    fi
```

#### 3. Scope Coverage Targets Appropriately

CodeTuneStudio has `core/`, `components/`, `utils/`, and `plugins/` directories (no `src/` or `app/`).

**❌ WRONG (overly broad coverage):**
```yaml
- name: Run tests with coverage
  run: pytest --cov=. --cov-report=xml
```

**✅ CORRECT (scope to main packages):**
```yaml
- name: Run tests with coverage
  run: |
    pytest --cov=core --cov=components --cov=utils --cov=plugins \
           --cov-report=xml --cov-report=term-missing \
           --cov-fail-under=70
```

**Coverage Thresholds:**
- **Minimum**: 70% (enforced in CI)
- **Target**: 80%+ for production code
- **Test/mock files**: Excluded via `.coveragerc`

### Example CI Workflow with Best Practices

**`.github/workflows/ci-secure.yml` (example snippet):**

```yaml
name: Secure CI Pipeline

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main]

permissions:
  contents: read

jobs:
  lint-and-format:
    name: Linting & Formatting
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@f43a0e5ff2bd294095638e18286ca9a3d1956744  # v3.6.0

      - name: Set up Python
        uses: actions/setup-python@65d7f2d534ac1bc67fcd62888c5f4f3d2cb2b236  # v4.7.1
        with:
          python-version: "3.10"
          cache: 'pip'

      - name: Install linting tools
        run: |
          python -m pip install --upgrade pip
          pip install ruff black flake8

      - name: Run Ruff linter
        run: ruff check . --output-format=github

      - name: Run Black formatter check
        run: black --check --diff .

      - name: Run Flake8
        run: |
          flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
          flake8 . --count --max-complexity=10 --max-line-length=88 --statistics

  type-check:
    name: Type Checking
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@f43a0e5ff2bd294095638e18286ca9a3d1956744  # v3.6.0

      - name: Set up Python
        uses: actions/setup-python@65d7f2d534ac1bc67fcd62888c5f4f3d2cb2b236  # v4.7.1
        with:
          python-version: "3.10"
          cache: 'pip'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install mypy types-requests

      - name: Run MyPy
        run: |
          # Run on source packages, not on root directory
          mypy core/ --config-file=mypy.ini --ignore-missing-imports

  test-with-coverage:
    name: Tests & Coverage
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11"]
    steps:
      - name: Checkout code
        uses: actions/checkout@f43a0e5ff2bd294095638e18286ca9a3d1956744  # v3.6.0

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@65d7f2d534ac1bc67fcd62888c5f4f3d2cb2b236  # v4.7.1
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-mock

      - name: Run tests with coverage
        run: |
          pytest -v \
            --cov=core --cov=components --cov=utils --cov=plugins \
            --cov-report=xml --cov-report=term-missing \
            --cov-fail-under=70

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@eaaf4bedf32dbdc6b720b63067d99c4d77d6047d  # v3.1.4
        if: matrix.python-version == '3.10'
        with:
          files: ./coverage.xml
          flags: unittests
          fail_ci_if_error: false

  security-scan:
    name: Security Scanning
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@f43a0e5ff2bd294095638e18286ca9a3d1956744  # v3.6.0

      - name: Set up Python
        uses: actions/setup-python@65d7f2d534ac1bc67fcd62888c5f4f3d2cb2b236  # v4.7.1
        with:
          python-version: "3.10"
          cache: 'pip'

      - name: Install security tools
        run: |
          python -m pip install --upgrade pip
          pip install safety bandit

      - name: Run Safety (dependency vulnerability scan)
        run: safety check --json

      - name: Run Bandit (Python security linter)
        run: bandit -r . -f json -o bandit-report.json

      - name: Generate SBOM
        uses: anchore/sbom-action@78fc58e266e87a38d4194b2137a3d4e9bcaf7ca1  # v0.14.3
        with:
          path: .
          format: cyclonedx-json
          output-file: sbom.json

      - name: Upload SBOM artifact
        uses: actions/upload-artifact@a8a3f3ad30e3422c9c7b888a15615d19a852ae32  # v3.1.3
        with:
          name: sbom
          path: sbom.json

  build:
    name: Build Package
    runs-on: ubuntu-latest
    needs: [lint-and-format, type-check, test-with-coverage, security-scan]
    steps:
      - name: Checkout code
        uses: actions/checkout@f43a0e5ff2bd294095638e18286ca9a3d1956744  # v3.6.0

      - name: Set up Python
        uses: actions/setup-python@65d7f2d534ac1bc67fcd62888c5f4f3d2cb2b236  # v4.7.1
        with:
          python-version: "3.10"

      - name: Install build tools
        run: |
          python -m pip install --upgrade pip
          pip install build setuptools wheel twine

      - name: Build package
        run: python -m build

      - name: Verify package
        run: twine check dist/*

      - name: Upload build artifacts
        uses: actions/upload-artifact@a8a3f3ad30e3422c9c7b888a15615d19a852ae32  # v3.1.3
        with:
          name: dist-packages
          path: dist/
```

### MyPy Configuration Requirements

**MyPy requires explicit configuration.** Create either:

**Option 1: `mypy.ini` (recommended):**
```ini
[mypy]
python_version = 3.10
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = False
ignore_missing_imports = True
exclude = (^venv/|^tests/|^migrations/)

[mypy-core.*]
disallow_untyped_defs = True

[mypy-components.*]
disallow_untyped_defs = False
```

**Option 2: `pyproject.toml` section:**
```toml
[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false
ignore_missing_imports = true
exclude = ["^venv/", "^tests/", "^migrations/"]

[[tool.mypy.overrides]]
module = "core.*"
disallow_untyped_defs = true
```

**Important:** Always run MyPy on **specific packages**, not on `.`:
```bash
# ✅ CORRECT
mypy core/ components/ --config-file=mypy.ini

# ❌ WRONG (includes tests, venv, migrations, etc.)
mypy .
```

### Semantic Release Setup

CodeTuneStudio uses semantic versioning with automated releases.

**Example Release Workflow (`.github/workflows/release.yml` snippet):**
```yaml
name: Semantic Release

on:
  push:
    branches: [main]

permissions:
  contents: write
  issues: write
  pull-requests: write

jobs:
  release:
    name: Release
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@f43a0e5ff2bd294095638e18286ca9a3d1956744  # v3.6.0
        with:
          fetch-depth: 0  # Required for semantic-release
          persist-credentials: false

      - name: Set up Node.js
        uses: actions/setup-node@5e21ff4d9bc1a8cf6de233a3057d20ec6b3fb69d  # v3.8.1
        with:
          node-version: '18'

      - name: Install semantic-release
        run: |
          npm install -g semantic-release @semantic-release/git @semantic-release/changelog

      - name: Run semantic-release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: npx semantic-release
```

**Conventional Commit Format:**
- `feat:` → Minor version bump (new feature)
- `fix:` → Patch version bump (bug fix)
- `BREAKING CHANGE:` → Major version bump
- `docs:`, `chore:`, `style:` → No version bump

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Flaky Tests

**Symptoms:**
- Tests pass locally but fail in CI
- Non-deterministic failures
- Timeout errors

**Solutions:**
```python
# Use fixed seeds for random operations
import random
random.seed(42)

# Use time mocking
from unittest.mock import patch
with patch('time.time', return_value=1609459200):
    # test code

# Avoid hardcoded waits
import asyncio
# ❌ WRONG
await asyncio.sleep(5)
# ✅ CORRECT (use polling with timeout)
for _ in range(50):
    if condition_met():
        break
    await asyncio.sleep(0.1)
else:
    raise TimeoutError("Condition not met")
```

#### 2. Slow CI Pipelines

**Optimization strategies:**
- Use `cache: 'pip'` in `actions/setup-python`
- Run jobs in parallel (not sequential)
- Use matrix strategy for multiple Python versions
- Cache dependencies with `actions/cache`
- Skip unnecessary jobs for docs-only PRs:

```yaml
on:
  pull_request:
    paths-ignore:
      - '**.md'
      - 'docs/**'
```

#### 3. MyPy and Ruff Conflicts

**Issue:** MyPy reports errors that Ruff doesn't catch, or vice versa.

**Solution:**
```ini
# mypy.ini
[mypy]
# Align with Ruff's line length
max_line_length = 88

# pyproject.toml
[tool.ruff]
line-length = 88
select = ["E", "F", "I", "N", "W"]
ignore = ["E501"]  # Let Black/Ruff-format handle line length
```

**Integration testing:**
```bash
# Run both together
ruff check . && black --check . && mypy core/
```

#### 4. Copilot Suggestions Not Appearing

**Checklist:**
- [ ] Verify Copilot subscription is active
- [ ] Check IDE extension is enabled
- [ ] Sign out/in to GitHub in IDE
- [ ] Check network connectivity (Copilot requires internet)
- [ ] Restart IDE
- [ ] Check VS Code settings for `inlineSuggest.enabled`

**Force refresh:**
```bash
# VS Code Command Palette (Ctrl+Shift+P / Cmd+Shift+P)
> GitHub Copilot: Restart Server
```

#### 5. Pre-Commit Hook Failures

**Issue:** Hooks fail on every commit.

**Debugging:**
```bash
# Run hooks manually to see detailed output
pre-commit run --all-files --verbose

# Update hooks to latest versions
pre-commit autoupdate

# Skip hooks temporarily (use sparingly!)
git commit -m "message" --no-verify
```

**Common fixes:**
- Ensure Python environment is activated
- Install missing dependencies: `pip install -r requirements.txt`
- Check `.pre-commit-config.yaml` syntax

#### 6. Environment Variable Issues

**Issue:** Application can't find `.env` variables.

**Solution:**
```python
# Use python-dotenv for local development
from dotenv import load_dotenv
import os

# Load .env file (development only)
if os.getenv('ENVIRONMENT') != 'production':
    load_dotenv()

# Access with fallback
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///local.db')
```

**CI environment variables:**
Set in GitHub Settings → Secrets → Actions:
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `HF_TOKEN`

---

## Best Practices

### 1. Code Review Workflow

**For Developers:**
1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes in small, logical commits
3. Run pre-commit hooks: `pre-commit run --all-files`
4. Push and open PR with descriptive title/body
5. Address review feedback promptly
6. Ensure all CI checks pass

**For Reviewers:**
1. Verify PR description explains **why** and **what**
2. Check that tests cover new functionality
3. Run code locally if complex changes
4. Use GitHub's suggestion feature for improvements
5. Approve only when all checks pass

### 2. Writing Quality PRs

**Good PR Structure:**
```markdown
## Summary
Brief description of changes (1-2 sentences)

## Motivation
Why is this change needed? What problem does it solve?

## Changes
- Added feature X
- Fixed bug Y
- Updated docs for Z

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

## Screenshots (if UI changes)
[Include before/after screenshots]

## Checklist
- [ ] Code follows style guide
- [ ] Documentation updated
- [ ] No secrets committed
- [ ] All checks passing
```

### 3. Effective Use of AI Assistance

**Do:**
- Use Copilot for boilerplate code, tests, docstrings
- Review and edit AI suggestions carefully
- Use Copilot Chat for complex problem-solving
- Generate test cases with AI assistance

**Don't:**
- Blindly accept all suggestions
- Use AI for security-critical code without review
- Rely on AI for understanding system architecture
- Skip manual testing of AI-generated code

### 4. Dependency Management

**Keep dependencies updated:**
```bash
# Check for outdated packages
pip list --outdated

# Update specific package
pip install --upgrade package-name

# Update all (with caution)
pip install --upgrade -r requirements.txt

# Scan for vulnerabilities
pip install safety
safety check
```

**Pinning strategy:**
```txt
# requirements.txt
# Pin exact versions for reproducibility
flask==2.3.2
sqlalchemy==2.0.19

# requirements-dev.txt
# Dev tools can use flexible versions
pytest>=7.0,<8.0
black>=23.0
```

### 5. Documentation Standards

**Always document:**
- Public API functions (comprehensive docstrings)
- Complex algorithms (inline comments)
- Configuration options (README/docs)
- Breaking changes (CHANGELOG)
- Security considerations

**Use clear examples:**
```python
def train_model(config: dict) -> dict:
    """
    Train ML model with given configuration.
    
    Args:
        config: Training configuration with keys:
            - model_type (str): "CodeT5" or "CodeBERT"
            - batch_size (int): Training batch size
            - epochs (int): Number of training epochs
    
    Returns:
        dict: Training metrics including loss and accuracy
    
    Example:
        >>> config = {"model_type": "CodeT5", "batch_size": 32, "epochs": 3}
        >>> metrics = train_model(config)
        >>> print(metrics["loss"])
        0.234
    
    Raises:
        ValueError: If config is invalid
        FileNotFoundError: If model checkpoint not found
    """
```

---

## Additional Resources

### Official Documentation
- **GitHub Copilot**: https://docs.github.com/en/copilot
- **GitHub Actions**: https://docs.github.com/en/actions
- **Pre-commit**: https://pre-commit.com/
- **Semantic Release**: https://semantic-release.gitbook.io/

### CodeTuneStudio Documentation
- **Agent Rules**: [`.github/copilot-instructions.md`](../.github/copilot-instructions.md)
- **Architecture**: [`docs/ARCHITECTURE.md`](./ARCHITECTURE.md)
- **Plugin Development**: [`docs/PLUGIN_GUIDE.md`](./PLUGIN_GUIDE.md)
- **Contributing**: [`CONTRIBUTING_CODE_QUALITY.md`](./CONTRIBUTING_CODE_QUALITY.md)

### Security Resources
- **OWASP Top 10**: https://owasp.org/www-project-top-ten/
- **Python Security**: https://python.readthedocs.io/en/stable/library/security_warnings.html
- **Bandit**: https://bandit.readthedocs.io/

---

## Conclusion

This guide provides a comprehensive workflow for developers working with AI assistants on **CodeTuneStudio**. By following these practices, you'll ensure high code quality, security, and maintainability.

**Remember:** AI assistants are powerful tools, but human oversight is essential. Always review, test, and validate AI-generated code before merging.

For questions or improvements to this guide, please open an issue or submit a PR.

---

*Last Updated: 2025-12-13*  
*Maintained by: CodeTuneStudio Contributors*
