# Testing Guide for CodeTuneStudio

This document provides comprehensive guidance for testing CodeTuneStudio.

## Table of Contents

1. [Overview](#overview)
2. [Test Structure](#test-structure)
3. [Running Tests](#running-tests)
4. [Test Coverage](#test-coverage)
5. [Writing Tests](#writing-tests)
6. [CI/CD Integration](#cicd-integration)
7. [Manual Testing](#manual-testing)

---

## Overview

CodeTuneStudio uses Python's built-in `unittest` framework for testing. Tests are organized in the `tests/` directory and cover:

- Application initialization
- Database operations
- Configuration validation
- Plugin system
- Code analysis tools

### Test Philosophy

- **Unit Tests**: Test individual functions and methods in isolation
- **Integration Tests**: Test interactions between components
- **Manual Tests**: User workflow verification before releases

---

## Test Structure

```
tests/
├── test_app.py                      # Core application tests
├── test_anthropic_code_suggester.py # Anthropic plugin tests
├── test_code_analyzer.py            # Code analyzer plugin tests
├── test_db_check.py                 # Database connectivity tests
├── test_manage.py                   # Management command tests
└── test_openai_code_analyzer.py     # OpenAI plugin tests
```

### Test Naming Conventions

- Test files: `test_<module_name>.py`
- Test classes: `Test<ClassName>`
- Test methods: `test_<description_of_what_is_tested>`

---

## Running Tests

### Run All Tests

```bash
# Basic test run
python -m unittest discover -s tests

# Verbose output
python -m unittest discover -s tests -v

# With coverage (requires coverage package)
pip install coverage
coverage run -m unittest discover -s tests
coverage report
coverage html  # Generate HTML report
```

### Run Specific Test Files

```bash
# Run single test file
python -m unittest tests.test_app

# Run specific test class
python -m unittest tests.test_app.TestMLFineTuningApp

# Run specific test method
python -m unittest tests.test_app.TestMLFineTuningApp.test_configure_database
```

### Run Tests with Environment Variables

```bash
# Set environment variables for tests
export DATABASE_URL="sqlite:///test.db"
export OPENAI_API_KEY="test-key"
python -m unittest discover -s tests
```

---

## Test Coverage

### Current Coverage

| Module | Coverage | Critical Paths |
|--------|----------|----------------|
| `app.py` | ~80% | ✅ Initialization, DB setup |
| `utils/database.py` | ~90% | ✅ Models, relationships |
| `utils/config_validator.py` | ~85% | ✅ Validation logic |
| `components/*` | ~70% | ⚠️ UI components (Streamlit) |
| `plugins/*` | ~75% | ✅ Plugin execution |

### Coverage Goals

- **Critical paths**: 90%+ coverage
- **Business logic**: 80%+ coverage
- **UI components**: 60%+ coverage (harder to test Streamlit)

### Generating Coverage Reports

```bash
# Install coverage
pip install coverage

# Run tests with coverage
coverage run -m unittest discover -s tests

# View console report
coverage report

# Generate HTML report
coverage html
# Open htmlcov/index.html in browser

# Generate XML report (for CI/CD)
coverage xml
```

---

## Writing Tests

### Test Template

```python
import unittest
from unittest.mock import patch, MagicMock


class TestYourFeature(unittest.TestCase):
    """Test suite for YourFeature functionality."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Initialize test data
        self.test_config = {
            'model_type': 'CodeT5',
            'batch_size': 16
        }
    
    def tearDown(self):
        """Clean up after each test method."""
        # Clean up resources
        pass
    
    def test_basic_functionality(self):
        """Test basic feature functionality."""
        # Arrange
        expected_result = "expected"
        
        # Act
        result = your_function()
        
        # Assert
        self.assertEqual(result, expected_result)
    
    @patch('module.external_dependency')
    def test_with_mock(self, mock_dependency):
        """Test functionality with mocked dependencies."""
        # Configure mock
        mock_dependency.return_value = "mocked"
        
        # Test
        result = function_using_dependency()
        
        # Verify
        self.assertEqual(result, "mocked")
        mock_dependency.assert_called_once()


if __name__ == '__main__':
    unittest.main()
```

### Testing Best Practices

1. **Test One Thing Per Test**
   ```python
   # Good
   def test_validates_batch_size_minimum(self):
       errors = validate_config({'batch_size': 0})
       self.assertIn('batch_size', str(errors))
   
   def test_validates_batch_size_maximum(self):
       errors = validate_config({'batch_size': 200})
       self.assertIn('batch_size', str(errors))
   
   # Avoid: Testing multiple things
   def test_validates_all_parameters(self):
       # Tests too many things at once
   ```

2. **Use Descriptive Test Names**
   ```python
   # Good
   def test_sanitize_string_removes_special_characters(self):
       pass
   
   # Avoid
   def test_sanitize(self):
       pass
   ```

3. **Use Mocks for External Dependencies**
   ```python
   @patch('utils.database.db.session')
   def test_database_operation(self, mock_session):
       # Test without hitting real database
       pass
   
   @patch('anthropic.Anthropic')
   def test_api_call(self, mock_anthropic):
       # Test without calling external API
       pass
   ```

4. **Test Edge Cases**
   ```python
   def test_handles_empty_input(self):
       result = process_data([])
       self.assertEqual(result, [])
   
   def test_handles_null_input(self):
       result = process_data(None)
       self.assertIsNone(result)
   
   def test_handles_large_input(self):
       large_data = ['x'] * 10000
       result = process_data(large_data)
       self.assertIsNotNone(result)
   ```

---

## CI/CD Integration

### GitHub Actions Workflow

Tests automatically run on:
- Push to `main` branch
- Pull requests to `main` branch
- Multiple Python versions (3.9, 3.10, 3.11, 3.12)

See `.github/workflows/ci.yml` for configuration.

### Local Pre-commit Testing

```bash
#!/bin/bash
# Save as .git/hooks/pre-commit

echo "Running tests before commit..."
python -m unittest discover -s tests

if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi

echo "All tests passed. Proceeding with commit."
```

---

## Manual Testing

### Pre-Release Manual Test Checklist

#### 1. Application Startup
- [ ] Application starts without errors: `python app.py`
- [ ] Streamlit UI loads at http://localhost:7860
- [ ] Version displayed correctly in logs
- [ ] Database initializes (or connects to existing)

#### 2. Dataset Selection
- [ ] Dataset browser displays Hugging Face datasets
- [ ] Search functionality works
- [ ] Dataset validation works (valid/invalid datasets)
- [ ] Error messages are clear and helpful

#### 3. Training Configuration
- [ ] Model selection dropdown works (CodeT5, Replit-v1.5)
- [ ] Batch size slider (1-128) works
- [ ] Learning rate input accepts scientific notation
- [ ] Epochs, max_seq_length, warmup_steps inputs work
- [ ] Configuration validation catches invalid inputs
- [ ] Error messages display for invalid configurations

#### 4. Training Monitor
- [ ] Training monitor displays (even if no active training)
- [ ] Metrics visualization loads
- [ ] Real-time updates work (if training active)

#### 5. Experiment Comparison
- [ ] Comparison interface loads
- [ ] Can select multiple experiments (if any exist)
- [ ] Charts render correctly

#### 6. Plugin System
- [ ] Plugin manager loads
- [ ] Plugins discovered and listed
- [ ] Plugin metadata displayed correctly

#### 7. Tokenizer Builder
- [ ] Tokenizer builder interface loads
- [ ] Model selection works
- [ ] Special tokens configuration works
- [ ] Build button functional

#### 8. Documentation Viewer
- [ ] Documentation viewer loads
- [ ] Documentation content displays correctly

#### 9. Database Operations
- [ ] Configuration saves to database
- [ ] Configurations can be retrieved
- [ ] Database migrations work (if applicable)

#### 10. Error Handling
- [ ] Invalid inputs show user-friendly errors
- [ ] Database connection failures handled gracefully
- [ ] Plugin errors don't crash application
- [ ] Network errors handled (API timeouts)

### Performance Testing

```bash
# Memory usage monitoring
pip install memory_profiler

# Profile application
python -m memory_profiler app.py

# Check database query performance
export SQL_DEBUG=True
python app.py
# Monitor query execution times in logs
```

### Load Testing (Optional)

```bash
# Install locust
pip install locust

# Create locustfile.py for load testing
# Run load test
locust -f locustfile.py
```

---

## Test Data

### Creating Test Fixtures

```python
# tests/fixtures.py
def get_test_config():
    """Return valid test configuration."""
    return {
        'model_type': 'CodeT5',
        'dataset_name': 'test_dataset',
        'batch_size': 16,
        'learning_rate': 2e-5,
        'epochs': 3,
        'max_seq_length': 256,
        'warmup_steps': 100
    }

def get_invalid_config():
    """Return invalid test configuration."""
    return {
        'model_type': 'InvalidModel',
        'batch_size': 0,  # Invalid
        'learning_rate': 999,  # Invalid
    }
```

### Using Test Database

```python
import os
import unittest
from utils.database import init_db

class DatabaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test database."""
        os.environ['DATABASE_URL'] = 'sqlite:///test.db'
        cls.app = create_app()
        with cls.app.app_context():
            init_db(cls.app)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test database."""
        if os.path.exists('test.db'):
            os.remove('test.db')
```

---

## Troubleshooting Tests

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure CodeTuneStudio is in Python path
   export PYTHONPATH="${PYTHONPATH}:/path/to/CodeTuneStudio"
   ```

2. **Module Not Found**
   ```bash
   # Install test dependencies
   pip install -r requirements.txt
   ```

3. **Database Errors**
   ```bash
   # Use test database
   export DATABASE_URL="sqlite:///test.db"
   ```

4. **API Key Errors**
   ```bash
   # Set test API keys
   export OPENAI_API_KEY="test-key"
   export ANTHROPIC_API_KEY="test-key"
   ```

### Debugging Failed Tests

```bash
# Run with verbose output
python -m unittest tests.test_app -v

# Run specific failing test
python -m unittest tests.test_app.TestMLFineTuningApp.test_failing_method -v

# Add breakpoint in test
import pdb; pdb.set_trace()
```

---

## Test Maintenance

### Updating Tests

When modifying code:
1. Update corresponding tests
2. Add tests for new functionality
3. Ensure all tests pass
4. Update test documentation

### Reviewing Test Coverage

```bash
# Monthly review
coverage run -m unittest discover -s tests
coverage report --show-missing

# Identify untested code
# Add tests for uncovered critical paths
```

### Deprecating Tests

When removing features:
1. Mark tests with `@unittest.skip("Feature deprecated")`
2. Document deprecation in test docstring
3. Remove in next major version

---

## Resources

- [Python unittest documentation](https://docs.python.org/3/library/unittest.html)
- [unittest.mock documentation](https://docs.python.org/3/library/unittest.mock.html)
- [Coverage.py documentation](https://coverage.readthedocs.io/)
- [Testing Flask applications](https://flask.palletsprojects.com/en/latest/testing/)

---

## Contributing Tests

When contributing to CodeTuneStudio:

1. **Write tests for new features**
   - Add test file in `tests/`
   - Follow naming conventions
   - Test happy path and edge cases

2. **Update existing tests**
   - Modify tests when changing behavior
   - Don't break existing tests

3. **Run tests before committing**
   ```bash
   python -m unittest discover -s tests
   ```

4. **Document test purpose**
   - Clear test names
   - Docstrings for complex tests

---

**Last Updated**: 2024-12-19  
**Version**: 1.0.0
