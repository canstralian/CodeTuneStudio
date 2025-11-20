# Changelog

All notable changes to CodeTuneStudio will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-11-20

### Added

#### CLI Interface
- Created unified `codetune-studio` command-line interface
- Support for running Streamlit web interface (default command)
- Support for running Flask API backend (`codetune-studio flask`)
- Database management commands (`codetune-studio db check|init`)
- Version information command (`codetune-studio version`)
- Custom port and host configuration options
- Headless mode support for Streamlit

#### Packaging & Distribution
- Full pyproject.toml configuration with project metadata
- Console scripts entry point for CLI
- Dynamic version sourcing via `__version__.py`
- MANIFEST.in for proper file inclusion in distributions
- setup.py for backward compatibility
- Package discovery configuration for multi-package setup
- Classifiers and keywords for PyPI
- Project URLs (homepage, documentation, repository, issues)

#### CI/CD Pipeline
- Multi-stage CI workflow (`ci-enhanced.yml`):
  - Environment validation stage
  - Linting stage (flake8, black, ruff)
  - Testing stage with Python 3.10, 3.11, 3.12 matrix
  - Build and package stage
  - Installation testing stage
  - Security scanning stage (safety, bandit)
  - CI summary generation
- Automated release workflow (`release.yml`):
  - Version validation
  - Distribution building and testing
  - GitHub release creation with changelog
  - PyPI publication on tagged releases
  - Test PyPI publication for pre-releases
- Artifact management with retention policies
- Workflow status summaries

#### Testing
- Comprehensive CLI test suite (17 tests)
- Tests for all CLI commands and options
- Tests for error handling and edge cases
- Mock-based testing for external dependencies
- Integration tests for CLI behavior

#### Documentation
- Updated README with CLI usage instructions
- Installation instructions for PyPI and source
- CLI command reference and examples
- CHANGELOG.md for version tracking

### Changed

- Recreated `app.py` as proper Python module (was HTML file)
- Enhanced pyproject.toml with production-ready configuration
- Moved HTML landing page to `index_old.html`
- Updated README with new installation and usage methods
- Improved package structure with codetunestudio package

### Fixed

- Package discovery issues in setuptools configuration
- Import errors when running CLI as script
- Linting errors (flake8 compliance)
- Test compatibility issues

### Technical Details

#### Package Structure
```
codetunestudio/
├── __init__.py          # Package initialization
├── __version__.py       # Version management
└── cli.py               # CLI implementation
```

#### CLI Commands
```bash
codetune-studio                    # Start Streamlit (default)
codetune-studio streamlit          # Start Streamlit explicitly
codetune-studio flask              # Start Flask backend
codetune-studio db check           # Check database connection
codetune-studio db init            # Initialize database
codetune-studio version            # Show version
```

#### CI/CD Features
- Parallel testing across Python versions
- Automatic artifact upload and retention
- Security vulnerability scanning
- Code quality checks (linting, formatting)
- Installation verification
- Comprehensive status reporting

### Security

- Added security scanning with safety and bandit
- No hardcoded secrets or credentials
- Proper error handling and logging
- Input validation throughout CLI

---

## [0.1.0] - Previous Release

Initial release with basic functionality.

[0.2.0]: https://github.com/canstralian/CodeTuneStudio/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/canstralian/CodeTuneStudio/releases/tag/v0.1.0
