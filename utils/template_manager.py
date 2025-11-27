"""
Centralized template manager for language-specific code templates.

This module provides a unified interface for managing code templates
across different programming languages. It centralizes template handling
previously scattered across multiple modules.
"""

import logging
import random
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class TemplateManager:
    """
    Centralized manager for language-specific code templates.

    This class provides a unified interface for storing, retrieving, and
    generating code templates for various programming languages. It supports
    caching for improved performance.

    Attributes:
        _templates: Dictionary mapping language names to template lists
    """

    def __init__(self) -> None:
        """Initialize the template manager with default templates."""
        self._templates: Dict[str, List[str]] = {}
        self._load_default_templates()

    def _load_default_templates(self) -> None:
        """Load default code templates for supported languages."""
        # Python templates for amphigory (nonsensical but valid) code
        self._templates["python"] = [
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
        ]

        # JavaScript templates
        self._templates["javascript"] = [
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
        ]

        logger.info(
            f"Loaded templates for {len(self._templates)} languages: "
            f"{', '.join(self._templates.keys())}"
        )

    def add_template(self, language: str, template: str) -> None:
        """
        Add a new template for a specific language.

        Args:
            language: Programming language identifier (e.g., 'python', 'javascript')
            template: Code template string

        Raises:
            ValueError: If template is empty or language is invalid
        """
        if not template or not template.strip():
            raise ValueError("Template cannot be empty")

        language_key = language.lower()
        if language_key not in self._templates:
            self._templates[language_key] = []

        self._templates[language_key].append(template)
        logger.debug(f"Added template for language: {language_key}")

    def get_templates(self, language: str) -> List[str]:
        """
        Get all templates for a specific language.

        Args:
            language: Programming language identifier

        Returns:
            List of template strings for the specified language

        Raises:
            ValueError: If language is not supported
        """
        language_key = language.lower()
        if language_key not in self._templates:
            raise ValueError(
                f"Language '{language}' not supported. "
                f"Available languages: {', '.join(self._templates.keys())}"
            )

        return self._templates[language_key].copy()

    def get_random_template(self, language: str) -> str:
        """
        Get a random template for a specific language.

        Args:
            language: Programming language identifier

        Returns:
            Random template string from the specified language

        Raises:
            ValueError: If language is not supported or has no templates
        """
        templates = self.get_templates(language)
        if not templates:
            raise ValueError(f"No templates available for language: {language}")

        return random.choice(templates)

    def get_supported_languages(self) -> List[str]:
        """
        Get list of supported language identifiers.

        Returns:
            List of supported programming language names
        """
        return list(self._templates.keys())

    def clear_templates(self, language: Optional[str] = None) -> None:
        """
        Clear templates for a specific language or all languages.

        Args:
            language: Optional language identifier. If None, clears all templates.
        """
        if language is None:
            self._templates.clear()
            logger.info("Cleared all templates")
        else:
            language_key = language.lower()
            if language_key in self._templates:
                del self._templates[language_key]
                logger.info(f"Cleared templates for language: {language_key}")

    def generate_template_variations(
        self, language: str, count: int = 1
    ) -> List[str]:
        """
        Generate multiple template variations for a language.

        Args:
            language: Programming language identifier
            count: Number of templates to generate

        Returns:
            List of template strings

        Raises:
            ValueError: If count is negative or language is not supported
        """
        if count < 0:
            raise ValueError("Count must be non-negative")

        if count == 0:
            return []

        templates = self.get_templates(language)
        if not templates:
            raise ValueError(f"No templates available for language: {language}")

        # If count exceeds available templates, repeat with shuffling
        if count <= len(templates):
            return random.sample(templates, count)

        # Generate more templates by repeating and shuffling
        result = templates * (count // len(templates) + 1)
        random.shuffle(result)
        return result[:count]


# Global singleton instance for easy access
_template_manager: Optional[TemplateManager] = None


def get_template_manager() -> TemplateManager:
    """
    Get the global TemplateManager singleton instance.

    Returns:
        Global TemplateManager instance
    """
    global _template_manager
    if _template_manager is None:
        _template_manager = TemplateManager()
    return _template_manager
