# Plugin Development Guide

CodeTune Studio uses a plugin architecture to extend code analysis capabilities. This guide will help you create custom plugins for your specific needs.

## Table of Contents

- [Overview](#overview)
- [Plugin Architecture](#plugin-architecture)
- [Creating a Plugin](#creating-a-plugin)
- [Plugin API Reference](#plugin-api-reference)
- [Best Practices](#best-practices)
- [Examples](#examples)

## Overview

Plugins in CodeTune Studio are Python modules that implement the `BaseTool` interface from `utils.plugins.base`. They are automatically discovered and loaded from the `plugins/` directory at application startup.

### Plugin Capabilities

Plugins can:
- Analyze code for patterns, issues, or improvements
- Suggest refactorings and optimizations
- Integrate with external services (OpenAI, Anthropic, etc.)
- Provide custom metrics and visualizations
- Extend training workflows with custom preprocessing

## Plugin Architecture

### Directory Structure

```
plugins/
├── __init__.py
├── my_plugin.py           # Your plugin implementation
└── third_party_plugin/    # Or as a package
    ├── __init__.py
    └── implementation.py
```

### Base Tool Interface

All plugins must inherit from `BaseTool`:

```python
from src.utils.plugins.base import BaseTool

class MyPlugin(BaseTool):
    """Plugin description"""
    
    def __init__(self):
        super().__init__()
        self.name = "my-plugin"
        self.description = "Description of what the plugin does"
        self.version = "1.0.0"
    
    def run(self, *args, **kwargs):
        """Execute the plugin's main functionality"""
        pass
```

## Creating a Plugin

### Step 1: Create the Plugin File

Create a new file in the `plugins/` directory:

```python
# plugins/code_complexity_analyzer.py

from typing import Any, Dict, List
from src.utils.plugins.base import BaseTool
import re


class CodeComplexityAnalyzer(BaseTool):
    """
    Analyzes code complexity and provides metrics.
    """
    
    def __init__(self):
        super().__init__()
        self.name = "code-complexity-analyzer"
        self.description = "Analyzes code complexity using various metrics"
        self.version = "1.0.0"
        self.author = "Your Name"
    
    def run(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Analyze code complexity.
        
        Args:
            code: Source code to analyze
            language: Programming language (default: python)
        
        Returns:
            Dictionary containing complexity metrics
        """
        return {
            "lines_of_code": len(code.splitlines()),
            "cyclomatic_complexity": self._calculate_complexity(code),
            "max_nesting_depth": self._calculate_nesting(code),
        }
    
    def _calculate_complexity(self, code: str) -> int:
        """Calculate cyclomatic complexity"""
        # Simplified implementation
        decision_points = len(re.findall(r'\b(if|for|while|elif|except)\b', code))
        return decision_points + 1
    
    def _calculate_nesting(self, code: str) -> int:
        """Calculate maximum nesting depth"""
        max_depth = 0
        current_depth = 0
        for line in code.splitlines():
            indent = len(line) - len(line.lstrip())
            current_depth = indent // 4  # Assuming 4-space indents
            max_depth = max(max_depth, current_depth)
        return max_depth
```

### Step 2: Register the Plugin

Plugins are automatically discovered if they:
1. Are in the `plugins/` directory
2. Inherit from `BaseTool`
3. Have a unique `name` attribute

No manual registration is required!

### Step 3: Test Your Plugin

Create a test file in `tests/`:

```python
# tests/test_code_complexity_analyzer.py

import unittest
from src.plugins.code_complexity_analyzer import CodeComplexityAnalyzer


class TestCodeComplexityAnalyzer(unittest.TestCase):
    def setUp(self):
        self.plugin = CodeComplexityAnalyzer()
    
    def test_simple_code(self):
        code = """
def hello():
    print("Hello, world!")
"""
        result = self.plugin.run(code)
        self.assertEqual(result["lines_of_code"], 3)
        self.assertEqual(result["cyclomatic_complexity"], 1)
    
    def test_complex_code(self):
        code = """
def process(data):
    if data:
        for item in data:
            if item > 0:
                return True
    return False
"""
        result = self.plugin.run(code)
        self.assertGreater(result["cyclomatic_complexity"], 1)


if __name__ == "__main__":
    unittest.main()
```

## Plugin API Reference

### BaseTool Class

```python
class BaseTool:
    """Base class for all plugins"""
    
    # Required attributes
    name: str           # Unique identifier (kebab-case)
    description: str    # Brief description of functionality
    version: str        # Semantic version (e.g., "1.0.0")
    
    # Optional attributes
    author: str         # Plugin author
    dependencies: List[str]  # Required Python packages
    
    # Required methods
    def run(self, *args, **kwargs) -> Any:
        """Execute plugin functionality"""
        raise NotImplementedError
```

### Plugin Registry

The plugin registry provides methods to interact with loaded plugins:

```python
from src.utils.plugins.registry import registry

# List all available plugins
plugins = registry.list_tools()

# Get a specific plugin
plugin = registry.get_tool("plugin-name")

# Run a plugin
result = plugin.run(*args, **kwargs)
```

## Best Practices

### 1. Error Handling

Always handle errors gracefully:

```python
def run(self, *args, **kwargs):
    try:
        # Plugin logic
        result = self._process(*args, **kwargs)
        return {"success": True, "result": result}
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }
```

### 2. Configuration

Use environment variables for configuration:

```python
import os

class MyPlugin(BaseTool):
    def __init__(self):
        super().__init__()
        self.api_key = os.environ.get("MY_PLUGIN_API_KEY")
        if not self.api_key:
            raise ValueError("MY_PLUGIN_API_KEY not set")
```

### 3. Logging

Use Python's logging module:

```python
import logging

logger = logging.getLogger(__name__)

class MyPlugin(BaseTool):
    def run(self, *args, **kwargs):
        logger.info(f"Running {self.name} plugin")
        # Plugin logic
        logger.debug(f"Processed {len(args)} arguments")
```

### 4. Type Hints

Use type hints for better IDE support and documentation:

```python
from typing import Dict, List, Optional

def run(
    self, 
    code: str, 
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process code with optional configuration.
    
    Args:
        code: Source code to process
        options: Optional configuration dictionary
    
    Returns:
        Dictionary with processing results
    """
    pass
```

### 5. Documentation

Provide comprehensive docstrings:

```python
class MyPlugin(BaseTool):
    """
    Brief one-line description.
    
    Detailed description of what the plugin does, its use cases,
    and any important implementation details.
    
    Attributes:
        name: Unique plugin identifier
        version: Plugin version
        
    Example:
        >>> plugin = MyPlugin()
        >>> result = plugin.run("def foo(): pass")
        >>> print(result["success"])
        True
    """
```

## Examples

### Example 1: Code Style Checker

```python
# plugins/style_checker.py

from src.utils.plugins.base import BaseTool
import ast
import re

class StyleChecker(BaseTool):
    """Checks Python code style compliance"""
    
    def __init__(self):
        super().__init__()
        self.name = "style-checker"
        self.description = "PEP 8 style checker for Python code"
        self.version = "1.0.0"
    
    def run(self, code: str) -> Dict[str, Any]:
        issues = []
        
        # Check line length
        for i, line in enumerate(code.splitlines(), 1):
            if len(line) > 88:
                issues.append({
                    "line": i,
                    "type": "line-too-long",
                    "message": f"Line exceeds 88 characters ({len(line)} chars)"
                })
        
        # Check for camelCase in functions
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if re.search(r'[A-Z]', node.name):
                        issues.append({
                            "line": node.lineno,
                            "type": "naming-convention",
                            "message": f"Function '{node.name}' should be snake_case"
                        })
        except SyntaxError:
            issues.append({
                "line": 0,
                "type": "syntax-error",
                "message": "Code contains syntax errors"
            })
        
        return {
            "success": True,
            "issues_found": len(issues),
            "issues": issues
        }
```

### Example 2: Integration with External API

```python
# plugins/openai_refactor.py

import os
from typing import Dict, Any
from src.utils.plugins.base import BaseTool
import openai

class OpenAIRefactor(BaseTool):
    """Uses OpenAI to suggest code refactorings"""
    
    def __init__(self):
        super().__init__()
        self.name = "openai-refactor"
        self.description = "AI-powered code refactoring suggestions"
        self.version = "1.0.0"
        self.dependencies = ["openai"]
        
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if self.api_key:
            openai.api_key = self.api_key
    
    def run(self, code: str, focus: str = "optimization") -> Dict[str, Any]:
        if not self.api_key:
            return {
                "success": False,
                "error": "OPENAI_API_KEY not configured"
            }
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a code refactoring expert."},
                    {"role": "user", "content": f"Suggest improvements for this code with focus on {focus}:\n\n{code}"}
                ],
                max_tokens=500
            )
            
            return {
                "success": True,
                "suggestions": response.choices[0].message.content,
                "model": response.model,
                "tokens_used": response.usage.total_tokens
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
```

## Testing Plugins

Run plugin tests with pytest:

```bash
# Test all plugins
pytest tests/test_*.py

# Test specific plugin
pytest tests/test_my_plugin.py -v

# Test with coverage
pytest tests/ --cov=plugins --cov-report=html
```

## Troubleshooting

### Plugin Not Loading

1. Check that the plugin file is in the `plugins/` directory
2. Ensure the class inherits from `BaseTool`
3. Verify the `name` attribute is set and unique
4. Check application logs for plugin discovery errors

### Import Errors

1. Install missing dependencies: `pip install package-name`
2. Add dependencies to `requirements.txt`
3. Verify relative imports use absolute paths

### Runtime Errors

1. Enable debug logging: `LOG_LEVEL=DEBUG codetune-studio`
2. Check plugin logs in the application output
3. Validate input data in the plugin's `run()` method

## Contributing Plugins

To share your plugin with the community:

1. Create a pull request to the main repository
2. Include tests for your plugin
3. Update this guide with your plugin's documentation
4. Add your plugin to the example list in the README

## Resources

- [Plugin Base Class](../utils/plugins/base.py)
- [Plugin Registry](../utils/plugins/registry.py)
- [Example Plugins](../plugins/)
- [Testing Guide](./TESTING.md)

---

For questions or support, please open an issue on [GitHub](https://github.com/canstralian/CodeTuneStudio/issues).
