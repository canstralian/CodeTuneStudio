# Refactoring Tasks - CodeTuneStudio

This document tracks specific refactoring tasks identified during the code quality review.
Each task includes priority, affected files, and acceptance criteria.

## Task Tracking Legend
- 🔴 High Priority - Should be completed first
- 🟡 Medium Priority - Important but not blocking
- 🟢 Low Priority - Nice to have
- ⚪ Not Started
- 🔵 In Progress
- ✅ Completed

---

## Category 1: Test Infrastructure 🔴

### Task 1.1: Fix Pytest Dependency Issue
**Priority:** 🔴 High
**Status:** ⚪ Not Started
**Effort:** 1-2 hours

**Problem:** 6 test files import pytest, but it's only in optional dev dependencies, causing ImportError.

**Affected Files:**
- `tests/test_anthropic_code_suggester.py`
- `tests/test_app.py`
- `tests/test_code_analyzer.py`
- `tests/test_db_check.py`
- `tests/test_manage.py`
- `tests/test_openai_code_analyzer.py`
- `pyproject.toml`

**Solution Options:**
1. Move pytest from optional dev dependencies to main dependencies
2. Convert these tests to pure unittest
3. Update test execution to install dev dependencies

**Recommended Approach:** Option 1 - Move pytest to main dependencies

**Acceptance Criteria:**
- [ ] All 6 test files can import pytest successfully
- [ ] `python -m pytest tests/` runs without ImportError
- [ ] All tests pass or have documented failures
- [ ] CI/CD pipeline updated to use pytest

**Implementation Steps:**
1. Edit `pyproject.toml` to move pytest from `[project.optional-dependencies]` to `[project.dependencies]`
2. Run `pip install -e .` to install updated dependencies
3. Run `pytest tests/ -v` to verify
4. Update CI workflow if needed

---

### Task 1.2: Fix Failing Test - pytest_available_for_build_job
**Priority:** 🔴 High
**Status:** ⚪ Not Started
**Effort:** 30 minutes

**Problem:** Test expects pytest to be available but it's not installed in the environment.

**Affected Files:**
- `tests/test_workflow_simulation.py`

**Acceptance Criteria:**
- [ ] Test passes when pytest is properly installed
- [ ] Test accurately validates build job requirements

**Dependencies:** Requires Task 1.1 completion

---

### Task 1.3: Set Up Coverage Reporting
**Priority:** 🟡 Medium
**Status:** ⚪ Not Started
**Effort:** 2-3 hours

**Problem:** No coverage metrics available to track test completeness.

**Affected Files:**
- `pyproject.toml`
- `.github/workflows/ci.yml`
- New file: `.coveragerc` or coverage config in pyproject.toml

**Acceptance Criteria:**
- [ ] pytest-cov installed and configured
- [ ] Coverage reports generated in HTML and terminal
- [ ] Coverage badge added to README
- [ ] CI uploads coverage to codecov.io or similar
- [ ] Minimum coverage threshold set (suggest 70%)

**Implementation:**
```bash
# Install
pip install pytest-cov

# Run
pytest --cov=. --cov-report=html --cov-report=term-missing --cov-report=xml

# Add to CI
- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v3
```

---

## Category 2: Code Style & Formatting 🔴

### Task 2.1: Fix Whitespace Issues (69 violations)
**Priority:** 🔴 High
**Status:** ⚪ Not Started
**Effort:** 10 minutes (automated)

**Problem:** 60 blank lines with whitespace, 9 trailing whitespace violations.

**Affected Files:**
- `tests/test_workflow_simulation.py` (47 violations)
- `utils/argilla_dataset.py` (9 violations)
- `core/server.py` (7 violations)
- `scripts/validate_pyproject.py` (6 violations)

**Solution:**
```bash
# Option 1: Using sed
find . -name "*.py" -type f ! -path "*/venv/*" -exec sed -i 's/[[:space:]]*$//' {} +

# Option 2: Using ruff
ruff format .

# Option 3: Using black
black .
```

