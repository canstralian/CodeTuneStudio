# CodeTuneStudio Python Rule Set

This document defines the minimal, strict rule set that CodeTuneStudio applies to Python code.

## Philosophy

CodeTuneStudio enforces rules that prevent:
1. **Security vulnerabilities** - Code that enables attacks
2. **Correctness bugs** - Code that will fail at runtime
3. **Maintainability issues** - Code that creates technical debt

It does NOT enforce:
- Style preferences (use Black/Ruff for that)
- Subjective "best practices"
- Micro-optimizations
- Over-engineering patterns

**Principle: Flag real problems, not stylistic choices.**

---

## Rule Categories

### 1. Security Rules (Blocking)

These rules prevent security vulnerabilities. Violations always block CI.

#### S01: SQL Injection Prevention

**What:** Detects SQL queries constructed with string formatting

**Pattern:**
```python
# ❌ VIOLATION
query = f"SELECT * FROM users WHERE id = {user_id}"
query = "SELECT * FROM users WHERE name = '%s'" % username

# ✅ CORRECT
query = "SELECT * FROM users WHERE id = ?"
cursor.execute(query, (user_id,))
```

**Why:** String formatting allows attackers to inject arbitrary SQL commands, leading to data theft, modification, or destruction.

**Fix:** Use parameterized queries or an ORM.

---

#### S02: Arbitrary Code Execution

**What:** Detects use of `eval()` or `exec()` with untrusted input

**Pattern:**
```python
# ❌ VIOLATION
result = eval(user_formula)
exec(user_code)

# ✅ CORRECT
# Use ast.literal_eval() for safe evaluation of literals
from ast import literal_eval
result = literal_eval(user_data)

# Or use a domain-specific parser
```

**Why:** `eval()`/`exec()` execute arbitrary Python code, allowing attackers to run malicious commands, access files, or compromise the system.

**Fix:** Use safe alternatives like `ast.literal_eval()`, JSON parsing, or domain-specific expression evaluators.

---

#### S03: Cryptographically Weak Random

**What:** Detects `random` module used for security purposes

**Pattern:**
```python
# ❌ VIOLATION
import random
token = ''.join(random.choices(string.ascii_letters, k=32))

# ✅ CORRECT
import secrets
token = secrets.token_urlsafe(32)
```

**Why:** The `random` module is not cryptographically secure and produces predictable values, allowing attackers to guess tokens, session IDs, or passwords.

**Fix:** Use `secrets` module for security-sensitive random values.

---

#### S04: Hardcoded Secrets

**What:** Detects passwords, API keys, or tokens in source code

**Pattern:**
```python
# ❌ VIOLATION
API_KEY = "sk-1234567890abcdef"
password = "admin123"

# ✅ CORRECT
import os
API_KEY = os.environ['API_KEY']
password = os.environ.get('DB_PASSWORD')
```

**Why:** Hardcoded secrets are exposed in version control, logs, and error messages, allowing unauthorized access.

**Fix:** Use environment variables, secret management systems, or configuration files (excluded from git).

---

### 2. Correctness Rules (Blocking)

These rules prevent runtime errors and logic bugs. Violations always block CI.

#### C01: Missing Input Validation

**What:** Detects dictionary access without checking key existence

**Pattern:**
```python
# ❌ VIOLATION
def process(data):
    user_id = data['user_id']  # KeyError if missing
    return user_id

# ✅ CORRECT
def process(data):
    if 'user_id' not in data:
        raise ValueError("Missing required field: user_id")
    return data['user_id']

# OR
def process(data):
    return data.get('user_id')  # Returns None if missing
```

**Why:** Accessing non-existent dictionary keys raises `KeyError`, causing crashes on unexpected input.

**Fix:** Check key existence with `in`, use `.get()`, or validate input schema.

---

#### C02: Bare Except Clause

**What:** Detects `except:` without specifying exception type

**Pattern:**
```python
# ❌ VIOLATION
try:
    risky_operation()
except:  # Catches EVERYTHING
    pass

# ✅ CORRECT
try:
    risky_operation()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
except ConnectionError as e:
    logger.error(f"Connection failed: {e}")
```

**Why:** Bare `except:` catches `SystemExit`, `KeyboardInterrupt`, and other critical exceptions, masking bugs and preventing clean shutdown.

**Fix:** Specify exact exception types you expect and can handle.

---

#### C03: Mutable Default Argument

**What:** Detects mutable objects (list, dict, set) as default arguments

**Pattern:**
```python
# ❌ VIOLATION
def add_item(item, items=[]):  # Default persists across calls!
    items.append(item)
    return items

# ✅ CORRECT
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

**Why:** Default arguments are evaluated once at function definition, so mutable defaults are shared across all calls, causing state bugs.

**Fix:** Use `None` as default and create new object inside function.

---

#### C04: Resource Leak

**What:** Detects file operations without context manager

**Pattern:**
```python
# ❌ VIOLATION
f = open('data.txt')
content = f.read()
# File handle not guaranteed to close

# ✅ CORRECT
with open('data.txt') as f:
    content = f.read()
# File automatically closed, even on exception
```

**Why:** Without context managers, files may not close on exceptions, leading to resource leaks, data corruption, or "too many open files" errors.

**Fix:** Always use `with` statement for file operations.

---

#### C05: TOCTOU Race Condition

**What:** Detects time-of-check to time-of-use race conditions

**Pattern:**
```python
# ❌ VIOLATION
if not os.path.exists(filename):
    # File could be created here by another process
    with open(filename, 'w') as f:
        f.write(data)

# ✅ CORRECT
try:
    with open(filename, 'x') as f:  # 'x' mode fails if exists
        f.write(data)
except FileExistsError:
    pass  # Or handle appropriately
```

**Why:** File state can change between the check and the operation, causing race conditions in concurrent environments.

**Fix:** Use atomic operations or appropriate file modes (`'x'` for exclusive creation).

---

### 3. Maintainability Rules (Advisory)

These rules improve code quality but don't cause immediate failures. Can be overridden with justification.

#### M01: Hardcoded Paths

**What:** Detects hardcoded filesystem paths

**Pattern:**
```python
# ❌ VIOLATION
config_path = "/tmp/config.json"
data_dir = "C:\\Users\\Admin\\data"

# ✅ CORRECT
import tempfile
import os

config_path = os.path.join(tempfile.gettempdir(), 'config.json')
data_dir = os.environ.get('DATA_DIR', './data')
```

**Why:** Hardcoded paths break across operating systems, deployment environments, and user configurations.

**Fix:** Use environment variables, `tempfile` module, or OS-agnostic path construction.

---

#### M02: Overly Broad Exception Handling

**What:** Detects catching `Exception` without specific handling

**Pattern:**
```python
# ⚠️ ADVISORY
try:
    operation()
except Exception as e:  # Too broad
    logger.error(e)

# ✅ BETTER
try:
    operation()
except (ValueError, TypeError) as e:
    logger.error(f"Invalid input: {e}")
except ConnectionError as e:
    logger.error(f"Network error: {e}")
    raise  # Re-raise if can't handle
```

**Why:** Broad exception catching may hide unexpected errors and make debugging difficult.

**Fix:** Catch specific exceptions you know how to handle. If unsure, let it propagate.

---

## Refusal Conditions

CodeTuneStudio will **explicitly refuse** to suggest changes when:

### R01: Unknown Schema

**Condition:** Data structure processing without documented schema

**Indicators:**
- Generic `dict`/`list` processing without type hints
- No docstring describing expected structure
- Dynamic key access patterns

**Example:**
```python
def process_config(config_dict):
    """Process configuration."""  # What configuration? What keys?
    result = {}
    for key in config_dict:  # What keys are valid? What types?
        result[key] = config_dict[key]
    return result
```

**Why refuse:** Without knowing the expected schema, any refactoring could break downstream code or violate invariants.

**To enable analysis:** Add type hints and docstring specifying expected keys, types, and constraints.

---

### R02: Unclear Side Effects

**Condition:** Function has undocumented side effects

**Indicators:**
- Modifies mutable arguments
- Updates global or class state
- Performs I/O operations without clear contract

**Example:**
```python
def initialize(self, config):
    """Initialize processor."""  # What does initialization do?
    self._state = config.copy()  # What state? What are the implications?
    self._initialized = True  # What happens if called twice?
