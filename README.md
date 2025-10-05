# 🎵💻 CodeTuneStudio

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/canstralian/CodeTuneStudio/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-%3E%3D3.9-blue.svg)](https://www.python.org/downloads)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![CI Status](https://github.com/canstralian/CodeTuneStudio/actions/workflows/ci.yml/badge.svg)](https://github.com/canstralian/CodeTuneStudio/actions/workflows/ci.yml)
[![Hugging Face](https://img.shields.io/badge/🤗-Hugging%20Face-orange.svg)](https://huggingface.co/spaces/)

---

🎯 **Fine-tune. Experiment. Optimize Your ML Models.**

CodeTuneStudio is a comprehensive ML model fine-tuning platform with PEFT/LoRA support, plugin architecture for code analysis, and experiment tracking — all within an intuitive Streamlit interface.

---

## ✨ Features

### Core ML Capabilities
- 🚀 **Model Fine-tuning** — Parameter-efficient fine-tuning with PEFT, LoRA, and QLoRA support
- 📊 **Experiment Tracking** — PostgreSQL/SQLite-based experiment tracking with metrics visualization
- 🔄 **Distributed Training** — Multi-GPU distributed training with Accelerate
- 📈 **Real-time Monitoring** — Live training metrics with interactive Plotly visualizations
- 🎛️ **Hyperparameter Config** — Comprehensive training parameter configuration and validation

### Data & Dataset Management
- 🗂️ **Dataset Integration** — Hugging Face Datasets, Reddit datasets, and Argilla support
- 🔍 **Dataset Browser** — Interactive dataset exploration and validation
- 🎨 **Data Augmentation** — Amphigory code generation for dataset enhancement
- 🔤 **Tokenizer Builder** — Custom tokenizer creation and Hugging Face upload

### Extensibility & Tools
- 🧩 **Plugin Architecture** — Extensible plugin system for custom code analysis tools
- 🤖 **AI Code Analysis** — Integrated Claude (Anthropic) and GPT-4 (OpenAI) code analyzers
- 📝 **Code Analyzer** — Python code structure and complexity analysis
- 📦 **Model Export** — Export and publish models to Hugging Face Hub

### Developer Experience
- 🎨 **Streamlit UI** — Modern, responsive web interface
- 🔐 **Security-First** — Environment variable secrets, input validation, parameterized queries
- 📚 **Comprehensive Docs** — In-app documentation viewer with developer guides
- 🔄 **Version Control** — Git-based model versioning

---

## 🛠️ Prerequisites

### Required
- 🐍 **Python** 3.9 or higher (3.11+ recommended)
- 💾 **Database** (optional): PostgreSQL 12+ for production (SQLite fallback included)

### Optional (for plugins)
- 🤖 **OpenAI API Key** — For GPT-4 code analysis
- 🧠 **Anthropic API Key** — For Claude code suggestions
- 🤗 **Hugging Face Token** — For model/dataset downloads and uploads

---

## 📥 Installation

### Quick Start

1. **🔄 Clone the Repository:**

   ```bash
   git clone https://github.com/canstralian/CodeTuneStudio.git
   cd CodeTuneStudio
   ```

2. **📦 Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **⚙️ Configure Environment Variables:**

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **🗄️ Initialize Database:**

   ```bash
   # Optional: Set DATABASE_URL for PostgreSQL
   export DATABASE_URL="postgresql://user:password@localhost:5432/codetunestudio"
   
   # Database will initialize automatically on first run
   python app.py
   ```

5. **⚡ Run the Application:**
   ```bash
   python app.py
   ```

### Docker Installation (Optional)

```bash
# Build the image
docker build -t codetunestudio .

# Run the container
docker run -p 7860:7860 \
  -e DATABASE_URL="your_database_url" \
  -v $(pwd)/models:/app/models \
  codetunestudio
```

---

## 🌐 Usage

### Starting the Application

```bash
python app.py
```

The application will start and be available at: 👉 [http://localhost:7860](http://localhost:7860)

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Database (Required for production, optional for development)
DATABASE_URL=postgresql://user:password@localhost:5432/codetunestudio

# Optional: API Keys for plugins
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here

# Optional: Hugging Face integration
HF_TOKEN=hf_your-token-here

# Optional: Debug settings
SQL_DEBUG=False
```

See `.env.example` for a complete list of configuration options.

### Basic Workflow

1. **Select a Dataset** — Browse and select from Hugging Face datasets or custom sources
2. **Configure Training** — Set model architecture, batch size, learning rate, and other parameters
3. **Start Training** — Launch training with real-time monitoring
4. **Compare Experiments** — Analyze and compare multiple training runs
5. **Export Model** — Save and publish your fine-tuned model

---

## 📁 Project Structure

```
CodeTuneStudio/
├── app.py                      # 🚀 Main application entry point
├── version.py                  # 📌 Version management
├── manage.py                   # 🛠️ Flask CLI management commands
├── components/                 # 🧩 Streamlit UI components
│   ├── dataset_selector.py    # Dataset browsing and selection
│   ├── parameter_config.py    # Training parameter configuration
│   ├── training_monitor.py    # Real-time training metrics
│   ├── experiment_compare.py  # Experiment comparison
│   ├── plugin_manager.py      # Plugin management UI
│   ├── tokenizer_builder.py   # Custom tokenizer creation
│   ├── model_export.py        # Model export functionality
│   └── documentation_viewer.py # In-app documentation
├── utils/                      # 🛠️ Utility modules
│   ├── database.py            # SQLAlchemy models and DB init
│   ├── config_validator.py    # Input validation and sanitization
│   ├── distributed_trainer.py # Multi-GPU training support
│   ├── peft_trainer.py        # PEFT/LoRA training
│   ├── reddit_dataset.py      # Reddit dataset management
│   ├── argilla_dataset.py     # Argilla integration
│   ├── model_versioning.py    # Git-based model versioning
│   ├── model_inference.py     # Model inference utilities
│   ├── visualization.py       # Metrics visualization
│   └── plugins/               # Plugin system
│       ├── base.py            # Base plugin class
│       └── registry.py        # Plugin registry
├── plugins/                    # 🔌 Plugin implementations
│   ├── code_analyzer.py       # Python code analyzer
│   ├── anthropic_code_suggester.py  # Claude integration
│   └── openai_code_analyzer.py      # GPT-4 integration
├── tests/                      # 🧪 Test suite
├── migrations/                 # 📊 Database migrations (Alembic)
├── styles/                     # 🎨 Custom CSS
├── requirements.txt            # 📦 Python dependencies
├── pyproject.toml             # 🔧 Project configuration
├── setup.cfg                  # ⚙️ Tool configuration
├── Dockerfile                 # 🐳 Docker configuration
├── README.md                  # 📖 This file
├── CHANGELOG.md               # 📝 Version history
├── CLAUDE.md                  # 🤖 Development guide
├── DATABASE_MIGRATION_GUIDE.md # 🗄️ Migration documentation
└── RELEASE_CHECKLIST.md       # ✅ Release procedures
```

---

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python -m unittest discover -s tests

# Run specific test file
python -m unittest tests.test_app

# Run with verbose output
python -m unittest discover -s tests -v
```

### Linting and Code Quality

```bash
# Flake8 critical errors
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

# Flake8 full check
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics

# Type checking (if mypy installed)
mypy app.py utils/ components/
```

### Test Coverage

Current test coverage focuses on:
- Core application initialization
- Database operations and migrations
- Configuration validation
- Plugin system
- Code analysis tools

---

## 📚 Documentation

### User Documentation
- **README.md** (this file) — Quick start and overview
- **CLAUDE.md** — Detailed architecture and development guide
- **DATABASE_MIGRATION_GUIDE.md** — Database schema and migration procedures

### Developer Documentation
- **CHANGELOG.md** — Version history and release notes
- **RELEASE_CHECKLIST.md** — Release preparation procedures
- **`.github/copilot-instructions.md`** — AI coding agent guidelines

### API Documentation
All functions include comprehensive docstrings following Google/NumPy style. Use Python's built-in help:

```python
from utils.config_validator import validate_config
help(validate_config)
```

---

## 🔒 Security

CodeTuneStudio follows security best practices:

### Implemented Security Measures
- ✅ **Environment Variable Secrets** — No hardcoded credentials
- ✅ **Input Validation** — Comprehensive validation for all user inputs
- ✅ **Parameterized Queries** — All database queries use SQLAlchemy ORM
- ✅ **Output Sanitization** — XSS prevention in web components
- ✅ **Secure Dependencies** — Regular security audits with `safety`

### Security Guidelines
For detailed security practices, see `.github/copilot-instructions.md`

### Reporting Security Issues
Please report security vulnerabilities to the maintainers privately. Do not open public issues for security concerns.

---

## 🔄 Version History

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

**Current Version**: 1.0.0 (Genesis)
**Release Date**: 2024-12-19
**Status**: Stable

---

## 🛠️ Development

### Development Setup

1. Clone repository and install dependencies (see Installation)

2. Install development tools:
   ```bash
   pip install flake8 black mypy pytest safety
   ```

3. Configure pre-commit hooks (optional):
   ```bash
   pip install pre-commit
   pre-commit install
   ```

4. Run tests to verify setup:
   ```bash
   python -m unittest discover -s tests
   ```

### Database Migrations

```bash
# Create new migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Rollback migration
flask db downgrade
```

See [DATABASE_MIGRATION_GUIDE.md](DATABASE_MIGRATION_GUIDE.md) for detailed migration procedures.

### Plugin Development

Create custom plugins by extending `AgentTool`:

```python
from utils.plugins.base import AgentTool, ToolMetadata

class MyCustomTool(AgentTool):
    def __init__(self):
        super().__init__()
        self.metadata = ToolMetadata(
            name="my_custom_tool",
            description="Description of tool",
            version="0.1.0",
            author="Your Name",
            tags=["custom", "analysis"]
        )
    
    def validate_inputs(self, inputs):
        return "code" in inputs
    
    def execute(self, inputs):
        # Your tool logic here
        return {"result": "analysis"}
```

Place your plugin in the `plugins/` directory for automatic discovery.

---

## 🤝 Contributing

We welcome contributions! 🫶

### How to Contribute

1. 🍴 **Fork** the repository
2. 🔄 **Clone** your fork: `git clone https://github.com/YOUR_USERNAME/CodeTuneStudio.git`
3. 🌱 **Create a branch**: `git checkout -b feature/AmazingFeature`
4. ✅ **Make changes** and test thoroughly
5. 📝 **Commit**: `git commit -m 'Add some AmazingFeature'`
6. 📤 **Push**: `git push origin feature/AmazingFeature`
7. 📬 **Open a Pull Request**

### Contribution Guidelines

- Follow PEP 8 style guidelines (max line length: 88)
- Add tests for new features
- Update documentation
- Ensure all tests pass
- Include type hints for functions
- Write comprehensive docstrings

### Code Review Process

1. All PRs require at least one approval
2. CI/CD checks must pass
3. Code coverage should not decrease
4. Security review for sensitive changes

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines (if available).

---

## 📊 Roadmap

### Upcoming Features

- [ ] Web-based configuration editor
- [ ] Enhanced model comparison tools
- [ ] Additional plugin integrations
- [ ] Multi-user support with authentication
- [ ] Advanced scheduling for training jobs
- [ ] Integration with MLflow and Weights & Biases
- [ ] Support for additional model architectures
- [ ] Automated hyperparameter tuning

See [GitHub Issues](https://github.com/canstralian/CodeTuneStudio/issues) for feature requests and bug reports.

---

## 📜 License

This project is licensed under the **MIT License**.  
See the [LICENSE](LICENSE) file for details.

### Third-Party Licenses

This project uses several open-source libraries. See their respective licenses:
- Streamlit (Apache 2.0)
- Flask (BSD-3-Clause)
- PyTorch (BSD-style)
- Transformers (Apache 2.0)
- SQLAlchemy (MIT)

---

## 🙌 Acknowledgements

### Contributors

Thanks to all contributors who have helped make CodeTuneStudio possible!

### Built With

- [Streamlit](https://streamlit.io/) — Interactive web framework
- [Flask](https://flask.palletsprojects.com/) — Backend framework
- [PyTorch](https://pytorch.org/) — Deep learning framework
- [Hugging Face Transformers](https://huggingface.co/transformers/) — Model library
- [SQLAlchemy](https://www.sqlalchemy.org/) — Database ORM
- [PEFT](https://github.com/huggingface/peft) — Parameter-efficient fine-tuning

### Special Thanks

💖 Huge thanks to the open-source community for their continuous inspiration and support.

> _"Like music, code achieves perfection through fine-tuning."_ 🎵💻

---

## 📞 Support

### Getting Help

- 📖 **Documentation**: Check CLAUDE.md and this README
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/canstralian/CodeTuneStudio/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/canstralian/CodeTuneStudio/discussions)
- 📧 **Contact**: See GitHub profile for contact information

### Community

- ⭐ Star the project if you find it useful
- 🐦 Follow for updates
- 🤝 Join our community discussions

---

## 📈 Project Stats

![GitHub stars](https://img.shields.io/github/stars/canstralian/CodeTuneStudio?style=social)
![GitHub forks](https://img.shields.io/github/forks/canstralian/CodeTuneStudio?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/canstralian/CodeTuneStudio?style=social)

---

**Made with ❤️ by the CodeTuneStudio Team**

[⬆ Back to top](#-codetunestudio)