**Acceptance Criteria:**
- [ ] No W291 (trailing whitespace) violations
- [ ] No W293 (blank line whitespace) violations
- [ ] Flake8 passes on affected files
- [ ] Git diff shows only whitespace changes

---

### Task 2.2: Fix Line Length Violations (32 violations)
**Priority:** 🟡 Medium
**Status:** ⚪ Not Started
**Effort:** 15 minutes (automated)

**Problem:** 32 lines exceed 88 character limit (most are 89-96 chars).

**Affected Files:**
- `core/server.py` (21 violations)
- `core/cli.py` (1 violation)
- `core/logging.py` (3 violations)
- `tests/test_workflow_security.py` (4 violations)
- Others (3 violations)

**Solution:**
```bash
black . --line-length 88
```

**Acceptance Criteria:**
- [ ] All lines ≤ 88 characters
- [ ] No E501 violations in flake8
- [ ] Code remains readable (no awkward breaks)

---

### Task 2.3: Remove Unused Imports (6 violations)
**Priority:** 🟡 Medium
**Status:** ⚪ Not Started
**Effort:** 10 minutes

**Problem:** Unused imports indicate potential dead code.

**Specific Changes:**

**File: `core/server.py:13`**
```python
# Remove:
from typing import Any, Dict, Optional

# Keep:
from typing import Any
```

**File: `scripts/validate_workflows.py:17`**
```python
# Remove:
from typing import Any, Dict, List, Tuple

# Keep:
from typing import Any, Dict, List
```

**File: `tests/test_core_package.py:77`**
```python
# Remove the line:
from core import __version__  # Currently imported but unused
```

**File: `tests/test_workflow_simulation.py:9`**
```python
# Remove:
from unittest.mock import MagicMock, patch, mock_open

# Keep:
from unittest.mock import patch, mock_open
```

**File: `tests/test_workflows.py:8`**
```python
# Remove:
import os
```

**Acceptance Criteria:**
- [ ] No F401 violations in flake8
- [ ] Tests still pass after removal
- [ ] Imports are actually unused (verified by grep/search)

---

### Task 2.4: Fix F-String Placeholders (2 violations)
**Priority:** 🟢 Low
**Status:** ⚪ Not Started
**Effort:** 5 minutes

**Problem:** F-strings used without placeholders (should be regular strings).

**Affected Files:**
- `scripts/validate_workflows.py:97`
- `scripts/validate_workflows.py:109`

**Acceptance Criteria:**
- [ ] Convert to regular strings or add placeholders
- [ ] No F541 violations in flake8

---

### Task 2.5: Fix Formatting Issue (1 violation)
**Priority:** 🟢 Low
**Status:** ⚪ Not Started
**Effort:** 2 minutes

**Problem:** Missing blank line before function definition.

**Affected Files:**
- `scripts/validate_pyproject.py:18`

**Solution:**
Add one blank line before the function definition at line 18.

**Acceptance Criteria:**
- [ ] No E302 violations in flake8
- [ ] Follows PEP 8 formatting

---

## Category 3: Complexity Reduction 🔴

### Task 3.1: Refactor training_monitor() Function
**Priority:** 🔴 High
**Status:** ⚪ Not Started
**Effort:** 4-6 hours

**Problem:** Cyclomatic complexity of 22 (max recommended: 10).

**Affected Files:**
- `components/training_monitor.py:149`

**Current Issues:**
- Too many responsibilities in one function
- Difficult to test individual behaviors
- Hard to maintain and debug

**Refactoring Strategy:**
1. Extract UI rendering logic
2. Separate state management
3. Extract training execution logic
4. Extract device management logic

**Proposed Structure:**
```python
def training_monitor():
    """Main coordinator - complexity ~5"""
    initialize_training_state()
    render_training_ui()
    if should_start_training():
        start_training_process()

def render_training_ui():
    """Handle all Streamlit UI components - complexity ~5"""
    render_device_selector()
    render_training_controls()
    render_progress_display()

def start_training_process():
    """Handle training execution - complexity ~5"""
    setup_distributed_training()
    execute_training_loop()
    handle_training_completion()

def setup_distributed_training():
    """Configure distributed training - complexity ~4"""
    # Device configuration logic

def execute_training_loop():
    """Run training iterations - complexity ~5"""
    # Training loop logic
```

