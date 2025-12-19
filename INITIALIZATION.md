# CodeTuneStudio Initialization Guide

## Overview

This document provides a comprehensive guide for initializing and setting up the CodeTuneStudio development environment.

## Prerequisites

- **Python**: 3.10 or higher
- **Git**: Latest stable version
- **PostgreSQL** (optional): For production database (falls back to SQLite)
- **System Requirements**:
  - Minimum 4GB RAM
  - 10GB free disk space (for ML dependencies)

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/canstralian/CodeTuneStudio.git
cd CodeTuneStudio
```

### 2. Install Dependencies

#### Option A: Using pip (Recommended)

```bash
# Install from PyPI
pip install codetune-studio
```

#### Option B: Development Installation

```bash
# Install in editable mode with all dependencies
pip install -e .

# Or install from requirements.txt (minimal dependencies)
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the project root:

```bash
# Database Configuration
DATABASE_URL=postgresql://<user>:<password>@<host>:<port>/<database>
# Or use SQLite (default):
# DATABASE_URL=sqlite:///database.db

# Optional: Enable SQL query logging
SQL_DEBUG=1

# Hugging Face Integration (optional)
SPACE_ID=your-space-id

# API Keys (for plugins)
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
```

### 4. Database Initialization

```bash
# Initialize database with Flask-Migrate
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

Or use the automatic initialization:

```bash
python app.py  # Will auto-initialize database on first run
```

### 5. Verify Installation

```bash
# Test core module imports
python -c "import core, utils, components, plugins; print('✓ All modules loaded')"

# Run the test suite
python -m pytest tests/ -v

# Check code quality
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
```

### 6. Launch the Application

```bash
# Using the CLI (recommended)
codetune-studio

# Or using Python directly
python app.py

# With custom configuration
codetune-studio --host 0.0.0.0 --port 8080 --log-level DEBUG
```

The application will start on http://localhost:7860 by default.

## Project Structure

```
CodeTuneStudio/
├── app.py                  # Main application entry point
├── core/                   # Core functionality
│   ├── cli.py             # Command-line interface
│   ├── server.py          # Server orchestration
│   └── logging.py         # Logging configuration
├── components/             # Streamlit UI components
│   ├── dataset_selector.py
│   ├── parameter_config.py
│   ├── training_monitor.py
│   ├── experiment_compare.py
│   ├── plugin_manager.py
│   ├── tokenizer_builder.py
│   └── documentation_viewer.py
├── utils/                  # Utility modules
│   ├── database.py        # SQLAlchemy models
│   ├── peft_trainer.py    # PEFT/LoRA training
│   ├── distributed_trainer.py
│   ├── model_inference.py
│   ├── model_versioning.py
│   ├── visualization.py
│   ├── config_validator.py
│   └── plugins/           # Plugin infrastructure
│       ├── base.py        # AgentTool base class
│       └── registry.py    # Plugin discovery/management
├── plugins/                # Plugin implementations
│   ├── code_analyzer.py
│   ├── openai_code_analyzer.py
│   └── anthropic_code_suggester.py
├── tests/                  # Test suite
├── docs/                   # Documentation
├── migrations/             # Database migrations
└── models/                 # Saved model artifacts
```

## Architecture Overview

### Hybrid Framework Design

CodeTuneStudio runs as a hybrid Streamlit/Flask application:

- **Streamlit** (Port 7860): Interactive web UI for model training and visualization
- **Flask**: Database operations via SQLAlchemy with connection pooling
- **Single Process**: Both frameworks run in the same process for efficiency

### Database Configuration

**PostgreSQL** (Production):
```bash
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

Features:
- Connection pooling (10 base, 20 overflow connections)
- Automatic retry with exponential backoff
- 30-second timeout, 1800-second connection recycle

**SQLite** (Development):
```bash
DATABASE_URL=sqlite:///database.db
```

Automatic fallback if PostgreSQL unavailable.

### Plugin System

Plugins extend CodeTuneStudio with custom analysis tools:

