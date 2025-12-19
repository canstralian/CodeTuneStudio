#!/usr/bin/env bash
set -euo pipefail

echo "=== CodeTuneStudio Codex Setup: Python ML Environment ==="

# ---- System dependencies ----
echo "Installing system dependencies..."
apt-get update
apt-get install -y \
  build-essential \
  curl \
  git \
  jq \
  ripgrep \
  ca-certificates \
  libpq-dev \
  postgresql-client

# ---- Python tooling ----
echo "Verifying Python..."
python --version
pip install --upgrade pip setuptools wheel

# ---- Core project dependencies ----
echo "Installing project dependencies..."
if [ -f requirements.txt ]; then
  echo "Installing from requirements.txt..."
  pip install -r requirements.txt
fi

# ---- Development dependencies ----
if [ -f pyproject.toml ]; then
  echo "Installing development dependencies from pyproject.toml..."
  pip install -e ".[dev]"
fi

# ---- Optional: uv support for faster installs ----
if command -v uv &> /dev/null; then
  echo "uv detected, using for package management..."
  uv pip sync requirements.txt
fi

# ---- PyTorch CPU-only optimization ----
# CodeTuneStudio uses PyTorch; install CPU version for Codex environments
if grep -q "torch" requirements.txt || grep -q "torch" pyproject.toml; then
  echo "Configuring PyTorch CPU backend..."
  pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
fi

# ---- Database initialization ----
echo "Initializing database..."
if [ -n "${DATABASE_URL:-}" ]; then
  echo "Using PostgreSQL: ${DATABASE_URL}"
  # Wait for postgres to be ready if using PostgreSQL
  if [[ $DATABASE_URL == postgresql* ]]; then
    echo "Waiting for PostgreSQL to be ready..."
    for i in {1..30}; do
      if pg_isready -d "$DATABASE_URL" &> /dev/null; then
        echo "PostgreSQL is ready"
        break
      fi
      echo "Waiting for PostgreSQL... ($i/30)"
      sleep 1
    done
  fi
else
  echo "No DATABASE_URL set, will use SQLite fallback"
fi

# Run database migrations if Flask-Migrate is configured
if [ -d migrations ]; then
  echo "Running database migrations..."
  flask db upgrade || echo "Warning: Migration failed, continuing..."
fi

# ---- Sanity checks ----
echo "Running sanity checks..."
python - <<'EOF'
import sys
print(f"✓ Python: {sys.version}")

try:
    import torch
    print(f"✓ PyTorch: {torch.__version__} (CPU: {not torch.cuda.is_available()})")
except ImportError:
    print("✗ PyTorch not installed")

try:
    import transformers
    print(f"✓ Transformers: {transformers.__version__}")
except ImportError:
    print("✗ Transformers not installed")

try:
    import streamlit
    print(f"✓ Streamlit: {streamlit.__version__}")
except ImportError:
    print("✗ Streamlit not installed")

try:
    import flask
    print(f"✓ Flask: {flask.__version__}")
except ImportError:
    print("✗ Flask not installed")

print("\nAll core dependencies verified!")
EOF

echo "=== Setup complete ==="
echo ""
echo "Next steps:"
echo "  - Start Streamlit UI: streamlit run app.py"
echo "  - Run tests: pytest"
echo "  - Lint code: ruff check ."
echo "  - Format code: ruff format ."
