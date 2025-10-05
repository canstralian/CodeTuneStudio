# Release Checklist for CodeTuneStudio

This document provides a comprehensive checklist for preparing and executing releases of CodeTuneStudio.

## Pre-Release Phase

### 1. Code Review and Quality Assurance

#### Code Quality
- [ ] All Python code follows PEP 8 standards (max line length: 88 characters)
- [ ] All functions have comprehensive docstrings (Google/NumPy style)
- [ ] Type hints are present for all function signatures
- [ ] No unnecessary comments or debug code remains
- [ ] Code complexity is within acceptable limits (max McCabe complexity: 18)
- [ ] All imports are organized and necessary

#### Security Review
- [ ] No hardcoded secrets, API keys, or credentials in code
- [ ] All secrets use environment variables
- [ ] All database queries use parameterized queries or ORM
- [ ] Input validation is implemented for all user inputs
- [ ] Output sanitization is applied where necessary
- [ ] Authentication mechanisms are properly implemented
- [ ] API endpoints have rate limiting where appropriate
- [ ] Dependencies have no known security vulnerabilities

#### Code Analysis
```bash
# Run security checks
bandit -r . -f json -o bandit-report.json
safety check --json

# Run linting
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics

# Type checking (if using mypy)
mypy app.py utils/ components/
```

### 2. Documentation Review

#### Core Documentation
- [ ] README.md is up-to-date with accurate installation instructions
- [ ] README.md includes all required environment variables
- [ ] CLAUDE.md reflects current architecture and development workflow
- [ ] CHANGELOG.md documents all changes since last release
- [ ] All function docstrings are complete and accurate
- [ ] Code examples in documentation are tested and working

#### API Documentation
- [ ] All public APIs are documented
- [ ] Breaking changes are clearly marked
- [ ] Migration guides are provided for breaking changes
- [ ] Example usage is provided for all major features

#### Developer Setup
- [ ] `.env.example` file is up-to-date with all required variables
- [ ] Development setup instructions are tested
- [ ] Prerequisites are clearly listed
- [ ] Common troubleshooting issues are documented

### 3. Database and Migrations

#### Migration Review
- [ ] All migration files are present in `migrations/` directory
- [ ] Migration files are properly sequenced
- [ ] Migrations can be applied cleanly to an empty database
- [ ] Migrations can be rolled back successfully
- [ ] Database schema matches ORM models

#### Testing Migrations
```bash
# Test fresh database creation
export DATABASE_URL="postgresql://user:pass@localhost/test_db"
flask db upgrade

# Test rollback
flask db downgrade

# Test re-upgrade
flask db upgrade
```

#### Rollback Plan
- [ ] Document current database schema version
- [ ] Create rollback SQL scripts for critical changes
- [ ] Test rollback procedures in staging environment
- [ ] Document data migration procedures if needed

### 4. Testing

#### Unit Tests
- [ ] All unit tests pass: `python -m unittest discover -s tests`
- [ ] Test coverage for critical paths is >= 80%
- [ ] New features have corresponding tests
- [ ] Edge cases are covered

#### Integration Tests
- [ ] Database integration tests pass
- [ ] API endpoint tests pass
- [ ] Plugin system tests pass
- [ ] External service integrations work (Hugging Face, OpenAI, Anthropic)

#### Manual Testing
- [ ] Test dataset selection and validation
- [ ] Test training configuration and parameter validation
- [ ] Test training monitor with live metrics
- [ ] Test experiment comparison
- [ ] Test plugin loading and execution
- [ ] Test tokenizer builder
- [ ] Test model export functionality
- [ ] Test error handling and recovery

#### Performance Testing
- [ ] Database connection pooling works under load
- [ ] Memory usage is acceptable during training
- [ ] No memory leaks in long-running processes
- [ ] UI remains responsive during operations

### 5. Versioning

#### Version Update
- [ ] Update `version.py` with new version number
- [ ] Update version in `pyproject.toml`
- [ ] Update version in `setup.cfg` (if applicable)
- [ ] Update version in documentation
- [ ] Follow semantic versioning (MAJOR.MINOR.PATCH)

#### Git Tagging
- [ ] Create annotated git tag: `git tag -a v1.0.0 -m "Release 1.0.0: Genesis"`
- [ ] Push tags: `git push origin v1.0.0`

### 6. Dependencies

#### Dependency Review
- [ ] All dependencies are necessary and actively maintained
- [ ] Dependencies are pinned to specific versions in `requirements.txt`
- [ ] Dependency versions are compatible with each other
- [ ] No deprecated dependencies
- [ ] License compatibility verified for all dependencies

#### Security Scan
```bash
# Check for vulnerabilities
pip install safety
safety check

# Check for outdated packages
pip list --outdated
```

### 7. Build and Packaging

#### Build Process
- [ ] Clean build artifacts: `rm -rf build/ dist/ *.egg-info/`
- [ ] Build process completes without errors
- [ ] Generated artifacts are correct and complete

#### Docker Build (if applicable)
- [ ] Dockerfile builds successfully
- [ ] Docker image runs correctly
- [ ] Environment variables are properly configured
- [ ] Volume mounts work correctly

### 8. CI/CD Pipeline

