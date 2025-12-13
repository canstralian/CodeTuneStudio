# AI Assistant Developer Workflow Guide

**Project:** CodeTuneStudio  
**Last Updated:** 2025-12-13

This guide documents the developer workflow for using AI coding assistants (GitHub Copilot, Cursor, etc.) with CodeTuneStudio. For behavioral rules and agent constraints, see [`.github/copilot-instructions.md`](../.github/copilot-instructions.md).

---

## Table of Contents
- [Tool Installation & Enablement](#tool-installation--enablement)
- [Repository Configuration](#repository-configuration)
- [Pre-Commit Hooks](#pre-commit-hooks)
- [CI/CD Pipeline Examples](#cicd-pipeline-examples)
- [Security Scanning](#security-scanning)
- [Semantic Release Pattern](#semantic-release-pattern)
- [Troubleshooting](#troubleshooting)

---

## Tool Installation & Enablement

### GitHub Copilot
1. **Subscription Required:** GitHub Copilot requires an active subscription (Individual, Business, or Enterprise)
2. **IDE Plugins:**
   - **VS Code:** Install "GitHub Copilot" extension from the marketplace
   - **JetBrains IDEs:** Install "GitHub Copilot" plugin
   - **Neovim:** Use `github/copilot.vim` or compatible plugin
3. **Authentication:** Sign in to GitHub through your IDE when prompted
4. **Configuration:** Enable/disable suggestions in IDE settings as needed

### Other AI Assistants
- **Cursor:** Download from cursor.sh, includes built-in AI capabilities
- **Amazon CodeWhisperer:** Available through AWS Toolkit extensions
- **Tabnine:** Install from IDE marketplace, supports multiple editors

### Best Practices
- Review all AI-generated code before accepting
- Use AI assistants to accelerate, not replace, code review
- Maintain human oversight on security-critical code
- Refer to [`.github/copilot-instructions.md`](../.github/copilot-instructions.md) for project-specific rules

---

## Repository Configuration

### Branch Protection
Configure branch protection rules for `main` branch:

```yaml
Protection Rules:
  - Require pull request reviews before merging (1+ approvals)
  - Require status checks to pass before merging:
    - lint-and-format
    - type-check
    - tests
    - security-scan
  - Require branches to be up to date before merging
  - Require signed commits (recommended for releases)
  - Restrict who can push to matching branches
  - Allow force pushes: disabled
  - Allow deletions: disabled
```

### Required CI Checks
The following checks must pass before merging:
- **Linting:** Ruff/Flake8 for Python code style
- **Formatting:** Black/Ruff format consistency
- **Type Checking:** MyPy static analysis
- **Unit Tests:** pytest with coverage reporting
- **Security Scan:** Bandit, Safety, and secret detection

### GitHub Settings
- Enable Dependabot security updates
- Enable Dependabot version updates
- Configure code scanning (CodeQL)
- Enable secret scanning and push protection

---

## Pre-Commit Hooks

CodeTuneStudio uses `pre-commit` to enforce quality standards before commits.

### Installation
```bash
# Install pre-commit
pip install pre-commit

# Install git hooks
pre-commit install
```

### Configuration Example
Current `.pre-commit-config.yaml` includes:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.2  # Update to latest stable version
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0  # Update to latest stable version
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=500']
      - id: check-merge-conflict
      - id: check-json
```

### Extending Pre-Commit Hooks
Add additional hooks for enhanced checking:

```yaml
  # MyPy type checking
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0  # Check for latest version
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        args: [--config-file=mypy.ini]
        
  # Security scanning
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5  # Check for latest version
    hooks:
      - id: bandit
        args: [-c, pyproject.toml]
        
  # Secret detection
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0  # Check for latest version
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
```

### Running Manually
```bash
# Run all hooks on all files
pre-commit run --all-files

# Run specific hook
pre-commit run ruff --all-files

# Update hook versions
pre-commit autoupdate
```

---

## CI/CD Pipeline Examples

### Quality Gates Workflow

**File:** `.github/workflows/quality-gates.yml`

```yaml
name: Quality Gates

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main]

jobs:
  lint-and-format:
    runs-on: ubuntu-latest
    steps:
      # Pin actions to commit SHA for security (example shows tag, replace with SHA)
      # To get SHA: Visit repo releases page and copy full commit hash
      - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11  # v4.1.1
        
      - name: Set up Python
        uses: actions/setup-python@82c7e631bb3cdc910f68e0081d67478d79c6982d  # v5.1.0
        with:
          python-version: '3.11'
          cache: 'pip'
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
          if [ -f requirements-dev.txt ]; then pip install -r requirements-dev.txt; fi
          
      - name: Lint with Ruff
        run: |
          pip install ruff
          ruff check . --output-format=github
          
      - name: Format check with Ruff
        run: |
          ruff format --check .

  type-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11  # v4.1.1
        
      - name: Set up Python
        uses: actions/setup-python@82c7e631bb3cdc910f68e0081d67478d79c6982d  # v5.1.0
        with:
          python-version: '3.11'
          cache: 'pip'
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
          if [ -f requirements-dev.txt ]; then pip install -r requirements-dev.txt; fi
          
      - name: Type check with MyPy
        run: |
          pip install mypy
          # Configure mypy via mypy.ini or pyproject.toml [tool.mypy]
          # Run on source packages, not root directory
          mypy utils/ components/ core/ models/ plugins/

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11  # v4.1.1
        
      - name: Set up Python
        uses: actions/setup-python@82c7e631bb3cdc910f68e0081d67478d79c6982d  # v5.1.0
        with:
          python-version: '3.11'
          cache: 'pip'
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
          if [ -f requirements-dev.txt ]; then pip install -r requirements-dev.txt; fi
          pip install pytest pytest-cov
          
      - name: Run tests with coverage
        run: |
          # Scope coverage to source packages (utils, components, core, models, plugins)
          pytest --cov=utils --cov=components --cov=core --cov=models --cov=plugins \
                 --cov-report=xml --cov-report=term-missing
          
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@e28ff129e5465c2c0dcc6f003fc735cb6ae0c673  # v4.5.0
        with:
          file: ./coverage.xml
          fail_ci_if_error: true
```

**CI Hygiene Notes:**
- **No Error Masking:** Never use `|| true` to hide failures
- **Conditional Installs:** Use `if [ -f file ]; then install; fi` for optional files
- **Pinned Actions:** Pin third-party actions to immutable commit SHAs (not tags like `@v3`)
  - To obtain SHA: Go to the action's GitHub repo → Releases → Copy full 40-character commit hash
  - Example: `actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11  # v4.1.1`
  - The SHA ensures immutability; the comment documents the version for reference
- **Scoped Coverage:** Always scope `--cov=` to source packages, never use `--cov=.`
- **MyPy Configuration:** Ensure `mypy.ini` or `pyproject.toml` `[tool.mypy]` exists with project settings

---

## Security Scanning

### Comprehensive Security Workflow

**File:** `.github/workflows/security-scan.yml`

```yaml
name: Security Scanning

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 0 * * 1'  # Weekly on Monday at midnight UTC

jobs:
  secret-scan:
    name: Secret Detection
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11  # v4.1.1
        with:
          fetch-depth: 0  # Full history for secret scanning
          
      - name: Run Gitleaks
        uses: gitleaks/gitleaks-action@1f3d10fb50cc38ec13f03aac6a93ce761e04e672  # v2.3.5
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  dependency-audit:
    name: Dependency Vulnerability Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11  # v4.1.1
        
      - name: Set up Python
        uses: actions/setup-python@82c7e631bb3cdc910f68e0081d67478d79c6982d  # v5.1.0
        with:
          python-version: '3.11'
          
      - name: Install audit tools
        run: |
          pip install safety pip-audit
          
      - name: Run Safety check
        run: |
          safety check --json || safety check
          
      - name: Run pip-audit
        run: |
          pip-audit --require-hashes --desc

  sast-scan:
    name: Static Application Security Testing
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11  # v4.1.1
        
      - name: Set up Python
        uses: actions/setup-python@82c7e631bb3cdc910f68e0081d67478d79c6982d  # v5.1.0
        with:
          python-version: '3.11'
          
      - name: Install Bandit
        run: pip install bandit[toml]
        
      - name: Run Bandit security scan
        run: |
          bandit -r . -f json -o bandit-report.json
          bandit -r . -f screen

  sbom-generation:
    name: Generate Software Bill of Materials
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11  # v4.1.1
        
      - name: Generate SBOM with Anchore
        uses: anchore/sbom-action@d94f46e13c6c62f59525ac9a1e147a99dc0b9bf5  # v0.17.0
        with:
          format: spdx-json
          output-file: sbom.spdx.json
          
      - name: Upload SBOM artifact
        uses: actions/upload-artifact@26f96dfa697d77e81fd5907df203aa23a56210a8  # v4.3.0
        with:
          name: sbom
          path: sbom.spdx.json
          
      - name: Scan SBOM for vulnerabilities
        uses: anchore/scan-action@d43cc1dfea6a99ed123bf8f3133f1797c9b44492  # v4.1.0
        with:
          sbom: sbom.spdx.json
          fail-build: true
          severity-cutoff: high

  codeql:
    name: CodeQL Analysis
    runs-on: ubuntu-latest
    permissions:
      security-events: write
      actions: read
      contents: read
    steps:
      - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11  # v4.1.1
        
      - name: Initialize CodeQL
        uses: github/codeql-action/init@afb54ba388a7dca6ecae48f608c4ff05ff4cc77a  # v3.25.15
        with:
          languages: python
          
      - name: Perform CodeQL Analysis
        uses: github/codeql-action/analyze@afb54ba388a7dca6ecae48f608c4ff05ff4cc77a  # v3.25.15
```

### Security Best Practices
- **Secret Scanning:** Enable GitHub secret scanning and push protection
- **Dependency Updates:** Use Dependabot for automated security updates
- **SBOM:** Generate and archive SBOM for compliance and audit trails
- **Severity Thresholds:** Fail builds on high/critical vulnerabilities
- **Regular Audits:** Schedule weekly security scans

---

## Semantic Release Pattern

### Automated Versioning Workflow

**File:** `.github/workflows/semantic-release.yml`

```yaml
name: Semantic Release

on:
  push:
    branches: [main]

jobs:
  release:
    name: Semantic Release
    runs-on: ubuntu-latest
    permissions:
      contents: write
      issues: write
      pull-requests: write
    steps:
      - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11  # v4.1.1
        with:
          fetch-depth: 0
          persist-credentials: false
          
      - name: Set up Node.js
        uses: actions/setup-node@60edb5dd545a775178f52524783378180af0d1f8  # v4.0.2
        with:
          node-version: '20'
          
      - name: Install semantic-release
        run: |
          npm install -g semantic-release @semantic-release/git @semantic-release/changelog
          
      - name: Run semantic-release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: npx semantic-release
```

### Configuration

**File:** `.releaserc.json`

```json
{
  "branches": ["main"],
  "plugins": [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    "@semantic-release/changelog",
    "@semantic-release/github",
    [
      "@semantic-release/git",
      {
        "assets": ["CHANGELOG.md", "package.json"],
        "message": "chore(release): ${nextRelease.version} [skip ci]\n\n${nextRelease.notes}"
      }
    ]
  ]
}
```

### Commit Message Convention
Use Conventional Commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature (minor version bump)
- `fix`: Bug fix (patch version bump)
- `docs`: Documentation only
- `style`: Code style changes (formatting, missing semicolons, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `ci`: CI/CD changes
- `build`: Build system changes

**Breaking Changes:**
- Add `BREAKING CHANGE:` in footer or `!` after type to trigger major version bump
- Example: `feat!: redesign API endpoints`

---

## Troubleshooting

### Flaky Tests

**Problem:** Tests pass locally but fail intermittently in CI

**Solutions:**
1. **Isolate the flaky test:**
   ```bash
   pytest -k test_flaky_function -v --tb=long
   ```

2. **Check for race conditions:**
   - Add explicit waits for async operations
   - Use `asyncio.wait_for()` with timeouts
   - Ensure proper cleanup in fixtures

3. **Database state issues:**
   - Use transaction rollback in fixtures
   - Clear caches between tests
   - Use separate test databases

4. **Timing-dependent tests:**
   - Avoid hard-coded sleep() calls
   - Use polling with timeout instead
   - Mock time-dependent functions

5. **Document known flakes:**
   - Add pytest markers: `@pytest.mark.flaky(reruns=3)`
   - Document root cause in test docstring
   - Create issue to fix properly

### Slow CI

**Problem:** CI pipeline takes too long to complete

**Optimizations:**
1. **Dependency caching:**
   ```yaml
   - uses: actions/setup-python@v5
     with:
       python-version: '3.11'
       cache: 'pip'  # Enable pip cache
   ```

2. **Parallel test execution:**
   ```bash
   pytest -n auto  # Run tests in parallel with pytest-xdist
   ```

3. **Skip non-code changes:**
   ```yaml
   on:
     pull_request:
       paths-ignore:
         - 'docs/**'
         - '**/*.md'
         - '.github/ISSUE_TEMPLATE/**'
   ```

4. **Optimize Docker builds:**
   - Use multi-stage builds
   - Leverage layer caching
   - Use smaller base images

5. **Matrix strategy for parallel jobs:**
   ```yaml
   strategy:
     matrix:
       python-version: ['3.10', '3.11', '3.12']
   ```

### MyPy and Ruff Conflicts

**Problem:** MyPy type errors conflict with Ruff formatting

**Resolution:**

1. **Configure MyPy properly:**

   Create or update `mypy.ini`:
   ```ini
   [mypy]
   python_version = 3.11
   warn_return_any = True
   warn_unused_configs = True
   disallow_untyped_defs = True
   
   # Ignore third-party packages without stubs
   [mypy-third_party_package.*]
   ignore_missing_imports = True
   ```

   Or use `pyproject.toml`:
   ```toml
   [tool.mypy]
   python_version = "3.11"
   warn_return_any = true
   warn_unused_configs = true
   disallow_untyped_defs = true
   
   [[tool.mypy.overrides]]
   module = "third_party_package.*"
   ignore_missing_imports = true
   ```

2. **Run MyPy on source packages:**
   ```bash
   # Good: Target specific packages
   mypy utils/ components/ core/
   
   # Avoid: Running on entire directory
   mypy .  # May include venv, build artifacts, etc.
   ```

3. **Add type stubs for dependencies:**
   ```bash
   pip install types-requests types-PyYAML types-setuptools
   ```

4. **Use type ignore comments sparingly:**
   ```python
   result = external_api_call()  # type: ignore[no-untyped-call]
   ```

5. **Ensure consistent line length:**
   ```toml
   [tool.ruff]
   line-length = 88  # Match Black default
   
   [tool.mypy]
   # MyPy doesn't enforce line length, but keep consistent
   ```

### Pre-Commit Hook Failures

**Problem:** Pre-commit hooks block commits with errors

**Solutions:**

1. **Run hooks manually first:**
   ```bash
   pre-commit run --all-files
   ```

2. **Auto-fix formatting issues:**
   ```bash
   ruff check --fix .
   ruff format .
   ```

3. **Skip hooks temporarily (not recommended):**
   ```bash
   git commit --no-verify -m "WIP: debugging"
   # Remember to fix and amend before pushing!
   ```

4. **Update hook versions:**
   ```bash
   pre-commit autoupdate
   pre-commit run --all-files
   ```

5. **Debug specific hook:**
   ```bash
   pre-commit run <hook-id> --verbose --all-files
   ```

### Import Errors in CI

**Problem:** Local imports work but fail in CI

**Solutions:**

1. **Add source directory to PYTHONPATH:**
   ```yaml
   - name: Run tests
     env:
       PYTHONPATH: ${{ github.workspace }}
     run: pytest
   ```

2. **Install package in editable mode:**
   ```bash
   pip install -e .
   ```

3. **Use absolute imports:**
   ```python
   # Good
   from utils.database import db
   
   # Avoid
   from ..utils.database import db
   ```

4. **Check for missing `__init__.py` in package directories:**
   ```bash
   # Find Python package directories that might be missing __init__.py
   for dir in utils components core models plugins; do
     if [ -d "$dir" ] && [ ! -f "$dir/__init__.py" ]; then
       echo "Missing __init__.py in $dir"
     fi
   done
   ```

---

## Additional Resources

### Official Documentation
- [GitHub Copilot Documentation](https://docs.github.com/en/copilot)
- [Pre-commit Documentation](https://pre-commit.com/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)

### CodeTuneStudio Specific
- **Agent Behavioral Rules:** [`.github/copilot-instructions.md`](../.github/copilot-instructions.md)
- **Architecture Guide:** [`docs/ARCHITECTURE.md`](ARCHITECTURE.md)
- **Contributing Guide:** [`docs/CONTRIBUTING_CODE_QUALITY.md`](CONTRIBUTING_CODE_QUALITY.md)
- **Plugin Development:** [`docs/PLUGIN_GUIDE.md`](PLUGIN_GUIDE.md)

### Security Resources
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [GitHub Security Best Practices](https://docs.github.com/en/code-security)

---

**Remember:** AI assistants are tools to augment your capabilities, not replace careful review and testing. Always validate generated code against project standards defined in [`.github/copilot-instructions.md`](../.github/copilot-instructions.md).
