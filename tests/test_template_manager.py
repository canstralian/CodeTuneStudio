"""
Tests for the centralized template manager.
"""

import pytest

from utils.template_manager import TemplateManager, get_template_manager


class TestTemplateManager:
    """Test cases for TemplateManager class."""

    def test_initialization(self):
        """Test template manager initialization."""
        manager = TemplateManager()
        assert len(manager.get_supported_languages()) > 0

    def test_get_templates_python(self):
        """Test getting Python templates."""
        manager = TemplateManager()
        templates = manager.get_templates("python")
        assert len(templates) > 0
        assert all(isinstance(t, str) for t in templates)

    def test_get_templates_javascript(self):
        """Test getting JavaScript templates."""
        manager = TemplateManager()
        templates = manager.get_templates("javascript")
        assert len(templates) > 0
        assert all(isinstance(t, str) for t in templates)

    def test_get_templates_case_insensitive(self):
        """Test that language names are case-insensitive."""
        manager = TemplateManager()
        python_lower = manager.get_templates("python")
        python_upper = manager.get_templates("PYTHON")
        assert python_lower == python_upper

    def test_get_templates_unsupported_language(self):
        """Test getting templates for unsupported language."""
        manager = TemplateManager()
        with pytest.raises(ValueError):
            manager.get_templates("unsupported_language")

    def test_add_template(self):
        """Test adding a new template."""
        manager = TemplateManager()
        initial_count = len(manager.get_templates("python"))
        manager.add_template("python", "def new_function(): pass")
        assert len(manager.get_templates("python")) == initial_count + 1

    def test_add_template_empty(self):
        """Test adding empty template raises error."""
        manager = TemplateManager()
        with pytest.raises(ValueError):
            manager.add_template("python", "")

    def test_get_random_template(self):
        """Test getting a random template."""
        manager = TemplateManager()
        template = manager.get_random_template("python")
        assert isinstance(template, str)
        assert len(template) > 0

    def test_get_supported_languages(self):
        """Test getting list of supported languages."""
        manager = TemplateManager()
        languages = manager.get_supported_languages()
        assert "python" in languages
        assert "javascript" in languages

    def test_clear_templates_specific(self):
        """Test clearing templates for specific language."""
        manager = TemplateManager()
        manager.clear_templates("python")
        with pytest.raises(ValueError):
            manager.get_templates("python")

    def test_clear_templates_all(self):
        """Test clearing all templates."""
        manager = TemplateManager()
        manager.clear_templates()
        assert len(manager.get_supported_languages()) == 0

    def test_generate_template_variations(self):
        """Test generating template variations."""
        manager = TemplateManager()
        variations = manager.generate_template_variations("python", count=5)
        assert len(variations) == 5

    def test_generate_template_variations_zero(self):
        """Test generating zero variations."""
        manager = TemplateManager()
        variations = manager.generate_template_variations("python", count=0)
        assert len(variations) == 0

    def test_generate_template_variations_negative(self):
        """Test that negative count raises error."""
        manager = TemplateManager()
        with pytest.raises(ValueError):
            manager.generate_template_variations("python", count=-1)

    def test_global_singleton(self):
        """Test that get_template_manager returns singleton."""
        manager1 = get_template_manager()
        manager2 = get_template_manager()
        assert manager1 is manager2
