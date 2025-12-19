# Codex Internet Access Policy Template

Configure this in **Environment → Network → Internet Access** in your Codex Cloud settings.

## Recommended Default: Restricted Allowlist

**Philosophy:** Deny by default, allow only known-necessary domains.

This ensures:
- **Deterministic builds** (no dynamic fetches from unknown sources)
- **Security** (limited attack surface)
- **Auditability** (know exactly what external resources are accessed)

---

## Allowlist for CodeTuneStudio

### Tier 1: Python Package Management
```
pypi.org
files.pythonhosted.org
```
**Why:** Core dependency installation via `pip`.

### Tier 2: Git/GitHub
```
github.com
raw.githubusercontent.com
api.github.com
```
**Why:**
- Cloning repositories
- Fetching GitHub-hosted dependencies (e.g., `pip install git+https://github.com/...`)
- GitHub API access (if using `gh` CLI or GitHub integrations)

### Tier 3: ML/AI Platforms
```
huggingface.co
cdn-lfs.huggingface.co
cdn.huggingface.co
```
**Why:**
- Downloading models/datasets from Hugging Face Hub
- LFS file access for large model weights

```
download.pytorch.org
```
**Why:**
- PyTorch wheel downloads (especially CPU-specific builds)

### Tier 4: Package Ecosystems (Optional)
```
anaconda.org
conda.anaconda.org
repo.anaconda.com
```
**Why:** If using conda instead of pip (not standard for this project).

```
gitlab.com
```
**Why:** If dependencies are hosted on GitLab.

---

## Full Allowlist (Copy-Paste)

**Minimal (Python + Git + ML):**
```
pypi.org
files.pythonhosted.org
github.com
raw.githubusercontent.com
huggingface.co
cdn-lfs.huggingface.co
download.pytorch.org
```

**Extended (add if needed):**
```
# API platforms (if tools call external APIs at runtime)
api.openai.com
api.anthropic.com

# Additional package registries
gitlab.com
anaconda.org

# CDNs (if loading external assets)
cdn.jsdelivr.net
unpkg.com
```

---

## Policy Tiers

### 🟢 Tier 1: Allowlist (Recommended)
**Use when:** You have a well-defined set of dependencies.

**Behavior:**
- Only listed domains are accessible
- All other requests are blocked
- Deterministic, secure, auditable

**Tradeoff:** May need to add domains as you discover new dependencies.

### 🟡 Tier 2: Full Access (Development)
**Use when:**
- Rapid prototyping
- Exploratory data fetching
- Dynamic API integrations

**Behavior:**
- All domains accessible
- Non-deterministic (external changes can break builds)
- Higher security risk

**Recommendation:** Use only temporarily, then migrate to allowlist.

### 🔴 Tier 3: No Access (Maximum Security)
**Use when:**
- All dependencies are pre-cached
- No runtime network calls
- Maximum isolation

**Behavior:**
- No external network access
- Requires pre-baked environment

**Setup pattern:**
```bash
# In setup script, cache everything needed
pip download -r requirements.txt -d /workspace/.cache/pip
huggingface-cli download model-name --cache-dir /workspace/.cache/huggingface

# At runtime, install from cache
pip install --no-index --find-links=/workspace/.cache/pip -r requirements.txt
```

---

## Debugging Network Issues

### Symptom: `pip install` fails
**Check:** Is `pypi.org` and `files.pythonhosted.org` in allowlist?

**Test:**
```bash
curl -I https://pypi.org/simple/torch/
curl -I https://files.pythonhosted.org
```

### Symptom: GitHub clone fails
**Check:** Is `github.com` in allowlist?

**Test:**
```bash
git ls-remote https://github.com/huggingface/transformers.git
```

### Symptom: Hugging Face model download fails
**Check:** Are Hugging Face CDN domains in allowlist?

**Test:**
```bash
curl -I https://huggingface.co/bert-base-uncased
curl -I https://cdn-lfs.huggingface.co
```

### Symptom: PyTorch install fails with index error
**Check:** Is `download.pytorch.org` in allowlist?

**Test:**
```bash
curl -I https://download.pytorch.org/whl/cpu/torch_stable.html
```

---

## Migration Path: Full Access → Allowlist

**Step 1: Run with full access + logging**
```bash
# In setup script, add:
export HTTPS_PROXY=http://logger.example.com:8080
./codex/setup.sh
# Review logs to see all accessed domains
```

**Step 2: Extract unique domains**
```bash
grep "CONNECT" proxy.log | awk '{print $2}' | sort -u > accessed_domains.txt
```

**Step 3: Create allowlist from logs**
```bash
# Review accessed_domains.txt
# Add to Codex allowlist
# Test with restricted access
```

**Step 4: Iterate**
- Switch to allowlist mode
- Run setup script
- Add any missing domains
- Repeat until stable

---

## Special Cases

### Private Package Registries
If using internal PyPI mirrors:
```
# Add your domain
pypi.internal.example.com
artifacts.example.com
```

**Auth:** Use secrets to configure `pip` to authenticate (see `SECRETS.md`).

### Dynamic API Calls (Runtime)
If agent makes API calls during execution:
```
# Add API endpoints
api.openai.com
api.anthropic.com
```

**Note:** This introduces non-determinism. Prefer caching responses if possible.

### CDNs for Static Assets
If loading JavaScript/CSS from CDNs (unlikely for Python projects):
```
cdn.jsdelivr.net
unpkg.com
cdnjs.cloudflare.com
```

---

## Recommended Configuration for CodeTuneStudio

**Phase 1: Initial Setup (Development)**
- Use **full access** to discover dependencies
- Log all network requests
- Document accessed domains

**Phase 2: Stabilization (Staging)**
- Switch to **allowlist** with discovered domains
- Test thoroughly
- Add any missing domains

**Phase 3: Production (Locked Down)**
- Use **minimal allowlist**:
  ```
  pypi.org
  files.pythonhosted.org
  github.com
  raw.githubusercontent.com
  huggingface.co
  cdn-lfs.huggingface.co
  download.pytorch.org
  ```
- Freeze dependency versions (`requirements.txt` with `==` pinning)
- Cache models locally if possible

---

## Testing Your Policy

**Before deploying to Codex:**

```bash
# 1. Block all network access
sudo iptables -A OUTPUT -j REJECT

# 2. Allow only your allowlist domains
for domain in pypi.org files.pythonhosted.org github.com huggingface.co; do
  sudo iptables -I OUTPUT -d $(dig +short $domain) -j ACCEPT
done

# 3. Run setup script
./codex/setup.sh

# 4. Verify it completes successfully
# 5. Clean up iptables rules
sudo iptables -F OUTPUT
```

**Expected:** Setup completes without network errors.

**If it fails:** Add the missing domain to your allowlist.

---

## Quick Reference

| Scenario | Allowlist | Why |
|----------|-----------|-----|
| **Minimal Python** | `pypi.org`, `files.pythonhosted.org` | Pip install |
| **+ GitHub deps** | `github.com`, `raw.githubusercontent.com` | Git clones |
| **+ ML models** | `huggingface.co`, `cdn-lfs.huggingface.co` | Model downloads |
| **+ PyTorch CPU** | `download.pytorch.org` | PyTorch wheels |
| **+ Runtime APIs** | `api.openai.com`, `api.anthropic.com` | API calls |

**Default recommendation for CodeTuneStudio:** Minimal Python + GitHub + ML models + PyTorch CPU.
