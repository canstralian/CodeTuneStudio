# Codex Environment Variables Template

Configure these in **Environment → Variables** in your Codex Cloud settings.

## Core Python Environment

```bash
# Prevent Python from buffering stdout/stderr (keeps logs readable)
PYTHONUNBUFFERED=1

# Prevent Python from writing .pyc files
PYTHONDONTWRITEBYTECODE=1

# Add workspace to Python path
PYTHONPATH=/workspace

# Disable pip version check warnings
PIP_DISABLE_PIP_VERSION_CHECK=1
```

## CI/CD Hints

```bash
# Signal CI environment to tools (disables interactive prompts)
CI=true

# Custom environment marker for conditional logic
CODEX_ENV=cloud
```

## Application Configuration

```bash
# Application server binding
HOST=0.0.0.0
PORT=7860

# Run in headless mode (no browser auto-open in cloud)
SERVER_HEADLESS=true

# Logging level
LOG_LEVEL=INFO
```

## Database Configuration

```bash
# PostgreSQL connection (recommended for multi-session use)
DATABASE_URL=postgresql://user:password@localhost:5432/codetune_studio

# Alternative: SQLite (single-user, simpler setup)
# DATABASE_URL=sqlite:///database.db

# Enable SQL query debugging (dev only)
SQL_DEBUG=false
```

## ML/Training Optimizations

```bash
# Force CPU-only PyTorch (reduces memory footprint in Codex)
CUDA_VISIBLE_DEVICES=""

# Disable Hugging Face telemetry
HF_HUB_DISABLE_TELEMETRY=1

# Use offline mode for transformers (if models pre-cached)
# TRANSFORMERS_OFFLINE=1

# Accelerate config for CPU-only training
ACCELERATE_USE_CPU=1
```

## Feature Flags

```bash
# Disable experimental features in cloud environments
ENABLE_EXPERIMENTAL_FEATURES=false

# Disable telemetry
ENABLE_TELEMETRY=false
```

## Tool Configuration

```bash
# Ruff configuration
RUFF_CACHE_DIR=/tmp/ruff-cache

# Pytest configuration
PYTEST_CACHE_DIR=/tmp/pytest-cache
```

---

## Usage Notes

### Variable Precedence
1. Secrets (highest priority, ephemeral)
2. Environment Variables (persistent across sessions)
3. `.env` file (local fallback, not recommended in Codex)

### Best Practices
- **Never** put secrets in environment variables (use Secrets instead)
- Set `PYTHONUNBUFFERED=1` always (critical for readable logs)
- Use `CI=true` to disable interactive prompts
- Keep `DATABASE_URL` deterministic across sessions

### Conditional Logic Example
```python
import os

if os.getenv("CODEX_ENV") == "cloud":
    # Cloud-specific behavior (e.g., use CPU-only models)
    device = "cpu"
else:
    # Local development (can use GPU if available)
    device = "cuda" if torch.cuda.is_available() else "cpu"
```

---

## Quick Reference: Required Variables

| Variable | Value | Why |
|----------|-------|-----|
| `PYTHONUNBUFFERED` | `1` | Readable logs |
| `PYTHONDONTWRITEBYTECODE` | `1` | Clean filesystem |
| `CI` | `true` | Non-interactive mode |
| `SERVER_HEADLESS` | `true` | Cloud-compatible |
| `DATABASE_URL` | `postgresql://...` or `sqlite:///...` | Persistent storage |

**Copy-paste starter block:**
```bash
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
PYTHONPATH=/workspace
PIP_DISABLE_PIP_VERSION_CHECK=1
CI=true
CODEX_ENV=cloud
SERVER_HEADLESS=true
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///database.db
CUDA_VISIBLE_DEVICES=""
HF_HUB_DISABLE_TELEMETRY=1
```
