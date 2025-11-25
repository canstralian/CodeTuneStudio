"""
Template Manager Module

This module provides centralized handling of language-specific code templates
for generating synthetic training data. Previously embedded in reddit_dataset.py,
this logic is now extracted for better maintainability and reusability.
"""

import logging
import random
from typing import Dict, List

# Configure logging
logger = logging.getLogger(__name__)


class TemplateManager:
    """
    Centralized manager for language-specific code templates.

    This class provides a unified interface for generating nonsensical but
    syntactically valid code snippets across multiple programming languages.
    Templates are used for augmenting training datasets with diverse examples.

    Attributes:
        templates (Dict[str, List[str]]): Dictionary mapping language names
            to lists of template strings.
    """

    def __init__(self) -> None:
        """Initialize the template manager with default templates."""
        self.templates: Dict[str, List[str]] = {
            "python": [
                (
                    "def dance_with_bytes(rainbow_bits):\n"
                    "    return ''.join([chr((ord(b) << 2) >> 1) "
                    "for b in rainbow_bits])"
                ),
                (
                    "class QuantumPancake:\n"
                    "    def flip_in_time(self, syrup_waves):\n"
                    "        return float('inf') if syrup_waves else None"
                ),
                (
                    "async def dream_compiler(thoughts):\n"
                    "    return await sorted(thoughts, "
                    "key=lambda x: hash(str(x)))"
                ),
            ],
            "javascript": [
                (
                    "function whisperToPromises(dreamState) {\n"
                    "    return new Promise(resolve => "
                    "setTimeout(() => resolve(undefined ?? dreamState), "
                    "Infinity))}"
                ),
                (
                    "const floatingPixels = bytes => bytes.map(b => "
                    "typeof b === 'number' ? String.fromCharCode(b) : '🌈')"
                ),
                (
                    "class TimeTravel {\n"
                    "    static async rewind(memories) {\n"
                    "        return [...memories].reverse().filter(Boolean)}}"
                ),
            ],
        }
        logger.info(
            f"TemplateManager initialized with {len(self.templates)} languages"
        )

    def add_template(self, language: str, template: str) -> None:
        """
        Add a new template for a specific language.

        Args:
            language: Programming language name (e.g., 'python', 'javascript')
            template: Template string to add

        Raises:
            ValueError: If language or template is empty
        """
        if not language or not template:
            raise ValueError("Language and template must be non-empty strings")

        if language.lower() not in self.templates:
            self.templates[language.lower()] = []

        self.templates[language.lower()].append(template)
        logger.debug(f"Added template for language: {language}")

    def get_template(self, language: str) -> str:
        """
        Get a random template for the specified language.

        Args:
            language: Programming language name

        Returns:
            Random template string for the language

        Raises:
            ValueError: If language is not supported
        """
        lang_lower = language.lower()

        if lang_lower not in self.templates:
            raise ValueError(
                f"Language '{language}' not supported. "
                f"Available: {', '.join(self.templates.keys())}"
            )

        return random.choice(self.templates[lang_lower])

    def get_templates(self, language: str) -> List[str]:
        """
        Get all templates for the specified language.

        Args:
            language: Programming language name

        Returns:
            List of template strings for the language

        Raises:
            ValueError: If language is not supported
        """
        lang_lower = language.lower()

        if lang_lower not in self.templates:
            raise ValueError(
                f"Language '{language}' not supported. "
                f"Available: {', '.join(self.templates.keys())}"
            )

        return self.templates[lang_lower].copy()

    def get_supported_languages(self) -> List[str]:
        """
        Get list of supported programming languages.

        Returns:
            List of language names
        """
        return list(self.templates.keys())

    def generate_code(self, language: str) -> str:
        """
        Generate nonsensical but syntactically valid code.

        This method is an alias for get_template() for backward compatibility
        and semantic clarity when generating code snippets.

        Args:
            language: Target programming language

        Returns:
            Generated code snippet

        Raises:
            ValueError: If language is not supported
        """
        return self.get_template(language)


# Global instance for shared use
_default_manager: TemplateManager | None = None


def get_default_template_manager() -> TemplateManager:
    """
    Get the default global template manager instance.

    This function implements a singleton pattern for the default template
    manager, ensuring consistent template access across the application.

    Returns:
        The default TemplateManager instance
    """
    global _default_manager
    if _default_manager is None:
        _default_manager = TemplateManager()
    return _default_manager
