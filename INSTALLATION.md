# CodeTuneStudio Installation Guide

This guide provides detailed installation instructions for CodeTuneStudio.

## Prerequisites

- Python 3.10 or higher
- pip (Python package installer)
- Git (for source installation)

## Installation Methods

### Method 1: Install from PyPI (Recommended)

Once published to PyPI, you can install CodeTuneStudio with:

```bash
pip install codetunestudio
```

### Method 2: Install from Source

#### For Users

1. Clone the repository:
```bash
git clone https://github.com/canstralian/CodeTuneStudio.git
cd CodeTuneStudio
```

2. Install the package:
```bash
pip install .
```

#### For Developers

1. Clone the repository:
```bash
git clone https://github.com/canstralian/CodeTuneStudio.git
cd CodeTuneStudio
```

2. Install in development mode with dev dependencies:
```bash
pip install -e ".[dev]"
```

This installs the package in editable mode, allowing you to make changes to the code and see them immediately without reinstalling.

## Running CodeTuneStudio

After installation, you can start CodeTuneStudio using the CLI:

```bash
codetune-studio
```

### CLI Options

```bash
codetune-studio --help          # Show help message
codetune-studio --version       # Show version
codetune-studio --port 8080     # Run on custom port (default: 7860)
codetune-studio --host 0.0.0.0  # Bind to all interfaces
codetune-studio --debug         # Enable debug logging
```

### Alternative Methods

You can also run CodeTuneStudio using:

```bash
# Using Python module
python -m core.cli

# Legacy method (if in source directory)
python app.py
```

## Environment Variables

CodeTuneStudio supports the following environment variables:

- `DATABASE_URL`: PostgreSQL connection string (optional, defaults to SQLite)
  ```bash
  export DATABASE_URL="postgresql://user:password@localhost:5432/codetunestudio"
  ```

- `SPACE_ID`: Hugging Face Space identifier (optional)
  ```bash
  export SPACE_ID="your-space-id"
  ```

- `SQL_DEBUG`: Enable SQLAlchemy query logging (optional)
  ```bash
  export SQL_DEBUG=1
  ```

## Verifying Installation

To verify that CodeTuneStudio is installed correctly:

1. Check the version:
```bash
codetune-studio --version
```

2. Import in Python:
```python
from core import __version__, MLFineTuningApp
print(f"CodeTuneStudio version: {__version__}")
```

## Troubleshooting

### ImportError: No module named 'codetunestudio'

This means the package is not installed. Try:
```bash
pip install --upgrade pip
pip install codetunestudio
```

### Port Already in Use

If port 7860 is already in use, specify a different port:
```bash
codetune-studio --port 8080
```

### Database Connection Issues

If you encounter database connection issues:

1. Check your DATABASE_URL environment variable
2. Ensure PostgreSQL is running (if using PostgreSQL)
3. CodeTuneStudio will automatically fall back to SQLite if PostgreSQL is unavailable

### Missing Dependencies

If you encounter missing dependencies:
```bash
pip install --upgrade -r requirements.txt
```

## Uninstallation

To uninstall CodeTuneStudio:

```bash
pip uninstall codetunestudio
```

## Getting Help

- Documentation: [README.md](README.md)
- Issues: [GitHub Issues](https://github.com/canstralian/CodeTuneStudio/issues)
- Discussions: [GitHub Discussions](https://github.com/canstralian/CodeTuneStudio/discussions)

## Next Steps

After installation, check out:
- [README.md](README.md) for an overview of features
- [CLAUDE.md](CLAUDE.md) for development and architecture details
- [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines
