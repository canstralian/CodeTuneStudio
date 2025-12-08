# Quick Start: Code Quality Refactoring

This guide provides a quick overview of the code quality issues and how to start addressing them.

## 📊 Current Status

| Category | Issues | Priority |
|----------|--------|----------|
| **Tests** | Broken (14 tests) | 🔥 P0 |
| **Security** | 3 real issues | 🔥 P0 |
| **Type Hints** | 126 missing | 🚨 P1 |
| **Logging** | 30+ anti-patterns | 🚨 P1 |
| **Style** | 606 total warnings | ⚠️ P1-P2 |

## 🚀 Quick Wins (2-4 hours each)

### 1. Fix Test Infrastructure (Critical)

**Problem:** Tests can't import dependencies
```bash
# Error: ModuleNotFoundError: anthropic, streamlit, flask...
```

**Fix:**
```bash
# Add tests/__init__.py
touch tests/__init__.py

# Update CI to install dependencies
# In .github/workflows/ci.yml, ensure:
pip install -e ".[dev]"
```

**Impact:** Enables test validation, blocks all other work

---

### 2. Security: Add Request Timeouts

**Problem:** Hanging connections possible
```python
# scripts/update_checklist.py:12
response = requests.get(url)  # ❌ No timeout
```

**Fix:**
```python
REQUEST_TIMEOUT = 30  # seconds

response = requests.get(url, timeout=REQUEST_TIMEOUT)  # ✅
```

**Impact:** Prevents DoS, security best practice

---

### 3. Security: Pin Model Versions

**Problem:** Models could change unexpectedly
```python
model = AutoModel.from_pretrained("model-name")  # ❌ Unpinned
```

**Fix:**
```python
model = AutoModel.from_pretrained(
    "model-name",
    revision="abc123def456"  # ✅ Specific commit
)
```

**Impact:** Reproducibility, security

---

### 4. Fix MD5 Security Warning (Non-Critical)

**Problem:** MD5 used for versioning (not security)
```python
# utils/model_versioning.py:29
config_hash = hashlib.md5(data).hexdigest()  # ⚠️ Not for security
```

**Fix Option 1 (Suppress warning):**
```python
config_hash = hashlib.md5(
    data,
    usedforsecurity=False  # ✅ Explicit non-security use
).hexdigest()
```

**Fix Option 2 (Use better hash):**
```python
config_hash = hashlib.sha256(data).hexdigest()[:8]  # ✅ Better practice
```

**Impact:** Removes security warning, best practice

---

## 🔧 Automated Fixes (Run Once)

Many issues can be auto-fixed:

```bash
# Format code with Black
black .

# Fix import sorting
ruff check . --select I --fix

# Fix safe issues with Ruff
ruff check . --fix --unsafe-fixes

# Remove trailing whitespace (pre-commit)
pre-commit run trailing-whitespace --all-files
```

**Impact:** Fixes ~100-200 issues automatically

---

## 📝 Manual Fixes by Priority

### P0: Critical (Do First)

1. ✅ **Fix test imports** → Enable test validation
2. ✅ **Add request timeouts** → Security fix
3. ✅ **Pin model versions** → Reproducibility

### P1: High Priority (Do Next)

4. **Add type annotations to core/server.py** (~30 functions)
   - Start with public API functions
   - Use mypy to verify

5. **Fix logging patterns** (30+ instances)
   - Replace f-strings with % formatting
   - Use logger.exception() for errors

6. **Fix line lengths** (34 instances)
   - Run Black formatter
   - Manual fixes for complex cases

### P2: Medium Priority (After P1)

7. **Modernize path operations** (15+ instances)
   - Replace os.path with pathlib
   - Use Path objects consistently

8. **Improve test quality**
   - Add type annotations to tests
   - Make exception assertions specific
   - Remove unused mocks

9. **Clean up imports**
   - Remove unused imports
   - Sort imports
   - Add __init__.py files

---

## 🎯 One-Week Sprint

Focus on high-impact items:

**Days 1-2: Critical Fixes**
- [ ] Fix test infrastructure
- [ ] Add security fixes (timeouts, model pinning)
- [ ] Verify tests pass

**Days 3-4: Type Annotations**
- [ ] core/server.py
- [ ] core/logging.py
- [ ] Plugin interfaces

**Day 5: Logging & Style**
- [ ] Fix logging patterns
- [ ] Run Black formatter
- [ ] Fix line lengths

**Result:** 
- Tests working ✅
- Security issues resolved ✅
- ~200 fewer warnings ✅
- 50%+ type coverage ✅

---

## 🛠️ Daily Workflow

1. **Pick one file/module**
2. **Run analysis on it:**
   ```bash
   ruff check path/to/file.py
   mypy path/to/file.py
   ```
3. **Fix issues (high → low priority)**
4. **Run tests:**
   ```bash
   pytest tests/test_related.py
   ```
5. **Commit:**
   ```bash
   git commit -m "refactor(file): fix type hints and logging"
   ```

---

## 📚 Resources

- **[CODE_QUALITY_REPORT.md](CODE_QUALITY_REPORT.md)** - Full analysis
- **[docs/REFACTORING_TASKS.md](docs/REFACTORING_TASKS.md)** - Detailed tasks
- **[docs/CONTRIBUTING_CODE_QUALITY.md](docs/CONTRIBUTING_CODE_QUALITY.md)** - Guidelines

---

## 💡 Tips

1. **Use automated tools first** - Black, Ruff, isort
2. **One file at a time** - Easier to review, less conflict
3. **Test after each change** - Catch regressions early
4. **Document why** - Comments for non-obvious fixes
5. **Ask for help** - Create issues for unclear cases

---

## ✅ Definition of Done

A refactoring task is complete when:

- [ ] Changes made and tested locally
- [ ] Tests pass (pytest)
- [ ] Linting passes (ruff, flake8)
- [ ] Type checking passes (mypy)
- [ ] Documentation updated (if needed)
- [ ] PR created and reviewed
- [ ] CI passes

---

**Ready to start?** Pick a task from the Quick Wins section above!

**Questions?** See [REFACTORING_TASKS.md](docs/REFACTORING_TASKS.md) or create an issue.

**Progress Tracking:** Update [CODE_QUALITY_REPORT.md](CODE_QUALITY_REPORT.md) weekly.
