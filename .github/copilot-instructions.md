# CodeTuneStudio - Copilot Development Instructions

## Project Overview

**CodeTuneStudio** is an AI-powered code optimization and analysis platform built with Streamlit. It provides intelligent code analysis, performance optimization suggestions, and best practices recommendations through an interactive web interface. The platform supports multiple AI providers (OpenAI, Anthropic) and includes a plugin architecture for extensibility.

### High-Level Architecture
- **Type**: Web application with ML/AI capabilities  
- **Primary Language**: Python 3.8+
- **Web Framework**: Streamlit (main UI) with Flask (backend services)
- **Database**: SQLAlchemy with PostgreSQL/SQLite support
- **AI Integration**: OpenAI GPT-4, Anthropic Claude
- **Size**: ~30 Python files, medium-scale project
- **Target**: Code analysis, ML model fine-tuning, developer tools

## Build & Development Instructions

### Environment Setup
**ALWAYS start with these steps in order:**

1. **Prerequisites**: Python 3.8+ (tested with 3.9-3.12)

2. **Install Dependencies** (REQUIRED before any other operation):
```bash
pip install -r requirements.txt
```

**IMPORTANT**: `requirements.txt` is incomplete. You MUST also install:
```bash
pip install flask flask-sqlalchemy flask-migrate datasets argilla
pip install flake8 black pytest  # Development tools
```

3. **Environment Variables** (set before running app):
```bash
export DATABASE_URL="sqlite:///database.db"  # Default SQLite database
```

### Core Commands

#### Running the Application
```bash
python app.py
```
- **Port**: Default 5000 (configurable in `.streamlit/config.toml`)
- **Access**: http://localhost:5000
- **Startup Time**: ~10-15 seconds for initial load

#### Linting (ALWAYS run before committing)
```bash
# Critical errors only (CI requirement)
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

# Full style check
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics
```

#### Code Formatting
```bash
black . --line-length=88
```

### Database Management
```bash
# Flask database management
python manage.py db init     # Initialize migrations (first time only)
python manage.py db migrate  # Create migration
python manage.py db upgrade  # Apply migration

# Check database status
python db_check.py
```

### Validation Steps
1. **Dependencies**: Install requirements.txt + missing packages (flask, datasets, argilla, etc.)
2. **Critical Linting**: `flake8 . --count --select=E9,F63,F7,F82` must return 0 errors
3. **Database Check**: `python db_check.py` (may fail with SQLAlchemy text() issues - not critical)
4. **Import Test**: `python -c "import app"` should not raise ImportError (after all deps installed)

**Known Issues**:
- `requirements.txt` is missing ~8+ key dependencies (Flask, datasets, argilla, etc.)
- Many style violations exist (367 violations) but don't block functionality  
- Database initialization may fail without proper environment variables
- SQLAlchemy raw SQL queries need text() wrapper (modern SQLAlchemy requirement)

## Project Layout & Architecture

### Directory Structure
```
CodeTuneStudio/
├── app.py                 # Main Streamlit application entry point
├── components/            # UI components (Streamlit widgets)
│   ├── dataset_selector.py
│   ├── parameter_config.py
│   ├── training_monitor.py
│   ├── plugin_manager.py
│   └── tokenizer_builder.py
├── utils/                 # Core utilities and business logic
│   ├── database.py        # SQLAlchemy models and DB config
│   ├── config_validator.py # Training parameter validation
│   ├── plugins/           # Plugin system
│   │   ├── base.py       # Plugin base classes
│   │   └── registry.py   # Plugin registry
│   └── *.py              # Various utilities
├── plugins/              # AI provider implementations
│   ├── openai_code_analyzer.py    # OpenAI GPT integration
│   └── anthropic_code_suggester.py # Anthropic Claude integration
├── migrations/           # Database migrations (Flask-Migrate)
├── .streamlit/          # Streamlit configuration
│   └── config.toml      # Server config (port 5000, headless mode)
└── requirements.txt     # Python dependencies
```

### Key Configuration Files
- **`.flake8`**: Linting config (max-line-length=88, excludes)
- **`setup.cfg`**: MyPy type checking config (requires typing)
- **`pyproject.toml`**: Modern Python project config with dependencies
- **`.streamlit/config.toml`**: Streamlit server configuration
- **`Dockerfile`**: Container deployment config

