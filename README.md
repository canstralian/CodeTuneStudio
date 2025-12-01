# 🎵💻 CodeTuneStudio

[![PyPI version](https://badge.fury.io/py/codetunestudio.svg)](https://pypi.org/project/codetunestudio/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-%3E%3D3.10-blue.svg)](https://www.python.org/downloads)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Documentation Status](https://readthedocs.org/projects/codetunestudio/badge/?version=latest)](https://codetunestudio.readthedocs.io/en/latest/)
[![Hugging Face Model CI/CD](https://github.com/canstralian/CodeTuneStudio/actions/workflows/huggingface-deploy.yml/badge.svg)](https://github.com/canstralian/CodeTuneStudio/actions/workflows/huggingface-deploy.yml)

---

🎯 **Optimize. Enhance. Perfect Your Code.**

CodeTuneStudio is your all-in-one platform for intelligent code analysis, performance optimization, and coding best practices — all within an intuitive Gradio-powered interface.

---

## ✨ Features

- ⚡ **Code Analysis** — Advanced static code analysis for multiple programming languages.
- 🚀 **Performance Optimization** — Smart suggestions to boost code efficiency.
- 🧑‍💻 **Best Practices** — Automated recommendations for cleaner, standard-compliant code.
- 🎨 **Interactive Interface** — Gradio-powered UI for an intuitive developer experience.

---

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed:

- 🐍 **Python** 3.10 or higher

---

## 📥 Installation

### Via pip (Recommended)

Install CodeTune Studio from PyPI:

```bash
pip install codetune-studio
```

### From Source

For development or the latest features:

1. **🔄 Clone the Repository:**

   ```bash
   git clone https://github.com/canstralian/CodeTuneStudio.git
   cd CodeTuneStudio
   ```

2. **📦 Install in Development Mode:**

   ```bash
   pip install -e .
   ```

---

## 🌐 Usage

### Quick Start

Simply run the CLI command:

```bash
codetune-studio
```

The application will start on [http://localhost:7860](http://localhost:7860) 🚀

### CLI Options

```bash
# Custom host and port
codetune-studio --host 0.0.0.0 --port 8501

# Enable debug logging
codetune-studio --log-level DEBUG

# Headless mode (no browser auto-open)
codetune-studio --no-browser

# Custom database
codetune-studio --database-url postgresql://user:pass@localhost/dbname

# Show version
codetune-studio --version

# Get help
codetune-studio --help
```

### Environment Variables

Alternatively, configure via environment variables in a `.env` file:

```bash
# Copy the example configuration
cp .env.example .env

# Edit with your settings
# Required: API keys for code analysis plugins
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here

# Optional: Database configuration
DATABASE_URL=postgresql://user:pass@localhost/dbname
LOG_LEVEL=INFO
HOST=localhost
PORT=7860
```

### Legacy Usage (Backward Compatible)

You can still run directly with Python:

```bash
python app.py
```

Or with Streamlit:

```bash
streamlit run app.py --server.port=7860
```

---

## 📁 Project Structure

```
CodeTuneStudio/
├── core/                   # 🎯 Core application modules
│   ├── __init__.py        # Version and exports
│   ├── cli.py             # Command-line interface
│   ├── server.py          # Application server logic
│   └── logging.py         # Centralized logging
├── components/             # 🧩 Streamlit UI components
├── utils/                  # 🛠️ Utility functions
│   ├── database.py        # Database models and operations
│   ├── plugins/           # Plugin system
│   └── ...                # Various utilities
├── plugins/                # 🔌 Extensible code analysis plugins
├── tests/                  # 🧪 Test suite
├── docs/                   # 📚 Documentation
│   ├── ARCHITECTURE.md    # System architecture
│   └── PLUGIN_GUIDE.md    # Plugin development guide
├── app.py                  # 🚀 Legacy entrypoint (backward compatible)
├── requirements.txt        # 📦 Project dependencies
├── pyproject.toml          # 📋 Package configuration
├── CHANGELOG.md            # 📝 Version history
└── README.md               # 📖 This file
```

---

## 📚 Documentation

- **[Architecture Guide](docs/ARCHITECTURE.md)** - System design and component overview
- **[Plugin Development Guide](docs/PLUGIN_GUIDE.md)** - Create custom code analysis plugins
- **[Changelog](CHANGELOG.md)** - Version history and migration guides
- **[Contributing Guidelines](CONTRIBUTING.md)** - How to contribute to the project

---

## 🔌 Plugin System

CodeTune Studio features an extensible plugin architecture for code analysis:

- **Built-in Plugins**: OpenAI, Anthropic Claude integration
- **Custom Plugins**: Easily create your own analyzers
- **Hot Reloading**: Plugins are discovered automatically

See the [Plugin Development Guide](docs/PLUGIN_GUIDE.md) for details.

---

## 🤝 Contributing

We welcome contributions! 🫶  
Feel free to check out the [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to get involved.

### Code Quality

We maintain high code quality standards using automated tools:

- 🎨 **Code Formatting**: [Black](https://github.com/psf/black) with 88 character line length
- ⚡ **Modern Linting**: [Ruff](https://github.com/astral-sh/ruff) for fast, comprehensive code checks
- 🔍 **Legacy Linting**: [Flake8](https://flake8.pycqa.org/) for PEP 8 compliance
- 🪝 **Pre-commit Hooks**: Automated checks before each commit (Black + Ruff)

**Quick Setup:**
```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Or use the setup script
./scripts/setup-pre-commit.sh
```

**Run manually:**
```bash
# Format code with Black
black .

# Check and fix with Ruff
ruff check . --fix

# Run all pre-commit hooks
pre-commit run --all-files
```

For detailed information, see [Code Quality Guidelines](docs/CONTRIBUTING_CODE_QUALITY.md).

### Contributing Workflow

1. 🍴 Fork the repository
2. 💡 Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. 🔧 Set up pre-commit hooks (`./scripts/setup-pre-commit.sh`)
4. ✅ Commit your changes (`git commit -m 'Add some AmazingFeature'`)
5. 📤 Push to the branch (`git push origin feature/AmazingFeature`)
6. 📬 Open a Pull Request

### Development Setup

```bash
# Clone and setup for development
git clone https://github.com/canstralian/CodeTuneStudio.git
cd CodeTuneStudio

# Install with development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Check code style
ruff check .
black --check .

# Run type checker
mypy core/
```

---

## 📜 License

This project is licensed under the **MIT License**.  
See the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

💖 Huge thanks to the open-source community for their continuous inspiration and support.

Special thanks to:
- **Streamlit** for the amazing web framework
- **Hugging Face** for transformers and model hosting
- **OpenAI** and **Anthropic** for AI capabilities
- All our contributors and users

---

## 📊 Project Status

- **Version**: 0.2.0
- **Status**: Beta (Production-Ready)
- **Python**: 3.10, 3.11, 3.12
- **License**: MIT
- **Maintainers**: [@canstralian](https://github.com/canstralian)

---

> _"Code is like music — when optimized, it flows perfectly."_ 🎵💻
