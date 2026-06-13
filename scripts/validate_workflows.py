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
        """
        Initialize the WorkflowValidator with the repository root and prepare validation state.

        Parameters:
                repo_root (Path): Path to the repository root; the validator will look for workflows under `<repo_root>/.github/workflows`.

        Attributes:
                repo_root (Path): The provided repository root.
                workflows_dir (Path): Path to the workflows directory (`repo_root/.github/workflows`).
                errors (list[str]): Collected error messages.
                warnings (list[str]): Collected warning messages.
                info (list[str]): Collected informational messages.
        """
        self.repo_root = repo_root
        self.workflows_dir = repo_root / ".github" / "workflows"
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.info: list[str] = []

    def validate_all(
        self, workflow_name: str | None = None, security_only: bool = False
    ) -> bool:
        """
        Validate workflows in the repository or a single specified workflow.

        Parameters:
            workflow_name (str | None): Name of a single workflow file to validate (relative to .github/workflows). If None, all workflow files (*.yml, *.yaml) under .github/workflows (including nested directories) are validated.
            security_only (bool): If True, run only security-related checks and skip structure and best-practice validations.

        Returns:
            bool: True if validation produced no errors, False otherwise.
        """
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
        """
        Select workflow files to validate from the repository workflows directory.

        If `workflow_name` is provided, returns a list containing that specific workflow file path; if the file does not exist, records an error and returns an empty list. If `workflow_name` is not provided, returns a sorted, deduplicated list of all files in the workflows directory matching `*.yml` or `*.yaml`, including files in nested subdirectories.

        Parameters:
            workflow_name (str | None): Optional filename of a single workflow to validate.

        Returns:
            list[Path]: A list of Path objects for the selected workflow files.
        """
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
        """
        Validate a single GitHub Actions workflow file and record any findings.

        Parses the workflow file at `workflow_path`, skips empty or metadata-only files, and runs configured checks: structure and best-practice checks unless `security_only` is True, and always runs security checks. Any errors, warnings, or info messages are appended to the validator's corresponding lists.

        Parameters:
                workflow_path (Path): Path to the workflow YAML file to validate.
                security_only (bool): If True, skip structure and best-practice checks and run only security checks.
        """
        relative = workflow_path.relative_to(self.repo_root)
        print(f"📄 Validating: {relative}")

        try:
            raw_content = workflow_path.read_text(encoding="utf-8")
        except OSError as exc:
            self.errors.append(f"{workflow_path.name}: Unable to read file - {exc}")
            return

        try:
            content = _yaml.safe_load(raw_content)
        except Exception as exc:
            self.errors.append(f"{workflow_path.name}: Invalid YAML syntax - {exc}")
            return

        if content is None:
            self.warnings.append(f"{workflow_path.name}: Empty workflow file")
            return

        if not isinstance(content, dict):
            self.errors.append(
                f"{workflow_path.name}: Top-level YAML must be a mapping/dictionary"
            )
            return

        if self._is_metadata_file(content):
            self.info.append(f"{workflow_path.name}: Metadata file skipped")
            return

        if not security_only:
            self._validate_structure(workflow_path.name, content)
            self._validate_best_practices(workflow_path.name, content)
        self._validate_security(workflow_path.name, raw_content, content)

    def _is_metadata_file(self, content: dict[str, Any]) -> bool:
        """
        Detect whether a parsed workflow YAML represents a metadata-only file.

        Parameters:
            content (dict[str, Any]): Parsed YAML mapping for a workflow file.

        Returns:
            True if the mapping appears to be metadata-only (contains any of "sdk", "emoji", or "colorFrom", or has a "title" without "jobs" or "on"), False otherwise.
        """
        return any(key in content for key in ("sdk", "emoji", "colorFrom")) or (
            "title" in content and "jobs" not in content and "on" not in content
        )

    def _validate_structure(self, filename: str, content: dict[str, Any]) -> None:
        """
        Validate basic GitHub Actions workflow structure and record any structural issues.

        Checks performed:
        - Warns if the top-level `name` field is missing.
        - Errors if the workflow trigger (`on`) is missing.
        - Errors if the top-level `jobs` section is missing (and returns immediately).
        - Errors if `jobs` exists but is not a non-empty mapping.

        Parameters:
            filename (str): The workflow file name used in reported messages.
            content (dict[str, Any]): Parsed YAML content of the workflow.

        Notes:
            Detected issues are appended to `self.errors` and `self.warnings`.
        """
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
        """
        Scan a workflow's raw and parsed YAML for security issues and record findings.

        Searches the raw file text for potential hardcoded secrets (passwords, tokens, GitHub tokens, OpenAI keys) and appends an error for each match. Warns if the workflow uses `pull_request_target`. If no top-level `permissions` and no job-level `permissions` are present, records an informational message that defaults may apply.

        Parameters:
            filename (str): Workflow file name used in recorded messages.
            raw_content (str): Raw YAML text of the workflow file.
            content (dict[str, Any]): Parsed YAML content (mapping) of the workflow.
        """
        secret_patterns = [
            (r"password\s*[:=]\s*['\"](?!.*\$\{)", "hardcoded password"),
            (r"token\s*[:=]\s*['\"](?!.*\$\{)", "hardcoded token"),
            (r"api[_-]?key\s*[:=]\s*['\"](?!.*\$\{)", "hardcoded api key"),
            (r"ghp_[A-Za-z0-9]{36}", "GitHub token"),
            (r"sk-[A-Za-z0-9]{48}", "OpenAI API key"),
        ]
        for pattern, secret_type in secret_patterns:
            if re.search(pattern, raw_content, flags=re.IGNORECASE):
                self.errors.append(
                    f"{filename}: Potential {secret_type} found; use GitHub secrets"
                )

        triggers = content.get("on", {}) or content.get(True, {})
        uses_pr_target = False
        if isinstance(triggers, dict):
            uses_pr_target = "pull_request_target" in triggers
        elif isinstance(triggers, list):
            uses_pr_target = "pull_request_target" in triggers
        elif isinstance(triggers, str):
            uses_pr_target = triggers == "pull_request_target"
        if uses_pr_target:
            self.errors.append(
                f"{filename}: Uses 'pull_request_target'; disallow or add explicit "
                "safety gates (untrusted code runs with write access to the repo)"
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
        """
        Add warnings for unpinned third-party actions used in job steps.

        Scans each job in the workflow content and, for every step that specifies a `uses`
        reference which is not a local action (does not start with "./") and does not
        include an `@` pin (version, tag, or digest), appends a warning indicating the
        job and the unpinned action reference.

        Parameters:
            filename (str): The workflow file name used in warning messages.
            content (dict[str, Any]): Parsed workflow YAML as a dictionary.
        """
        jobs = content.get("jobs", {})
        for job_name, job_config in jobs.items():
            if not isinstance(job_config, dict):
                continue
            for step in job_config.get("steps", []):
                if not isinstance(step, dict):
                    continue
                uses = step.get("uses", "")
                if not uses or uses.startswith("./") or uses.startswith("docker://"):
                    continue
                # A fully pinned action references an immutable 40-char commit
                # SHA (e.g. ``owner/repo@<sha>``). Tag/branch pins such as
                # ``owner/repo@v4`` are mutable and reported as unpinned.
                if not re.search(r"@[0-9a-fA-F]{40}$", uses):
                    self.warnings.append(
                        f"{filename}: Action not pinned to a full commit SHA in "
                        f"job '{job_name}': {uses}"
                    )

    def _print_results(self) -> None:
        """
        Print a consolidated report of collected validation errors, warnings, and informational messages to standard output.

        Prints sectioned output with a header and footer, shows counts for each category and lists each message as a bullet. If there are no errors or warnings, prints a success message.
        """
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
    """
    Parse command-line arguments and validate GitHub Actions workflow files in the repository.

    Supports --workflow to validate a single workflow file name and --security-only to restrict checks to security rules. Prints validation results and error messages to standard output.

    Returns:
        int: Exit code: 0 when validation completed with no recorded errors, 1 on validation failure or if the .github/workflows directory is missing.
    """
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