```

**Why refuse:** Changes could break assumptions about state management, idempotency, or resource handling.

**To enable analysis:** Document side effects, state transitions, and idempotency guarantees.

---

### R03: Missing Invariants

**Condition:** Validation or state management without documented requirements

**Indicators:**
- Validation logic without documented requirements
- State management without lifecycle documentation
- Complex business logic without specification

**Example:**
```python
def reconcile_records(local, remote, strategy='merge'):
    """Reconcile records."""
    # How do we identify records? What defines equality?
    # What are valid strategies? What are conflict resolution rules?
    pass
```

**Why refuse:** Cannot suggest improvements without understanding correctness requirements.

**To enable analysis:** Document identity/equality definitions, valid values, and business rules.

---

### R04: Ambiguous Dependencies

**Condition:** Operations with unclear order dependencies

**Indicators:**
- Order-sensitive operations without documentation
- Initialization requirements not specified
- Concurrency constraints unclear

**Example:**
```python
class DataProcessor:
    def initialize(self, config): pass
    def process(self, item): pass  # Must initialize first? Can't tell
    def finalize(self): pass  # When to call? What does it do?
```

**Why refuse:** Refactoring could break required operation ordering or concurrency assumptions.

**To enable analysis:** Document lifecycle, method ordering requirements, and concurrency safety.

---

## Confidence Threshold

CodeTuneStudio requires **85% confidence** before suggesting changes.

If confidence < 85%:
- Explicitly refuse
- Explain missing context
- Suggest what documentation would enable analysis

**This threshold prevents:**
- Speculative "improvements" that break behavior
- Silent logic changes
- "Looks cleaner but behaves differently" bugs

---

## Summary Table

| Category | Rule | Severity | Action |
|----------|------|----------|--------|
| Security | SQL Injection | Blocking | Fail CI |
| Security | Arbitrary Code Execution | Blocking | Fail CI |
| Security | Weak Random | Blocking | Fail CI |
| Security | Hardcoded Secrets | Blocking | Fail CI |
| Correctness | Missing Validation | Blocking | Fail CI |
| Correctness | Bare Except | Blocking | Fail CI |
| Correctness | Mutable Default | Blocking | Fail CI |
| Correctness | Resource Leak | Blocking | Fail CI |
| Correctness | TOCTOU Race | Blocking | Fail CI |
| Maintainability | Hardcoded Paths | Advisory | Warn |
| Maintainability | Broad Exception | Advisory | Warn |
| Refusal | Unknown Schema | Refusal | Fail CI + Explain |
| Refusal | Unclear Side Effects | Refusal | Fail CI + Explain |
| Refusal | Missing Invariants | Refusal | Fail CI + Explain |
| Refusal | Ambiguous Dependencies | Refusal | Fail CI + Explain |

---

## Exit Codes

- `0`: Clean - No violations, no refusals
- `1`: Violations found OR refusals issued (both block CI)
- `2`: Analysis error (internal CodeTuneStudio failure)

---

## What CodeTuneStudio Does NOT Do

❌ Style formatting (use Black/Ruff)
❌ Import sorting (use isort)
❌ Type checking (use mypy)
❌ Complexity metrics (use radon)
❌ Auto-refactoring without human review
❌ Speculative improvements
❌ "Clever" optimizations

✅ Prevents security vulnerabilities
✅ Catches runtime errors before they happen
✅ Refuses when context is insufficient
✅ Explains reasoning clearly
✅ Requires human judgment for all changes

---

## Validation

To validate these rules, run CodeTuneStudio against the canonical test PR:

```bash
# This SHOULD fail CI with:
# - 10 violations from violation_examples.py
# - 1 refusal from ambiguous_refactoring.py

python -m codetunestudio analyze --config .codetunestudio.yml
```

If it passes, something is wrong with CodeTuneStudio.

---

*This rule set is intentionally minimal. Each rule must earn its place by preventing real problems, not satisfying stylistic preferences.*
