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

### Option 1: Install from PyPI (Production)

```bash
pip install codetunestudio
```

### Option 2: Install from Source (Development)

1. **🔄 Clone the Repository:**

   ```bash
   git clone https://github.com/canstralian/CodeTuneStudio.git
   cd CodeTuneStudio
   ```

2. **📦 Install Dependencies:**

   ```bash
   pip install -e .
   ```

   Or for development with additional tools:

   ```bash
   pip install -e ".[dev]"
   ```

---

## 🌐 Usage

### Using the CLI (Recommended)

After installation, launch CodeTuneStudio with the new CLI:

```bash
codetune-studio
```

Optional CLI arguments:
```bash
codetune-studio --help          # Show help message
codetune-studio --version       # Show version
codetune-studio --port 8080     # Run on custom port
codetune-studio --host 0.0.0.0  # Bind to all interfaces
codetune-studio --debug         # Enable debug logging
```

### Using Python Module

You can also run it directly:

```bash
python -m core.cli
```

Or run the legacy app.py:

```bash
python app.py
```

The Streamlit interface will be available at 👉 [http://localhost:7860](http://localhost:7860)

---

## 📁 Project Structure

```
CodeTuneStudio/
├── app.py               # 🚀 Main application file
├── components/          # 🧩 UI components
├── utils/               # 🛠️ Utility functions
├── requirements.txt     # 📦 Project dependencies
└── README.md            # 📖 Documentation
```

---

## 🤝 Contributing

We welcome contributions! 🫶  
Feel free to check out the [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to get involved.

### Code Quality

We maintain high code quality standards using automated tools:

- 🎨 **Code Formatting**: [Black](https://github.com/psf/black) with 88 character line length
- 🔍 **Linting**: [Flake8](https://flake8.pycqa.org/) for PEP 8 compliance
- 🪝 **Pre-commit Hooks**: Automated checks before each commit

**Quick Setup:**
```bash
./scripts/setup-pre-commit.sh
```

For detailed information, see [Code Quality Guidelines](docs/CONTRIBUTING_CODE_QUALITY.md).

### Contributing Workflow

1. 🍴 Fork the repository
2. 💡 Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. 🔧 Set up pre-commit hooks (`./scripts/setup-pre-commit.sh`)
4. ✅ Commit your changes (`git commit -m 'Add some AmazingFeature'`)
5. 📤 Push to the branch (`git push origin feature/AmazingFeature`)
6. 📬 Open a Pull Request

---

## 📜 License

This project is licensed under the **MIT License**.  
See the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

💖 Huge thanks to the open-source community for their continuous inspiration and support.

> _"Code is like music — when optimized, it flows perfectly."_ 🎵💻
