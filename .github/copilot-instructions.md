# GitHub Copilot Instructions for CodeTuneStudio

## Project Overview

CodeTuneStudio is an all-in-one platform for intelligent code analysis, performance optimization, and ML model fine-tuning. It provides a Streamlit-powered web interface with Flask backend and modular plugin architecture.

**Key Technologies:**
- **Frontend**: Streamlit (primary UI)
- **Backend**: Flask + SQLAlchemy 
- **Database**: PostgreSQL (production) / SQLite (development)
- **ML/AI**: Transformers, PyTorch, Datasets, PEFT, Accelerate
- **Code Analysis**: OpenAI, Anthropic Claude APIs
- **Deployment**: Hugging Face Spaces, Docker

## Architecture & Design Patterns

### Core Components
- `app.py` - Main application entry point with MLFineTuningApp class
- `components/` - Streamlit UI components (modular, reusable)
- `utils/` - Utility functions, database models, configuration
- `plugins/` - Extensible plugin system for code analysis and AI tools
- `models/` - ML model definitions and training logic

### Plugin Architecture
All analysis tools inherit from `utils.plugins.base.AgentTool`:
- Implement `execute()` and `validate_inputs()` methods
- Use `ToolMetadata` for plugin information
- Follow error handling patterns with try/catch and logging
- Return consistent Dict[str, Any] response format

### Database Models
- `TrainingConfig` - Stores training configurations and parameters
- `TrainingMetric` - Stores training metrics and progress data
- Use SQLAlchemy ORM with Flask-SQLAlchemy integration
- Database migrations managed via Flask-Migrate

## Coding Standards & Conventions

### Python Style
- **Line length**: 88 characters (Black formatter)
- **Import organization**: stdlib, third-party, local imports (separated)
- **Type hints**: Required for all function signatures
- **Docstrings**: Google style for all public functions and classes
- **Error handling**: Use specific exceptions with informative messages

### Code Quality Tools
- **Linter**: Flake8 with max-line-length=88, extend-ignore=E203
- **Formatter**: Black (implied from style settings)
- **Type checker**: MyPy (configured for Python 3.8+)
- **CI/CD**: GitHub Actions with style checks on PRs

### Naming Conventions
- **Variables/Functions**: snake_case
- **Classes**: PascalCase
- **Constants**: UPPER_SNAKE_CASE
- **Private methods**: _single_leading_underscore
- **File names**: snake_case.py

### Streamlit Components
- Use descriptive component keys and help text
- Implement proper state management with st.session_state
- Follow the existing UI/UX patterns (emojis, consistent styling)
- Wrap components in error handling with user-friendly messages

## Development Guidelines

### Adding New Features

1. **UI Components** (`components/`):
   - Create reusable functions that return Streamlit elements
   - Use type hints: `def component_name() -> Optional[Dict[str, Any]]:`
   - Include comprehensive input validation
   - Add proper error handling with user-friendly messages

2. **Plugin Development** (`plugins/`):
   ```python
   class NewAnalyzerTool(AgentTool):
       def __init__(self):
           super().__init__()
           self.metadata = ToolMetadata(
               name="tool_name",
               description="Tool description",
               version="0.1.0",
               author="CodeTuneStudio",
               tags=["relevant", "tags"]
           )
       
       def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
           # Implement validation logic
           
       def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
           # Implement main functionality
   ```

3. **Database Changes**:
   - Create new models in `utils/database.py`
   - Use Flask-Migrate for schema changes: `flask db migrate -m "description"`
   - Test migrations both up and down

### Configuration Management

- Environment variables for sensitive data (API keys, DB URLs)
- Use `os.environ.get()` with sensible defaults
- Configuration validation in `utils/config_validator.py`
- Support for both development and production environments

### API Integration Patterns

- **OpenAI**: Use structured outputs with `response_format={"type": "json_object"}`
- **Anthropic**: Use latest models (claude-3-5-sonnet-20241022)
- **Error Handling**: Catch API-specific exceptions and provide fallbacks
- **Rate Limiting**: Implement retry logic with exponential backoff

### Testing Guidelines

- Unit tests should be in `tests/` directory (create if needed)
- Test plugin functionality with mock data
- Test database operations with test database
- Integration tests for Streamlit components
- Use `unittest.mock` for external API calls

## Common Patterns & Best Practices

### Error Handling
```python
try:
    result = risky_operation()
    return {"status": "success", "data": result}
except SpecificException as e:
    logger.error(f"Operation failed: {str(e)}")
    return {"status": "error", "error": str(e)}
```

### Logging
- Use module-level logger: `logger = logging.getLogger(__name__)`
- Log levels: INFO for normal operations, ERROR for failures, DEBUG for development
- Include context in log messages: `f"Operation {operation_name} failed: {error}"`

### Database Operations
```python
try:
    with app.app_context():
        db.session.add(new_record)
        db.session.commit()
        return new_record.id
except Exception as e:
    db.session.rollback()
    logger.error(f"Database operation failed: {str(e)}")
    raise
```

### Streamlit State Management
- Use `st.session_state` for persistent data
- Initialize state variables with defaults
- Clear state when switching between major sections

## Dependencies & Environment

### Core Dependencies
- `streamlit>=1.26.0` - Web UI framework
- `flask>=3.0.0` - Backend API server
- `torch>=2.0.1` - ML framework
- `transformers>=4.33.0` - Pre-trained models
- `sqlalchemy>=2.0.22` - Database ORM
- `openai` & `anthropic` - AI API clients

### Development Tools
- Python 3.8+ (CI uses 3.9)
- Virtual environment recommended
- PostgreSQL for production, SQLite for development

### Environment Variables
- `DATABASE_URL` - Database connection string
- `OPENAI_API_KEY` - OpenAI API access
- `ANTHROPIC_API_KEY` - Anthropic Claude API access
- `HUGGINGFACE_TOKEN` - HF model access (if needed)
- `SPACE_ID` - For Hugging Face Spaces deployment

## Deployment Considerations

- **Hugging Face Spaces**: Primary deployment target
- **Docker**: Containerized deployment option
- **Database**: Ensure migrations run on deployment
- **Secrets**: Use platform-specific secret management
- **Performance**: Consider Streamlit caching for expensive operations

## File Structure Guidelines

```
CodeTuneStudio/
├── app.py                 # Main application entry point
├── components/            # Reusable Streamlit components
├── utils/                 # Utilities, database, configuration
│   └── plugins/           # Plugin base classes and registry
├── plugins/               # Specific analysis and AI tools
├── models/                # ML model definitions
├── .github/               # GitHub workflows and configuration
├── tests/                 # Unit and integration tests
└── requirements.txt       # Python dependencies
```

## Security & Privacy

- Never commit API keys or sensitive data
- Use environment variables for all secrets
- Validate all user inputs
- Sanitize data before database operations
- Log security events appropriately

## Performance Guidelines

- Use `@lru_cache` for expensive operations
- Implement Streamlit caching where appropriate
- Optimize database queries (use indexes, limit results)
- Consider pagination for large datasets
- Monitor memory usage for ML operations

When contributing to this project, always refer to these guidelines and maintain consistency with existing code patterns. Focus on creating maintainable, well-documented, and thoroughly tested code.