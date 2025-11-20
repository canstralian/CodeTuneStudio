# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CodeTuneStudio is a production-grade Streamlit/Flask hybrid application for ML model fine-tuning with parameter-efficient training (PEFT/LoRA), plugin architecture for extensible code analysis tools, and PostgreSQL/SQLite database backend for experiment tracking.

**Package Name**: `codetunestudio`  
**Version**: 1.0.0  
**CLI Command**: `codetune-studio`

## Core Architecture

### Package Structure
- **core/__init__.py**: Package initialization and exports
- **core/__version__.py**: Version management (semantic versioning)
- **core/server.py**: Server module (re-exports from app.py for modularity)
- **core/cli.py**: Command-line interface with argparse
- **app.py**: Main application logic (backward compatible entry point)

### Hybrid Framework Structure
- **app.py**: Main application logic orchestrating both Streamlit UI and Flask backend
- **core/cli.py**: Production CLI with `codetune-studio` command
- **Streamlit** handles the interactive web UI (port 7860 by default, configurable via CLI)
- **Flask** manages database operations via SQLAlchemy with connection pooling
- Database fallback: PostgreSQL (via DATABASE_URL env var) with automatic SQLite fallback

### Component System (components/)
UI components are modular Streamlit interfaces:
- `dataset_selector.py`: Dataset browsing with validation
- `parameter_config.py`: Training hyperparameter configuration
- `training_monitor.py`: Real-time training metrics visualization
- `experiment_compare.py`: Multi-experiment comparison
- `plugin_manager.py`: Dynamic plugin lifecycle management
- `tokenizer_builder.py`: Custom tokenizer creation
- `documentation_viewer.py`: In-app documentation browser

### Plugin Architecture (utils/plugins/)
Extensible tool system with dynamic discovery:
- **base.py**: `AgentTool` abstract base class with `ToolMetadata` and `execute()` pattern
- **registry.py**: `PluginRegistry` singleton for dynamic plugin discovery from `plugins/` directory
- Plugins must subclass `AgentTool` and implement `execute()` and `validate_inputs()`
- Registry auto-discovers plugins at startup via `discover_tools()`

Example plugin structure (see plugins/code_analyzer.py):
```python
class MyTool(AgentTool):
    def __init__(self):
        self.metadata = ToolMetadata(name="tool_name", description="...")
    def validate_inputs(self, inputs: Dict) -> bool: ...
    def execute(self, inputs: Dict) -> Dict: ...
```

### Database Schema (utils/database.py)
- **TrainingConfig**: Stores hyperparameters (model_type, dataset_name, batch_size, learning_rate, epochs, max_seq_length, warmup_steps)
- **TrainingMetric**: Time-series metrics (config_id FK, epoch, step, train_loss, eval_loss, process_rank for distributed training)
- Migrations managed via Flask-Migrate (manage.py)

### Training Infrastructure (utils/)
- **peft_trainer.py**: LoRA/PEFT wrapper with quantization support (bitsandbytes)
- **distributed_trainer.py**: Multi-GPU/distributed training orchestration
- **model_inference.py**: Model loading and inference utilities
- **model_versioning.py**: Experiment version control
- **visualization.py**: Plotly-based training curve generation

## Development Commands

### Running the Application
```bash
# Using the CLI (recommended for production)
codetune-studio

# With custom options
codetune-studio --port 8080 --host 0.0.0.0 --debug

# Using Python module
python -m core.cli

# Legacy method (backward compatible)
python app.py

# Alternative: Using Streamlit directly
streamlit run app.py
```

### Database Operations
```bash
# Initialize/reset database
DATABASE_URL="postgresql://user:pass@host/db" python app.py

# Run Flask CLI commands
python manage.py

# Database migrations (Flask-Migrate)
flask db init
flask db migrate -m "migration message"
flask db upgrade
```

### Testing & Linting
```bash
# Run tests (per CI pipeline)
python -m unittest discover -s tests

# Flake8 linting (critical errors only)
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

# Flake8 full check (non-blocking)
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics
```

### Hugging Face Deployment
```bash
# Login to HF Hub
huggingface-cli login --token $HF_TOKEN

# Push model (see .github/workflows/huggingface-deploy.yml)
huggingface-cli repo create my-model --type=model
huggingface-cli upload ./model_path --repo my-model
```

## Environment Variables
- **DATABASE_URL**: PostgreSQL connection string (falls back to `sqlite:///database.db`)
- **SPACE_ID**: Hugging Face Space identifier (affects UI layout)
- **SQL_DEBUG**: Enable SQLAlchemy query logging (set to any truthy value)

## Key Implementation Details

### Plugin Loading Flow
1. App initialization calls `_load_plugins()` in app.py:32
2. Clears existing registry to prevent duplicates
3. Calls `registry.discover_tools("plugins")`
4. Registry scans `plugins/*.py`, imports modules, finds `AgentTool` subclasses
5. Available tools stored in `registry._tools` dict and displayed in sidebar

### Database Connection Resilience
- Exponential backoff retry (3 attempts) in `_initialize_database_with_retry()` (app.py:64)
- Connection pooling: 10 base connections, 20 overflow, 30s timeout, 1800s recycle
- Auto-fallback to SQLite on PostgreSQL failure

### Training Configuration Workflow
1. User selects dataset via `dataset_browser()` → validates with `validate_dataset_name()`
2. User configures parameters via `training_parameters()` → returns config dict
3. Config validated via `validate_config()` (utils/config_validator.py)
4. Config saved to DB via `save_training_config()` → returns config_id
5. Config_id stored in `st.session_state.current_config_id` for tracking

### PEFT Training Pattern
Initialize `PEFTTrainer` with base model → applies LoRA config → optionally prepares for quantized training (4/8-bit) → returns trainable PEFT model with drastically reduced parameters

## Code Style
- PEP 8 compliant (Black formatter compatible)
- Max line length: 88 characters
- Type hints for function signatures
- Comprehensive logging with `logger.info/warning/error`
- Context managers for resource management (database sessions, GPU memory)

## CI/CD Pipelines
- **ci.yml**: Flake8 linting + unittest on push/PR to main
- **huggingface-deploy.yml**: Auto-deploy to HF Hub on main branch push (requires HF_TOKEN secret)
- **python-style-checks.yml**: Additional style validation
- Tests must pass before deployment triggers