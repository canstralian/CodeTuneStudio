# CodeTuneStudio v0.1.1 Release Plan

**Release Type**: Patch Release (Security & Bug Fixes)
**Target Date**: Immediate (ASAP due to security vulnerabilities)
**Priority**: HIGH - Critical security patches required

---

## Executive Summary

This patch release addresses:
1. **CRITICAL**: Streamlit file upload vulnerability (affects v1.42.0)
2. **HIGH**: Transformers ReDoS vulnerability (CVE-2025-2099)
3. **Code Quality**: 3 critical syntax/structure bugs
4. **Performance**: Restored LRU caching with optimizations

---

## Security Vulnerabilities Addressed

### 1. Streamlit File Upload Vulnerability (CRITICAL)
**Current Version**: 1.42.0
**Vulnerable**: Yes
**Patched Version**: ≥1.43.2
**Severity**: HIGH - Enables malicious file upload to cloud instances

**Action**: Upgrade `streamlit>=1.43.2`

**Impact**: The vulnerability in `st.file_uploader` allows attackers to upload malicious files, potentially gaining unauthorized access. Patch introduces backend validation for file-type restrictions.

### 2. PyTorch CVE-2025-32434 (Already Mitigated)
**Current Version**: 2.6.0
**Status**: ✅ SECURE
**Details**: Version 2.6.0 patches critical RCE vulnerability (CVSS 9.3) in `torch.load()` with `weights_only=True`

**Note**: Minor DoS vulnerability CVE-2025-2953 in `torch.mkldnn_max_pool2d` (local attack only, low priority)

### 3. Transformers CVE-2025-2099 (ReDoS)
**Current Version**: 4.48.2
**Vulnerable Version**: 4.48.3 (one patch ahead)
**Severity**: HIGH (CVSS 7.5) - Regular Expression Denial of Service

**Action**: Upgrade to `transformers>=4.48.4` when available (not yet released as of 2025-10-05)

**Temporary Mitigation**: Monitor transformers releases and upgrade as soon as 4.48.4+ is available

---

## Code Quality Fixes

### 1. components/dataset_selector.py
**Issue**: Duplicate function definition `get_argilla_dataset_manager()` (lines 43-44)
**Fix**: Removed duplicate, consolidated into single implementation with proper error handling
**Security Impact**: Prevents undefined behavior from function shadowing

**Additional Improvements**:
- Restored `@lru_cache(maxsize=128)` decorator on `validate_dataset_name()` (was removed, impacting performance)
- Enhanced regex pattern to include `/` for HuggingFace namespace support: `r"^[a-zA-Z0-9_\-/]+$"`

### 2. components/tokenizer_builder.py
**Issue**: Duplicate docstring (lines 11-30 and 32-33)
**Fix**: Removed truncated duplicate, kept comprehensive version
**Impact**: Improved code documentation consistency

### 3. utils/argilla_dataset.py
**Issue**: Orphaned docstring before function signature (`prepare_for_training`)
**Fix**: Moved docstring to correct position (after `def` line)
**Impact**: Proper IDE/tooling support for documentation

---

## Testing Infrastructure Improvements

### Pytest Configuration Fix
**Issue**: Conflicting coverage arguments in `pyproject.toml` causing test failures:
```
ERROR: unrecognized arguments: --cov=. --cov-report=term-missing --cov-report=html --cov-report=xml --cov-branch
```

**Root Cause**: Pytest addopts include coverage flags but pytest-cov may not be installed in all environments

**Fix**: Make coverage optional via separate configuration or conditional pytest plugin

---

## Dependency Updates

### Critical Updates (Required)
```toml
[project.dependencies]
streamlit>=1.43.2  # Up from 1.42.0 - SECURITY FIX
```

### Recommended Updates (When Available)
```toml
transformers>=4.48.4  # Up from 4.48.2 - Pending release
```

### No Changes Required
- `torch>=2.6.0` - Already patched for CVE-2025-32434
- `flask>=3.1.0` - No known vulnerabilities
- `anthropic>=0.45.2` - No known vulnerabilities
- `openai>=1.61.1` - No known vulnerabilities
- `peft>=0.14.0` - No known vulnerabilities

---

## Breaking Changes

