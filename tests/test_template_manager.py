"""
Tests for Template Manager

Unit tests for the centralized template management system.
"""

import unittest

from utils.template_manager import (
    TemplateManager,
    get_default_template_manager,
)


class TestTemplateManager(unittest.TestCase):
    """Test cases for TemplateManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = TemplateManager()

    def test_initialization(self):
        """Test that manager initializes with default templates."""
        self.assertIsNotNone(self.manager.templates)
        self.assertIn("python", self.manager.templates)
        self.assertIn("javascript", self.manager.templates)

    def test_get_supported_languages(self):
        """Test getting list of supported languages."""
        languages = self.manager.get_supported_languages()
        self.assertIsInstance(languages, list)
        self.assertIn("python", languages)
        self.assertIn("javascript", languages)

    def test_get_template_python(self):
        """Test getting a Python template."""
        template = self.manager.get_template("python")
        self.assertIsInstance(template, str)
        self.assertGreater(len(template), 0)

    def test_get_template_javascript(self):
        """Test getting a JavaScript template."""
        template = self.manager.get_template("javascript")
        self.assertIsInstance(template, str)
        self.assertGreater(len(template), 0)

    def test_get_template_case_insensitive(self):
        """Test that language names are case-insensitive."""
        template1 = self.manager.get_template("Python")
        template2 = self.manager.get_template("PYTHON")
        # Both should succeed and return valid templates
        self.assertIsInstance(template1, str)
        self.assertIsInstance(template2, str)

    def test_get_template_unsupported_language(self):
        """Test that unsupported language raises ValueError."""
        with self.assertRaises(ValueError):
            self.manager.get_template("unsupported_language")

    def test_add_template(self):
        """Test adding a new template."""
        test_code = "print('test')"
        self.manager.add_template("python", test_code)
        templates = self.manager.get_templates("python")
        self.assertIn(test_code, templates)

    def test_add_template_new_language(self):
        """Test adding template for a new language."""
        test_code = "echo 'test'"
        self.manager.add_template("bash", test_code)
        self.assertIn("bash", self.manager.get_supported_languages())
        template = self.manager.get_template("bash")
        self.assertEqual(template, test_code)

    def test_add_template_invalid_input(self):
        """Test that invalid inputs raise ValueError."""
        with self.assertRaises(ValueError):
            self.manager.add_template("", "code")
        with self.assertRaises(ValueError):
            self.manager.add_template("python", "")

    def test_get_templates(self):
        """Test getting all templates for a language."""
        templates = self.manager.get_templates("python")
        self.assertIsInstance(templates, list)
        self.assertGreater(len(templates), 0)

    def test_generate_code(self):
        """Test the generate_code alias method."""
        code = self.manager.generate_code("python")
        self.assertIsInstance(code, str)
        self.assertGreater(len(code), 0)

    def test_default_template_manager_singleton(self):
        """Test that default manager is a singleton."""
        manager1 = get_default_template_manager()
        manager2 = get_default_template_manager()
        self.assertIs(manager1, manager2)


if __name__ == "__main__":
    unittest.main()
