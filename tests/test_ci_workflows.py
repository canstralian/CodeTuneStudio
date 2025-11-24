"""
Tests for GitHub Actions CI workflow configuration.

These tests verify that CI workflows are properly configured with
correct Python versions and caching settings.
"""

import os
import unittest
import yaml


class TestCIWorkflows(unittest.TestCase):
    """Test CI workflow configurations"""

    def setUp(self):
        """Set up test fixtures"""
        self.repo_root = os.path.dirname(os.path.dirname(__file__))
        self.workflows_dir = os.path.join(self.repo_root, ".github", "workflows")
        self.ci_yml_path = os.path.join(self.workflows_dir, "ci.yml")
        self.release_yml_path = os.path.join(self.workflows_dir, "release.yml")

    def test_ci_workflow_exists(self):
        """Test that ci.yml workflow file exists"""
        self.assertTrue(
            os.path.exists(self.ci_yml_path),
            "ci.yml workflow file should exist"
        )

    def test_ci_workflow_valid_yaml(self):
        """Test that ci.yml is valid YAML"""
        with open(self.ci_yml_path, 'r') as f:
            try:
                config = yaml.safe_load(f)
                self.assertIsInstance(config, dict)
            except yaml.YAMLError as e:
                self.fail(f"ci.yml is not valid YAML: {e}")

    def test_ci_workflow_python_versions(self):
        """Test that ci.yml tests on correct Python versions"""
        with open(self.ci_yml_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Check test job matrix
        test_job = config.get('jobs', {}).get('test', {})
        matrix = test_job.get('strategy', {}).get('matrix', {})
        python_versions = matrix.get('python-version', [])
        
        # Should test on Python 3.9, 3.10, and 3.11
        expected_versions = ["3.9", "3.10", "3.11"]
        self.assertEqual(
            python_versions,
            expected_versions,
            f"Test matrix should include Python {expected_versions}, got {python_versions}"
        )

    def test_ci_workflow_uses_pip_cache(self):
        """Test that ci.yml uses pip caching"""
        with open(self.ci_yml_path, 'r') as f:
            content = f.read()
        
        # Check for cache: 'pip' in Python setup steps
        self.assertIn("cache: 'pip'", content,
                     "CI workflow should use pip caching")
        
        # Check for cache-dependency-path
        self.assertIn("cache-dependency-path: 'requirements.txt'", content,
                     "CI workflow should use cache-dependency-path for better caching")

    def test_ci_workflow_runs_on_ubuntu(self):
        """Test that ci.yml runs on Ubuntu"""
        with open(self.ci_yml_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Check that all jobs run on ubuntu-latest
        jobs = config.get('jobs', {})
        for job_name, job_config in jobs.items():
            runs_on = job_config.get('runs-on')
            self.assertIn(
                'ubuntu',
                str(runs_on).lower(),
                f"Job '{job_name}' should run on Ubuntu"
            )

    def test_release_workflow_exists(self):
        """Test that release.yml workflow file exists"""
        self.assertTrue(
            os.path.exists(self.release_yml_path),
            "release.yml workflow file should exist"
        )

    def test_release_workflow_valid_yaml(self):
        """Test that release.yml is valid YAML"""
        with open(self.release_yml_path, 'r') as f:
            try:
                config = yaml.safe_load(f)
                self.assertIsInstance(config, dict)
            except yaml.YAMLError as e:
                self.fail(f"release.yml is not valid YAML: {e}")

    def test_release_workflow_python_versions(self):
        """Test that release.yml tests on correct Python versions"""
        with open(self.release_yml_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Check test-install job matrix
        test_install_job = config.get('jobs', {}).get('test-install', {})
        matrix = test_install_job.get('strategy', {}).get('matrix', {})
        python_versions = matrix.get('python-version', [])
        
        # Should test on Python 3.9, 3.10, and 3.11
        expected_versions = ["3.9", "3.10", "3.11"]
        self.assertEqual(
            python_versions,
            expected_versions,
            f"Release test-install matrix should include Python {expected_versions}, got {python_versions}"
        )

    def test_release_workflow_uses_pip_cache(self):
        """Test that release.yml uses pip caching"""
        with open(self.release_yml_path, 'r') as f:
            content = f.read()
        
        # Check for cache: 'pip' in Python setup steps
        self.assertIn("cache: 'pip'", content,
                     "Release workflow should use pip caching")

    def test_all_workflows_valid_yaml(self):
        """Test that all workflow files are valid YAML"""
        workflow_files = [f for f in os.listdir(self.workflows_dir) 
                         if f.endswith('.yml') or f.endswith('.yaml')]
        
        for workflow_file in workflow_files:
            workflow_path = os.path.join(self.workflows_dir, workflow_file)
            
            # Skip directories
            if not os.path.isfile(workflow_path):
                continue
                
            with open(workflow_path, 'r') as f:
                try:
                    config = yaml.safe_load(f)
                    self.assertIsInstance(
                        config, dict,
                        f"{workflow_file} should be a valid YAML dictionary"
                    )
                except yaml.YAMLError as e:
                    self.fail(f"{workflow_file} is not valid YAML: {e}")


if __name__ == "__main__":
    unittest.main()
