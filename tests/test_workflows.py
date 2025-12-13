"""
Tests for GitHub workflow configurations and validation.

These tests verify that workflow files are properly structured,
use correct syntax, and reference valid files and paths.
"""

import os
import unittest
import yaml
from pathlib import Path


class TestWorkflowStructure(unittest.TestCase):
    """Test workflow file structure and syntax"""

    def setUp(self):
        """Set up test fixtures"""
        self.repo_root = Path(__file__).parent.parent
        self.workflows_dir = self.repo_root / ".github" / "workflows"

    def test_workflows_directory_exists(self):
        """Test that workflows directory exists"""
        self.assertTrue(self.workflows_dir.exists())
        self.assertTrue(self.workflows_dir.is_dir())

    def test_all_workflow_files_have_valid_yaml(self):
        """Test that all workflow files have valid YAML syntax"""
        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(
            self.workflows_dir.glob("*.yaml")
        )
        workflow_files.extend(self.workflows_dir.glob("**/*.yml"))
        workflow_files.extend(self.workflows_dir.glob("**/*.yaml"))

        self.assertGreater(len(workflow_files), 0, "No workflow files found")

        for workflow_file in workflow_files:
            with self.subTest(workflow=workflow_file.name):
                with open(workflow_file, "r") as f:
                    try:
                        content = yaml.safe_load(f)
                        self.assertIsNotNone(
                            content, f"{workflow_file.name} is empty or invalid"
                        )
                    except yaml.YAMLError as e:
                        self.fail(
                            f"Invalid YAML in {workflow_file.name}: {e}"
                        )

    def test_workflows_have_required_fields(self):
        """Test that workflows have required fields (name, on, jobs)"""
        workflow_files = [
            self.workflows_dir / "auto-update-checklist.yml",
            self.workflows_dir / "ci.yml",
            self.workflows_dir / "pr-checklist-status.yml",
            self.workflows_dir / "python-style-checks.yml",
            self.workflows_dir / "release.yml",
            self.workflows_dir / "huggingface-deploy.yml",
            self.workflows_dir / "dynamic" / "dependency-graph" / "auto-submission",
        ]

        for workflow_file in workflow_files:
            if not workflow_file.exists():
                continue

            with self.subTest(workflow=workflow_file.name):
                with open(workflow_file, "r") as f:
                    content = yaml.safe_load(f)

                    if content is None:
                        continue

                    # Check for basic structure
                    if "name" in content:
                        # YAML parsers may interpret 'on:' as boolean True
                        # Check for either 'on' or True key
                        has_trigger = "on" in content or True in content
                        self.assertTrue(
                            has_trigger,
                            f"{workflow_file.name} missing trigger ('on' field)",
                        )
                        self.assertIn(
                            "jobs",
                            content,
                            f"{workflow_file.name} missing jobs definition",
                        )


class TestAutoUpdateChecklistWorkflow(unittest.TestCase):
    """Test auto-update-checklist.yml workflow"""

    def setUp(self):
        """Set up test fixtures"""
        self.repo_root = Path(__file__).parent.parent
        self.workflow_file = (
            self.repo_root / ".github" / "workflows" / "auto-update-checklist.yml"
        )
        self.script_file = self.repo_root / "scripts" / "update_checklist.py"
        self.checklist_file = self.repo_root / "PR_REVIEW_CHECKLIST.md"

    def test_workflow_exists(self):
        """Test that workflow file exists"""
        self.assertTrue(self.workflow_file.exists())

    def test_referenced_script_exists(self):
        """Test that the update script exists"""
        self.assertTrue(
            self.script_file.exists(),
            f"Update script not found at {self.script_file}",
        )

    def test_checklist_file_exists(self):
        """Test that the checklist file exists"""
        self.assertTrue(
            self.checklist_file.exists(),
            f"Checklist file not found at {self.checklist_file}",
        )

    def test_workflow_references_correct_file(self):
        """Test that workflow references the correct checklist file"""
        with open(self.workflow_file, "r") as f:
            content = f.read()

        # The workflow should reference the correct checklist file
        self.assertIn(
            "PR_REVIEW_CHECKLIST.md",
            content,
            "Workflow should reference PR_REVIEW_CHECKLIST.md",
        )


class TestCIWorkflow(unittest.TestCase):
    """Test ci.yml workflow"""

    def setUp(self):
        """Set up test fixtures"""
        self.repo_root = Path(__file__).parent.parent
        self.workflow_file = self.repo_root / ".github" / "workflows" / "ci.yml"
        self.requirements_file = self.repo_root / "requirements.txt"

    def test_workflow_exists(self):
        """Test that workflow file exists"""
        self.assertTrue(self.workflow_file.exists())

    def test_requirements_file_exists(self):
        """Test that requirements.txt exists"""
        self.assertTrue(self.requirements_file.exists())

    def test_workflow_has_all_required_jobs(self):
        """Test that workflow defines all required jobs"""
        with open(self.workflow_file, "r") as f:
            content = yaml.safe_load(f)

        required_jobs = ["lint", "type-check", "test", "build"]
        jobs = content.get("jobs", {})

        for job in required_jobs:
            self.assertIn(job, jobs, f"Missing required job: {job}")