1. **Base Class**: `AgentTool` in `utils/plugins/base.py`
2. **Registry**: `PluginRegistry` in `utils/plugins/registry.py`
3. **Discovery**: Automatic loading from `plugins/` directory at startup

**Creating a Plugin:**

```python
from utils.plugins.base import AgentTool, ToolMetadata
from typing import Dict

class MyAnalyzer(AgentTool):
    def __init__(self):
        self.metadata = ToolMetadata(
            name="my_analyzer",
            description="Analyzes code for specific patterns",
            version="1.0.0",
            author="Your Name"
        )

    def validate_inputs(self, inputs: Dict) -> bool:
        return "code" in inputs

    def execute(self, inputs: Dict) -> Dict:
        code = inputs["code"]
        # Your analysis logic here
        return {"result": "analysis_output"}
```

Place in `plugins/my_analyzer.py` for automatic discovery.

## Development Workflow

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_app.py -v

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html
```

### Code Quality

```bash
# Flake8 linting (CI configuration)
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

# Full linting check
flake8 . --count --max-complexity=10 --max-line-length=88 --statistics

# Pre-commit hooks
pre-commit install
pre-commit run --all-files
```

### Database Management

```bash
# Create new migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Rollback migration
flask db downgrade

# View migration history
flask db history
```

## CI/CD Pipeline

### GitHub Actions Workflows

1. **ci.yml**: Linting and testing on push/PR
2. **huggingface-deploy.yml**: Auto-deploy to Hugging Face Hub on main branch
3. **python-style-checks.yml**: Additional code style validation

### Required Secrets

- `HF_TOKEN`: Hugging Face API token for deployment

## Deployment

### Hugging Face Spaces

```bash
# Login to Hugging Face
huggingface-cli login --token $HF_TOKEN

# Push to Space
git push https://huggingface.co/spaces/USERNAME/SPACE_NAME main
```

### Docker

```bash
# Build image
docker build -t codetunestudio .

# Run container
docker run -p 7860:7860 \
  -e DATABASE_URL=postgresql://user:password@host/db \
  codetunestudio
```

## Troubleshooting

### Import Errors

```bash
# Ensure all dependencies are installed
pip install -e .

# Verify Python version
python --version  # Should be 3.10+
```

### Database Connection Issues

```bash
# Test PostgreSQL connection
psql -h localhost -U user -d codetunestudio

# Check SQLite database
sqlite3 database.db ".tables"

# View connection pool status
python db_check.py
```

### Plugin Not Loading

```bash
# Check plugin discovery
python -c "from utils.plugins.registry import PluginRegistry; r = PluginRegistry(); r.discover_tools('plugins'); print(r.list_tools())"

# Verify plugin syntax
python -m py_compile plugins/your_plugin.py
```

### Port Already in Use

```bash
# Kill process on port 7860
lsof -ti:7860 | xargs kill -9

# Or use a different port
codetune-studio --port 8080
```

## Next Steps

After initialization:

1. **Explore the UI**: Navigate to http://localhost:7860
2. **Load a Dataset**: Use the dataset selector component
3. **Configure Training**: Set hyperparameters in the parameter config
4. **Run Training**: Monitor progress in real-time
5. **Try Plugins**: Experiment with code analysis tools
6. **Review Documentation**: Check `docs/` for detailed guides

## References

- **Main Documentation**: [README.md](README.md)
- **Architecture Guide**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **Plugin Development**: [docs/PLUGIN_GUIDE.md](docs/PLUGIN_GUIDE.md)
- **Contributing**: [docs/CONTRIBUTING_CODE_QUALITY.md](docs/CONTRIBUTING_CODE_QUALITY.md)
- **System Contracts**: [SYSTEM.md](SYSTEM.md)
- **Quick Start**: [docs/LANDING.md](docs/LANDING.md)

## Support

For issues, questions, or contributions:
- **GitHub Issues**: https://github.com/canstralian/CodeTuneStudio/issues
- **Pull Requests**: https://github.com/canstralian/CodeTuneStudio/pulls
- **Documentation**: https://codetunestudio.readthedocs.io

---

**Initialization Complete!** You're ready to start fine-tuning ML models with CodeTuneStudio.
