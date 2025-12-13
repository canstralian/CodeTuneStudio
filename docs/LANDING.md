# CodeTuneStudio

**Fine-tune ML models with AI-powered code analysis in a plugin-based platform**

---

## 🎯 The Problem

AI-assisted ML workflows generate countless fine-tuning strategies, but validating which approach actually works—without breaking your codebase—requires tedious manual testing cycles. You need a system that can both analyze code improvements _and_ verify they work before deployment.

**CodeTuneStudio** is a hybrid Flask + Streamlit application that combines ML model fine-tuning with plugin-based code analysis powered by LLMs (OpenAI, Anthropic). Built for ML engineers and researchers who need a UI-first workflow to experiment with training configurations and get AI-powered code insights.

---

## ✅ What Exists Today

CodeTuneStudio provides a working end-to-end experience for ML fine-tuning with integrated code analysis:

### Core Capabilities
- **🚀 Interactive Web UI**: Streamlit-based interface (port 7860) for configuring and monitoring training jobs
- **🔌 Plugin Architecture**: Extensible system (`utils/plugins/`) for adding custom code analysis tools
  - OpenAI GPT-4 code analyzer (`plugins/openai_code_analyzer.py`)
  - Anthropic Claude code suggester (`plugins/anthropic_code_suggester.py`)
  - Dynamic plugin discovery and lifecycle management via registry
- **📊 Experiment Tracking**: PostgreSQL/SQLite database backend with SQLAlchemy ORM
  - Store training configurations (hyperparameters, dataset metadata)
  - Track time-series metrics (loss curves, distributed training stats)
  - Compare multiple experiments side-by-side
- **⚙️ Parameter-Efficient Training**: PEFT/LoRA support with bitsandbytes quantization
- **🎨 Component System**: Modular Streamlit UI components
  - Dataset browser with validation
  - Training parameter configurator
  - Real-time training monitor with Plotly visualizations
  - Plugin manager interface
  - Tokenizer builder
  - Documentation viewer
- **🔒 Security Posture**: Environment variable-based configuration, no hardcoded secrets, SQLAlchemy parameterized queries

### Stack
- **Backend**: Flask with SQLAlchemy ORM
- **UI**: Streamlit (hybrid architecture in single process)
- **Database**: PostgreSQL via `DATABASE_URL` with SQLite fallback
- **Entry Points**: 
  - `codetune-studio` CLI (primary, via `core.cli:main`)
  - `python app.py` legacy wrapper (calls `core.server.run_app`)
- **Source Layout**: `core/`, `components/`, `utils/`, `plugins/`, `tests/`

### CI/CD Discipline
- Flake8 linting enforced in CI
- Unit test suite (`tests/`)
- Pre-commit hooks available
- Hugging Face Hub deployment workflow

---

## 🚧 What's Being Built Next: Validation Pipeline MVP

The next milestone is a **strategy validation pipeline** that automates testing candidate code changes _before_ you apply them. This feature is currently **in-progress** and not yet available in the UI.

**Planned MVP Capabilities:**
- **Generate Candidates**: Use LLM plugins to produce multiple fine-tuning strategy candidates (patch/diff format)
- **Isolated Validation**: Apply each candidate in a sandboxed workspace and run:
  - `pytest` (existing test suite)
  - `ruff` / `flake8` (linting)
  - `mypy` (type checking)
- **UI Results**: Present validation results in Streamlit for side-by-side comparison
  - Which strategies pass tests?
  - Which introduce lint errors?
  - Detailed diff viewer
- **Export Patches**: Download validated patch files for manual application via `git apply`

**Status**: Design phase. Not yet implemented as a cohesive subsystem. Contributions welcome!

---

## 👥 Who This Is For

### ✅ Good Fit
- **ML Engineers**: Need a UI-first tool to experiment with fine-tuning hyperparameters and track results
- **Researchers**: Want LLM-powered code analysis integrated into their ML workflow
- **Platform Builders**: Looking for a plugin-based architecture to extend with custom analyzers
- **Experimenters**: Prefer interactive UIs over pure CLI tools for ML iteration

### ❌ Not a Good Fit (Yet)
- **Production ML Pipelines**: Currently optimized for experimentation, not production orchestration
- **Automated CI/CD Validation**: The validation pipeline MVP is not yet complete
- **Non-Python Codebases**: Plugin ecosystem is Python-focused

---

## 🚀 Try It in 5 Minutes (UI-First)

### Prerequisites
- Python 3.10 or higher
- PostgreSQL (optional, uses SQLite by default)

### Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/canstralian/CodeTuneStudio.git
   cd CodeTuneStudio
   ```

2. **Install the package:**
   ```bash
   pip install -e .
   ```

3. **Configure environment (optional for code analysis plugins):**
   ```bash
   # Copy example configuration
   cp .env.example .env
   
   # Edit .env to add your API keys (optional)
   # OPENAI_API_KEY=sk-...
   # ANTHROPIC_API_KEY=sk-ant-...
   # DATABASE_URL=postgresql://user:pass@localhost/dbname  # or leave blank for SQLite
   ```

4. **Launch the application:**
   ```bash
   codetune-studio
   ```
   
   **OR** (legacy method):
   ```bash
   python app.py
   ```

5. **Access the UI:**
   - Open your browser to [http://localhost:7860](http://localhost:7860)
   - Start configuring training jobs, exploring datasets, and using code analysis plugins!

### CLI Options

The `codetune-studio` command supports various options:

```bash
# Custom host/port
codetune-studio --host 0.0.0.0 --port 8080

# Debug mode
codetune-studio --log-level DEBUG

# Custom database
codetune-studio --database-url postgresql://user:pass@localhost/dbname

# Headless mode (no browser auto-open)
codetune-studio --no-browser

# Show version
codetune-studio --version
```

For full options, run:
```bash
codetune-studio --help
```

---

## 🔒 Security Expectations

CodeTuneStudio follows secure development practices:

- **No Secrets in Code**: All API keys and credentials are read from environment variables (`.env` file or system env)
- **Parameterized Queries**: SQLAlchemy ORM prevents SQL injection
- **Input Validation**: All user inputs are validated before processing
- **Least Privilege**: Database connections use connection pooling with timeouts
- **Dependency Scanning**: CI pipeline checks for known vulnerabilities

**Required Environment Variables for LLM Plugins:**
- `OPENAI_API_KEY` (optional): For OpenAI code analyzer plugin
- `ANTHROPIC_API_KEY` (optional): For Anthropic Claude suggester plugin
- `DATABASE_URL` (optional): PostgreSQL connection string (defaults to SQLite)
- `HF_TOKEN` (optional): For Hugging Face Hub deployments

**Security Best Practices:**
- Never commit `.env` files to version control (already in `.gitignore`)
- Rotate API keys regularly
- Use PostgreSQL with strong credentials for production
- Review plugin code before running (plugins have full system access via Python)

---

## 🤝 Join the Build (Early Builders Wanted!)

CodeTuneStudio is an active open-source project. We're especially looking for contributors to help build the **Validation Pipeline MVP**.

### Ways to Contribute
- **Code**: Implement MVP features, fix bugs, improve documentation
- **Plugins**: Create new code analysis plugins (see [Plugin Development Guide](PLUGIN_GUIDE.md))
- **Testing**: Run the app, report issues, suggest improvements
- **Documentation**: Improve guides, write tutorials, add examples

### Getting Started
1. Check [open issues](https://github.com/canstralian/CodeTuneStudio/issues) tagged `help wanted` or `good first issue`
2. Read [ARCHITECTURE.md](ARCHITECTURE.md) and [PLUGIN_GUIDE.md](PLUGIN_GUIDE.md)
3. Review [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md) and [CONTRIBUTING_CODE_QUALITY.md](CONTRIBUTING_CODE_QUALITY.md)
4. Fork, branch, code, test, and submit a PR!

**Particularly Needed:**
- Validation pipeline architecture design (see "What's Being Built Next" above)
- Isolated workspace sandboxing for patch testing
- UI components for comparing validation results
- Integration tests for end-to-end workflows

### Discussion & Support
- **Issues**: [https://github.com/canstralian/CodeTuneStudio/issues](https://github.com/canstralian/CodeTuneStudio/issues)
- **PRs**: [https://github.com/canstralian/CodeTuneStudio/pulls](https://github.com/canstralian/CodeTuneStudio/pulls)
- **Docs**: [https://github.com/canstralian/CodeTuneStudio/tree/main/docs](https://github.com/canstralian/CodeTuneStudio/tree/main/docs)

---

## 📚 Additional Resources

- **[README.md](../README.md)**: Full project overview and installation instructions
- **[ARCHITECTURE.md](ARCHITECTURE.md)**: Detailed system design and component documentation
- **[PLUGIN_GUIDE.md](PLUGIN_GUIDE.md)**: Create custom code analysis plugins
- **[CLAUDE.md](../CLAUDE.md)**: Development guidance for AI assistants
- **[CHANGELOG.md](../CHANGELOG.md)**: Version history and migration guides

---

## 📊 Current Status

- **Version**: 0.2.0
- **Status**: Beta (Experimental)
- **Python**: 3.10, 3.11, 3.12
- **License**: MIT
- **Maintainers**: [@canstralian](https://github.com/canstralian)

---

> _"Build ML tools that validate themselves before they ship."_ 🎵💻
