# Codex Cloud Configuration

**Purpose:** Drop-in templates for deploying CodeTuneStudio to Codex Cloud environments.

These templates create a **deterministic, reproducible Python ML environment** with:
- Pre-installed dependencies (PyTorch, Transformers, Streamlit, Flask)
- Database initialization (PostgreSQL or SQLite)
- Network access control
- Secure secret handling

---

## Quick Start

### 1. Setup Script
**Location:** `codex/setup.sh`

**What it does:**
- Installs system dependencies (build tools, PostgreSQL client, git)
- Upgrades Python tooling (pip, setuptools, wheel)
- Installs project dependencies from `requirements.txt` and `pyproject.toml`
- Configures PyTorch for CPU-only execution
- Initializes database and runs migrations
- Verifies all core dependencies are working

**Usage in Codex:**
1. Go to **Environment → Setup Script**
2. Upload or paste `codex/setup.sh`
3. Save configuration

**Local testing:**
```bash
chmod +x codex/setup.sh
./codex/setup.sh
```

---

### 2. Environment Variables
**Template:** `codex/templates/ENVIRONMENT_VARIABLES.md`

**What to configure:**
- Python runtime settings (`PYTHONUNBUFFERED`, `PYTHONPATH`)
- Application server config (`HOST`, `PORT`, `SERVER_HEADLESS`)
- Database connection (`DATABASE_URL`)
- ML optimizations (`CUDA_VISIBLE_DEVICES=""`, `HF_HUB_DISABLE_TELEMETRY`)

**Usage in Codex:**
1. Go to **Environment → Variables**
2. Copy variables from template
3. Adjust values as needed
4. Save configuration

**Recommended minimal set:**
```bash
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
PYTHONPATH=/workspace
CI=true
CODEX_ENV=cloud
SERVER_HEADLESS=true
DATABASE_URL=sqlite:///database.db
CUDA_VISIBLE_DEVICES=""
```

---

### 3. Secrets
**Template:** `codex/templates/SECRETS.md`

**What to configure:**
- Private package registry credentials (`PIP_INDEX_URL`)
- Git authentication tokens (`GITHUB_TOKEN`, `GITLAB_TOKEN`)
- API keys for setup-time tool configuration (`HF_TOKEN`, `OPENAI_API_KEY`)
- Database credentials (`POSTGRES_PASSWORD`)

**Usage in Codex:**
1. Go to **Environment → Secrets**
2. Add secrets needed for setup
3. Save configuration

**Important:**
- Secrets are **only available during setup script execution**
- They are **removed after setup completes**
- Agent **never sees** raw secret values at runtime

**Common pattern:**
```bash
# In setup.sh
if [ -n "${HF_TOKEN:-}" ]; then
  huggingface-cli login --token "$HF_TOKEN"
  # Token is persisted to ~/.cache/huggingface/token
  # Original secret is removed after setup
fi
```

---

### 4. Internet Access Policy
**Template:** `codex/templates/INTERNET_ACCESS_POLICY.md`

**What to configure:**
Allowlist of domains the environment can access.

**Usage in Codex:**
1. Go to **Environment → Network → Internet Access**
2. Choose **Allowlist** mode
3. Add domains from template
4. Save configuration

**Recommended allowlist for CodeTuneStudio:**
```
pypi.org
files.pythonhosted.org
github.com
raw.githubusercontent.com
huggingface.co
cdn-lfs.huggingface.co
cdn.huggingface.co
download.pytorch.org
```

**Why restrict?**
- **Determinism:** Prevents dynamic fetches that could break builds
- **Security:** Limits attack surface
- **Auditability:** Know exactly what external resources are accessed

---

### 5. Agent Instructions
**Location:** `AGENTS.md` (project root)

**What it does:**
Tells Codex agents how to work with this environment.

**Key sections:**
- **Setup assumptions:** What's pre-configured
- **Constraints:** What NOT to do (e.g., install packages at runtime)
- **Preferred commands:** How to run tests, lint, format
- **Common tasks:** Workflows for features, bugs, plugins
- **Troubleshooting:** Common errors and fixes

**Usage:**
Agents automatically read `AGENTS.md` from project root. No Codex configuration needed.

---

## Directory Structure

```
codex/
├── README.md                          ← You are here
├── setup.sh                           ← Main setup script
└── templates/
    ├── ENVIRONMENT_VARIABLES.md       ← Variable reference
    ├── SECRETS.md                     ← Secret handling guide
    └── INTERNET_ACCESS_POLICY.md      ← Network policy guide

AGENTS.md                              ← Agent instructions (project root)
```

---

## Configuration Workflow

### Phase 1: Initial Setup (First Time)
1. **Read templates** to understand configuration options
2. **Configure Codex environment:**
   - Upload `codex/setup.sh` as setup script
   - Add environment variables (start with minimal set)
   - Add secrets (if needed for private packages/repos)
   - Configure internet allowlist
3. **Test setup:**
   - Trigger a Codex build
   - Verify setup script completes successfully
   - Check that dependencies are installed
   - Verify app runs: `streamlit run app.py`

### Phase 2: Iteration (As Needed)
1. **Add missing domains** if network requests fail
2. **Add environment variables** for new features
3. **Update setup script** if dependencies change
4. **Add secrets** if integrating new external services

