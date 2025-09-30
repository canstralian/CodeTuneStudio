# 🎵💻 CodeTuneStudio

[![PyPI version](https://badge.fury.io/py/codetunestudio.svg)](https://pypi.org/project/codetunestudio/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-%3E%3D3.11-blue.svg)](https://www.python.org/downloads)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![CI Pipeline](https://github.com/canstralian/CodeTuneStudio/actions/workflows/ci.yml/badge.svg)](https://github.com/canstralian/CodeTuneStudio/actions/workflows/ci.yml)

---

🎯 **Optimize. Fine-tune. Perfect Your ML Models.**

CodeTuneStudio is an AI-powered platform for fine-tuning machine learning models with parameter-efficient training (PEFT/LoRA), real-time monitoring, and extensible plugin architecture — all within an intuitive Streamlit interface.

---

## ✨ Features

- 🤖 **ML Model Fine-tuning** — Support for CodeT5, Replit-v1.5, and custom models
- ⚡ **PEFT/LoRA Training** — Parameter-efficient fine-tuning with quantization support
- 📊 **Real-time Monitoring** — Live training metrics and visualization with Plotly
- 🔌 **Plugin Architecture** — Extensible tool system with OpenAI, Anthropic integrations
- 💾 **Experiment Tracking** — PostgreSQL/SQLite backend for configuration and metrics
- 🚀 **Distributed Training** — Multi-GPU support with automatic optimization
- 🎨 **Dataset Management** — Built-in support for HuggingFace datasets and Argilla
- 📈 **Version Control** — Model versioning and experiment comparison

---

## 🛠️ Prerequisites

- 🐍 **Python** 3.11 or higher
- 💻 **uv** package manager (recommended) or pip
- 🎮 **CUDA** (optional, for GPU acceleration)

---

## 📥 Installation

### Quick Start (Recommended)

```bash
# Install uv (fast package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/canstralian/CodeTuneStudio.git
cd CodeTuneStudio

# Install dependencies
uv pip install -e ".[dev]"

# Setup environment
cp .env.example .env
# Edit .env with your API keys and configuration
```

### Traditional Installation

```bash
# Clone the repository
git clone https://github.com/canstralian/CodeTuneStudio.git
cd CodeTuneStudio

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Setup environment
cp .env.example .env
# Edit .env with your API keys and configuration
```

### PyPI Installation (Coming Soon)

```bash
pip install codetunestudio
```

---

## ⚙️ Configuration

Create a `.env` file with your configuration:

```bash
# Database (use PostgreSQL for production)
DATABASE_URL=sqlite:///database.db

# AI/ML API Keys (optional, for plugins)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
HF_TOKEN=hf_...

# Argilla (optional, for dataset management)
ARGILLA_API_KEY=...
ARGILLA_WORKSPACE=default

# Distributed Training (optional)
MASTER_ADDR=localhost
MASTER_PORT=12355
```

See `.env.example` for complete configuration options.

---

## 🚀 Usage

### Starting the Application

```bash
# Run Streamlit interface
python app.py

# Or use streamlit directly
streamlit run app.py
```

Access the interface at **http://localhost:7860**

### Using Flask CLI

```bash
# Database migrations
python manage.py db init
python manage.py db migrate -m "Initial migration"
python manage.py db upgrade

# Interactive shell
python manage.py shell
```

### Running with Make

```bash
# Install dependencies
make install

# Run application
make run

# Run tests
make test

# Lint code
make lint

# Format code
make format

# Clean build artifacts
make clean
```

---

## 📁 Project Structure

```
CodeTuneStudio/
├── app.py                      # Main Streamlit application
├── manage.py                   # Flask CLI for database management
├── pyproject.toml              # Project metadata and dependencies
├── .env.example                # Environment variable template
│
├── components/                 # Streamlit UI components
│   ├── dataset_selector.py    # Dataset browsing and selection
│   ├── parameter_config.py    # Training hyperparameter configuration
│   ├── training_monitor.py    # Real-time training visualization
│   ├── experiment_compare.py  # Multi-experiment comparison
│   ├── plugin_manager.py      # Plugin lifecycle management
│   ├── tokenizer_builder.py   # Custom tokenizer creation
│   └── documentation_viewer.py # In-app documentation
│
├── utils/                      # Core utilities
│   ├── config.py              # Centralized configuration
│   ├── logging_config.py      # Logging setup
│   ├── database.py            # Database models and session management
│   ├── config_validator.py    # Configuration validation
│   ├── peft_trainer.py        # PEFT/LoRA training logic
│   ├── distributed_trainer.py # Multi-GPU training orchestration
│   ├── model_inference.py     # Model loading and inference
│   ├── model_versioning.py    # Experiment version control
│   ├── visualization.py       # Plotly chart generation
│   └── plugins/               # Plugin system
│       ├── base.py            # AgentTool abstract base class
│       └── registry.py        # Plugin discovery and registration
│
├── plugins/                    # Extensible tool plugins
│   ├── code_analyzer.py       # Python AST-based code analysis
│   ├── openai_code_analyzer.py # OpenAI GPT-powered analysis
│   └── anthropic_code_suggester.py # Claude-powered suggestions
│
├── tests/                      # Test suite
│   ├── test_app.py
│   ├── test_db_check.py
│   └── test_manage.py
│
└── .github/workflows/          # CI/CD pipelines
    ├── ci.yml                 # Linting and testing
    ├── huggingface-deploy.yml # HF Hub deployment
    └── python-style-checks.yml # Code style validation
```

---

## 🎯 Key Workflows

### Fine-tuning a Model

1. **Select Dataset**: Browse HuggingFace datasets or connect to Argilla
2. **Configure Training**: Set hyperparameters (batch size, learning rate, epochs)
3. **Monitor Progress**: View real-time loss curves and metrics
4. **Compare Experiments**: Analyze multiple training runs side-by-side
5. **Export Model**: Save fine-tuned model with version control

### Creating Custom Plugins

```python
from utils.plugins.base import AgentTool, ToolMetadata

class MyCustomTool(AgentTool):
    def __init__(self):
        super().__init__()
        self.metadata = ToolMetadata(
            name="my_custom_tool",
            description="Does something amazing",
            version="0.1.0",
            author="Your Name",
            tags=["custom", "analysis"]
        )

    def validate_inputs(self, inputs: dict) -> bool:
        return "data" in inputs

    def execute(self, inputs: dict) -> dict:
        # Your logic here
        return {"result": "success"}
```

Place in `plugins/` directory and it will be auto-discovered on startup.

---

## 🧪 Development

### Running Tests

```bash
# Run all tests
python -m unittest discover -s tests

# Run specific test file
python -m unittest tests.test_app

# With coverage
pytest --cov=. --cov-report=html
```

### Code Quality

```bash
# Lint with Ruff
ruff check .

# Format code
ruff format .

# Type checking (optional)
mypy .
```

### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Setup hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

---

## 📊 Supported Models & Datasets

### Models
- CodeT5 (Salesforce)
- Replit-v1.5
- Custom transformer models via HuggingFace

### Datasets
- HuggingFace Hub datasets
- Argilla datasets
- Reddit code datasets
- Custom JSON/CSV datasets

### Training Techniques
- LoRA (Low-Rank Adaptation)
- QLoRA (Quantized LoRA)
- Full fine-tuning
- 4-bit/8-bit quantization

---

## 🐛 Troubleshooting

### Common Issues

**Database connection errors:**
```bash
# Reset database
rm database.db
python manage.py db upgrade
```

**Plugin not loading:**
- Check API keys in `.env`
- Verify plugin file is in `plugins/` directory
- Check logs for errors: `tail -f codetunestudio.log`

**CUDA out of memory:**
- Reduce batch size
- Enable gradient checkpointing
- Use quantization (4-bit/8-bit)

See [CLAUDE.md](CLAUDE.md) for detailed architecture documentation.

---

## 🤝 Contributing

We welcome contributions! 🫶

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

- **HuggingFace** for transformers and datasets
- **Streamlit** for the beautiful UI framework
- **PEFT** library for parameter-efficient training
- The open-source ML community

---

## 📧 Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/canstralian/CodeTuneStudio/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/canstralian/CodeTuneStudio/discussions)
- 📖 **Documentation**: [CLAUDE.md](CLAUDE.md)

---

> _"Code is like music — when fine-tuned, it performs perfectly."_ 🎵💻

**Built with ❤️ by the CodeTuneStudio Team**
