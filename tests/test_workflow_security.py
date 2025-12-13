"""
Security tests for GitHub workflows.

These tests verify that workflows follow security best practices
and don't expose sensitive information or use insecure patterns.
"""

import unittest
import yaml
from pathlib import Path
import re


class TestWorkflowSecurity(unittest.TestCase):
    """Test workflow security configurations"""

    def setUp(self):
        """Set up test fixtures"""
        self.repo_root = Path(__file__).parent.parent
        self.workflows_dir = self.repo_root / ".github" / "workflows"

    def get_workflow_files(self):
        """Get all workflow files"""
        workflow_files = []
        for pattern in ["*.yml", "*.yaml"]:
            workflow_files.extend(self.workflows_dir.glob(pattern))
            workflow_files.extend(self.workflows_dir.glob(f"**/{pattern}"))
        return workflow_files

    def test_no_hardcoded_secrets(self):
        """Test that workflows don't contain hardcoded secrets"""
        # Patterns that might indicate hardcoded secrets
        secret_patterns = [
            r"password\s*[:=]\s*['\"](?!.*\$\{)",  # password: "value"
            r"token\s*[:=]\s*['\"](?!.*\$\{)",  # token: "value"
            r"api[_-]?key\s*[:=]\s*['\"](?!.*\$\{)",  # api_key: "value"
            r"ghp_[a-zA-Z0-9]{36}",  # GitHub personal access token
            r"sk-[a-zA-Z0-9]{48}",  # OpenAI API key
        ]

        for workflow_file in self.get_workflow_files():
            with self.subTest(workflow=workflow_file.name):
                with open(workflow_file, "r") as f:
                    content = f.read()

                for pattern in secret_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    # Filter out legitimate uses (like variable references)
                    suspicious_matches = [
                        m
                        for m in matches
                        if "${{" not in str(m) and "secrets." not in str(m)
                    ]

                    self.assertEqual(
                        len(suspicious_matches),
                        0,
                        f"Potential hardcoded secret in {workflow_file.name}: {suspicious_matches}",
                    )

    def test_secrets_use_github_secrets(self):
        """Test that workflows use GitHub secrets properly"""
        for workflow_file in self.get_workflow_files():
            with self.subTest(workflow=workflow_file.name):
                with open(workflow_file, "r") as f:
                    content = yaml.safe_load(f)

                if content is None or "jobs" not in content:
                    continue

                # Check that sensitive environment variables use secrets
                self._check_secrets_usage(content, workflow_file.name)

    def _check_secrets_usage(self, content, filename):
        """Helper to check secrets usage in workflow"""
        sensitive_vars = [
            "GITHUB_TOKEN",
            "HF_TOKEN",
            "PYPI_API_TOKEN",
            "API_KEY",
        ]

        def check_env_section(env_section):
            if not isinstance(env_section, dict):
                return
            for key, value in env_section.items():
                if key in sensitive_vars:
                    # Should use ${{ secrets.* }} or ${{ github.token }}
                    value_str = str(value)
                    if "${{" not in value_str:
                        self.fail(
                            f"{filename}: {key} should use GitHub secrets, found: {value}"
                        )

        # Check all jobs
        jobs = content.get("jobs", {})
        if True in content:  # Handle YAML boolean key issue
            jobs = content[True].get("jobs", {}) if isinstance(content[True], dict) else jobs

        for job_name, job_config in jobs.items():
            if not isinstance(job_config, dict):
                continue

            # Check job-level env
            if "env" in job_config:
                check_env_section(job_config["env"])

            # Check step-level env
            if "steps" in job_config:
                for step in job_config.get("steps", []):
                    if isinstance(step, dict) and "env" in step:
                        check_env_section(step["env"])

    def test_workflows_have_permissions(self):
        """Test that workflows define appropriate permissions"""
        for workflow_file in self.get_workflow_files():
            with self.subTest(workflow=workflow_file.name):
                with open(workflow_file, "r") as f:
                    content = yaml.safe_load(f)

                if content is None:
                    continue

                # Workflows should define permissions (least privilege)
                # Some workflows may not need this if they don't access GitHub APIs
                if "jobs" in content:
                    has_permissions = (
                        "permissions" in content
                        or any(
                            "permissions" in job
                            for job in content["jobs"].values()
                            if isinstance(job, dict)
                        )
                    )
                    # This is a warning, not a hard failure
                    # Some workflows don't need special permissions
                    if not has_permissions:
                        print(
                            f"INFO: {workflow_file.name} doesn't define permissions (may be OK)"
                        )

    def test_no_pull_request_target_without_safety(self):
        """Test that pull_request_target is used safely"""
        for workflow_file in self.get_workflow_files():
            with self.subTest(workflow=workflow_file.name):
                with open(workflow_file, "r") as f:
                    content = yaml.safe_load(f)

                if content is None:
                    continue

                # Check for pull_request_target trigger
                triggers = content.get("on", {}) or content.get(True, {})
                if not isinstance(triggers, dict):
                    continue

                if "pull_request_target" in triggers:
                    # If using pull_request_target, should have safety checks
                    # This is dangerous as it runs with write permissions on PRs from forks
                    self.fail(
                        f"{workflow_file.name} uses pull_request_target which can be dangerous. "
                        "Ensure proper safety checks are in place."
                    )

    def test_checkout_uses_specific_ref(self):
        """Test that dangerous workflows checkout specific refs"""
        for workflow_file in self.get_workflow_files():
            with self.subTest(workflow=workflow_file.name):
                with open(workflow_file, "r") as f:
                    content = f.read()

                # Look for pull_request_target
                if "pull_request_target" in content:
                    # Should have explicit ref in checkout
                    if "actions/checkout@" in content:
                        # This is informational - manual review needed
                        print(
                            f"INFO: {workflow_file.name} uses pull_request_target - "
                            "verify checkout ref is safe"
                        )

    def test_third_party_actions_are_pinned(self):
        """Test that third-party actions are pinned to specific versions"""
        # This is a best practice but not strictly required
        for workflow_file in self.get_workflow_files():
            with self.subTest(workflow=workflow_file.name):
                with open(workflow_file, "r") as f:
                    content = f.read()

                # Find all action uses
                action_uses = re.findall(r"uses:\s*([^\s]+)", content)

                for action in action_uses:
                    # Skip local actions
                    if action.startswith("./"):
                        continue

                    # Should have @version or @sha
                    if "@" not in action:
                        print(
                            f"WARNING: {workflow_file.name} uses unpinned action: {action}"
                        )


