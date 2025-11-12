# 🎵💻 CodeTuneStudio

[![PyPI version](https://badge.fury.io/py/codetunestudio.svg)](https://pypi.org/project/codetunestudio/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-%3E%3D3.10-blue.svg)](https://www.python.org/downloads)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Documentation Status](https://readthedocs.org/projects/codetunestudio/badge/?version=latest)](https://codetunestudio.readthedocs.io/en/latest/)
[![Hugging Face Model CI/CD](https://github.com/canstralian/CodeTuneStudio/actions/workflows/huggingface-deploy.yml/badge.svg)](https://github.com/canstralian/CodeTuneStudio/actions/workflows/huggingface-deploy.yml)

---

🎯 **Optimize. Enhance. Perfect Your Code.**

CodeTuneStudio is your all-in-one platform for ML model fine-tuning, intelligent code analysis, performance optimization, and coding best practices — all within an intuitive Streamlit-powered interface.

---

## ✨ Features

- 🤖 **ML Model Fine-Tuning** — Parameter-efficient training with PEFT/LoRA for code models.
- ⚡ **Code Analysis** — Advanced static code analysis via extensible plugin architecture.
- 🚀 **Performance Optimization** — Smart suggestions to boost code efficiency.
- 🧑‍💻 **Best Practices** — Automated recommendations for cleaner, standard-compliant code.
- 🎨 **Interactive Interface** — Streamlit-powered UI for an intuitive developer experience.
- 📊 **Experiment Tracking** — PostgreSQL/SQLite backend for training metrics and model versioning.

---

## 🛠️ Installation and Running

### Prerequisites

* **Operating System:** Kali Linux (recommended) or any modern Linux distribution
* **Python:** 3.10 or higher
* **Docker:** (optional) for containerized deployment

---

### Method 1: Quick Start with Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/canstralian/CodeTuneStudio.git
cd CodeTuneStudio

# Build and run with Docker
docker build -t codetunestudio .
docker run -p 5000:5000 codetunestudio
```

Access the interface at [http://localhost:5000](http://localhost:5000)

---

### Method 2: Installation from Source

**On your Kali or Linux machine:**

```bash
# Clone the repository
git clone https://github.com/canstralian/CodeTuneStudio.git
cd CodeTuneStudio

# Create and activate a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your settings (DATABASE_URL, API keys, etc.)

# Initialize the database (first time only)
python manage.py db upgrade

# Run the application
streamlit run app.py --server.port 5000
```

---

### Method 3: Hugging Face Spaces Deployment

```bash
# Create a new space at https://huggingface.co/spaces
# Choose Streamlit SDK with A100 hardware for optimal performance

# Clone your space
git clone https://huggingface.co/spaces/YOUR_USERNAME/codetunestudio
cd codetunestudio

# Copy project files
cp -r /path/to/CodeTuneStudio/* .

# Configure secrets in Space settings:
# - DATABASE_URL (PostgreSQL connection string)
# - HF_TOKEN (Hugging Face API token)
# - OPENAI_API_KEY (optional, for OpenAI plugin)
# - ANTHROPIC_API_KEY (optional, for Anthropic plugin)

# Push to deploy
git add .
git commit -m "Initial deployment"
git push
```

---

### Command Line Options

When running locally with Streamlit:

| Option                   | Description                                             |
| :----------------------- | :------------------------------------------------------ |
| `--server.port <port>`   | Server port (default: `5000`)                           |
| `--server.address <ip>`  | Bind to a specific IP (default: `localhost`)            |
|                          | `localhost` → Local only *(secure, recommended)*        |
|                          | `0.0.0.0` → All interfaces *(for remote access)*        |
| `--server.headless true` | Run without opening browser automatically               |

**Examples:**

```bash
# Run on localhost (secure)
streamlit run app.py

# Run on all interfaces (less secure)
streamlit run app.py --server.address 0.0.0.0

# Custom port
streamlit run app.py --server.port 8080

# Headless mode for server deployment
streamlit run app.py --server.headless true
```

---

### Method 4: Development Setup

```bash
# Clone and setup
git clone https://github.com/canstralian/CodeTuneStudio.git
cd CodeTuneStudio

# Install with development dependencies
pip install -e ".[dev]"

# Run tests
pytest -v

# Run linters
flake8 .
pylint components/ utils/

# Check database
python db_check.py
```

---

### Environment Configuration

Create a `.env` file in the project root (copy from `.env.example`):

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
# Alternative SQLite (default): sqlite:///database.db

# API Keys for Code Analysis Plugins
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Hugging Face Hub
HF_TOKEN=your_huggingface_token_here

# Debug Settings (optional)
SQL_DEBUG=False
SPACE_ID=your_space_id
```

**Required Variables:**
- `DATABASE_URL`: PostgreSQL connection string (falls back to SQLite if not set)
- `HF_TOKEN`: Required for model downloads and Hugging Face integration

**Optional Variables:**
- `OPENAI_API_KEY`: For OpenAI-powered code analysis features
- `ANTHROPIC_API_KEY`: For Claude-powered code suggestions
- `SQL_DEBUG`: Enable SQL query logging for debugging

---

## 🌐 Usage

Once the application is running:

1. **Access the Interface:** Open [http://localhost:5000](http://localhost:5000) in your browser
2. **Select a Dataset:** Choose from available datasets or upload your own
3. **Configure Training:** Set hyperparameters (batch size, learning rate, epochs)
4. **Monitor Training:** Real-time metrics visualization and progress tracking
5. **Export Models:** Save trained models to Hugging Face Hub or local storage

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

1. 🍴 Fork the repository
2. 💡 Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. ✅ Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. 📤 Push to the branch (`git push origin feature/AmazingFeature`)
5. 📬 Open a Pull Request

---

## 📜 License

This project is licensed under the **MIT License**.  
See the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

💖 Huge thanks to the open-source community for their continuous inspiration and support.

> _"Code is like music — when optimized, it flows perfectly."_ 🎵💻