**Acceptance Criteria:**
- [ ] Each function has complexity ≤ 10
- [ ] Main function has complexity ≤ 5
- [ ] All existing functionality preserved
- [ ] Unit tests added for each extracted function
- [ ] Integration test verifies overall behavior

---

### Task 3.2: Refactor _check_secrets_usage() Function
**Priority:** 🟡 Medium
**Status:** ⚪ Not Started
**Effort:** 2-3 hours

**Problem:** Cyclomatic complexity of 14.

**Affected Files:**
- `tests/test_workflow_security.py:74`

**Refactoring Strategy:**
Extract secret pattern checking into separate validator functions.

**Proposed Structure:**
```python
def _check_secrets_usage(workflow_content):
    """Main coordinator"""
    suspicious_patterns = get_suspicious_patterns()
    violations = []
    for pattern in suspicious_patterns:
        violations.extend(check_pattern(workflow_content, pattern))
    return violations

def get_suspicious_patterns():
    """Return list of secret patterns"""
    return [...]

def check_pattern(content, pattern):
    """Check single pattern and return violations"""
    # Single pattern checking logic
```

**Acceptance Criteria:**
- [ ] Complexity reduced to ≤ 10
- [ ] Pattern checking is modular
- [ ] Tests still pass
- [ ] New patterns can be easily added

---

### Task 3.3: Refactor validate_config() Function
**Priority:** 🟡 Medium
**Status:** ⚪ Not Started
**Effort:** 3-4 hours

**Problem:** Cyclomatic complexity of 12.

**Affected Files:**
- `utils/config_validator.py:55`

**Refactoring Strategy:**
Split into separate validators per config section.

**Proposed Structure:**
```python
def validate_config(config: dict) -> list[str]:
    """Main validator coordinator"""
    errors = []
    errors.extend(validate_required_fields(config))
    errors.extend(validate_model_type(config))
    errors.extend(validate_numeric_ranges(config))
    errors.extend(validate_dataset_options(config))
    return errors

def validate_required_fields(config: dict) -> list[str]:
    """Validate presence and types of required fields"""
    # ...

def validate_model_type(config: dict) -> list[str]:
    """Validate model type is supported"""
    # ...

def validate_numeric_ranges(config: dict) -> list[str]:
    """Validate all numeric parameters"""
    # ...

def validate_dataset_options(config: dict) -> list[str]:
    """Validate dataset enhancement options"""
    # ...
```

**Acceptance Criteria:**
- [ ] Complexity reduced to ≤ 10
- [ ] Each validator is independently testable
- [ ] All existing validations preserved
- [ ] Unit tests for each validator function
- [ ] Easy to add new validation rules

---

## Category 4: Test Coverage 🟡

### Task 4.1: Add Tests for utils/peft_trainer.py
**Priority:** 🟡 Medium
**Status:** ⚪ Not Started
**Effort:** 4-6 hours

**Problem:** No test coverage for PEFT training utilities.

**Test Coverage Needed:**
- [ ] PEFTTrainer initialization
- [ ] LoRA configuration application
- [ ] Quantization setup (4-bit, 8-bit)
- [ ] Model parameter counting
- [ ] Training step execution
- [ ] Error handling for invalid configs

**Estimated Tests:** 8-10 test cases

---

### Task 4.2: Add Tests for utils/distributed_trainer.py
**Priority:** 🟡 Medium
**Status:** ⚪ Not Started
**Effort:** 4-6 hours

**Problem:** No test coverage for distributed training logic.

**Test Coverage Needed:**
- [ ] Device discovery
- [ ] Distributed strategy selection
- [ ] Multi-GPU coordination
- [ ] Rank assignment
- [ ] Communication setup
- [ ] Error handling for missing GPUs

