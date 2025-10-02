# Contributing to CodeTuneStudio

Thank you for your interest in contributing to CodeTuneStudio! This document provides guidelines and information for contributors.

## Development Setup

### Prerequisites
- Python 3.11+
- Git

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/canstralian/CodeTuneStudio.git
   cd CodeTuneStudio
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install flake8 black bandit safety pytest pytest-cov
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

## Code Standards

### Style Guidelines
- Follow PEP 8 style guide
- Use type hints for all functions and methods
- Maximum line length: 88 characters
- Use descriptive variable and function names

### Code Quality Tools
```bash
# Linting
flake8 .

# Code formatting
black .

# Security scanning
bandit -r .

# Dependency scanning
safety check

# Testing
pytest --cov=.
```

### Pre-commit Checklist
- [ ] All tests pass
- [ ] Code follows style guidelines
- [ ] Security scanning passes
- [ ] Documentation is updated
- [ ] Type hints are present
- [ ] Docstrings are comprehensive

## Plugin Development

### Creating a Plugin
1. Create a new file in the `plugins/` directory
2. Inherit from `AgentTool` base class
3. Implement required methods:
   - `__init__()`: Initialize metadata
   - `validate_inputs()`: Validate input parameters
   - `execute()`: Core plugin functionality

### Plugin Example
```python
from typing import Dict, Any
from utils.plugins.base import AgentTool, ToolMetadata

class MyPlugin(AgentTool):
    def __init__(self):
        super().__init__()
        self.metadata = ToolMetadata(
            name="my_plugin",
            description="Example plugin",
            version="1.0.0",
            author="Your Name",
            tags=["example"]
        )
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        return "input_key" in inputs
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        # Plugin logic here
        return {"result": "success"}
```

## Security Guidelines

### Input Validation
- Always validate and sanitize user inputs
- Use Pydantic models for configuration validation
- Never execute user-provided code without sandboxing

### Secrets Management
- Never commit secrets to version control
- Use environment variables for sensitive configuration
- Validate secret presence at startup

### Plugin Security
- Plugins should run in isolated environments
- Limit plugin access to system resources
- Validate plugin metadata and code before execution

## Testing

### Test Structure
```
tests/
├── unit/
│   ├── test_components.py
│   ├── test_utils.py
│   └── test_plugins.py
├── integration/
│   ├── test_database.py
│   └── test_workflows.py
└── fixtures/
    └── sample_data.py
```

### Writing Tests
- Write unit tests for individual functions
- Write integration tests for component interactions
- Use fixtures for test data
- Mock external dependencies

## Database Changes

### Migrations
1. Make model changes in `utils/database.py`
2. Generate migration:
   ```bash
   python manage.py db migrate -m "Description of changes"
   ```
3. Review generated migration file
4. Apply migration:
   ```bash
   python manage.py db upgrade
   ```

## Submitting Changes

### Pull Request Process
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run all quality checks
5. Submit a pull request with:
   - Clear description of changes
   - Link to related issues
   - Test results and screenshots

### Review Criteria
- Code quality and style compliance
- Test coverage and passing tests
- Security considerations addressed
- Documentation updated
- Performance impact considered

## Getting Help

- Open an issue for bugs or feature requests
- Join our discussions for questions
- Review existing documentation and code examples

## Code of Conduct

Please be respectful and constructive in all interactions. We're committed to providing a welcoming environment for all contributors.