#### GitHub Actions
- [ ] All CI/CD workflows pass
- [ ] Lint checks pass (`.github/workflows/python-style-checks.yml`)
- [ ] Unit tests pass (`.github/workflows/ci.yml`)
- [ ] Deployment workflow is ready (`.github/workflows/huggingface-deploy.yml`)

#### Required Secrets
- [ ] `HF_TOKEN` is set for Hugging Face deployment
- [ ] `ANTHROPIC_API_KEY` for Anthropic plugin (optional)
- [ ] `OPENAI_API_KEY` for OpenAI plugin (optional)
- [ ] Database credentials are properly configured

## Release Phase

### 1. Create Release Branch
```bash
git checkout main
git pull origin main
git checkout -b release/v1.0.0
```

### 2. Final Pre-Release Checks
- [ ] All tests pass
- [ ] Documentation is complete
- [ ] CHANGELOG.md is updated
- [ ] Version numbers are correct

### 3. Merge to Main
```bash
git checkout main
git merge release/v1.0.0
git push origin main
```

### 4. Tag Release
```bash
git tag -a v1.0.0 -m "Release 1.0.0: Genesis"
git push origin v1.0.0
```

### 5. Create GitHub Release
- [ ] Go to GitHub Releases page
- [ ] Create new release from tag v1.0.0
- [ ] Copy relevant sections from CHANGELOG.md
- [ ] Upload any release artifacts
- [ ] Mark as pre-release if applicable
- [ ] Publish release

### 6. Deploy to Production

#### Hugging Face Space
- [ ] Deployment workflow triggers automatically on tag push
- [ ] Verify deployment completes successfully
- [ ] Test deployed application on Hugging Face
- [ ] Check logs for any errors

#### Manual Deployment (if needed)
```bash
# Build and deploy
git push origin main

# Verify deployment
curl https://your-huggingface-space.hf.space/
```

### 7. Post-Release Verification
- [ ] Application is accessible at deployment URL
- [ ] All features work as expected in production
- [ ] No critical errors in logs
- [ ] Database migrations applied successfully
- [ ] Monitor for first 24 hours

## Post-Release Phase

### 1. Monitoring
- [ ] Monitor application logs for errors
- [ ] Check GitHub Issues for bug reports
- [ ] Monitor performance metrics
- [ ] Verify database performance

### 2. Communication
- [ ] Announce release on project channels
- [ ] Update project website/documentation
- [ ] Notify users of breaking changes (if any)
- [ ] Create blog post or release notes (optional)

### 3. Cleanup
- [ ] Delete release branch: `git branch -d release/v1.0.0`
- [ ] Archive old documentation versions
- [ ] Update project roadmap

### 4. Hotfix Preparation
- [ ] Document hotfix procedure
- [ ] Keep release branch available for critical fixes
- [ ] Plan for patch release if issues are found

## Hotfix Procedure

If critical issues are found after release:

1. **Create hotfix branch**:
   ```bash
   git checkout -b hotfix/v1.0.1 v1.0.0
   ```

2. **Fix the issue**:
   - Make minimal changes to fix the critical issue
   - Add tests to prevent regression
   - Update CHANGELOG.md

3. **Test thoroughly**:
   - Run all tests
   - Verify fix addresses the issue
   - Check for side effects

4. **Release hotfix**:
   ```bash
   git checkout main
   git merge hotfix/v1.0.1
   git tag -a v1.0.1 -m "Hotfix 1.0.1: Critical bug fixes"
   git push origin main v1.0.1
   ```

5. **Deploy and monitor**

## Rollback Procedure

If critical issues cannot be quickly resolved:

1. **Revert to previous version**:
   ```bash
   git revert <problematic-commit>
   git push origin main
   ```

2. **Restore database** (if needed):
   ```bash
   # PostgreSQL
   psql your_database < backup.sql
   
   # SQLite
   cp database.db.backup database.db
   ```

3. **Redeploy previous version**

4. **Communicate rollback** to users

5. **Fix issues** in development environment

6. **Prepare patch release** with fixes

## Release Notes Template

Use this template for GitHub releases:

```markdown
# CodeTuneStudio v1.0.0 - Genesis

**Release Date**: 2024-12-19
**Status**: Stable

## Highlights

[Brief description of major features or changes]

## What's New

### Features
- Feature 1
- Feature 2

### Improvements
- Improvement 1
- Improvement 2

### Bug Fixes
- Fix 1
- Fix 2

## Breaking Changes

[List any breaking changes and migration instructions]

## Installation

\`\`\`bash
pip install codetunestudio==1.0.0
\`\`\`

## Upgrade Instructions

[Include upgrade instructions]

## Known Issues

[List any known issues]

## Contributors

Thanks to all contributors who made this release possible!

## Full Changelog

See [CHANGELOG.md](CHANGELOG.md) for complete details.
```

## Checklist Sign-off

### Release Manager
- [ ] All pre-release checks completed
- [ ] Release approved
- [ ] Sign-off: _________________ Date: _________

### QA Lead
- [ ] All tests passed
- [ ] Manual testing completed
- [ ] Sign-off: _________________ Date: _________

### Security Lead
- [ ] Security review completed
- [ ] No critical vulnerabilities
- [ ] Sign-off: _________________ Date: _________

---

**Note**: This checklist should be reviewed and updated for each release cycle to reflect any changes in the release process.

**Last Updated**: 2024-12-19
**Version**: 1.0
