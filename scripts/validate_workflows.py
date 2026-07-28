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
        Initialize the validator with the repository root path.

        Parameters:
            repo_root (Path): The repository root; workflows are expected at `<repo_root>/.github/workflows`.
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
        Validate GitHub Actions workflow files in the repository.

        Validates all workflow files found under .github/workflows (including nested directories) or a single specified workflow. Unless security_only is True, runs structure and best-practice checks in addition to security validation.

        Parameters:
            workflow_name (str | None): Name of a specific workflow file to validate relative to .github/workflows. If None, all *.yml and *.yaml files are validated.
            security_only (bool): If True, only security-related checks are performed. Defaults to False.

        Returns:
            bool: `true` if no errors were found, `false` otherwise.
        """
        # Reset accumulated findings so repeated calls on the same instance
        # do not report stale errors/warnings from a previous run.
        self.errors = []
        self.warnings = []
        self.info = []

        print("🔍 GitHub Workflow Validator")
        print("=" * 60)

        if _yaml is None:
            self.errors.append("PyYAML is required to validate workflow files")
            self._print_results()
            return False

        workflows = self._select_workflows(workflow_name)
        if not workflows:
            # _select_workflows may already have recorded a specific error
            # (e.g. a named file was not found); avoid a duplicate generic one.
            if not self.errors:
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
        Select workflow files to validate based on the given filter.

        If a workflow name is provided, returns that file path if it exists; records an error and returns an empty list otherwise. If no name is provided, returns all .yml and .yaml files in the workflows directory and subdirectories, deduplicated and sorted.

        Parameters:
            workflow_name (str | None): Optional filename of a specific workflow.

        Returns:
            list[Path]: Paths of selected workflow files.
        """
        if workflow_name:
            candidate = Path(workflow_name)
            if candidate.is_absolute() or ".." in candidate.parts:
                self.errors.append(f"Invalid workflow path: {workflow_name}")
                return []
            if candidate.suffix not in (".yml", ".yaml"):
                self.errors.append(
                    f"Workflow file must be a .yml/.yaml file: {workflow_name}"
                )
                return []
            workflow_file = self.workflows_dir / workflow_name
            try:
                resolved = workflow_file.resolve()
                resolved.relative_to(self.workflows_dir.resolve())
            except (OSError, ValueError):
                self.errors.append(
                    f"Workflow path escapes workflows directory: {workflow_name}"
                )
                return []
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
        Validate a single workflow file.

        Reads and parses the workflow YAML. Skips empty and metadata-only files. Runs structure and best-practice checks unless `security_only` is True; security checks always run. Records findings as errors, warnings, or informational messages.

        Parameters:
                security_only (bool): If True, skip structure and best-practice checks.
        """
        try:
            relative = workflow_path.relative_to(self.repo_root)
        except ValueError:
            self.errors.append(
                f"{workflow_path.name}: Workflow path is outside the repository"
            )
            return
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
        Determine if a parsed workflow YAML is metadata-only.

        Returns:
            `true` if the mapping contains SDK/theme metadata ("sdk", "emoji", "colorFrom") or has "title" without "jobs" and "on", `false` otherwise.
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

        Searches the raw file text for potential hardcoded secrets (passwords, tokens, GitHub tokens, OpenAI keys) and appends an error for each match. Records an error if the workflow uses `pull_request_target`. If no top-level `permissions` and no job-level `permissions` are present, records an informational message that defaults may apply.

        Parameters:
            filename (str): Workflow file name used in recorded messages.
            raw_content (str): Raw YAML text of the workflow file.
            content (dict[str, Any]): Parsed YAML content (mapping) of the workflow.
        """
        secret_patterns = [
            # Quote is optional so unquoted YAML (``token: abc123``) is caught,
            # while templated ``${{ ... }}`` values and GitHub permission scopes
            # (``id-token: write``) are excluded.
            (
                r"password\s*[:=]\s*['\"]?(?!\$\{)(?!(?:read|write|none)\b)[^\s'\"]",
                "hardcoded password",
            ),
            (
                r"token\s*[:=]\s*['\"]?(?!\$\{)(?!(?:read|write|none)\b)[^\s'\"]",
                "hardcoded token",
            ),
            (
                r"api[_-]?key\s*[:=]\s*['\"]?(?!\$\{)(?!(?:read|write|none)\b)[^\s'\"]",
                "hardcoded api key",
            ),
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
        if isinstance(triggers, (dict, list)):
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
            if not isinstance(jobs, dict):
                jobs = {}
            has_job_permissions = any(
                isinstance(job, dict) and "permissions" in job for job in jobs.values()
            )
            if not has_job_permissions:
                self.info.append(
                    f"{filename}: No permissions defined; defaults may apply"
                )

    def _validate_best_practices(self, filename: str, content: dict[str, Any]) -> None:
        """
        Record warnings for third-party actions not pinned to a full commit SHA.

        Iterates through each job and its steps. For third-party actions (not
        local, not docker images), warns if the action is not pinned to exactly
        a 40-character commit SHA. Actions pinned to tags or branches are flagged
        as unpinned.

        Parameters:
            filename (str): The workflow file name used in warning messages.
            content (dict[str, Any]): Parsed workflow YAML as a dictionary.
        """
        jobs = content.get("jobs", {})
        if not isinstance(jobs, dict):
            return
        for job_name, job_config in jobs.items():
            if not isinstance(job_config, dict):
                continue
            for step in job_config.get("steps", []):
                if not isinstance(step, dict):
                    continue
                uses = step.get("uses", "")
                if not uses or uses.startswith(("./", "docker://")):
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
        Print a formatted validation report of errors, warnings, and informational messages to stdout.

        Displays each error, warning, and info message with their respective counts. Shows a success message if both errors and warnings are empty.
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
    Validate GitHub Actions workflow files in the repository.

    Returns:
        int: Exit code 0 if validation completed with no errors, 1 if validation failed or the .github/workflows directory is missing.
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
