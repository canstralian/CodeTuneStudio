# Changelog

All notable changes to CodeTune Studio will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

#### Repository Structure (Breaking Changes)
- **Source Code Organization**: Moved all Python source code to `src/` directory
  - All packages (`core`, `components`, `utils`, `models`, `plugins`, `migrations`) now under `src/`
  - Python scripts (`app.py`, `db_check.py`, `kali_server.py`, `manage.py`) moved to `src/`
  - Created `src/__init__.py` to make it a proper Python package
  - Updated all imports across the codebase to use `src.*` prefix
- **Configuration Files**: Moved to dedicated `config/` directory
  - `.env.example` → `config/.env.example`
  - `replit.nix` → `config/replit.nix`
  - `space.yaml` → `config/space.yaml`
- **Package Configuration**: Updated `pyproject.toml` for new structure
  - Entry point: `src.core.cli:main`
  - Version attribute: `src.core.__version__`
  - Package discovery: includes `src*` packages
  - Updated ruff/isort configuration for `src` as known-first-party
- **Test Suite**: Updated all test imports to use `src.*` prefix
- **Backward Compatibility**: Created root-level `app.py` wrapper for existing deployments
  - Maintains compatibility with `python app.py` usage
  - Shows deprecation warning directing users to new CLI
  - Imports from new `src.app` location

### Added

#### Documentation Improvements
- **Development Environment Setup**: Added comprehensive setup guides
  - VS Code setup with Python extension, linting, and formatting configuration
  - Replit setup with environment configuration and run instructions
  - Kali Linux setup with system dependencies and virtual environment
- **Project Structure**: Updated README with new directory layout
  - Clear visualization of `src/`, `config/`, `tests/`, `docs/` structure
  - Descriptions for each major directory and file
- **Configuration Documentation**: Added notes about `config/` directory usage
  - Environment variable templates location
  - Platform-specific configuration files

### Migration Guide

For developers and users migrating from version 0.2.0 or earlier:

1. **Update imports** in any custom code or plugins:
   ```python
   # Old (v0.2.0 and earlier)
   from core.server import MLFineTuningApp
   from utils.database import db
   from plugins.code_analyzer import CodeAnalyzerTool
   
   # New (v0.3.0+)
   from src.core.server import MLFineTuningApp
   from src.utils.database import db
   from src.plugins.code_analyzer import CodeAnalyzerTool
   ```

2. **Update configuration file paths**:
   ```bash
   # Old
   cp .env.example .env
   
   # New
   cp config/.env.example .env
   ```

3. **Preferred usage** (no changes needed):
   - CLI: `codetune-studio` (recommended, unchanged)
   - Package install: `pip install codetune-studio` (unchanged)

4. **Legacy usage** (still supported with deprecation warning):
   - `python app.py` - now shows deprecation warning
   - Redirects to `src.app.main()` automatically

## [0.2.0] - 2024-11-19

### Added

#### Package & Distribution
- **CLI Entrypoint**: Added `codetune-studio` command-line interface for easy application launch
  - Support for custom host and port configuration via CLI flags
  - Environment variable support for all configuration options
  - Automatic browser management with `--no-browser` flag
  - Version display with `--version` flag
- **Package Structure**: Refactored application into proper Python package
  - Created `core` module with `__init__.py`, `server.py`, `cli.py`, and `logging.py`
  - Version management through `core.__version__`
  - Dynamic version configuration in `pyproject.toml`
- **Console Script**: Defined `codetune-studio` entry point in `pyproject.toml` for pip installation

#### Infrastructure & Configuration
- **Centralized Logging**: New `core/logging.py` module with structured logging
  - Configurable log levels via environment variable or CLI flag
  - Color-coded console output for better readability
  - Rotating file handler support for production deployments
  - Separate formatters for console and file output
- **Enhanced Environment Configuration**: Comprehensive `.env.example` file
  - Application server settings (host, port, headless mode)
  - Database configuration with pool settings
  - Logging configuration
  - API keys for all supported plugins
  - Distributed training configuration
  - Security settings (secret key, CORS)
  - Performance tuning parameters
  - Feature flags

#### Documentation
- **CHANGELOG.md**: Version history tracking (this file)
- **Updated pyproject.toml**: 
  - Changed package name from `repl-nix-workspace` to `codetune-studio`
  - Added proper project metadata (description, authors, keywords, classifiers)
  - Configured dynamic versioning
  - Added dev dependencies (black, flake8, mypy, pytest)

### Changed

- **Application Entry Point**: Refactored `app.py` to be a lightweight compatibility layer
  - All application logic moved to `core.server.py`
  - Maintains backward compatibility for direct `python app.py` execution
  - Cleaner separation of concerns between CLI and server logic
- **Logging Configuration**: Moved from inline configuration to centralized module
  - Better log formatting with timestamps and source location
  - Support for multiple log handlers
- **Package Metadata**: Updated project name and metadata in `pyproject.toml`
  - Changed from generic `repl-nix-workspace` to `codetune-studio`
  - Added comprehensive project information for PyPI publication

### Fixed

- Restored corrupted `app.py` file that was replaced with HTML content

### Developer Experience

- Improved development workflow with proper package structure
- Better error handling and logging throughout the application
- Cleaner code organization for easier maintenance
- Enhanced configuration management with environment variables

### Migration Guide

For existing deployments:

1. **Update Environment Variables**: Review and update your `.env` file based on the new `.env.example`
2. **Install Updated Package**: Run `pip install -e .` to reinstall with new entry point
3. **Update Deployment Scripts**: 
   - Old: `streamlit run app.py`
   - New: `codetune-studio` (or continue using `python app.py` for compatibility)
4. **Docker**: Update Dockerfile CMD to use `codetune-studio` instead of direct streamlit invocation

### Breaking Changes

None - this release maintains full backward compatibility.

---

## [0.1.0] - Previous Release

Initial prototype release with core functionality:
- Streamlit-based web interface
- Flask backend with SQLAlchemy ORM
- Plugin architecture for code analysis tools
- Model training configuration and monitoring
- Dataset selection and validation
- Experiment comparison and tracking

---

[0.2.0]: https://github.com/canstralian/CodeTuneStudio/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/canstralian/CodeTuneStudio/releases/tag/v0.1.0
