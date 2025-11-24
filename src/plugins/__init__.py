"""
Code analysis plugins for CodeTune Studio.

Plugins are automatically discovered by the plugin registry.
Import specific plugins as needed:
    from src.plugins.openai_code_analyzer import OpenAICodeAnalyzerTool
    from src.plugins.anthropic_code_suggester import AnthropicCodeSuggesterTool
    from src.plugins.code_analyzer import CodeAnalyzerTool

The plugin registry handles dynamic loading, so there's no need
to list plugins explicitly in __all__.
"""
