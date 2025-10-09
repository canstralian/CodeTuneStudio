# 📝 CodeTuneStudio High-Priority PR Review Checklist

This checklist is designed to guide you through reviewing, verifying, and merging high-priority PRs for CodeTuneStudio. Use this to track progress and ensure CI, linting, and security best practices are followed.

---

## **Instructions for Use**
1. **Clone or pull the latest repository** to ensure you have the newest code.
2. **Check out PR branches locally** to review code.
3. **Run local linting & formatting**:
   ```bash
   black .
   flake8 .
   ```
4. **Follow the checklist step by step**, checking each item as completed.
5. **Use Pomodoro sprints** to stay focused:

   * 25 min work
   * 5 min break
6. **Commit any local fixes** before merging if CI fails.
7. **Confirm all CI checks pass** on GitHub Actions before finalizing merges.

---

## **Step 1: Preparation**

* [ ] Pull the latest `main` branch.
* [ ] Check out each PR locally.
* [ ] Run `black . && flake8 .` to ensure code formatting and linting compliance.
* [ ] Confirm Python version (prefer 3.10 or 3.11).

---

## **Step 2: Style & Linting (PR #55)**

* [ ] Verify line lengths, unused imports, and whitespace fixes.
* [ ] Merge PR if CI passes.
* [ ] If CI fails, fix locally, commit, and push corrections.

---

## **Step 3: Dependency Resolution**

### PR #52

* [ ] Confirm `evaluate==0.4.6` is compatible with your Python version.
* [ ] Merge if compatible.

### PR #50

* [ ] Confirm Python 3.10 standardization works.
* [ ] Run tests to ensure stable builds.
* [ ] Merge after verification.

---

## **Step 4: Security & Permissions (PR #53)**

* [ ] Ensure workflow grants **minimum necessary permissions**.
* [ ] Document all secrets in `.env.example`.
* [ ] Merge if compliant.

---

## **Step 5: Dependency Upgrades (PR #49)**

* [ ] Validate upgrades: Plotly, Transformers, Flask-Migrate.
* [ ] Run test scripts to check for regressions.
* [ ] Merge if all tests pass.

---

## **Step 6: Code Quality & Security PRs (#41, #37, #33)**

* [ ] Confirm unused imports removed.
* [ ] Verify linting issues fixed.
* [ ] Check for hardcoded secrets and proper input validation.
* [ ] Merge PRs after verification.

---

## **Step 7: Final Verification**

* [ ] Confirm **all merged PRs pass CI** on GitHub Actions.
* [ ] Document any anomalies in repository notes.

---

### ✅ Notes

* Use GitHub’s **checkbox feature** to mark items as complete directly in this file.
* Keep this checklist updated with new high-priority PRs.
```
