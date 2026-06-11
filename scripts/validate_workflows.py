#!/usr/bin/env python3
"""Validate GitHub workflow files for syntax, security, and best practices."""

import argparse
import importlib
import importlib.util
import re
import sys
from pathlib import Path
from typing import Any

_yaml = None
if importlib.util.find_spec("yaml") is not None:
    _yaml = importlib.import_module("yaml")


class WorkflowValidator:
    """Validates GitHub workflow files."""

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.workflows_dir = repo_root / ".github" / "workflows"
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.info: list[str] = []

    def validate_all(
        self, workflow_name: str | None = None, security_only: bool = False
    ) -> bool:
        """Validate all workflows or a single workflow."""
        print("🔍 GitHub Workflow Validator")
        print("=" * 60)

        if _yaml is None:
            self.errors.append("PyYAML is required to validate workflow files")
            self._print_results()
            return False

        workflows = self._select_workflows(workflow_name)
        if not workflows:
            self.errors.append("No workflow files found")
            self._print_results()
            return False

        print(f"📻 Found {len(workflows)} workflow file(s) to validate\n")
        for workflow in workflows:
            self._validate_workflow(workflow, security_only=security_only)

        self._print_results()
        return len(self.errors) == 0

    def _select_workflows(self, workflow_name: str | None) -> list[Path]:
        if workflow_name:
            workflow_file = self.workflows_dir / workflow_name
            if not workflow_file.exists():
                self.errors.append(f"Workflow file not found: {workflow_name}")
                return []
            return [workflow_file]

        workflows: list[Path] = []
        for pattern in ("*.yml", "*.yaml"):
            workflows.extend(self.workflows_dir.glob(pattern))
            workflows.extend(self.workflows_dir.glob(f"**/{pattern}"))
        return sorted(set(workflows))

    def _validate_workflow(self, workflow_path: Path, security_only: bool) -> None:
        relative = workflow_path.relative_to(self.repo_root)
        print(f"📄 Validating: {relative}")

        raw_content = workflow_path.read_text(encoding="utf-8")
        content = _yaml.safe_load(raw_content)
        if content is None:
            self.warnings.append(f"{workflow_path.name}: Empty workflow file")
            return

        if self._is_metadata_file(content):
            self.info.append(f"{workflow_path.name}: Metadata file skipped")
            return

        if not security_only:
            self._validate_structure(workflow_path.name, content)
            self._validate_best_practices(workflow_path.name, content)
        self._validate_security(workflow_path.name, raw_content, content)

    def _is_metadata_file(self, content: dict[str, Any]) -> bool:
        return any(key in content for key in ("sdk", "emoji", "colorFrom")) or (
            "title" in content and "jobs" not in content and "on" not in content
        )

    def _validate_structure(self, filename: str, content: dict[str, Any]) -> None:
        if "name" not in content:
            self.warnings.append(f"{filename}: Missing 'name' field")

        has_trigger = "on" in content or True in content
        if not has_trigger:
            self.errors.append(f"{filename}: Missing workflow trigger ('on')")

        if "jobs" not in content:
            self.errors.append(f"{filename}: Missing 'jobs' section")
            return

        jobs = content.get("jobs", {})
        if not isinstance(jobs, dict) or not jobs:
            self.errors.append(f"{filename}: 'jobs' must be a non-empty mapping")

    def _validate_security(
        self, filename: str, raw_content: str, content: dict[str, Any]
    ) -> None:
        secret_patterns = [
            (r"['\"]password['\"]\s*:\s*['\"][^$\{]", "hardcoded password"),
            (r"['\"]token['\"]\s*:\s*['\"][^$\{]", "hardcoded token"),
            (r"ghp_[A-Za-z0-9]{36}", "GitHub token"),
            (r"sk-[A-Za-z0-9]{48}", "OpenAI API key"),
        ]
        for pattern, secret_type in secret_patterns:
            if re.search(pattern, raw_content, flags=re.IGNORECASE):
                self.errors.append(
                    f"{filename}: Potential {secret_type} found; use GitHub secrets"
                )

        triggers = content.get("on", {}) or content.get(True, {})
        if isinstance(triggers, dict) and "pull_request_target" in triggers:
            self.warnings.append(
                f"{filename}: Uses 'pull_request_target'; verify checkout and script safety"
            )

        if "permissions" not in content:
            jobs = content.get("jobs", {})
            has_job_permissions = any(
                isinstance(job, dict) and "permissions" in job for job in jobs.values()
            )
            if not has_job_permissions:
                self.info.append(
                    f"{filename}: No permissions defined; defaults may apply"
                )

    def _validate_best_practices(self, filename: str, content: dict[str, Any]) -> None:
        jobs = content.get("jobs", {})
        for job_name, job_config in jobs.items():
            if not isinstance(job_config, dict):
                continue
            for step in job_config.get("steps", []):
                if not isinstance(step, dict):
                    continue
                uses = step.get("uses", "")
                if uses and not uses.startswith("./") and "@" not in uses:
                    self.warnings.append(
                        f"{filename}: Unpinned action in job '{job_name}': {uses}"
                    )

    def _print_results(self) -> None:
        print("\n" + "=" * 60)
        print("🔎 Validation Results")
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


def main() -> int:
    """Main entry point."""
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
    repo_root = Path(__file__).parent.parent
    if not (repo_root / ".github" / "workflows").exists():
        print("❌ Error: .github/workflows directory not found")
        print(f"   Searched in: {repo_root}")
        return 1

    validator = WorkflowValidator(repo_root)
    success = validator.validate_all(
        workflow_name=args.workflow,
        security_only=args.security_only,
    )
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
