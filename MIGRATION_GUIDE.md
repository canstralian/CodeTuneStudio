# Migration Guide: v0.x to v1.0.0

This guide helps existing users migrate from the prototype version to the production-ready v1.0.0.

## What's Changed

### Package Name
- **Old**: Not published as a package
- **New**: `codetunestudio` (PyPI package)

### Running the Application

#### Old Way (Still Works)
```bash
python app.py
```

#### New Way (Recommended)
```bash
# Install the package first
pip install codetunestudio

# Then run with CLI
codetune-studio
```

## Installation Changes

### Before v1.0.0
```bash
git clone https://github.com/canstralian/CodeTuneStudio.git
cd CodeTuneStudio
pip install -r requirements.txt
python app.py
```

### After v1.0.0
```bash
# Option 1: Install from PyPI (when published)
pip install codetunestudio
codetune-studio

# Option 2: Install from source
git clone https://github.com/canstralian/CodeTuneStudio.git
cd CodeTuneStudio
pip install -e .
codetune-studio
```

## New Features in v1.0.0

### 1. CLI Interface
```bash
# Show version
codetune-studio --version

# Custom port
codetune-studio --port 8080

# Bind to all interfaces
codetune-studio --host 0.0.0.0

# Enable debug logging
codetune-studio --debug

# Get help
codetune-studio --help
```

### 2. Package Structure
The application now has a proper package structure:
```
codetunestudio/
├── core/              # Core modules
│   ├── __init__.py
│   ├── __version__.py
│   ├── server.py
│   └── cli.py
├── components/        # UI components
├── utils/             # Utilities
└── app.py            # Main application (backward compatible)
```

### 3. Python Import
You can now import CodeTuneStudio as a package:
```python
from core import __version__, MLFineTuningApp

print(f"Version: {__version__}")
app = MLFineTuningApp()
```

## Breaking Changes

### None! 
This release is fully backward compatible:
- ✅ `python app.py` still works
- ✅ All existing imports work
- ✅ All environment variables work
- ✅ All database configurations work
- ✅ All plugins work

## Upgrade Steps

### For Users
1. **Install the new version:**
   ```bash
   pip install codetunestudio
   ```

2. **Start using the CLI:**
   ```bash
   codetune-studio
   ```

3. **Optional:** Update any scripts that use `python app.py` to use `codetune-studio`

### For Developers
1. **Update your development setup:**
   ```bash
   cd CodeTuneStudio
   pip install -e ".[dev]"
   ```

2. **Use the new CLI during development:**
   ```bash
   codetune-studio --debug
   ```

3. **Run tests:**
   ```bash
   pytest tests/
   ```

## Configuration Changes

### Environment Variables
No changes required. All existing environment variables work:
- `DATABASE_URL`
- `SPACE_ID`
- `SQL_DEBUG`

### Database
No migration required. All existing databases work with v1.0.0.

### Plugins
No changes required. All existing plugins work with v1.0.0.

## Testing Your Migration

After upgrading, verify everything works:

1. **Check version:**
   ```bash
   codetune-studio --version
   # Should show: CodeTuneStudio 1.0.0
   ```

2. **Start the application:**
   ```bash
   codetune-studio
   # Should start on http://localhost:7860
   ```

3. **Test database connection:**
   ```bash
   python db_check.py
   # Should show: Database connection successful!
   ```

4. **Run tests:**
   ```bash
   pytest tests/
   # Should pass all tests
   ```

## Common Issues

### Issue: `codetune-studio` command not found
**Solution:** Install the package:
```bash
pip install codetunestudio
```

### Issue: Port already in use
**Solution:** Use a different port:
```bash
codetune-studio --port 8080
```

### Issue: Import errors after upgrade
**Solution:** Reinstall with:
```bash
pip uninstall codetunestudio
pip install codetunestudio
```

## Rollback

If you need to rollback to the old version:

1. Uninstall v1.0.0:
   ```bash
   pip uninstall codetunestudio
   ```

2. Use the old method:
   ```bash
   python app.py
   ```

## Getting Help

If you encounter any issues during migration:

1. Check the [INSTALLATION.md](INSTALLATION.md) guide
2. Review [README.md](README.md) for updated documentation
3. Open an issue on [GitHub](https://github.com/canstralian/CodeTuneStudio/issues)

## What's Next

After migrating, check out:
- New CLI features with `codetune-studio --help`
- Updated documentation in [CLAUDE.md](CLAUDE.md)
- Installation guide in [INSTALLATION.md](INSTALLATION.md)

## Feedback

We'd love to hear about your migration experience! Please:
- Report any issues on GitHub
- Share feedback in discussions
- Contribute improvements via pull requests

---

**Thank you for using CodeTuneStudio!** 🎉
