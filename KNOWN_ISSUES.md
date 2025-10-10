# Known Issues

## app.py File Issue

**Status**: Requires Investigation
**Priority**: High
**Discovered**: During PR review implementation

### Description
The `app.py` file currently contains HTML content instead of the expected Python code. This causes:
- Test failures (tests expect `MLFineTuningApp` Python class)
- Flake8 syntax errors when trying to lint as Python code

### Current Workaround
- Added `app.py` to flake8 exclude list in `.flake8` configuration
- This prevents linting errors but doesn't fix the root cause

### Recommended Fix
1. Investigate git history to find when app.py was changed from Python to HTML
2. Restore the original Python application file
3. Rename the current HTML file appropriately (e.g., `landing.html` or merge with `index.html`)
4. Update any references to the renamed file

### Impact
- Tests cannot run until Python app.py is restored
- CI/CD pipeline will fail on test stage
- This issue is separate from the PR review improvements documented in PR_REVIEW_CHECKLIST.md