**Estimated Tests:** 10-12 test cases

---

### Task 4.3: Add Tests for utils/model_inference.py
**Priority:** 🟡 Medium
**Status:** ⚪ Not Started
**Effort:** 3-4 hours

**Problem:** No test coverage for model inference.

**Test Coverage Needed:**
- [ ] Model loading
- [ ] Inference execution
- [ ] Batch processing
- [ ] Error handling
- [ ] Memory management

**Estimated Tests:** 6-8 test cases

---

### Task 4.4: Add Tests for utils/model_versioning.py
**Priority:** 🟢 Low
**Status:** ⚪ Not Started
**Effort:** 2-3 hours

**Test Coverage Needed:**
- [ ] Version creation
- [ ] Version comparison
- [ ] Version retrieval
- [ ] Metadata handling

**Estimated Tests:** 5-7 test cases

---

### Task 4.5: Add Tests for utils/visualization.py
**Priority:** 🟢 Low
**Status:** ⚪ Not Started
**Effort:** 2-3 hours

**Test Coverage Needed:**
- [ ] Metrics chart creation
- [ ] Chart data formatting
- [ ] Plotly configuration
- [ ] Error handling for invalid data

**Estimated Tests:** 4-6 test cases

---

### Task 4.6: Add Component Integration Tests
**Priority:** 🟡 Medium
**Status:** ⚪ Not Started
**Effort:** 6-8 hours

**Problem:** Component modules have limited test coverage.

**Components to Test:**
- [ ] `dataset_selector.py` - Dataset browsing and validation
- [ ] `parameter_config.py` - Parameter configuration UI
- [ ] `training_monitor.py` - Training monitoring UI
- [ ] `plugin_manager.py` - Plugin lifecycle management
- [ ] `tokenizer_builder.py` - Custom tokenizer creation
- [ ] `experiment_compare.py` - Experiment comparison

**Test Types:**
- Unit tests for individual functions
- Integration tests for component interactions
- UI state management tests

**Estimated Tests:** 25-30 test cases

---

## Category 5: Dependency Management 🟡

### Task 5.1: Consolidate Dependency Definitions
**Priority:** 🟡 Medium
**Status:** ⚪ Not Started
**Effort:** 1-2 hours

**Problem:** Mismatch between requirements.txt and pyproject.toml.

**Current State:**
- `requirements.txt` has 26 lines with older versions
- `pyproject.toml` has newer versions and more packages
- Creates confusion about which is source of truth

**Recommendation:** Use pyproject.toml as single source of truth.

**Implementation:**
1. Verify all dependencies are in pyproject.toml
2. Update versions to match requirements.txt where appropriate
3. Either delete requirements.txt or auto-generate it from pyproject.toml
4. Update documentation

**Option A: Delete requirements.txt**
```bash
rm requirements.txt
# Update all pip install commands to use: pip install -e .
```

**Option B: Auto-generate requirements.txt**
```bash
pip install pip-tools
pip-compile pyproject.toml -o requirements.txt
```

**Acceptance Criteria:**
- [ ] Single source of truth for dependencies
- [ ] All environments install correctly
- [ ] Documentation updated
- [ ] CI/CD updated if needed

---

### Task 5.2: Align Dependency Versions
**Priority:** 🟢 Low
**Status:** ⚪ Not Started
**Effort:** 1 hour

**Problem:** Version mismatches between requirements.txt and pyproject.toml.

**Examples:**
- streamlit: 1.37.0 (req) vs 1.42.0 (pyproject)
- transformers: 4.53.0 (req) vs 4.48.2 (pyproject)
- numpy: <2 (req) vs >=2.2.2 (pyproject)

**Acceptance Criteria:**
- [ ] Versions aligned across files
- [ ] Tests pass with aligned versions
- [ ] No breaking changes introduced

---

## Category 6: Logging & Monitoring 🟡

### Task 6.1: Standardize Logging Configuration
**Priority:** 🟡 Medium
**Status:** ⚪ Not Started
**Effort:** 2-3 hours

