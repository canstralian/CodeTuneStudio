# GitHub Workflows Testing Guide

This guide explains how to test and validate GitHub workflows in the CodeTuneStudio repository.

## Table of Contents

- [Overview](#overview)
- [Test Suite](#test-suite)
- [Running Tests](#running-tests)
- [Validation Script](#validation-script)
- [Manual Testing](#manual-testing)
- [Troubleshooting](#troubleshooting)

---

## Overview

The CodeTuneStudio repository includes comprehensive testing for GitHub workflows:

1. **Structural Tests** - Validate YAML syntax and required fields
2. **Security Tests** - Check for security vulnerabilities and best practices
3. **Validation Script** - Command-line tool for quick validation
4. **Manual Testing** - Guide for testing workflow execution

---

## Test Suite

### 1. Workflow Structure Tests (`tests/test_workflows.py`)

**Purpose:** Validate workflow file structure, syntax, and references

**Test Coverage:**
- YAML syntax validation
- Required fields (name, on, jobs)
- File and script references
- Job definitions
- Python version compatibility

**Running:**
```bash
pytest tests/test_workflows.py -v
```

**Example Output:**
```
tests/test_workflows.py::TestWorkflowStructure::test_all_workflow_files_have_valid_yaml PASSED
tests/test_workflows.py::TestWorkflowStructure::test_workflows_directory_exists PASSED
tests/test_workflows.py::TestAutoUpdateChecklistWorkflow::test_workflow_exists PASSED
...
==================== 24 passed, 23 subtests passed in 0.17s ====================
```

### 2. Workflow Security Tests (`tests/test_workflow_security.py`)

**Purpose:** Validate security best practices and identify vulnerabilities

**Test Coverage:**
- No hardcoded secrets
- Proper use of GitHub Secrets
- Permission configurations
- Safe trigger usage
- Pinned action versions
- Supported Python versions

**Running:**
```bash
pytest tests/test_workflow_security.py -v
```

**Example Output:**
```
tests/test_workflow_security.py::TestWorkflowSecurity::test_no_hardcoded_secrets PASSED
tests/test_workflow_security.py::TestWorkflowSecurity::test_secrets_use_github_secrets PASSED
...
==================== 8 passed, 139 subtests passed in 0.26s ====================
```

### 3. Combined Test Run

Run all workflow tests:
```bash
pytest tests/test_workflows.py tests/test_workflow_security.py -v
```

Run with coverage:
```bash
pytest tests/test_workflows.py tests/test_workflow_security.py --cov=.github/workflows --cov-report=html
```

---

## Validation Script

### Quick Validation Tool (`scripts/validate_workflows.py`)

A standalone script for quick workflow validation.

**Usage:**

Validate all workflows:
```bash
python scripts/validate_workflows.py
```

Validate specific workflow:
```bash
python scripts/validate_workflows.py --workflow ci.yml
```

Security checks only:
```bash
python scripts/validate_workflows.py --security-only
```

**Output Example:**
```
🔍 GitHub Workflow Validator
============================================================
📋 Found 8 workflow file(s) to validate

📄 Validating: .github/workflows/ci.yml
  ✓ Validation complete

============================================================
📊 Validation Results
============================================================

✅ All validations passed!

============================================================
```

**Exit Codes:**
- `0` - All validations passed
- `1` - Validation errors found

---

## Manual Testing

### Prerequisites

1. GitHub CLI (`gh`) installed
2. Repository access
3. GitHub token with appropriate permissions

### Testing Individual Workflows

#### 1. Auto Update Checklist Workflow

**Test Locally:**
```bash
# Set up environment
export GITHUB_TOKEN="your_github_token"

# Run the update script
python scripts/update_checklist.py

# Check for changes
git status
```

**Test on GitHub:**
1. Create a test PR and merge it
2. Wait for cron schedule or trigger manually
3. Check if PR_REVIEW_CHECKLIST.md is updated

**Expected Behavior:**
- Script fetches closed/merged PRs
- Updates checklist with PR references
- Commits changes automatically

#### 2. CI Workflow

**Test Locally:**
```bash
# Install dependencies
pip install ruff flake8 black mypy pytest pytest-cov

# Run linting
ruff check . --output-format=github
flake8 . --count --select=E9,F63,F7,F82
black --check --diff .

# Run type checking
mypy core/ --ignore-missing-imports

# Run tests
pytest -v --cov=. --cov-report=term
```

**Test on GitHub:**
1. Create a PR with code changes
2. Workflow should trigger automatically
3. Check workflow run in Actions tab

**Expected Behavior:**
- Linting job passes
- Type checking completes
- Tests run on Python 3.10 and 3.11
- Build artifacts created

#### 3. Python Style Checks Workflow

**Test Locally:**
```bash
# Install style tools
pip install black==25.11.0 flake8==7.3.0 pre-commit==4.5.0 ruff==0.14.6

# Run Black
black --check --diff --line-length=88 .

# Run Flake8
flake8 . --max-line-length=88 --statistics

# Run Ruff
ruff check . --ignore E501

# Run pre-commit
pre-commit run --all-files
```

**Test on GitHub:**
1. Create PR with style violations
2. Workflow should fail with clear messages
3. Fix style issues and push again

**Expected Behavior:**
- Black catches formatting issues
- Flake8 catches style violations
- Ruff provides fast linting
- Pre-commit hooks run

#### 4. Release Workflow

**Test Locally:**
```bash
# Install build tools
pip install build setuptools wheel twine

# Build package
python -m build

# Validate distributions
twine check dist/*

# Test installation
pip install dist/*.whl

# Verify version
python -c "import core; print(core.__version__)"

# Test CLI
codetune-studio --version
```

**Test on GitHub (Dry Run):**
1. Use `workflow_dispatch` to test without creating release
2. Check logs for each job
3. Verify artifacts are created

**Full Release Test:**
1. Update version in `core/__init__.py`
2. Update CHANGELOG.md
3. Create and push tag: `git tag v0.2.1 && git push origin v0.2.1`
4. Workflow triggers automatically
5. Verify PyPI publication and GitHub release

**Expected Behavior:**
- Version validation passes
- Builds successfully on all Python versions
- Distributions are valid
- PyPI publishing works (if secrets configured)
- GitHub release created with notes

#### 5. Dependency Graph Workflow

**Test Locally:**
```bash
# Install validation tools
pip install pip-tools safety

# Validate requirements
pip-compile --dry-run --resolver=backtracking requirements.txt

# Check for vulnerabilities
safety check --file requirements.txt

# Install dependencies
pip install -r requirements.txt

# Generate dependency tree
pip install pipdeptree
pipdeptree
```

**Test on GitHub:**
1. Modify requirements.txt or pyproject.toml
2. Create PR
3. Workflow validates dependencies

**Expected Behavior:**
- Detects missing dependency files
- Validates dependency compatibility
- Reports security vulnerabilities
- Generates dependency report

#### 6. Hugging Face Deploy Workflow

**Test Preparation:**
```bash
# Install HF tools
pip install huggingface_hub

# Set token (for local testing)
export HF_TOKEN="your_hf_token"

# Login
huggingface-cli login --token $HF_TOKEN

# Test repo creation
huggingface-cli repo create test-model --type=model
```

**Note:** This workflow has placeholder paths that need updating before use.

**Update Required:**
- Replace `./path_to_model` with actual model path
- Replace `my-model` with actual HF repo name

#### 7. PR Checklist Status Workflow

**Test Locally:**
```bash
# Run format checks
black --check --diff . --exclude 'app.py'

# Run lint checks
ruff check . --ignore E501 --exit-non-zero-on-fix
```

**Test on GitHub:**
1. Create PR without completing checklist
2. Workflow should fail checklist validation
3. Complete checklist items
4. Workflow should pass

**Expected Behavior:**
- Format checks fail if code needs formatting
- Lint checks fail if fixes needed
- Checklist validation checks PR description
- Skips validation on draft PRs

#### 8. Stale Sweeper Workflow

**Test Configuration:**
```bash
# Review configuration
cat .github/workflows/stalesweeper.yml

# Check for stale issues
gh issue list --state open --label stale

# Check for old issues
gh issue list --state open --json createdAt,number,title
```

**Test on GitHub:**
1. Wait for cron trigger (1:00 AM UTC) or trigger manually
2. Check for stale labels added
3. Verify messages posted on stale items

**Expected Behavior:**
- Marks issues stale after 60 days
- Closes after 7 additional days
- Skips pinned/security/bug labels
- Posts helpful messages

---

## Workflow Simulation

### Creating Test Fixtures

For testing workflows with mock data:

```python
# tests/fixtures/mock_pr_data.py
def mock_github_pr_response():
    """Mock PR data for testing"""
    return [
        {
            "number": 123,
            "title": "Test PR",
            "state": "closed",
            "merged_at": "2024-01-01T00:00:00Z",
        }
    ]
```

### Running Workflow Jobs Locally with Act

Install [act](https://github.com/nektos/act) to run workflows locally:

```bash
# Install act
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# List workflow jobs
act -l

# Run specific workflow
act -j lint

# Run with secrets
act -j deploy --secret-file .secrets

# Dry run
act -n
```

---

## Continuous Integration

### Pre-Commit Hooks

Install pre-commit hooks to validate workflows before committing:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

**Add to `.pre-commit-config.yaml`:**
```yaml
- repo: local
  hooks:
    - id: validate-workflows
      name: Validate GitHub Workflows
      entry: python scripts/validate_workflows.py
      language: system
      pass_filenames: false
      files: ^\.github/workflows/.*\.ya?ml$
```

### CI Integration

Add workflow validation to CI:

```yaml
# .github/workflows/validate-workflows.yml
name: Validate Workflows

on:
  pull_request:
    paths:
      - '.github/workflows/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install pyyaml pytest
      - name: Run validation script
        run: python scripts/validate_workflows.py
      - name: Run tests
        run: pytest tests/test_workflows.py tests/test_workflow_security.py -v
```

---

## Troubleshooting

### Common Issues

#### 1. YAML Syntax Errors

**Symptom:** Workflow fails to parse

**Solution:**
```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"

# Use online validator
# https://www.yamllint.com/
```

#### 2. File Reference Errors

**Symptom:** Workflow can't find referenced files

**Solution:**
```bash
# Check file exists
ls -la scripts/update_checklist.py

# Check path in workflow matches actual path
grep -r "update_checklist" .github/workflows/
```

#### 3. Permission Errors

**Symptom:** Workflow fails with permission denied

**Solution:**
```yaml
# Add appropriate permissions
permissions:
  contents: write
  issues: write
```

#### 4. Secret Not Found

**Symptom:** Workflow fails accessing secrets

**Solution:**
1. Verify secret exists in repository settings
2. Check secret name matches workflow
3. Ensure proper secret access in organization

#### 5. Action Version Issues

**Symptom:** Action not found or deprecated

**Solution:**
```yaml
# Update to latest version
- uses: actions/checkout@v4  # was v3
- uses: actions/setup-python@v5  # was v4
```

### Debugging Workflows

**Enable debug logging:**
1. Go to repository Settings → Secrets
2. Add secret: `ACTIONS_STEP_DEBUG` = `true`
3. Add secret: `ACTIONS_RUNNER_DEBUG` = `true`

**View detailed logs:**
```bash
# Using GitHub CLI
gh run view <run-id> --log

# View specific job
gh run view <run-id> --job <job-id> --log
```

**Check workflow syntax:**
```bash
# Validate workflow syntax (requires GitHub CLI)
gh workflow view ci.yml
```

---

## Best Practices

### 1. Test Before Committing

Always run validation before committing workflow changes:
```bash
python scripts/validate_workflows.py
pytest tests/test_workflows.py -v
```

### 2. Use Descriptive Names

```yaml
# Good
- name: Install Python dependencies for testing
  run: pip install -r requirements.txt

# Bad
- name: Install
  run: pip install -r requirements.txt
```

### 3. Add Comments

```yaml
# Explain complex logic
- name: Extract version
  run: |
    # Parse version from tag (e.g., v1.2.3 -> 1.2.3)
    VERSION="${GITHUB_REF#refs/tags/v}"
    echo "VERSION=$VERSION" >> $GITHUB_OUTPUT
```

### 4. Use Caching

```yaml
- uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
```

### 5. Handle Failures Gracefully

```yaml
- name: Optional step
  run: some-command
  continue-on-error: true

- name: Cleanup
  if: always()  # Run even if previous steps failed
  run: cleanup-command
```

---

## Additional Resources

### Documentation
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax Reference](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [Security Hardening Guide](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)

### Tools
- [act](https://github.com/nektos/act) - Run workflows locally
- [actionlint](https://github.com/rhysd/actionlint) - Workflow linter
- [GitHub CLI](https://cli.github.com/) - Manage workflows from command line

### CodeTuneStudio Specific
- [Workflow Audit Report](./WORKFLOW_AUDIT_REPORT.md)
- [Repository README](../README.md)
- [Contributing Guide](../CODE_OF_CONDUCT.md)

---

## Support

For issues with workflows:
1. Check the [Workflow Audit Report](./WORKFLOW_AUDIT_REPORT.md)
2. Run validation: `python scripts/validate_workflows.py`
3. Review workflow logs in GitHub Actions tab
4. Create an issue with workflow logs and error messages

---

**Last Updated:** December 13, 2024  
**Maintainer:** CodeTuneStudio Team