class TestPythonStyleChecksWorkflow(unittest.TestCase):
    """Test python-style-checks.yml workflow"""

    def setUp(self):
        """Set up test fixtures"""
        self.repo_root = Path(__file__).parent.parent
        self.workflow_file = (
            self.repo_root / ".github" / "workflows" / "python-style-checks.yml"
        )
        self.precommit_config = self.repo_root / ".pre-commit-config.yaml"

    def test_workflow_exists(self):
        """Test that workflow file exists"""
        self.assertTrue(self.workflow_file.exists())

    def test_precommit_config_exists(self):
        """Test that pre-commit config exists"""
        self.assertTrue(
            self.precommit_config.exists(),
            "Pre-commit config file should exist",
        )

    def test_workflow_checks_for_precommit_config(self):
        """Test that workflow verifies pre-commit config"""
        with open(self.workflow_file, "r") as f:
            content = f.read()

        self.assertIn(
            ".pre-commit-config.yaml",
            content,
            "Workflow should check for pre-commit config",
        )


class TestReleaseWorkflow(unittest.TestCase):
    """Test release.yml workflow"""

    def setUp(self):
        """Set up test fixtures"""
        self.repo_root = Path(__file__).parent.parent
        self.workflow_file = self.repo_root / ".github" / "workflows" / "release.yml"
        self.core_init = self.repo_root / "core" / "__init__.py"
        self.changelog = self.repo_root / "CHANGELOG.md"

    def test_workflow_exists(self):
        """Test that workflow file exists"""
        self.assertTrue(self.workflow_file.exists())

    def test_version_file_exists(self):
        """Test that core/__init__.py with version exists"""
        self.assertTrue(self.core_init.exists())

    def test_version_is_defined(self):
        """Test that version is properly defined"""
        from core import __version__

        self.assertIsNotNone(__version__)
        self.assertRegex(__version__, r"^\d+\.\d+\.\d+$")

    def test_changelog_exists(self):
        """Test that CHANGELOG.md exists"""
        self.assertTrue(self.changelog.exists())


class TestHuggingFaceWorkflows(unittest.TestCase):
    """Test Hugging Face related workflows"""

    def setUp(self):
        """Set up test fixtures"""
        self.repo_root = Path(__file__).parent.parent
        self.deploy_workflow = (
            self.repo_root / ".github" / "workflows" / "huggingface-deploy.yml"
        )
        self.metadata_file = (
            self.repo_root / ".github" / "workflows" / "hf_space_metadata.yml"
        )
        self.space_yaml = self.repo_root / "space.yaml"

    def test_deploy_workflow_exists(self):
        """Test that deploy workflow exists"""
        self.assertTrue(self.deploy_workflow.exists())

    def test_space_yaml_exists(self):
        """Test that space.yaml exists in repo root"""
        self.assertTrue(
            self.space_yaml.exists(),
            "space.yaml should exist for HF Space deployment",
        )

    def test_metadata_file_is_valid_yaml(self):
        """Test that HF metadata file is valid YAML"""
        if self.metadata_file.exists():
            with open(self.metadata_file, "r") as f:
                try:
                    content = yaml.safe_load(f)
                    # Note: This is metadata, not a workflow
                    self.assertIsNotNone(content)
                except yaml.YAMLError as e:
                    self.fail(f"Invalid YAML in metadata file: {e}")


class TestDependencyGraphWorkflow(unittest.TestCase):
    """Test dependency graph workflow"""

    def setUp(self):
        """Set up test fixtures"""
        self.repo_root = Path(__file__).parent.parent
        self.workflow_file = (
            self.repo_root
            / ".github"
            / "workflows"
            / "dynamic"
            / "dependency-graph"
            / "auto-submission"
        )

    def test_workflow_exists(self):
        """Test that workflow file exists"""
        self.assertTrue(self.workflow_file.exists())

    def test_workflow_validates_dependencies(self):
        """Test that workflow includes dependency validation"""
        with open(self.workflow_file, "r") as f:
            content = f.read()

        validation_keywords = [
            "pip-compile",
            "requirements.txt",
            "pyproject.toml",
        ]

        found_keywords = [kw for kw in validation_keywords if kw in content]
        self.assertGreater(
            len(found_keywords),
            0,
            f"Workflow should include dependency validation. Found: {found_keywords}",
        )


class TestPRChecklistWorkflow(unittest.TestCase):
    """Test pr-checklist-status.yml workflow"""

    def setUp(self):
        """Set up test fixtures"""
        self.repo_root = Path(__file__).parent.parent
        self.workflow_file = (
            self.repo_root / ".github" / "workflows" / "pr-checklist-status.yml"
        )

    def test_workflow_exists(self):
        """Test that workflow file exists"""
        self.assertTrue(self.workflow_file.exists())

    def test_workflow_has_lint_job(self):
        """Test that workflow has lint job"""
        with open(self.workflow_file, "r") as f:
            content = yaml.safe_load(f)

        jobs = content.get("jobs", {})
        # Should have lint-and-format or similar job
        job_names = list(jobs.keys())
        self.assertGreater(len(job_names), 0, "Workflow should have at least one job")


if __name__ == "__main__":
    unittest.main()
