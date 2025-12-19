# Codex Secrets Template

Configure these in **Environment → Secrets** in your Codex Cloud settings.

## 🔒 Security Model

**Critical properties of Codex Secrets:**
- Available **only during setup script execution**
- **Automatically removed** after setup completes
- **Never visible** to the agent during runtime
- Used to configure tools, then **discarded**

## Common Secrets for CodeTuneStudio

### Python Package Repositories

```bash
# Private PyPI index (if using internal packages)
PIP_INDEX_URL=https://username:token@pypi.example.com/simple

# Additional package index (e.g., private artifact registry)
PIP_EXTRA_INDEX_URL=https://username:token@artifacts.example.com/pypi/simple

# PyPI authentication token (for publishing packages)
PYPI_TOKEN=pypi-AgEIcHlwaS5vcmc...
```

**Setup script usage:**
```bash
if [ -n "${PIP_INDEX_URL:-}" ]; then
  pip config set global.index-url "$PIP_INDEX_URL"
fi

if [ -n "${PIP_EXTRA_INDEX_URL:-}" ]; then
  pip config set global.extra-index-url "$PIP_EXTRA_INDEX_URL"
fi
```

### Git Authentication

```bash
# GitHub personal access token (for private repos)
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx

# GitLab private token
GITLAB_TOKEN=glpat-xxxxxxxxxxxxxxxxxxxx

# Generic git credential (for multiple services)
GIT_CREDENTIALS=https://username:token@github.com
```

**Setup script usage:**
```bash
if [ -n "${GITHUB_TOKEN:-}" ]; then
  git config --global credential.helper store
  echo "https://${GITHUB_TOKEN}:x-oauth-basic@github.com" >> ~/.git-credentials
fi
```

### API Keys (Setup-Time Only)

```bash
# Hugging Face token (for downloading gated models during setup)
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxx

# OpenAI API key (for setup-time code analysis tool configuration)
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx

# Anthropic API key (for setup-time initialization)
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxx
```

**Setup script usage:**
```bash
# Login to Hugging Face CLI (persists credentials)
if [ -n "${HF_TOKEN:-}" ]; then
  huggingface-cli login --token "$HF_TOKEN"
fi

# Configure tool credentials (write to config file)
if [ -n "${OPENAI_API_KEY:-}" ]; then
  mkdir -p ~/.config/codetune-studio
  echo "openai_api_key: $OPENAI_API_KEY" >> ~/.config/codetune-studio/config.yaml
fi
```

### Database Credentials

```bash
# PostgreSQL password (for constructing DATABASE_URL during setup)
POSTGRES_PASSWORD=secure_password_here

# Database connection string with embedded credentials
DATABASE_URL=postgresql://codetune:${POSTGRES_PASSWORD}@db.example.com:5432/codetune_studio
```

**Setup script usage:**
```bash
# Write database config to persistent location
if [ -n "${DATABASE_URL:-}" ]; then
  echo "DATABASE_URL=${DATABASE_URL}" >> /workspace/.env.local
fi
```

---

## Setup Script Pattern: Secrets → Persistent Config

The canonical pattern for handling secrets:

```bash
#!/usr/bin/env bash
set -euo pipefail

# 1. Secrets are available here
if [ -n "${HF_TOKEN:-}" ]; then
  # 2. Use secret to configure tool
  huggingface-cli login --token "$HF_TOKEN"

  # Tool writes credentials to ~/.cache/huggingface/token
  # Secret is no longer needed in environment
fi

# 3. After setup completes, Codex removes HF_TOKEN
# 4. Agent runs with persistent ~/.cache/huggingface/token
# 5. Agent never sees the raw HF_TOKEN value
```

**Why this works:**
- Tools like `huggingface-cli`, `git`, `pip` write credentials to disk
- These files persist after setup
- Original secrets are removed
- Agent operates on persistent config, not ephemeral secrets

---

## Runtime Secrets (Different Pattern)

If you need secrets **during agent runtime** (not setup), use environment variables instead:

| Need | Use | Why |
|------|-----|-----|
| **Setup-time authentication** | Secret | Removed after setup |
| **Runtime API calls** | Environment Variable | Available during execution |

**Example:**
```bash
# ❌ Wrong: API key as secret (unavailable at runtime)
OPENAI_API_KEY=sk-xxx...  # Secret → disappears after setup

# ✅ Correct: API key as environment variable
OPENAI_API_KEY=sk-xxx...  # Environment Variable → available during runtime
```

**However:** If you can configure the tool during setup to store credentials persistently, **prefer secrets**.

---

## Security Best Practices

### ✅ DO
- Use secrets for **bootstrap credentials** (package repos, git auth, initial logins)
- Configure tools to **persist credentials** locally (`~/.cache`, `~/.config`)
- Validate secrets exist before use: `${SECRET_NAME:-}`
- Use setup script to **transform secrets → persistent config**

### ❌ DON'T
- Put secrets in environment variables (they persist too long)
- Hardcode secrets in setup scripts (use parameter expansion)
- Echo secrets to logs (they may be visible)
- Use secrets for **runtime** operations (they won't exist)

---

## Quick Reference: Common Secret Names

**Copy-paste starter (remove unused):**
```bash
# Python packages
PIP_INDEX_URL=
PIP_EXTRA_INDEX_URL=

# Git authentication
GITHUB_TOKEN=
GITLAB_TOKEN=

# ML platform tokens
HF_TOKEN=

# API keys (if configuring tools at setup)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# Database credentials
POSTGRES_PASSWORD=
DATABASE_URL=
```

---

## Testing Secrets Locally

Before deploying to Codex:

```bash
# Simulate setup script with secrets
export HF_TOKEN="hf_test_token"
export GITHUB_TOKEN="ghp_test_token"
./codex/setup.sh

# Verify persistent config was created
cat ~/.cache/huggingface/token
git config --get credential.helper

# Verify secrets are no longer needed
unset HF_TOKEN GITHUB_TOKEN
# Try running app - should still work
streamlit run app.py
```
