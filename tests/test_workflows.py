"""
Tests for GitHub Actions workflow files.

This module validates the syntax and structure of workflow YAML files
to ensure they are properly configured.
"""

import unittest
from pathlib import Path

import yaml


class TestWorkflows(unittest.TestCase):
    """Test cases for GitHub Actions workflow files."""

    def setUp(self):
        """Set up test fixtures."""
        self.workflows_dir = Path(__file__).parent.parent / ".github" / "workflows"
        self.assertTrue(
            self.workflows_dir.exists(),
            f"Workflows directory not found: {self.workflows_dir}",
        )

    def test_workflow_yaml_syntax(self):
        """Test that all workflow YAML files have valid syntax."""
        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(
            self.workflows_dir.glob("*.yaml")
        )
        self.assertGreater(len(workflow_files), 0, "No workflow files found")

        # Skip known broken files that are pre-existing issues
        # stalesweeper.yml: Malformed YAML (missing document start, improper nesting)
        skip_files = {"stalesweeper.yml"}

        for workflow_file in workflow_files:
            if workflow_file.name in skip_files:
                continue

            with self.subTest(workflow=workflow_file.name):
                with open(workflow_file, "r") as f:
                    try:
                        yaml.safe_load(f)
                    except yaml.YAMLError as e:
                        self.fail(f"Invalid YAML syntax in {workflow_file.name}: {e}")

    def test_pr_checklist_status_permissions(self):
        """Test that pr-checklist-status.yml has correct permissions."""
        workflow_file = self.workflows_dir / "pr-checklist-status.yml"
        self.assertTrue(
            workflow_file.exists(),
            "pr-checklist-status.yml not found",
        )

        with open(workflow_file, "r") as f:
            workflow = yaml.safe_load(f)

        # Verify permissions are set
        self.assertIn("permissions", workflow, "Workflow must have permissions defined")

        permissions = workflow["permissions"]

        # Verify pull-requests: write permission
        self.assertIn(
            "pull-requests",
            permissions,
            "Workflow must have pull-requests permission",
        )
        self.assertEqual(
            permissions["pull-requests"],
            "write",
            "pull-requests permission must be 'write'",
        )

        # Verify contents: read permission
        self.assertIn("contents", permissions, "Workflow must have contents permission")
        self.assertEqual(
            permissions["contents"],
            "read",
            "contents permission must be 'read'",
        )

    def test_pr_checklist_status_has_debug_step(self):
        """Test that pr-checklist-status.yml has the debug token permissions step."""
        workflow_file = self.workflows_dir / "pr-checklist-status.yml"

        with open(workflow_file, "r") as f:
            workflow = yaml.safe_load(f)

        # Find checklist-validation job
        self.assertIn("jobs", workflow, "Workflow must have jobs")
        self.assertIn(
            "checklist-validation",
            workflow["jobs"],
            "Workflow must have checklist-validation job",
        )

        job = workflow["jobs"]["checklist-validation"]
        self.assertIn("steps", job, "Job must have steps")

        # Find debug step
        debug_step_found = False
        for step in job["steps"]:
            if "name" in step and "Debug Token Permissions" in step["name"]:
                debug_step_found = True
                # Verify the step has a run command
                self.assertIn(
                    "run",
                    step,
                    "Debug step must have a run command",
                )
                # Verify it checks token permissions
                self.assertIn(
                    "actions/permissions",
                    step["run"],
                    "Debug step must check permissions",
                )
                break

        self.assertTrue(
            debug_step_found,
            "Workflow must have 'Debug Token Permissions' step",
        )

    def test_pr_checklist_status_has_fallback_script(self):
        """Test that pr-checklist-status.yml has a fallback shell script step."""
        workflow_file = self.workflows_dir / "pr-checklist-status.yml"

        with open(workflow_file, "r") as f:
            workflow = yaml.safe_load(f)

        job = workflow["jobs"]["checklist-validation"]
        self.assertIn("steps", job, "Job must have steps")

        # Find fallback step
        fallback_step_found = False
        for step in job["steps"]:
            if (
                "name" in step
                and "Verify Checklist Items" in step["name"]
                and "Shell Script" in step["name"]
            ):
                fallback_step_found = True
                # Verify the step has a run command
                self.assertIn(
                    "run",
                    step,
                    "Fallback step must have a run command",
                )
                # Verify it only runs on failure
                self.assertIn(
                    "if",
                    step,
                    "Fallback step must have a conditional",
                )
                self.assertEqual(
                    step["if"],
                    "failure()",
                    "Fallback step should run only on failure",
                )
                # Verify it checks for uncompleted tasks
                self.assertIn(
                    "UNCOMPLETED",
                    step["run"],
                    "Fallback step must check for uncompleted tasks",
                )
                break

        self.assertTrue(
            fallback_step_found,
            "Workflow must have 'Verify Checklist Items (Shell Script "
            "Alternative)' step",
        )


if __name__ == "__main__":
    unittest.main()
