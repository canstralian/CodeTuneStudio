# AI Assistant Developer Workflow Guide

**Canonical guide for developers using AI coding assistants with CodeTuneStudio**

## Overview

This guide provides the complete developer workflow for contributing to CodeTuneStudio using AI coding assistants (GitHub Copilot, Cursor, etc.). It documents the enforced CI/CD checks, local pre-flight commands, and best practices specific to this repository.

For AI agent behavioral rules, see [`.github/copilot-instructions.md`](../.github/copilot-instructions.md).

---

## 🎯 Project Stack Reality Check

Before generating code, understand CodeTuneStudio's actual technology stack:

### Backend Architecture
- **Web Framework**: Flask (REST API) + Streamlit (Interactive UI on port 7860)
- **NOT FastAPI**: This project uses Flask, not FastAPI
- **Database**: PostgreSQL (production) / SQLite (development) hybrid
- **ORM**: SQLAlchemy with Flask-SQLAlchemy extension

### Machine Learning Stack
- **Framework**: PyTorch (NOT TensorFlow/Keras)
- **Model Library**: HuggingFace Transformers
- **Fine-tuning**: Parameter-Efficient Fine-Tuning (PEFT) with LoRA adapters
- **Acceleration**: HuggingFace Accelerate for distributed training

### Directory Structure
```
CodeTuneStudio/
├── core/           # Core server and CLI functionality
├── models/         # Database models (SQLAlchemy)
├── utils/          # Utilities (training, datasets, validation)
├── plugins/        # Extensible plugin system
├── components/     # Streamlit UI components
├── tests/          # Test suite
├── .github/        # Workflows and agent instructions
└── docs/           # Documentation
```

**Important**: There is NO `src/` directory. All code lives in the directories above.

---

## 🔐 Enforced Workflows and Required Checks

CodeTuneStudio uses hardened CI workflows that are **blocking** and **must pass** before merge.

### Quality Pipeline (`.github/workflows/quality.yml`)

**Triggers**: Every push and pull request

#### Job 1: Style Checks
- **Black** formatter validation (88 char line length)
- **Flake8** linting with error reporting
- **Ruff** additional modern linting
- **Scope**: `core/ models/ utils/ plugins/ components/`

#### Job 2: Type Checking
- **MyPy** static type analysis
- **Scope**: `core/ models/ utils/ plugins/ components/`
- **Requirement**: All functions must have type hints

#### Job 3: Tests with Coverage
- **Pytest** test suite execution
- **Coverage**: Scoped to `core/ models/ utils/ plugins/ components/`
- **Threshold**: 80% minimum coverage (hard fail below this)
- **Upload**: Results sent to Codecov for tracking

**Action Pins** (commit SHAs):
```yaml
actions/checkout@6b42224f41ee5dfe5395e27c8b2746f1f9955030      # v4.2.2
actions/setup-python@0b93645e9fea7318ecaed2b359559ac225c90a2b  # v5.3.0
codecov/codecov-action@5c47607acb93fed5485fdbf7232e8a31425f672a  # v5.0.2
```

**Tool Versions**:
- `black==25.11.0`
- `flake8==7.3.0`
- `ruff==0.14.6`
- `mypy==1.13.0`

### Security Pipeline (`.github/workflows/security.yml`)

**Triggers**: Every push and pull request

#### Job 1: Secret Scanning
- **TruffleHog** secret detection with full git history
- **Flag**: `--only-verified` (reduces false positives)
- **Blocks**: Any verified secrets (API keys, tokens, credentials)

#### Job 2: Dependency Audit
- **pip-audit** vulnerability scanner
- **Input**: `requirements.txt`
- **Blocks**: Known vulnerabilities in dependencies

#### Job 3: SBOM Generation
- **Anchore SBOM** action generates Software Bill of Materials
- **Format**: CycloneDX JSON
- **Artifact**: Stored for 90 days
- **Purpose**: Supply chain security and compliance

**Action Pins** (commit SHAs):
```yaml
actions/checkout@6b42224f41ee5dfe5395e27c8b2746f1f9955030
actions/setup-python@0b93645e9fea7318ecaed2b359559ac225c90a2b
trufflesecurity/trufflehog@ecb05f407947857f313624ee2f13b0ab9519c271
pypa/gh-action-pip-audit@3152ba5c5483e87342795b7d5d35b472fc5becfd
anchore/sbom-action@ad568ce3311e234f70bfb2e9f0a98d0139e685ad
actions/upload-artifact@6f51ac03b9356f520e9adb1b1b7802705f340c2b  # v4.5.0
```

---

## 🚀 Local Pre-Flight Commands

Run these checks locally BEFORE pushing to avoid CI failures:

### 1. Setup Development Environment

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install development tools (match CI versions exactly)
pip install \
  black==25.11.0 \
  flake8==7.3.0 \
  ruff==0.14.6 \
  mypy==1.13.0 \
  pytest \
  pytest-cov \
  pytest-mock
```

### 2. Code Style Checks

```bash
# Check formatting with Black (don't auto-fix yet)
black --check --diff --line-length=88 core/ models/ utils/ plugins/ components/

# Fix formatting if needed
black --line-length=88 core/ models/ utils/ plugins/ components/

# Run Flake8 linting
flake8 core/ models/ utils/ plugins/ components/ \
  --max-line-length=88 \
  --statistics \
  --show-source \
  --count

