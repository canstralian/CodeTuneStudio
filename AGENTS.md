# Agent Instructions for CodeTuneStudio

## Environment Contract

### Setup Assumptions
- **Python dependencies** are preinstalled via `codex/setup.sh`
- **Database** is initialized (PostgreSQL or SQLite fallback)
- **Internet access** is restricted to declared allowlist (see `codex/templates/INTERNET_ACCESS_POLICY.md`)
- **Environment variables** are configured (see `codex/templates/ENVIRONMENT_VARIABLES.md`)
- **PyTorch** is configured for CPU-only execution
- **Hugging Face CLI** is authenticated (if `HF_TOKEN` secret was provided)

### Do NOT During Runtime
- Install new Python packages (all dependencies are pre-installed)
- Access external networks beyond allowed domains
- Modify system-level configuration
- Run GPU-dependent code (environment is CPU-only)

---

## Project Architecture

CodeTuneStudio is a **Streamlit/Flask hybrid application** for ML model fine-tuning with:
- **Frontend:** Streamlit UI (port 7860)
- **Backend:** Flask + SQLAlchemy for database operations
- **ML Stack:** PyTorch, Transformers, PEFT/LoRA, Accelerate
- **Plugin System:** Dynamic tool discovery from `plugins/` directory

**Key files:**
- `app.py`: Main entry point
- `components/`: Modular UI components
- `utils/`: Training infrastructure, database, visualization
- `plugins/`: Extensible tool plugins
- `models/`: SQLAlchemy database models
- `tests/`: Unit and integration tests

---

## Preferred Commands

### Running the Application
```bash
# Start Streamlit UI (recommended)
streamlit run app.py

# Alternative: Direct Python execution
python app.py
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=term-missing

# Run specific test file
pytest tests/test_database.py

# Run tests matching pattern
pytest -k "test_training"
```

### Code Quality

#### Linting
```bash
# Ruff (preferred - fast, comprehensive)
ruff check .

# Fix auto-fixable issues
ruff check --fix .

# Flake8 (legacy, still in CI)
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
```

#### Formatting
```bash
# Ruff format (preferred)
ruff format .

# Check formatting without changes
ruff format --check .

# Black (alternative)
black .
```

#### Type Checking
```bash
# MyPy (if enabled in dev dependencies)
mypy core/ utils/ components/
```

### Database Operations
```bash
# Initialize database
python app.py  # Auto-initializes on first run

# Run migrations
flask db upgrade

# Create new migration
flask db migrate -m "description"

# Check database status
python db_check.py
```

### Plugin Management
```bash
# List available plugins
python -c "from utils.plugins.registry import PluginRegistry; r = PluginRegistry(); r.discover_tools('plugins'); print([t.metadata.name for t in r.list_tools()])"

# Validate plugin
python -c "from plugins.code_analyzer import CodeAnalyzer; print(CodeAnalyzer().metadata)"
```

---

## Constraints

### 🚫 Never
1. **Install dependencies at runtime**
   ```bash
   # ❌ WRONG
   pip install new-package

   # ✅ CORRECT
   # Add to requirements.txt or pyproject.toml
   # Re-run setup script
   ```

2. **Access disallowed networks**
   ```python
   # ❌ WRONG
   requests.get("https://random-api.com")

   # ✅ CORRECT
   # Use only allowed domains (see INTERNET_ACCESS_POLICY.md)
   # Or use cached data
   ```

3. **Run GPU code**
   ```python
   # ❌ WRONG
   model.to("cuda")

   # ✅ CORRECT
   device = "cpu"  # Environment is CPU-only
   model.to(device)
   ```

4. **Modify environment**
   ```bash
   # ❌ WRONG
   export PYTHONPATH=/new/path
   apt-get install new-package

   # ✅ CORRECT
   # Environment is immutable after setup
   # Request changes to setup script
   ```

### ✅ Always
1. **Check test pass before committing**
   ```bash
   pytest && git commit
   ```

2. **Lint before pushing**
   ```bash
   ruff check . && ruff format .
   ```

3. **Use CPU-compatible code**
   ```python
   # Detect device safely
   import torch
   device = "cpu"  # Explicit in Codex
   ```

4. **Handle database gracefully**
   ```python
   # Database may be SQLite or PostgreSQL
   # Code must work with both
   ```

---

## Common Tasks

### Adding a New Feature
```bash
# 1. Create feature branch (if not in Codex)
git checkout -b feature/new-feature

# 2. Write code
# ... edit files ...

# 3. Write tests
# ... create tests/test_new_feature.py ...

# 4. Run tests
pytest tests/test_new_feature.py

# 5. Lint and format
ruff check --fix .
ruff format .

# 6. Commit
git add .
git commit -m "feat: add new feature"
```

### Fixing a Bug
```bash
# 1. Write failing test that reproduces bug
# ... edit tests/test_bugfix.py ...
pytest tests/test_bugfix.py  # Should fail

# 2. Fix bug
# ... edit relevant files ...

# 3. Verify test passes
pytest tests/test_bugfix.py  # Should pass

# 4. Run full test suite
pytest

# 5. Lint and commit
ruff check --fix . && ruff format .
git commit -am "fix: resolve issue with X"
```