### Phase 3: Optimization (Stable)
1. **Lock dependency versions** in `requirements.txt`
2. **Minimize allowlist** to only required domains
3. **Remove unused environment variables**
4. **Cache heavy assets** to reduce network usage

---

## Testing Locally

### Test Setup Script
```bash
# Create clean environment
python -m venv test_venv
source test_venv/bin/activate

# Run setup script
./codex/setup.sh

# Verify app works
streamlit run app.py
```

### Test Environment Variables
```bash
# Export variables
export PYTHONUNBUFFERED=1
export CODEX_ENV=cloud
export DATABASE_URL=sqlite:///test.db

# Run app
python app.py
```

### Test Network Policy
```bash
# Block all network access
sudo iptables -A OUTPUT -j REJECT

# Allow only specific domains
for domain in pypi.org github.com huggingface.co; do
  sudo iptables -I OUTPUT -d $(dig +short $domain) -j ACCEPT
done

# Run setup
./codex/setup.sh

# Clean up
sudo iptables -F OUTPUT
```

### Test Secrets Pattern
```bash
# Set secret
export HF_TOKEN="test_token"

# Run setup script section that uses secret
if [ -n "${HF_TOKEN:-}" ]; then
  huggingface-cli login --token "$HF_TOKEN"
fi

# Verify persistent config created
cat ~/.cache/huggingface/token

# Remove secret
unset HF_TOKEN

# Verify app still works (using persistent config)
python -c "from transformers import AutoModel; print('OK')"
```

---

## Troubleshooting

### Setup script fails with "command not found"
**Cause:** System dependency missing
**Fix:** Add to `apt-get install` section in `setup.sh`

### App fails with "ModuleNotFoundError"
**Cause:** Dependency not installed
**Fix:** Add to `requirements.txt` or `pyproject.toml`, re-run setup

### Network request fails during setup
**Cause:** Domain not in allowlist
**Fix:** Add domain to internet access policy in Codex

### Secret not available at runtime
**Cause:** Secrets are removed after setup
**Fix:** Use setup script to persist secret to config file, or move to environment variables

### Database connection fails
**Cause:** `DATABASE_URL` not set or incorrect
**Fix:** Check environment variables configuration

### PyTorch tries to use CUDA
**Cause:** Code assumes GPU availability
**Fix:** Set `CUDA_VISIBLE_DEVICES=""` in environment variables

---

## Best Practices

### ✅ DO
- **Version pin** all dependencies (`package==1.2.3`)
- **Test setup script locally** before deploying to Codex
- **Use minimal allowlist** (start small, add as needed)
- **Document** any custom configuration in this README
- **Commit** setup script and templates to version control

### ❌ DON'T
- **Install packages at runtime** (defeats determinism)
- **Use full internet access** in production (security risk)
- **Store secrets in environment variables** (use Codex Secrets instead)
- **Hardcode paths** that differ between local and Codex
- **Skip testing** setup script changes

---

## Customization

### Adding New Dependencies
1. Add to `requirements.txt` or `pyproject.toml`
2. Test locally: `pip install -r requirements.txt`
3. Re-run setup script in Codex
4. Verify app works

### Adding New External Service
1. Document API key in `templates/SECRETS.md`
2. Add authentication logic to `setup.sh`
3. Add domain to `templates/INTERNET_ACCESS_POLICY.md`
4. Update `AGENTS.md` with usage instructions

### Optimizing for Speed
1. **Cache PyPI packages:**
   ```bash
   pip download -r requirements.txt -d /workspace/.cache/pip
   pip install --no-index --find-links=/workspace/.cache/pip -r requirements.txt
   ```

2. **Pre-download models:**
   ```bash
   huggingface-cli download model-name --cache-dir /workspace/.cache/huggingface
   ```

3. **Skip unnecessary checks:**
   ```bash
   export PIP_DISABLE_PIP_VERSION_CHECK=1
   export HF_HUB_DISABLE_TELEMETRY=1
   ```

### Supporting Multiple Environments
```bash
# In setup.sh
if [ "${CODEX_ENV}" == "production" ]; then
  # Minimal dependencies, strict network policy
  pip install -r requirements-prod.txt
elif [ "${CODEX_ENV}" == "development" ]; then
  # Full dependencies, relaxed policy
  pip install -r requirements-dev.txt
fi
```

---

## Migration Guide

### From Manual Setup to Codex Templates

**Before (manual):**
```bash
# User manually runs:
pip install -r requirements.txt
streamlit run app.py
```

**After (automated):**
1. Create `codex/setup.sh` with all manual steps
2. Configure environment variables in Codex
3. Agent automatically gets pre-configured environment

**Benefits:**
- ✅ Reproducible across sessions
- ✅ No manual setup steps
- ✅ Deterministic builds
- ✅ Faster agent startup

---

## Support

### Questions?
1. Check templates in `codex/templates/`
2. Review `AGENTS.md` for runtime instructions
3. Consult `CLAUDE.md` for project architecture
4. Open issue in GitHub repository

### Contributing
Improvements to these templates are welcome! Please:
1. Test changes locally first
2. Document any new configuration
3. Update relevant template files
4. Submit PR with clear description

---

## Version History

- **v1.0** (2025-12-19): Initial Codex templates
  - Setup script for Python ML environment
  - Environment variables template
  - Secrets handling template
  - Internet access policy template
  - Agent instructions

---

## License

Same as parent project (MIT License). See `LICENSE` file.