# Run Ruff linting
ruff check core/ models/ utils/ plugins/ components/
```

### 3. Type Checking

```bash
# Run MyPy type checker
mypy core/ models/ utils/ plugins/ components/ --ignore-missing-imports
```

### 4. Run Tests with Coverage

```bash
# Run full test suite with coverage
pytest -v \
  --cov=core \
  --cov=models \
  --cov=utils \
  --cov=plugins \
  --cov=components \
  --cov-report=xml \
  --cov-report=term \
  --cov-fail-under=80

# View coverage report
coverage report -m
```

### 5. Security Checks (Optional Local)

```bash
# Install security tools
pip install pip-audit

# Run dependency audit
pip-audit -r requirements.txt

# Secret scanning (requires TruffleHog binary)
# Note: This runs automatically in CI
```

---

## 🛡️ Branch Protection Guidance

When setting up branch protection rules for `main`, require these status checks:

### Required Status Checks (Quality Pipeline)
- `style` - Code Style Checks
- `types` - Type Checking
- `tests` - Tests with Coverage

### Required Status Checks (Security Pipeline)
- `secrets` - Secret Scanning
- `dependencies` - Dependency Audit
- `sbom` - SBOM Generation

### Recommended Branch Protection Settings
```yaml
Branch Protection Rules for 'main':
  ✓ Require a pull request before merging
  ✓ Require approvals (minimum 1)
  ✓ Dismiss stale pull request approvals when new commits are pushed
  ✓ Require status checks to pass before merging
    - Mark as required: style, types, tests, secrets, dependencies, sbom
  ✓ Require conversation resolution before merging
  ✓ Require signed commits (recommended)
  ✓ Require linear history
  ✓ Include administrators
```

---

## 📋 AI Assistant Best Practices

### When Using GitHub Copilot / Cursor / etc.

1. **Understand the Stack**: Always reference the stack reality check above
2. **Follow Directory Layout**: Use `core/`, `models/`, `utils/`, `plugins/`, `components/`
3. **Type Everything**: Add type hints to all function signatures
4. **Document Functions**: Include docstrings (Google/NumPy style)
5. **Validate Inputs**: Never trust user input without validation
6. **Use ORM**: SQLAlchemy queries only; no raw SQL
7. **Async Properly**: Use `async`/`await` for I/O; don't block the event loop
8. **Scope Coverage**: Use specific coverage paths, not `--cov=.`

### Code Review Checklist

Before submitting a PR with AI-generated code:

- [ ] **Security**: No hardcoded secrets or credentials
- [ ] **Types**: All functions have type hints
- [ ] **Docs**: All public functions have docstrings
- [ ] **Tests**: New code has corresponding tests
- [ ] **Coverage**: Tests maintain 80%+ coverage
- [ ] **Style**: Passes Black, Flake8, Ruff
- [ ] **Types**: Passes MyPy type checking
- [ ] **Database**: Uses SQLAlchemy ORM (no raw SQL)
- [ ] **Async**: Proper async/await patterns (no blocking I/O)
- [ ] **Logging**: Uses structured logging (no secrets in logs)

---

## 🔗 Related Documentation

- [**`.github/copilot-instructions.md`**](../.github/copilot-instructions.md) - AI agent behavioral rules and security practices
- [**`CLAUDE.md`**](../CLAUDE.md) - Detailed architecture and development commands
- [**`README.md`**](../README.md) - Project overview and setup instructions
- [**`SECURITY.md`**](../SECURITY.md) - Security policy and vulnerability reporting

---

## 📦 Deprecated Documentation

Historical Copilot/Codex guides have been archived to reduce documentation sprawl:

- Location: [`docs/archive/deprecated-copilot-guides/`](./archive/deprecated-copilot-guides/)
- These files contained overlapping content and references to non-existent projects
- This guide (`docs/ai-assistant-guide.md`) supersedes all archived guides
- PR #150's proposed guide was reviewed, and relevant content has been incorporated here

---

## 🚨 Common Pitfalls to Avoid

### ❌ DON'T:
- Use `--cov=.` for test coverage (too broad; includes vendor code)
- Use `continue-on-error: true` to mask failures
- Use `|| true` to ignore error codes
- Hardcode database credentials or API keys
- Use raw SQL with string interpolation
- Use mutable action tags like `@v3` or `@latest`
- Reference FastAPI (this project uses Flask)
- Look for a `src/` directory (it doesn't exist)

### ✅ DO:
- Scope coverage to specific directories
- Let CI fail fast on quality issues
- Store secrets in `.env` files (excluded from git)
- Use SQLAlchemy ORM for all database access
- Pin actions to exact commit SHAs
- Reference Flask and Streamlit documentation
- Use the correct directory structure

---

## 🎓 Learning Resources

### Project-Specific
- HuggingFace Transformers: https://huggingface.co/docs/transformers
- PEFT/LoRA Documentation: https://huggingface.co/docs/peft
- SQLAlchemy ORM: https://docs.sqlalchemy.org/en/latest/orm/

### Security
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- GitHub Secret Scanning: https://docs.github.com/en/code-security/secret-scanning
- Python Security Best Practices: https://python.readthedocs.io/en/stable/library/security_warnings.html

### CI/CD
- GitHub Actions: https://docs.github.com/en/actions
- Action Pinning: https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions

---

*Last Updated: 2025-12-13*  
*Questions? Open an issue at: https://github.com/canstralian/CodeTuneStudio/issues*
