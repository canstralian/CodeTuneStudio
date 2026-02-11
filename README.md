
⸻

# 🎵💻 CodeTuneStudio


⸻

🎯 Optimize. Enhance. Perfect Your Code.

CodeTuneStudio is an all-in-one platform for intelligent code analysis, performance optimization, and coding best practices — delivered through an intuitive, developer-friendly interface.

⸻

## ✨ Features
	•	⚡ Code Analysis — Advanced static analysis for multiple programming languages
	•	🚀 Performance Optimization — Smart, actionable efficiency recommendations
	•	🧑‍💻 Best Practices — Automated guidance for clean, standard-compliant code
	•	🎨 Interactive Interface — Gradio-powered UI for fast iteration and insight

⸻

## 🛠️ Prerequisites
	•	🐍 Python 3.10 or higher

⸻

## 📥 Installation

Via pip (Recommended)

pip install codetune-studio

From Source (Development)

git clone https://github.com/canstralian/CodeTuneStudio.git
cd CodeTuneStudio
pip install -e .


⸻

## 🌐 Usage

Quick Start

codetune-studio

The application starts at:
👉 http://localhost:7860

CLI Options

codetune-studio --host 0.0.0.0 --port 8501
codetune-studio --log-level DEBUG
codetune-studio --no-browser
codetune-studio --database-url postgresql://user:pass@localhost/dbname
codetune-studio --version
codetune-studio --help


⸻

## 🔐 Configuration via Environment Variables

Create a .env file (see .env.example):

OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here

DATABASE_URL=postgresql://user:pass@localhost/dbname
LOG_LEVEL=INFO
HOST=localhost
PORT=7860


⸻

## 🤖 Codex Cloud / Agent Environment Setup (Recommended)

CodeTuneStudio is designed to run cleanly in automated agent environments such as OpenAI Codex Cloud.

Setup Script (Python Base)

Use the following as your Codex environment setup script:

#!/usr/bin/env bash
set -euo pipefail

apt-get update
apt-get install -y build-essential git curl jq ripgrep

python --version
pip install --upgrade pip setuptools wheel

pip install -r requirements.txt

Environment Variables (Codex Environment)

PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
PYTHONPATH=/workspace
CI=true
CODEX_ENV=cloud

Secrets (Setup-Time Only)

OPENAI_API_KEY
ANTHROPIC_API_KEY
DATABASE_URL

Secrets are used only during setup and are not exposed to the agent at runtime.

Internet Access Policy

Recommended allowlist:

pypi.org
files.pythonhosted.org
github.com
raw.githubusercontent.com

This enables dependency installation while preserving determinism and security.

⸻

## 📁 Project Structure

CodeTuneStudio/
├── automation/             # GitHub automation tools
│   ├── create_branch.py
│   ├── create_issue.py
│   ├── manage_project.py
│   └── utils/
├── core/                   # Core application modules
│   ├── cli.py
│   ├── server.py
│   └── logging.py
├── components/             # UI components
├── plugins/                # Extensible analysis plugins
├── utils/                  # Shared utilities
├── tests/                  # Test suite
├── docs/                   # Documentation
├── app.py                  # Legacy entrypoint
├── requirements.txt
├── pyproject.toml
├── CHANGELOG.md
└── README.md


⸻

## 🤖 GitHub Automation Tools

CodeTuneStudio includes powerful automation scripts for GitHub operations:

- **Branch Management**: Automated branch creation, switching, and deletion
- **Issue Creation**: Template-based issue creation with labels and metadata
- **Project Management**: Project board creation and management

Quick examples:
```bash
# Create a feature branch
python -m automation.create_branch feature/new-api

# Create a bug issue with template
python -m automation.create_issue --template bug --title "Fix login" --labels bug,urgent

# Create a project board
python -m automation.manage_project --create "Sprint 1" --description "Tasks for Sprint 1"
```

See [automation/README.md](automation/README.md) for complete documentation.

⸻

## 🔌 Plugin System
	•	Built-in AI plugins (OpenAI, Anthropic)
	•	Hot-discovered custom plugins
	•	Clean extension boundaries

See docs/PLUGIN_GUIDE.md for details.

⸻

## 🧪 Development & Code Quality

pip install -e ".[dev]"
pytest tests/
ruff check .
black --check .
mypy core/

We use:
	•	Black for formatting
	•	Ruff for linting
	•	Pre-commit hooks for enforcement

./scripts/setup-pre-commit.sh


⸻

## 📚 Documentation
	•	Architecture: docs/ARCHITECTURE.md
	•	Plugin Guide: docs/PLUGIN_GUIDE.md
	•	Refactoring Tasks: docs/REFACTORING_TASKS.md
	•	Changelog: CHANGELOG.md

⸻

## 📜 License

MIT License — see LICENSE.

⸻

## 📊 Project Status
	•	Version: 0.2.0
	•	Status: Beta (Production-Ready)
	•	Python: 3.10–3.12
	•	Maintainer: @canstralian

⸻

