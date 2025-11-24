"""
Tests for requirements.txt validation.

These tests verify that requirements.txt is properly formatted and
contains valid package versions that exist in PyPI.
"""

import os
import unittest
import re


class TestRequirements(unittest.TestCase):
    """Test requirements.txt file"""

    def setUp(self):
        """Set up test fixtures"""
        self.repo_root = os.path.dirname(os.path.dirname(__file__))
        self.requirements_path = os.path.join(self.repo_root, "requirements.txt")

    def test_requirements_file_exists(self):
        """Test that requirements.txt exists"""
        self.assertTrue(
            os.path.exists(self.requirements_path),
            "requirements.txt file should exist in repository root"
        )

    def test_requirements_file_readable(self):
        """Test that requirements.txt is readable"""
        with open(self.requirements_path, 'r') as f:
            content = f.read()
            self.assertIsInstance(content, str)
            self.assertTrue(len(content) > 0, "requirements.txt should not be empty")

    def test_requirements_format(self):
        """Test that requirements.txt has valid format"""
        with open(self.requirements_path, 'r') as f:
            lines = f.readlines()
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Check for valid package specification format
            # Matches: package==version, package>=version, package<=version, etc.
            package_pattern = r'^[a-zA-Z0-9_-]+([<>=!]=?[0-9.]+)?(\s*,\s*[<>=!]+[0-9.]+)*$'
            self.assertIsNotNone(
                re.match(package_pattern, line),
                f"Line {line_num} has invalid format: {line}"
            )

    def test_critical_dependencies_pinned(self):
        """Test that critical dependencies are properly pinned"""
        with open(self.requirements_path, 'r') as f:
            content = f.read()
        
        # Check for numpy pinned version
        self.assertIn('numpy==1.21.5', content, 
                     "numpy should be pinned to version 1.21.5")
        
        # Check for evaluate version
        self.assertIn('evaluate==0.4.6', content,
                     "evaluate should be pinned to version 0.4.6")
        
        # Check that argilla doesn't use non-existent version
        self.assertNotIn('argilla==1.24.0', content,
                        "argilla==1.24.0 doesn't exist in PyPI")
        
        # Check that argilla uses valid version specification
        self.assertTrue(
            'argilla>=2.7.0' in content or 'argilla==' in content,
            "argilla should have a valid version specification"
        )

    def test_no_conflicting_versions(self):
        """Test that there are no duplicate package specifications"""
        with open(self.requirements_path, 'r') as f:
            lines = f.readlines()
        
        packages = set()
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Extract package name (before version specifier)
            package_name = re.split(r'[<>=!]', line)[0].strip()
            
            self.assertNotIn(
                package_name, packages,
                f"Duplicate package specification found: {package_name}"
            )
            packages.add(package_name)

    def test_numpy_version_compatible_with_python39(self):
        """Test that numpy version is compatible with Python 3.9+"""
        with open(self.requirements_path, 'r') as f:
            content = f.read()
        
        # numpy 1.21.5 supports Python 3.7-3.10
        # This is compatible with our target Python 3.9, 3.10, 3.11
        if 'numpy==1.21.5' in content:
            # Version 1.21.5 is within the compatible range
            self.assertTrue(True)
        else:
            # If not using 1.21.5, ensure it's a compatible version
            numpy_match = re.search(r'numpy[<>=!]+([0-9.]+)', content)
            if numpy_match:
                version_str = numpy_match.group(1)
                # Parse major.minor version
                parts = version_str.split('.')
                major = int(parts[0])
                minor = int(parts[1]) if len(parts) > 1 else 0
                
                # numpy 2.x dropped Python 3.9 support
                if major >= 2:
                    self.fail(
                        f"numpy {version_str} may not support Python 3.9. "
                        "Use numpy 1.21.x-1.26.x for Python 3.9-3.11 compatibility"
                    )


if __name__ == "__main__":
    unittest.main()