**Problem:** Logging configured inconsistently across files.

**Current Issues:**
- `core/server.py:33` - Custom basicConfig
- `core/logging.py` - Centralized config
- Multiple modules configure logging independently

**Solution:**
1. Use `core.logging.setup_logging()` everywhere
2. Remove duplicate basicConfig calls
3. Standardize logger creation pattern

**Files to Update:**
- `core/server.py`
- `utils/config_validator.py`
- `utils/plugins/registry.py`
- `components/training_monitor.py`
- All other files with `logging.basicConfig()`

**Proposed Pattern:**
```python
# At top of each module
from core.logging import get_logger
logger = get_logger(__name__)

# Instead of:
import logging
logging.basicConfig(...)
logger = logging.getLogger(__name__)
```

**Acceptance Criteria:**
- [ ] All modules use `core.logging`
- [ ] No duplicate logging configuration
- [ ] Consistent log format across application
- [ ] Structured logging works correctly

---

## Category 7: Type Hints & Static Analysis 🟢

### Task 7.1: Run Mypy and Fix Type Errors
**Priority:** 🟢 Low
**Status:** ⚪ Not Started
**Effort:** 4-8 hours (depends on errors found)

**Problem:** Type coverage is partial and inconsistent.

**Implementation:**
```bash
# Install mypy
pip install mypy

# Run initial analysis
mypy . --install-types --non-interactive

# Fix errors iteratively
mypy . --show-error-codes --pretty

# Add to CI
```

**Acceptance Criteria:**
- [ ] Mypy runs without errors in strict mode
- [ ] All public functions have type hints
- [ ] Return types specified
- [ ] Type stubs installed for third-party libraries

---

### Task 7.2: Add Missing Type Hints
**Priority:** 🟢 Low
**Status:** ⚪ Not Started
**Effort:** 4-6 hours

**Target Files:**
- Component modules
- Plugin system
- Utility functions

**Acceptance Criteria:**
- [ ] All function signatures have type hints
- [ ] Class attributes typed
- [ ] Return types specified
- [ ] Mypy passes

---

## Category 8: Documentation 🟢

### Task 8.1: Add Docstrings to Complex Functions
**Priority:** 🟢 Low
**Status:** ⚪ Not Started
**Effort:** 3-4 hours

**Target Functions:**
- `training_monitor()` in `components/training_monitor.py`
- `discover_tools()` in `utils/plugins/registry.py`
- Complex functions in `utils/distributed_trainer.py`
- Complex functions in `utils/peft_trainer.py`

**Format:** Google-style docstrings

**Example:**
```python
def complex_function(param1: str, param2: int) -> dict:
    """
    Brief description of what the function does.

    Longer description if needed, explaining the logic,
    algorithms, or important implementation details.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When param1 is empty
        RuntimeError: When operation fails

    Example:
        >>> result = complex_function("test", 42)
        >>> print(result["status"])
        "success"
    """
```

**Acceptance Criteria:**
- [ ] All functions with complexity > 5 have docstrings
- [ ] Docstrings follow Google style
- [ ] Args, returns, and raises documented
- [ ] Examples provided for complex functions

---

### Task 8.2: Create Plugin Development Guide
**Priority:** 🟢 Low
**Status:** ⚪ Not Started
**Effort:** 4-6 hours

**Problem:** Plugin system exists but lacks documentation for developers.

**Content Needed:**
- Plugin architecture overview
- Step-by-step plugin creation guide
- API reference for `AgentTool` base class
- Example plugins with explanations
- Best practices
- Testing plugins
- Debugging tips

**Deliverable:** `docs/PLUGIN_DEVELOPMENT.md`

**Acceptance Criteria:**
- [ ] Guide is complete and accurate
- [ ] Example plugin works as documented
- [ ] Developer can create plugin following guide
- [ ] Linked from main README

---

## Category 9: Configuration & Constants 🟢

