# Changelog

All notable changes to CodeTuneStudio will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-12-19

### Release: Genesis (Stable)

First stable release of CodeTuneStudio with comprehensive ML model fine-tuning capabilities.

### Added

#### Core Features
- **ML Model Fine-tuning Framework**: Complete infrastructure for fine-tuning machine learning models with PEFT/LoRA support
- **Streamlit/Flask Hybrid Architecture**: Interactive web UI (Streamlit) with robust backend (Flask/SQLAlchemy)
- **PostgreSQL/SQLite Database Support**: Automatic fallback from PostgreSQL to SQLite with connection pooling
- **Plugin System**: Extensible architecture for code analysis tools
- **Dataset Management**: Support for Hugging Face datasets, Reddit datasets, and Argilla integration
- **Real-time Training Monitor**: Live metrics visualization with Plotly
- **Experiment Comparison**: Multi-experiment tracking and comparison
- **Custom Tokenizer Builder**: Build and upload tokenizers to Hugging Face

#### Components
- `dataset_selector.py`: Dataset browsing and validation
- `parameter_config.py`: Training hyperparameter configuration
- `training_monitor.py`: Real-time training metrics visualization
- `experiment_compare.py`: Multi-experiment comparison interface
- `plugin_manager.py`: Dynamic plugin lifecycle management
- `tokenizer_builder.py`: Custom tokenizer creation
- `documentation_viewer.py`: In-app documentation browser
- `model_export.py`: Model export and Hugging Face integration

#### Utilities
- `config_validator.py`: Comprehensive input validation with sanitization
- `database.py`: SQLAlchemy ORM models with migrations support
- `distributed_trainer.py`: Multi-GPU distributed training support
- `peft_trainer.py`: Parameter-efficient fine-tuning (LoRA, QLoRA)
- `model_versioning.py`: Git-based model version control
- `visualization.py`: Training metrics visualization utilities
- `reddit_dataset.py`: Reddit dataset management with amphigory augmentation
- `argilla_dataset.py`: Argilla dataset integration

#### Plugins
- `code_analyzer.py`: Python code structure and complexity analysis
- `anthropic_code_suggester.py`: AI-powered code suggestions using Claude
- `openai_code_analyzer.py`: Code analysis using GPT-4

#### Security Features
- Environment variable-based secrets management (no hardcoded credentials)
- Parameterized database queries via SQLAlchemy ORM
- Input validation and sanitization for all user inputs
- Output escaping in Streamlit components
- Secure API key handling for third-party services

#### Development Tools
- Comprehensive test suite with unittest
- CI/CD pipelines (GitHub Actions)
- Code style enforcement (Flake8, Black, Ruff)
- Type hints throughout codebase
- Detailed logging with structured format

#### Documentation
- `README.md`: Project overview and quick start
- `CLAUDE.md`: Development guide and architecture documentation
- `.github/copilot-instructions.md`: AI coding agent guidelines with security best practices
- Code-level docstrings following Google/NumPy style

### Changed
- Migrated from Gradio to Streamlit for improved UI/UX
- Enhanced database connection pooling for better performance
- Improved error handling with exponential backoff retry logic
- Updated dependencies to latest stable versions

### Security
- **Authentication**: Environment variable-based API key management
- **Input Validation**: Comprehensive validation for all configuration parameters
- **SQL Injection Prevention**: All queries use SQLAlchemy ORM or parameterized queries
- **XSS Prevention**: Output sanitization in web components
- **Secrets Management**: No hardcoded credentials, all secrets via environment variables

### Dependencies
- Python >= 3.9 (recommended 3.11+)
- Streamlit >= 1.26.0
- Flask >= 3.0.0
- SQLAlchemy >= 2.0.22
- PyTorch >= 2.2.0
- Transformers >= 4.48.0
- PEFT >= 0.14.0
- Accelerate >= 0.23.0
- PostgreSQL support via psycopg2-binary >= 2.9.7

### Fixed
- Database initialization race conditions
- Memory leaks in training loops
- Plugin discovery path issues
- CSS loading errors in Streamlit

### Infrastructure
- Docker support for containerized deployment
- Hugging Face Space deployment automation
- CI/CD with automated testing and style checks
- Database migrations with Flask-Migrate/Alembic

### Known Issues
- PyTorch installation may timeout on slow connections (use CPU-only builds for faster installation)
- Some tests require environment variables to be set (see test documentation)

### Breaking Changes
- None (initial stable release)

### Migration Guide
- Not applicable (initial release)

---

## Version History

### Pre-release Versions

Development versions (0.x.x) were used during initial development and are not documented here. 
Version 1.0.0 represents the first stable, production-ready release.

---

## Versioning Strategy

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR** version for incompatible API changes
- **MINOR** version for backwards-compatible functionality additions
- **PATCH** version for backwards-compatible bug fixes

---

## Upgrade Instructions

### From Development Version to 1.0.0

1. Back up your database:
   ```bash
   pg_dump your_database > backup.sql  # PostgreSQL
   # or
   cp database.db database.db.backup  # SQLite
   ```

2. Update dependencies:
   ```bash
   pip install -r requirements.txt --upgrade
   ```

3. Run database migrations:
   ```bash
   flask db upgrade
   ```

4. Update environment variables (see `.env.example`)

5. Test the application:
   ```bash
   python -m unittest discover -s tests
   ```

---

## Support

For issues, questions, or contributions, please visit:
- GitHub Issues: https://github.com/canstralian/CodeTuneStudio/issues
- Documentation: See CLAUDE.md and README.md

---

**Note**: This changelog is maintained by the CodeTuneStudio development team. 
All dates use ISO 8601 format (YYYY-MM-DD).