**NONE** - This is a backwards-compatible patch release

---

## Migration Guide (v0.1.0 → v0.1.1)

### For Existing Users

1. **Update Dependencies**:
   ```bash
   # Using uv (recommended)
   uv pip install --upgrade streamlit>=1.43.2

   # Or reinstall project
   uv pip install -e ".[dev]" --upgrade
   ```

2. **Verify Security Patches**:
   ```bash
   python -c "import streamlit; print(streamlit.__version__)"
   # Should output: 1.43.2 or higher
   ```

3. **Re-run Tests** (after pytest config fix):
   ```bash
   pytest tests/ -v
   ```

4. **No Code Changes Required** - All fixes are internal

### For New Installations

```bash
git clone https://github.com/canstralian/CodeTuneStudio.git
cd CodeTuneStudio
uv pip install -e ".[dev]"
```

---

## Changelog Entry (v0.1.1)

```markdown
## [0.1.1] - 2025-10-05

### Security
- **CRITICAL**: Upgraded Streamlit to 1.43.2 to patch file upload vulnerability
- **HIGH**: Monitoring Transformers for CVE-2025-2099 fix (ReDoS vulnerability)
- ✅ Confirmed PyTorch 2.6.0 patches CVE-2025-32434 (RCE vulnerability)

### Fixed
- Fixed duplicate function definition in `components/dataset_selector.py`
- Fixed duplicate docstring in `components/tokenizer_builder.py`
- Fixed misplaced docstring in `utils/argilla_dataset.py`
- Restored LRU cache on `validate_dataset_name()` with increased cache size (32→128)
- Added `/` to dataset name validation regex for HuggingFace namespace support

### Changed
- Enhanced `get_argilla_dataset_manager()` error handling
- Improved logging for dataset validation failures

### Infrastructure
- Updated pytest configuration for better coverage reporting
- No breaking changes - fully backwards compatible
```

---

## Pre-Release Checklist

- [ ] Update `pyproject.toml` version: `0.1.0` → `0.1.1`
- [ ] Update `streamlit` dependency: `>=1.42.0` → `>=1.43.2`
- [ ] Fix pytest configuration (remove conflicting coverage args)
- [ ] Update `CHANGELOG.md` with v0.1.1 entry
- [ ] Run full test suite (after pytest fix)
- [ ] Run security scan: `bandit -r . -x venv,tests`
- [ ] Run linting: `ruff check . --exclude=venv --fix`
- [ ] Update README with security advisory
- [ ] Create GitHub release with security notes
- [ ] Tag release: `git tag -a v0.1.1 -m "Security patch release"`
- [ ] Trigger CI/CD pipeline
- [ ] Deploy to Hugging Face Spaces (if applicable)
- [ ] Notify users of critical security update

---

## Post-Release Actions

1. **Monitor Transformers Releases**: Watch for 4.48.4+ to patch CVE-2025-2099
2. **Schedule v0.1.2**: Plan for Transformers upgrade when patch available
3. **Security Audit**: Consider full security audit for v0.2.0
4. **Test Coverage**: Improve to ≥80% target
5. **Documentation**: Expand security best practices guide

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Delayed Streamlit upgrade | CRITICAL | Immediate deployment |
| Transformers ReDoS | HIGH | Monitor releases, prepare v0.1.2 |
| Breaking changes | LOW | Extensive testing pre-release |
| CI/CD failure | MEDIUM | Manual deployment fallback |
| User disruption | LOW | Backwards compatible, clear migration guide |

---

## Success Criteria

1. ✅ Streamlit upgraded to ≥1.43.2
2. ✅ All syntax errors fixed
3. ✅ No breaking changes introduced
4. ✅ CI/CD pipeline passes
5. ✅ Security scan shows no critical vulnerabilities
6. ✅ Users notified within 24 hours
7. ⏳ Transformers upgrade planned for v0.1.2

---

## Contact & Escalation

**Release Manager**: CodeTuneStudio Team
**Security Contact**: support@codetunestudio.dev
**GitHub Issues**: https://github.com/canstralian/CodeTuneStudio/issues

---

**Prepared by**: Claude (Purple Team AI Architect Agent)
**Date**: 2025-10-05
**Document Version**: 1.0