class TestWorkflowDependencies(unittest.TestCase):
    """Test workflow dependencies and versions"""

    def setUp(self):
        """Set up test fixtures"""
        self.repo_root = Path(__file__).parent.parent
        self.workflows_dir = self.repo_root / ".github" / "workflows"

    def test_python_versions_are_supported(self):
        """Test that workflows use supported Python versions"""
        supported_versions = ["3.10", "3.11", "3.12"]

        for workflow_file in self.workflows_dir.glob("*.yml"):
            with open(workflow_file, "r") as f:
                content = f.read()

            # Find Python version specifications
            version_matches = re.findall(
                r"python-version:\s*['\"]?(\d+\.\d+)['\"]?", content
            )

            for version in version_matches:
                with self.subTest(workflow=workflow_file.name, version=version):
                    self.assertIn(
                        version,
                        supported_versions,
                        f"{workflow_file.name} uses unsupported Python {version}",
                    )

    def test_actions_use_recent_versions(self):
        """Test that workflows use recent action versions"""
        # Minimum recommended versions
        min_versions = {
            "actions/checkout": 3,
            "actions/setup-python": 4,
            "actions/cache": 3,
            "actions/upload-artifact": 3,
            "actions/download-artifact": 3,
        }

        for workflow_file in self.workflows_dir.glob("*.yml"):
            with open(workflow_file, "r") as f:
                content = f.read()

            for action, min_version in min_versions.items():
                # Find action usage
                pattern = f"{action}@v(\\d+)"
                matches = re.findall(pattern, content)

                for version in matches:
                    with self.subTest(
                        workflow=workflow_file.name, action=action, version=version
                    ):
                        self.assertGreaterEqual(
                            int(version),
                            min_version,
                            f"{workflow_file.name} uses outdated {action}@v{version}",
                        )


if __name__ == "__main__":
    unittest.main()
