#!/usr/bin/env python3
"""
Workflow Validation Script

This script validates GitHub workflow files for syntax, security, and best practices.
Can be run locally or in CI to ensure workflows are properly configured.

Usage:
    python scripts/validate_workflows.py
    python scripts/validate_workflows.py --workflow ci.yml
    python scripts/validate_workflows.py --security-only
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml


class WorkflowValidator:
    """Validates GitHub workflow files"""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.workflows_dir = repo_root / ".github" / "workflows"
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.info: list[str] = []

    def validate_all(self, workflow_name: str = None) -> bool:
        """
        Validate all workflows or a specific workflow.

        Args:
            workflow_name: Optional specific workflow to validate

        Returns:
            True if validation passes, False otherwise
        """
        print("🔍 GitHub Workflow Validator")
        print("=" * 60)

        if workflow_name:
            workflow_file = self.workflows_dir / workflow_name
            if not workflow_file.exists():
                self.errors.append(f"Workflow file not found: {workflow_name}")
                return False
            workflows = [workflow_file]
        else:
            workflows = self._get_workflow_files()

        if not workflows:
            self.errors.append("No workflow files found")
            return False

        print(f"📋 Found {len(workflows)} workflow file(s) to validate\n")

        for workflow in workflows:
            self._validate_workflow(workflow)

        self._print_results()
        return len(self.errors) == 0

    def _get_workflow_files(self) -> list[Path]:
        """Get all workflow files"""
        workflows = []
        for pattern in ["*.yml", "*.yaml"]:
            workflows.extend(self.workflows_dir.glob(pattern))
            workflows.extend(self.workflows_dir.glob(f"**/{pattern}"))
        return sorted(set(workflows))

    def _validate_workflow(self, workflow_path: Path):
        """Validate a single workflow file"""
        print(f"📄 Validating: {workflow_path.relative_to(self.repo_root)}")

        # Check YAML syntax
        try:
            with open(workflow_path) as f:
                raw_content = f.read()
                f.seek(0)
                content = yaml.safe_load(f)
        except yaml.YAMLError as e:
            self.errors.append(f"{workflow_path.name}: Invalid YAML - {e}")
            return
        except Exception as e:
            self.errors.append(f"{workflow_path.name}: Error reading file - {e}")
            return

        if content is None:
            self.warnings.append(f"{workflow_path.name}: Empty workflow file")
            return

        # Check if this is a metadata file (not a workflow)
        if self._is_metadata_file(workflow_path.name, content):
            print(
                "  ℹ️  Metadata file (not a workflow) - skipping workflow validation\n"
            )
            return

        # Validate structure
        self._validate_structure(workflow_path.name, content)

        # Validate security
        self._validate_security(workflow_path.name, raw_content, content)

        # Validate best practices
        self._validate_best_practices(workflow_path.name, content)

        print("  ✓ Validation complete\n")

    def _is_metadata_file(self, filename: str, content: dict[str, Any]) -> bool:
        """Check if file is metadata rather than a workflow"""
        # Check for HF Space metadata indicators
        if "sdk" in content or "emoji" in content or "colorFrom" in content:
            return True

        # Files that contain 'title' but no 'jobs' are likely metadata
        if "title" in content and "jobs" not in content and "on" not in content:
            return True

        return False

    def _validate_structure(self, filename: str, content: dict[str, Any]):
        """Validate workflow structure"""
        # Check required fields
        if "name" not in content:
            self.warnings.append(f"{filename}: Missing 'name' field")

        # Check for trigger (on: or True for YAML boolean)
        has_trigger = "on" in content or True in content
        if not has_trigger:
            self.errors.append(f"{filename}: Missing trigger ('on' field)")

        if "jobs" not in content:
            self.errors.append(f"{filename}: Missing 'jobs' definition")
            return

        # Validate jobs
        jobs = content.get("jobs", {})
        if not isinstance(jobs, dict):
            self.errors.append(f"{filename}: 'jobs' must be a dictionary")
            return

        if not jobs:
            self.errors.append(f"{filename}: No jobs defined")
            return

        # Validate each job
        for job_name, job_config in jobs.items():
            if not isinstance(job_config, dict):
                continue

            if "runs-on" not in job_config:
                self.errors.append(f"{filename}: Job '{job_name}' missing 'runs-on'")

            if "steps" not in job_config:
                self.errors.append(f"{filename}: Job '{job_name}' missing 'steps'")

    def _validate_security(
        self, filename: str, raw_content: str, content: dict[str, Any]
    ):
        """Validate security best practices"""
        # Check for hardcoded secrets
        secret_patterns = [
            (r"ghp_[a-zA-Z0-9]{36}", "GitHub personal access token"),
            (r"sk-[a-zA-Z0-9]{48}", "OpenAI API key"),
            (
                r"['\"]password['\"]:\s*['\"][^$\{]",
                "Hardcoded password",
            ),
            (r"['\"]token['\"]:\s*['\"][^$\{]", "Hardcoded token"),
        ]

        for pattern, secret_type in secret_patterns:
            if re.search(pattern, raw_content, re.IGNORECASE):
                self.errors.append(
                    f"{filename}: Potential {secret_type} found - use GitHub secrets"
                )

        # Check for pull_request_target
        triggers = content.get("on", {}) or content.get(True, {})
        if isinstance(triggers, dict) and "pull_request_target" in triggers:
            self.warnings.append(
                f"{filename}: Uses 'pull_request_target' - ensure proper safety checks"
            )

        # Check permissions
        if "permissions" not in content:
            jobs = content.get("jobs", {})
            has_job_permissions = any(
                "permissions" in job for job in jobs.values() if isinstance(job, dict)
            )
            if not has_job_permissions:
                self.info.append(
                    f"{filename}: No permissions defined (may use default)"
                )

    def _validate_best_practices(self, filename: str, content: dict[str, Any]):
        """Validate best practices"""
        # Check Python versions
        raw_str = str(content)
        python_versions = re.findall(
            r"python-version['\"]?:\s*['\"]?(\d+\.\d+)", raw_str
        )

        supported_versions = ["3.10", "3.11", "3.12"]
        for version in python_versions:
            if version not in supported_versions:
                self.warnings.append(
                    f"{filename}: Python {version} may not be supported"
                )

        # Check action versions
        jobs = content.get("jobs", {})
        for job_name, job_config in jobs.items():
            if not isinstance(job_config, dict):
                continue

            steps = job_config.get("steps", [])
            for step in steps:
                if not isinstance(step, dict):
                    continue

                uses = step.get("uses", "")
                if uses and not uses.startswith("./"):
                    # Check if action is pinned
                    if "@" not in uses:
                        self.warnings.append(
                            f"{filename}: Unpinned action in job '{job_name}': {uses}"
                        )

    def _print_results(self):
        """Print validation results"""
        print("\n" + "=" * 60)
        print("📊 Validation Results")
        print("=" * 60)

        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")

        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  • {warning}")

        if self.info:
            print(f"\nℹ️  Info ({len(self.info)}):")
            for info in self.info:
                print(f"  • {info}")

        if not self.errors and not self.warnings:
            print("\n✅ All validations passed!")

        print("\n" + "=" * 60)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Validate GitHub workflow files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--workflow",
        help="Specific workflow file to validate (e.g., ci.yml)",
    )
    parser.add_argument(
        "--security-only",
        action="store_true",
        help="Only run security checks",
    )

    args = parser.parse_args()

    # Find repository root
    repo_root = Path(__file__).parent.parent
    if not (repo_root / ".github" / "workflows").exists():
        print("❌ Error: .github/workflows directory not found")
        print(f"   Searched in: {repo_root}")
        return 1

    validator = WorkflowValidator(repo_root)
    success = validator.validate_all(workflow_name=args.workflow)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