### Adding a Plugin
```bash
# 1. Create plugin file in plugins/
cat > plugins/my_tool.py <<EOF
from utils.plugins.base import AgentTool, ToolMetadata

class MyTool(AgentTool):
    def __init__(self):
        self.metadata = ToolMetadata(
            name="my_tool",
            description="Does something useful",
            version="1.0.0"
        )

    def validate_inputs(self, inputs):
        return "required_key" in inputs

    def execute(self, inputs):
        return {"result": "success"}
EOF

# 2. Test plugin loads
python -c "from plugins.my_tool import MyTool; print(MyTool().metadata)"

# 3. Write tests
cat > tests/test_my_tool.py <<EOF
from plugins.my_tool import MyTool

def test_my_tool():
    tool = MyTool()
    result = tool.execute({"required_key": "value"})
    assert result["result"] == "success"
EOF

# 4. Run tests
pytest tests/test_my_tool.py

# 5. Commit
git add plugins/my_tool.py tests/test_my_tool.py
git commit -m "feat: add my_tool plugin"
```

### Debugging Database Issues
```bash
# Check database connection
python db_check.py

# Inspect database schema
python -c "from utils.database import db, TrainingConfig; print(TrainingConfig.__table__.columns.keys())"

# Run migrations
flask db upgrade

# Reset database (DESTRUCTIVE)
rm -f database.db  # If using SQLite
flask db upgrade
```

---

## Code Style Compliance

### Line Length
- **Maximum:** 88 characters (Black/Ruff default)

### Imports
- **Order:** stdlib → third-party → first-party
- **Style:** One import per line (unless `from X import a, b` is clearer)
- **Sorting:** Ruff automatically handles this

Example:
```python
import os
import sys

import torch
from flask import Flask
from transformers import AutoModel

from core.config import Config
from utils.database import db
```

### Type Hints
```python
# Prefer type hints for function signatures
def train_model(
    model_name: str,
    dataset: str,
    epochs: int = 3
) -> dict[str, float]:
    ...
```

### Logging
```python
import logging

logger = logging.getLogger(__name__)

# Use appropriate levels
logger.debug("Detailed info for debugging")
logger.info("High-level status")
logger.warning("Unexpected but handled")
logger.error("Error occurred", exc_info=True)
```

---

## CI/CD Integration

### Pre-commit Checks (Local)
```bash
# Install pre-commit hooks (if not in Codex)
pre-commit install

# Run manually
pre-commit run --all-files
```

### CI Pipeline (GitHub Actions)
Runs on push/PR:
1. **Lint:** `flake8` and `ruff check`
2. **Test:** `pytest` with coverage
3. **Type check:** `mypy` (if configured)

**Your responsibility:**
- Ensure tests pass locally before pushing
- Fix linting errors before committing
- Maintain test coverage

---

## Troubleshooting

### "Module not found" error
**Cause:** Dependency not installed
**Fix:** Check `requirements.txt` or `pyproject.toml`, re-run setup script

### "Database locked" error
**Cause:** SQLite doesn't support concurrent writes
**Fix:** Use PostgreSQL for multi-session work (set `DATABASE_URL`)

### "CUDA not available" warnings
**Cause:** Code assumes GPU
**Fix:** Ensure code uses `device = "cpu"`

### "Connection refused" on port 7860
**Cause:** Streamlit not binding to correct host
**Fix:** Check `HOST=0.0.0.0` in environment variables

### "Import error" for plugins
**Cause:** Plugin not following `AgentTool` interface
**Fix:** Verify plugin subclasses `AgentTool` and implements required methods

---

## Environment-Specific Behavior

### Detecting Codex Environment
```python
import os

if os.getenv("CODEX_ENV") == "cloud":
    # Cloud-specific behavior
    device = "cpu"
    enable_telemetry = False
else:
    # Local development
    device = "cuda" if torch.cuda.is_available() else "cpu"
    enable_telemetry = True
```

### Conditional Imports
```python
# Import heavy dependencies only when needed
if require_gpu:
    import bitsandbytes  # Skip in CPU-only environments
```

### Feature Flags
```python
import os

ENABLE_EXPERIMENTAL = os.getenv("ENABLE_EXPERIMENTAL_FEATURES", "false").lower() == "true"

if ENABLE_EXPERIMENTAL:
    from experimental.new_feature import NewFeature
```

---

## Quick Reference Card

| Task | Command |
|------|---------|
| **Run app** | `streamlit run app.py` |
| **Run tests** | `pytest` |
| **Lint** | `ruff check .` |
| **Format** | `ruff format .` |
| **Fix linting** | `ruff check --fix .` |
| **Type check** | `mypy core/ utils/` |
| **DB upgrade** | `flask db upgrade` |
| **Coverage** | `pytest --cov=.` |
| **Single test** | `pytest tests/test_file.py::test_name` |
| **Watch tests** | `pytest-watch` (if installed) |

---

## Summary

**This environment is:**
- ✅ Deterministic (dependencies pre-installed)
- ✅ Isolated (network allowlist enforced)
- ✅ CPU-only (no GPU assumptions)
- ✅ Auditable (all changes via git)

**Your job as an agent:**
- Use pre-installed tools
- Follow code style (Ruff/Black)
- Write tests for new code
- Commit working, tested, linted code
- Never improvise with external dependencies

**When in doubt:**
1. Check this file
2. Review `CLAUDE.md` for project details
3. Inspect existing code for patterns
4. Ask for clarification before making assumptions