### Task 9.1: Extract Magic Numbers to Constants
**Priority:** 🟢 Low
**Status:** ⚪ Not Started
**Effort:** 2-3 hours

**Problem:** Hardcoded values throughout codebase.

**Examples:**
```python
# core/server.py:99-102
"pool_size": 10,              # Magic number
"max_overflow": 20,           # Magic number
"pool_timeout": 30,           # Magic number
"pool_recycle": 1800,         # Magic number

# Retry logic
max_retries: int = 3          # Magic number
base_delay: float = 1.0       # Magic number
```

**Solution:**
Create `config/constants.py`:
```python
# Database configuration
DB_POOL_SIZE = 10
DB_MAX_OVERFLOW = 20
DB_POOL_TIMEOUT = 30  # seconds
DB_POOL_RECYCLE = 1800  # seconds

# Retry configuration
MAX_RETRIES = 3
RETRY_BASE_DELAY = 1.0  # seconds

# Training configuration
DEFAULT_BATCH_SIZE = 8
MAX_BATCH_SIZE = 128
DEFAULT_LEARNING_RATE = 5e-5
```

**Acceptance Criteria:**
- [ ] All magic numbers extracted to constants
- [ ] Constants file well-organized
- [ ] Constants used throughout codebase
- [ ] Documentation updated

---

## Category 10: CI/CD & Automation 🟢

### Task 10.1: Set Up Pre-commit Hooks
**Priority:** 🟢 Low
**Status:** ⚪ Not Started
**Effort:** 1-2 hours

**Problem:** Code style issues could be caught before commit.

**Implementation:**
Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

**Setup:**
```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files  # Initial run
```

**Acceptance Criteria:**
- [ ] Pre-commit hooks installed
- [ ] Hooks run on commit
- [ ] Documentation for setup in README
- [ ] CI verifies hooks pass

---

### Task 10.2: Add Coverage Reporting to CI
**Priority:** 🟡 Medium
**Status:** ⚪ Not Started
**Effort:** 1-2 hours

**Problem:** No automated coverage tracking.

**Implementation:**
Update `.github/workflows/ci.yml`:
```yaml
- name: Run tests with coverage
  run: |
    pytest --cov=. --cov-report=xml --cov-report=term-missing

- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
    fail_ci_if_error: true
```

**Acceptance Criteria:**
- [ ] Coverage runs in CI
- [ ] Results uploaded to Codecov
- [ ] Badge in README
- [ ] Coverage threshold enforced

---

### Task 10.3: Add Security Scanning to CI
**Priority:** 🟡 Medium
**Status:** ⚪ Not Started
**Effort:** 2-3 hours

**Problem:** No automated dependency vulnerability scanning.

**Implementation:**
Add to `.github/workflows/`:

**File: `security.yml`**
```yaml
name: Security Scan

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Safety check
        run: |
          pip install safety
          safety check

      - name: Run Bandit
        run: |
          pip install bandit
          bandit -r . -f json -o bandit-report.json
```

**Acceptance Criteria:**
- [ ] Security scan runs on every push
- [ ] Vulnerabilities reported
- [ ] Critical vulnerabilities block merge
- [ ] Reports accessible in CI logs

---

## Summary Statistics

**Total Tasks:** 31
- 🔴 High Priority: 8 tasks (~30-40 hours)
- 🟡 Medium Priority: 13 tasks (~35-50 hours)
- 🟢 Low Priority: 10 tasks (~25-35 hours)

**Estimated Total Effort:** 90-125 hours

**Recommended Iteration Plan:**

**Sprint 1 (High Priority - Week 1-2):**
- Fix test infrastructure
- Fix code style issues
- Basic refactoring of high-complexity functions

**Sprint 2 (Medium Priority - Week 3-4):**
- Add missing test coverage
- Standardize logging
- Set up coverage reporting
- Dependency consolidation

**Sprint 3 (Low Priority - Week 5-6):**
- Type hints and mypy
- Documentation
- Extract constants
- CI/CD enhancements

---

**Last Updated:** 2025-12-15
**Document Version:** 1.0
