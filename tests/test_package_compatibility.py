"""Test package compatibility and versions."""

import unittest


class TestPackageCompatibility(unittest.TestCase):
    """Test that critical packages are installed with correct versions."""

    def test_argilla_installed(self):
        """Test that argilla is installed and importable."""
        try:
            import argilla
            self.assertTrue(hasattr(argilla, '__version__'))
        except ImportError:
            self.fail("argilla package is not installed")

    def test_evaluate_installed(self):
        """Test that evaluate package is installed and importable."""
        try:
            import evaluate
            self.assertTrue(hasattr(evaluate, '__version__'))
        except ImportError:
            self.fail("evaluate package is not installed")

    def test_transformers_installed(self):
        """Test that transformers is installed and importable."""
        try:
            import transformers
            self.assertTrue(hasattr(transformers, '__version__'))
        except ImportError:
            self.fail("transformers package is not installed")

    def test_datasets_installed(self):
        """Test that datasets is installed and importable."""
        try:
            import datasets
            self.assertTrue(hasattr(datasets, '__version__'))
        except ImportError:
            self.fail("datasets package is not installed")

    def test_accelerate_installed(self):
        """Test that accelerate is installed and importable."""
        try:
            import accelerate
            self.assertTrue(hasattr(accelerate, '__version__'))
        except ImportError:
            self.fail("accelerate package is not installed")


if __name__ == '__main__':
    unittest.main()