### Main Entry Points
- **`app.py`**: Primary application (MLFineTuningApp class)
- **`manage.py`**: Flask CLI for database operations
- **`db_check.py`**: Database connectivity verification

### Plugin Architecture
- **Base Classes**: `utils/plugins/base.py` (AgentTool, ToolMetadata)
- **Registry**: `utils/plugins/registry.py` manages plugin discovery
- **AI Providers**: 
  - OpenAI: Uses `gpt-4o` model (latest as of May 2024)
  - Anthropic: Uses `claude-3-5-sonnet-20241022` model

## CI/CD Pipeline

### GitHub Workflows
1. **`.github/workflows/ci.yml`**: Main CI pipeline
   - Runs on push/PR to main
   - Python 3.9 environment
   - Steps: checkout → install deps → flake8 → test discovery

2. **`.github/workflows/python-style-checks.yml`**: Style validation
   - Runs flake8 with `--max-line-length=88`
   - Auto-commits style fixes on failure

3. **`.github/workflows/huggingface-deploy.yml`**: HuggingFace deployment
   - Python 3.10 environment  
   - Requires `HF_TOKEN` secret
   - Runs pytest for testing

### Validation Requirements
- **Flake8**: Zero critical errors (E9,F63,F7,F82) required for CI pass
- **Line Length**: Max 88 characters (Black formatter standard)
- **Import Style**: F401 ignored in `__init__.py` files

## Common Development Patterns

### Streamlit Components
- Components in `components/` return Streamlit widgets
- Use `@lru_cache` for expensive operations (see `dataset_selector.py`)
- Follow pattern: `st.subheader()` → form inputs → `st.button()` → processing

### Database Models
- SQLAlchemy models in `utils/database.py`
- Use `TrainingConfig` model for ML experiment tracking
- Connection pooling configured with `QueuePool`

### Plugin Development
1. Inherit from `AgentTool` base class
2. Implement `validate_inputs()` and `execute()` methods
3. Define `ToolMetadata` with name, description, version
4. Register in `utils/plugins/registry.py`

### Error Handling
- Use structured logging: `logging.getLogger(__name__)`
- Catch and log exceptions in plugin execution
- Return dict with `status: "error"/"success"` from plugins

## Environment Variables
- **`DATABASE_URL`**: Database connection (defaults to SQLite)
- **`OPENAI_API_KEY`**: Required for OpenAI plugin
- **`ANTHROPIC_API_KEY`**: Required for Anthropic plugin
- **`HF_TOKEN`**: HuggingFace API token for deployment

## File Listing (Repository Root)
- `app.py`, `manage.py`, `db_check.py` - Python entry points
- `requirements.txt`, `pyproject.toml`, `setup.cfg` - Dependency config
- `Dockerfile`, `replit.nix` - Deployment config
- `.flake8`, `.prettierignore` - Linting config
- `README.md`, `CODE_OF_CONDUCT.md`, `HUGGINGFACE.md` - Documentation
- `generated-icon.png` - Application icon (886KB)
- `uv.lock` - UV package manager lock file

## Important Notes

### Trust These Instructions
- These instructions are comprehensive and tested
- Only explore/search if information is incomplete or incorrect
- Command sequences have been validated in the actual environment

### Common Issues & Solutions
1. **Import Errors**: Run `pip install -r requirements.txt` first
2. **Database Errors**: Check `DATABASE_URL` environment variable
3. **Port Conflicts**: Default port 5000 can be changed in `.streamlit/config.toml`
4. **Plugin Errors**: Verify API keys are set for AI providers

### Dependencies Note
- `requirements.txt` is **incomplete** - missing Flask, datasets, argilla, and other core dependencies
- `pyproject.toml` has more complete dependency list with newer versions
- **Always install additional packages**: `flask flask-sqlalchemy flask-migrate datasets argilla`
- For development: `flake8 black pytest` for linting and testing tools

This project follows modern Python development practices with comprehensive CI/CD, plugin architecture, and AI integration. Always run linting before commits and test the Streamlit app startup to ensure changes don't break the core functionality.