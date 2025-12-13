# GitHub Workflows Quick Reference

Quick reference guide for GitHub workflows in CodeTuneStudio repository.

## 📋 Available Workflows

| Workflow | Trigger | Purpose | Status |
|----------|---------|---------|--------|
| [auto-update-checklist.yml](#auto-update-checklist) | Push to main, Daily cron | Auto-update PR checklist | ✅ Active |
| [ci.yml](#ci) | Pull requests, Issue comments | CI/CD pipeline | ✅ Active |
| [python-style-checks.yml](#python-style-checks) | PR/Push to main | Style enforcement | ✅ Active |
| [pr-checklist-status.yml](#pr-checklist-status) | Pull requests | PR validation | ✅ Active |
| [release.yml](#release) | Version tags, Manual | Release automation | ✅ Active |
| [huggingface-deploy.yml](#huggingface-deploy) | Push to main | HF Hub deployment | ⚠️ Needs config |
| [stalesweeper.yml](#stalesweeper) | Daily cron, Manual | Stale cleanup | ✅ Active |
| [dependency-graph/auto-submission](#dependency-validation) | PR/Push, Manual | Dependency validation | ✅ Active |

---

## 🔧 Workflow Details

### auto-update-checklist

**File:** `.github/workflows/auto-update-checklist.yml`

**Purpose:** Automatically updates PR checklist based on merged PRs

**Triggers:**
- Push to `main` branch
- Daily at 2:00 AM UTC

**Required Secrets:**
- `GITHUB_TOKEN` (auto-provided)

**Configuration:**
```yaml
Python: 3.10
Dependencies: requests
Permissions: contents:write
```

**Manual Trigger:**
```bash
# Not available (cron/push only)
```

---

### ci

**File:** `.github/workflows/ci.yml`

**Purpose:** Comprehensive CI/CD with linting, testing, building

**Triggers:**
- Pull requests (opened, synchronize, reopened)
- Issue comments

**Jobs:**
1. **lint** - Ruff, Flake8, Black checks
2. **type-check** - MyPy type checking
3. **test** - Pytest with coverage
4. **build** - Package building
5. **ai-command** - AI command processor

**Configuration:**
```yaml
Python: 3.10, 3.11
Test Framework: pytest
Code Coverage: Codecov
```

**AI Commands:**
- `/gemini review`
- `/killer optimize`
- `/claude summarize`
- `/dependabot rebase`
- `/copilot explain`

---

### python-style-checks

**File:** `.github/workflows/python-style-checks.yml`

**Purpose:** Enforce Python code style standards

**Triggers:**
- Pull requests to `main`
- Push to `main`

**Tools:**
- Black 25.11.0 (formatting)
- Flake8 7.3.0 (linting)
- Ruff 0.14.6 (modern linting)
- Pre-commit 4.5.0 (hooks)

**Configuration:**
```yaml
Python: 3.10
Line Length: 88
Exclusions: app.py, index.html
```

**Local Testing:**
```bash
black --check --diff .
flake8 .
ruff check .
pre-commit run --all-files
```

---

### pr-checklist-status

**File:** `.github/workflows/pr-checklist-status.yml`

**Purpose:** Validate PR checklist completion and code style

**Triggers:**
- Pull requests to `main`

**Jobs:**
1. **lint-and-format** - Style validation
2. **checklist-validation** - Task completion check

**Configuration:**
```yaml
Python: 3.10
Concurrency: One per PR (cancels old)
Skip: Draft PRs
```

**Checklist Requirements:**
- All tasks must be marked complete `[x]`
- Checklist in PR description
- Uses: kentaro-m/task-completed-checker-action@v0.1.2

---

### release

**File:** `.github/workflows/release.yml`

**Purpose:** Automated release building and PyPI publishing

**Triggers:**
- Tags matching `v*.*.*` (e.g., v0.2.0)
- Manual dispatch

**Jobs:**
1. **validate** - Version sync, changelog
2. **build** - Create distributions
3. **test-install** - Test on Python 3.10/3.11/3.12
4. **publish-pypi** - Publish to PyPI
5. **create-release** - GitHub release
6. **notify** - Log results

**Required Secrets:**
- `PYPI_API_TOKEN`

**Creating a Release:**
```bash
# 1. Update version
vim core/__init__.py  # Update __version__

# 2. Update changelog
vim CHANGELOG.md

# 3. Commit changes
git add core/__init__.py CHANGELOG.md
git commit -m "Release v0.2.1"

# 4. Create and push tag
git tag v0.2.1
git push origin v0.2.1

# 5. Workflow runs automatically
```

**Configuration:**
```yaml
Python: 3.10, 3.11, 3.12
Build Tool: python -m build
Validation: twine check
```

---

### huggingface-deploy

**File:** `.github/workflows/huggingface-deploy.yml`

**Purpose:** Deploy models to Hugging Face Hub

**Triggers:**
- Push to `main` branch

**Jobs:**
1. **build** - Install deps, run tests
2. **deploy** - Login to HF Hub, push model

**Required Secrets:**
- `HF_TOKEN`

**⚠️ Configuration Required:**
```yaml
# Update these placeholders:
repo_name: my-model  # → your-hf-repo-name
model_path: ./path_to_model  # → actual/model/path
```

**Manual Setup:**
```bash
# Set HF token in repository secrets
gh secret set HF_TOKEN

# Update workflow file
vim .github/workflows/huggingface-deploy.yml
```

**Configuration:**
```yaml
Python: 3.10
Dependencies: huggingface_hub
```

---

### stalesweeper

**File:** `.github/workflows/stalesweeper.yml`

**Purpose:** Automatically close stale issues and discussions

**Triggers:**
- Daily at 1:00 AM UTC
- Manual dispatch

**Configuration:**
```yaml
Issues:
  - Mark stale after: 60 days
  - Close after: 7 more days
  - Exempt labels: pinned, security, bug

Discussions:
  - Close after: 60 days
  - Include unanswered: yes
```

**Manual Trigger:**
```bash
gh workflow run stalesweeper.yml
```

**Permissions:**
```yaml
issues: write
discussions: write
```

---

### dependency-validation

**File:** `.github/workflows/dynamic/dependency-graph/auto-submission`

**Purpose:** Validate Python dependencies and detect conflicts

**Triggers:**
- Push to `main`
- Pull requests to `main`
- Manual dispatch

**Validation Steps:**
1. Check project structure
2. Validate with pip-compile
3. Security scan with safety
4. Install dependencies
5. Generate dependency report

**Configuration:**
```yaml
Python: 3.11
Tools: pip-tools, safety, pipdeptree
```

**Manual Trigger:**
```bash
gh workflow run auto-submission
```

---

## 🧪 Testing Workflows

### Run All Tests

```bash
# Structure and security tests
pytest tests/test_workflows.py tests/test_workflow_security.py -v

# Simulation tests
pytest tests/test_workflow_simulation.py -v

# All workflow tests
pytest tests/test_workflows.py tests/test_workflow_security.py tests/test_workflow_simulation.py -v
```

### Validate Workflows

```bash
# Validate all workflows
python scripts/validate_workflows.py

# Validate specific workflow
python scripts/validate_workflows.py --workflow ci.yml
```

### Test Locally

```bash
# Install dependencies
pip install black ruff flake8 pytest pre-commit

# Run style checks
black --check .
ruff check .
flake8 .

# Run tests
pytest -v

# Run pre-commit hooks
pre-commit run --all-files
```

---

## 🔐 Required Secrets

### Repository Secrets

Set these in: `Settings → Secrets and variables → Actions`

| Secret | Required For | Description |
|--------|--------------|-------------|
| `GITHUB_TOKEN` | Most workflows | Auto-provided by GitHub |
| `HF_TOKEN` | huggingface-deploy | Hugging Face API token |
| `PYPI_API_TOKEN` | release | PyPI publishing token |

### Setting Secrets

```bash
# Using GitHub CLI
gh secret set HF_TOKEN
gh secret set PYPI_API_TOKEN

# Or via web UI
# Settings → Secrets → New repository secret
```

---

## 📊 Workflow Status

### View Workflow Runs

```bash
# List recent runs
gh run list

# View specific run
gh run view <run-id>

# Watch workflow
gh run watch <run-id>

# View logs
gh run view <run-id> --log
```

### Trigger Manual Workflow

```bash
# Release workflow
gh workflow run release.yml

# Stalesweeper
gh workflow run stalesweeper.yml

# Dependency validation
gh workflow run auto-submission
```

---

## 🐛 Troubleshooting

### Common Issues

**Workflow Not Triggering:**
```bash
# Check workflow syntax
python scripts/validate_workflows.py --workflow <workflow-name>

# View workflow details
gh workflow view <workflow-name>
```

**Secret Not Found:**
```bash
# List secrets
gh secret list

# Set secret
gh secret set SECRET_NAME
```

**Job Failing:**
```bash
# View logs
gh run view <run-id> --log

# Re-run failed jobs
gh run rerun <run-id> --failed
```

**Permission Denied:**
```yaml
# Add to workflow
permissions:
  contents: write  # or read
  issues: write
```

---

## 📚 Resources

### Documentation
- [Full Audit Report](./WORKFLOW_AUDIT_REPORT.md)
- [Testing Guide](./WORKFLOW_TESTING_GUIDE.md)
- [Repository README](../README.md)

### Tools
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [GitHub CLI](https://cli.github.com/)

### Validation
```bash
# Validate workflows
python scripts/validate_workflows.py

# Run tests
pytest tests/test_workflows.py -v

# Check security
pytest tests/test_workflow_security.py -v
```

---

## 🎯 Quick Commands

```bash
# Validate all workflows
python scripts/validate_workflows.py

# Run all tests
pytest tests/test_workflows.py tests/test_workflow_security.py -v

# Check workflow status
gh run list --limit 10

# Trigger release (after tagging)
git tag v0.2.1 && git push origin v0.2.1

# Manual workflow trigger
gh workflow run <workflow-name>

# View workflow logs
gh run view --log

# List available workflows
gh workflow list
```

---

**Last Updated:** December 13, 2024  
**Status:** All workflows validated and tested
