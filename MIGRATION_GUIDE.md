# Migration Guide: v0.1.0 → v0.2.0

This guide helps you migrate from CodeTuneStudio v0.1.0 to v0.2.0 with the new CLI interface and improved architecture.

## Overview of Changes

Version 0.2.0 introduces a unified command-line interface (`codetune-studio`) and production-ready packaging. The core functionality remains the same, but the way you start and interact with the application has improved.

## Installation

### Old Method (v0.1.0)
```bash
git clone https://github.com/canstralian/CodeTuneStudio.git
cd CodeTuneStudio
pip install -r requirements.txt
python app.py
```

### New Method (v0.2.0)

#### Option 1: Install from PyPI (Recommended)
```bash
pip install codetunestudio
codetune-studio
```

#### Option 2: Install from source
```bash
git clone https://github.com/canstralian/CodeTuneStudio.git
cd CodeTuneStudio
pip install -e .
codetune-studio
```

## Running the Application

### Old Method (v0.1.0)
```bash
# Start Streamlit
python app.py

# Start Flask (via manage.py)
python manage.py run
```

### New Method (v0.2.0)
```bash
# Start Streamlit interface (default)
codetune-studio

# Start Streamlit with custom port
codetune-studio --port 8080

# Start Flask API backend
codetune-studio flask --port 5000

# Get help
codetune-studio --help
```

## Database Management

### Old Method (v0.1.0)
```bash
# Check database
python db_check.py

# Flask database commands
python manage.py db init
python manage.py db migrate
python manage.py db upgrade
```

### New Method (v0.2.0)
```bash
# Check database connection
codetune-studio db check

# Initialize database
codetune-studio db init

# Flask-Migrate commands (still available)
flask db migrate -m "description"
flask db upgrade
```

## Environment Variables

No changes required. All environment variables work the same way:

```bash
# Database configuration
export DATABASE_URL="postgresql://user:pass@localhost/db"

# Or use SQLite (default)
export DATABASE_URL="sqlite:///database.db"

# Space ID (for Hugging Face deployment)
export SPACE_ID="your-space-id"
```

## Breaking Changes

### None for End Users

The v0.2.0 update is **fully backward compatible** for standard usage:
- `python app.py` still works
- All existing environment variables are respected
- Database schema unchanged
- API endpoints unchanged

### For Developers/Contributors

If you're developing or contributing:

1. **Import Paths**: If you import from the package, use:
   ```python
   from codetunestudio import __version__
   ```

2. **CLI Extension**: To add new CLI commands, extend `codetunestudio/cli.py`

3. **Testing**: New test infrastructure expects pytest:
   ```bash
   pip install pytest pytest-mock
   pytest tests/
   ```

## New Features

### CLI Commands

```bash
# Show version
codetune-studio version

# Get detailed help
codetune-studio --help
codetune-studio streamlit --help
codetune-studio flask --help
codetune-studio db --help
```

### Package Management

```bash
# Install with development dependencies
pip install codetunestudio[dev]

# Install with test dependencies
pip install codetunestudio[test]

# Install with documentation dependencies
pip install codetunestudio[docs]
```

## Troubleshooting

### Issue: `codetune-studio` command not found

**Solution**: Ensure the package is properly installed:
```bash
pip install --upgrade codetunestudio
# or for editable install from source:
pip install -e .
```

### Issue: Import errors

**Solution**: Install all dependencies:
```bash
pip install -r requirements.txt
```

### Issue: Database connection errors

**Solution**: Check database configuration and initialize:
```bash
codetune-studio db check
codetune-studio db init
```

### Issue: Port already in use

**Solution**: Specify a different port:
```bash
codetune-studio --port 8080
```

## Rollback Procedure

If you need to rollback to v0.1.0:

```bash
# Uninstall v0.2.0
pip uninstall codetunestudio

# Checkout previous version
git checkout v0.1.0

# Install dependencies
pip install -r requirements.txt

# Run with old method
python app.py
```

## Questions and Support

- **Documentation**: [README.md](README.md)
- **Issues**: [GitHub Issues](https://github.com/canstralian/CodeTuneStudio/issues)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)

## Summary

The migration to v0.2.0 is **seamless** for most users:
- ✅ Install from PyPI or source
- ✅ Use new `codetune-studio` command
- ✅ Enjoy improved CLI and enhanced CI/CD
- ✅ Maintain all existing functionality

**No database migrations or configuration changes required!**
