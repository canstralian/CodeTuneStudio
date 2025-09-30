# Release Guide for CodeTuneStudio

This document outlines the release process for CodeTuneStudio.

## Release Checklist

### Pre-Release

- [ ] All tests passing (`make test`)
- [ ] Code linted and formatted (`make lint && make format`)
- [ ] CHANGELOG.md updated with release notes
- [ ] Version bumped in `pyproject.toml`
- [ ] Documentation updated (README.md, CLAUDE.md)
- [ ] All open critical/high priority issues resolved
- [ ] Security audit completed (`make security-check`)
- [ ] Dependencies reviewed and updated if needed

### Release Preparation

1. **Create Release Branch**
   ```bash
   git checkout -b release/v0.1.0
   ```

2. **Update Version**
   - Edit `pyproject.toml` to set version number
   - Follow semantic versioning (MAJOR.MINOR.PATCH)

3. **Update CHANGELOG.md**
   - Add release date
   - Ensure all changes are documented
   - Follow Keep a Changelog format

4. **Commit Changes**
   ```bash
   git add pyproject.toml CHANGELOG.md
   git commit -m "chore: prepare release v0.1.0"
   ```

5. **Run Pre-Release Checks**
   ```bash
   make release-check
   ```

### Creating the Release

1. **Merge to Main**
   ```bash
   git checkout main
   git merge release/v0.1.0
   ```

2. **Create and Push Tag**
   ```bash
   git tag -a v0.1.0 -m "Release v0.1.0"
   git push origin main --tags
   ```

3. **GitHub Actions** will automatically:
   - Build distribution packages
   - Create GitHub Release with changelog
   - Upload wheels and source dist
   - Publish to PyPI (for stable releases)
   - Publish to Test PyPI (for pre-releases)

### Post-Release

1. **Verify Release**
   - Check GitHub Releases page
   - Verify PyPI package page
   - Test installation: `pip install codetunestudio==0.1.0`

2. **Update Documentation**
   - Announce on GitHub Discussions
   - Update any external documentation
   - Post on social media if applicable

3. **Monitor Issues**
   - Watch for installation problems
   - Track bug reports related to new release
   - Be ready for hotfix if critical issues found

## Version Numbering

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR** version (1.0.0): Incompatible API changes
- **MINOR** version (0.1.0): Add functionality (backwards compatible)
- **PATCH** version (0.1.1): Bug fixes (backwards compatible)

### Pre-Release Versions

- **Alpha** (0.1.0-alpha.1): Early testing, unstable
- **Beta** (0.1.0-beta.1): Feature complete, testing
- **RC** (0.1.0-rc.1): Release candidate, final testing

## Building Locally

### Test Build

```bash
# Clean previous builds
make clean

# Build packages
make build

# Check build
make build-check
```

### Test PyPI Upload

```bash
# Upload to Test PyPI (requires credentials)
make publish-test

# Test installation
pip install --index-url https://test.pypi.org/simple/ codetunestudio
```

### PyPI Upload

```bash
# Upload to PyPI (requires credentials)
make publish

# Verify
pip install codetunestudio
```

## GitHub Release Workflow

The `.github/workflows/release.yml` workflow triggers on tags matching `v*.*.*`:

1. **Tag Detection**: Triggers when tag is pushed
2. **Build**: Creates wheel and source distribution
3. **Validation**: Runs twine check on distributions
4. **Release Creation**: Creates GitHub release with changelog
5. **Package Upload**: Uploads artifacts to release
6. **PyPI Publish**:
   - Stable tags → PyPI
   - Pre-release tags → Test PyPI

## Required Secrets

Set these in GitHub repository settings:

- `PYPI_API_TOKEN`: PyPI API token for publishing
- `TEST_PYPI_API_TOKEN`: Test PyPI API token (optional)

### Getting PyPI Tokens

1. Create account on [PyPI](https://pypi.org/)
2. Verify email address
3. Enable 2FA (recommended)
4. Go to Account Settings → API Tokens
5. Create new token with:
   - Name: "GitHub Actions - CodeTuneStudio"
   - Scope: "Entire account" or specific project
6. Copy token and add to GitHub Secrets

## Hotfix Release Process

For critical bugs in production:

1. **Create Hotfix Branch**
   ```bash
   git checkout -b hotfix/v0.1.1 v0.1.0
   ```

2. **Fix the Issue**
   ```bash
   # Make necessary changes
   git commit -m "fix: critical bug description"
   ```

3. **Update Version** (patch increment)
   - Edit `pyproject.toml`: version = "0.1.1"
   - Update CHANGELOG.md with hotfix notes

4. **Merge and Release**
   ```bash
   git checkout main
   git merge hotfix/v0.1.1
   git tag -a v0.1.1 -m "Hotfix v0.1.1"
   git push origin main --tags
   ```

## Rollback Procedure

If a release has critical issues:

1. **Yank from PyPI** (doesn't delete, marks as unavailable)
   ```bash
   pip install twine
   twine yank codetunestudio -v 0.1.0
   ```

2. **Delete GitHub Release** (if needed)
   - Go to Releases page
   - Delete the problematic release
   - Optionally delete the tag

3. **Prepare Hotfix**
   - Follow hotfix release process
   - Document what went wrong

## Versioning Strategy

### Current Phase: 0.x.x (Pre-1.0)

- Breaking changes allowed in minor versions
- Focus on stabilization and feedback
- Rapid iteration acceptable

### Post-1.0 Phase

- Strict semantic versioning
- Breaking changes only in major versions
- Long-term stability commitment

## Release Schedule

### Regular Releases
- **Minor releases**: Every 4-6 weeks
- **Patch releases**: As needed for bugs
- **Major releases**: When breaking changes accumulated

### Emergency Releases
- Critical security fixes: Within 24 hours
- Major bugs: Within 1 week
- Minor bugs: Next scheduled release

## Communication

### Release Announcements

1. **GitHub Release**: Automated with changelog
2. **GitHub Discussions**: Manual announcement post
3. **README badges**: Automatically updated
4. **Social media**: Optional, for major releases

### Template for Announcements

```markdown
🎉 CodeTuneStudio v0.1.0 Released!

We're excited to announce the release of CodeTuneStudio v0.1.0!

## Highlights
- Feature 1
- Feature 2
- Feature 3

## Installation
```bash
pip install codetunestudio
```

## Full Changelog
[View full changelog](link-to-changelog)

## Upgrade Guide
[View upgrade guide](link-if-applicable)

Thank you to all contributors!
```

## FAQ

**Q: What if CI fails after tagging?**
A: Delete the tag locally and remotely, fix the issue, and re-tag.

```bash
git tag -d v0.1.0
git push origin :refs/tags/v0.1.0
```

**Q: Can I test the release process?**
A: Yes, use alpha/beta tags to publish to Test PyPI without affecting production.

**Q: What if PyPI upload fails?**
A: Re-run the workflow or upload manually with `make publish`.

**Q: How do I deprecate a feature?**
A: Add deprecation warnings, document in changelog, remove in next major version.

---

**Last Updated**: 2025-09-30
**Next Review**: Before v0.2.0 release
