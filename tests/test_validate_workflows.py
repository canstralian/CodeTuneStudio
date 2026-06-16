"""
Tests for scripts/validate_workflows.py - WorkflowValidator class.

Covers:
- WorkflowValidator.__init__
- validate_all (specific workflow, all workflows, missing workflow)
- _get_workflow_files
- _is_metadata_file
- _validate_structure (name, trigger, jobs, runs-on, steps)
- _validate_security (hardcoded secrets, pull_request_target, permissions)
- _validate_best_practices (Python versions, action pinning)
- _redact
"""

import sys
import os
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.validate_workflows import WorkflowValidator


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_file(path: Path, content: str) -> Path:
    """Write content to a file, creating parent dirs as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content))
    return path


def _make_validator(tmp_path: Path) -> WorkflowValidator:
    """Create a WorkflowValidator rooted at a temp directory."""
    return WorkflowValidator(tmp_path)


VALID_WORKFLOW_YAML = """\
name: CI
on:
  push:
    branches: [main]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
"""

VALID_WORKFLOW_NO_NAME = """\
on:
  push:
    branches: [main]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
"""

MISSING_JOBS_YAML = """\
name: CI
on:
  push:
    branches: [main]
"""

MISSING_RUNS_ON_YAML = """\
name: CI
on:
  push:
    branches: [main]
jobs:
  build:
    steps:
      - run: echo hello
"""

MISSING_STEPS_YAML = """\
name: CI
on:
  push:
    branches: [main]
jobs:
  build:
    runs-on: ubuntu-latest
"""

EMPTY_JOBS_YAML = """\
name: CI
on:
  push:
    branches: [main]
jobs: {}
"""

METADATA_SDK_YAML = """\
sdk: gradio
emoji: 🚀
title: My App
"""

METADATA_TITLE_ONLY_YAML = """\
title: My Metadata File
description: Some content
"""

HARDCODED_TOKEN_YAML = """\
name: CI
on: push
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: echo hello
    env:
      TOKEN: "token_abc123"
"""

PULL_REQUEST_TARGET_YAML = """\
name: CI
on:
  pull_request_target:
    branches: [main]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
"""

WITH_PERMISSIONS_YAML = """\
name: CI
on: push
permissions:
  contents: read
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
"""

WITH_JOB_PERMISSIONS_YAML = """\
name: CI
on: push
jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@v3
"""

UNSUPPORTED_PYTHON_YAML = """\
name: CI
on: push
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/setup-python@v4
        with:
          python-version: '3.8'
"""

UNPINNED_ACTION_YAML = """\
name: CI
on: push
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout
"""

INVALID_YAML = "key: [unclosed bracket"


# ---------------------------------------------------------------------------
# Tests for _is_metadata_file
# ---------------------------------------------------------------------------

class TestIsMetadataFile(unittest.TestCase):
    def setUp(self):
        self.validator = WorkflowValidator(Path("/tmp/fake"))

    def test_sdk_key_indicates_metadata(self):
        content = {"sdk": "gradio", "emoji": "🚀"}
        self.assertTrue(self.validator._is_metadata_file("meta.yml", content))

    def test_emoji_key_indicates_metadata(self):
        content = {"emoji": "🔥", "title": "App"}
        self.assertTrue(self.validator._is_metadata_file("meta.yml", content))

    def test_colorFrom_key_indicates_metadata(self):
        content = {"colorFrom": "blue", "title": "App"}
        self.assertTrue(self.validator._is_metadata_file("meta.yml", content))

    def test_title_without_jobs_or_on_indicates_metadata(self):
        content = {"title": "My File", "description": "Content"}
        self.assertTrue(self.validator._is_metadata_file("meta.yml", content))

    def test_title_with_jobs_is_not_metadata(self):
        content = {"title": "CI", "jobs": {"build": {}}, "on": "push"}
        self.assertFalse(self.validator._is_metadata_file("ci.yml", content))

    def test_title_with_on_is_not_metadata(self):
        content = {"title": "CI", "on": "push"}
        self.assertFalse(self.validator._is_metadata_file("ci.yml", content))

    def test_standard_workflow_is_not_metadata(self):
        content = {"name": "CI", "on": "push", "jobs": {}}
        self.assertFalse(self.validator._is_metadata_file("ci.yml", content))

    def test_empty_dict_is_not_metadata(self):
        self.assertFalse(self.validator._is_metadata_file("ci.yml", {}))


# ---------------------------------------------------------------------------
# Tests for _validate_structure
# ---------------------------------------------------------------------------

class TestValidateStructure(unittest.TestCase):
    def setUp(self):
        self.validator = WorkflowValidator(Path("/tmp/fake"))

    def test_valid_structure_no_errors(self):
        import yaml
        content = yaml.safe_load(VALID_WORKFLOW_YAML)
        self.validator._validate_structure("ci.yml", content)
        self.assertEqual(self.validator.errors, [])
        self.assertEqual(self.validator.warnings, [])

    def test_missing_name_adds_warning(self):
        import yaml
        content = yaml.safe_load(VALID_WORKFLOW_NO_NAME)
        self.validator._validate_structure("ci.yml", content)
        self.assertTrue(
            any("Missing 'name'" in w for w in self.validator.warnings),
            f"Warnings: {self.validator.warnings}",
        )

    def test_missing_jobs_adds_error(self):
        import yaml
        content = yaml.safe_load(MISSING_JOBS_YAML)
        self.validator._validate_structure("ci.yml", content)
        self.assertTrue(
            any("Missing 'jobs'" in e for e in self.validator.errors),
            f"Errors: {self.validator.errors}",
        )

    def test_missing_runs_on_adds_error(self):
        import yaml
        content = yaml.safe_load(MISSING_RUNS_ON_YAML)
        self.validator._validate_structure("ci.yml", content)
        self.assertTrue(
            any("runs-on" in e for e in self.validator.errors),
            f"Errors: {self.validator.errors}",
        )

    def test_missing_steps_adds_error(self):
        import yaml
        content = yaml.safe_load(MISSING_STEPS_YAML)
        self.validator._validate_structure("ci.yml", content)
        self.assertTrue(
            any("steps" in e for e in self.validator.errors),
            f"Errors: {self.validator.errors}",
        )

    def test_empty_jobs_dict_adds_error(self):
        import yaml
        content = yaml.safe_load(EMPTY_JOBS_YAML)
        self.validator._validate_structure("ci.yml", content)
        self.assertTrue(
            any("No jobs defined" in e for e in self.validator.errors),
            f"Errors: {self.validator.errors}",
        )

    def test_jobs_not_dict_adds_error(self):
        content = {"name": "CI", "on": "push", "jobs": "not-a-dict"}
        self.validator._validate_structure("ci.yml", content)
        self.assertTrue(
            any("'jobs' must be a dictionary" in e for e in self.validator.errors),
            f"Errors: {self.validator.errors}",
        )

    def test_non_dict_job_config_skipped(self):
        """A non-dict job value should not cause an error, just be skipped."""
        content = {
            "name": "CI",
            "on": "push",
            "jobs": {"build": None},
        }
        self.validator._validate_structure("ci.yml", content)
        # No runs-on/steps error should be emitted for a non-dict job
        self.assertFalse(
            any("runs-on" in e for e in self.validator.errors),
            f"Errors: {self.validator.errors}",
        )

    def test_multiple_jobs_all_validated(self):
        content = {
            "name": "CI",
            "on": "push",
            "jobs": {
                "build": {"runs-on": "ubuntu-latest", "steps": []},
                "test": {},  # missing both
            },
        }
        self.validator._validate_structure("ci.yml", content)
        runs_on_errors = [e for e in self.validator.errors if "runs-on" in e]
        steps_errors = [e for e in self.validator.errors if "'steps'" in e or "steps" in e]
        self.assertTrue(len(runs_on_errors) >= 1)
        self.assertTrue(len(steps_errors) >= 1)


# ---------------------------------------------------------------------------
# Tests for _redact
# ---------------------------------------------------------------------------

class TestRedact(unittest.TestCase):
    def setUp(self):
        self.validator = WorkflowValidator(Path("/tmp/fake"))

    def test_redacts_github_pat(self):
        # 36 alphanumeric chars after "ghp_"
        text = "token: ghp_" + "a" * 36
        result = self.validator._redact(text)
        self.assertIn("[REDACTED]", result)
        self.assertNotIn("ghp_", result)

    def test_redacts_openai_key(self):
        # 48 alphanumeric chars after "sk-"
        text = "key: sk-" + "b" * 48
        result = self.validator._redact(text)
        self.assertIn("[REDACTED]", result)
        self.assertNotIn("sk-" + "b" * 48, result)

    def test_redacts_hardcoded_password(self):
        text = """env:\n  'password': 'mysecret'\n"""
        result = self.validator._redact(text)
        self.assertIn("[REDACTED]", result)

    def test_redacts_hardcoded_token(self):
        text = """config:\n  "token": "abc123"\n"""
        result = self.validator._redact(text)
        self.assertIn("[REDACTED]", result)

    def test_no_redaction_for_secret_reference(self):
        # Secret references like ${{ secrets.TOKEN }} should not be redacted
        text = "token: ${{ secrets.MY_TOKEN }}"
        result = self.validator._redact(text)
        self.assertEqual(text, result)

    def test_clean_text_unchanged(self):
        text = "name: CI\non: push\n"
        result = self.validator._redact(text)
        self.assertEqual(text, result)

    def test_case_insensitive_redaction(self):
        text = """env:\n  'PASSWORD': 'secret123'\n"""
        result = self.validator._redact(text)
        self.assertIn("[REDACTED]", result)


# ---------------------------------------------------------------------------
# Tests for _validate_security
# ---------------------------------------------------------------------------

class TestValidateSecurity(unittest.TestCase):
    def setUp(self):
        self.validator = WorkflowValidator(Path("/tmp/fake"))

    def test_hardcoded_github_pat_adds_error(self):
        raw = "token: ghp_" + "x" * 36
        content = {"name": "CI", "on": "push", "jobs": {}}
        self.validator._validate_security("ci.yml", raw, content)
        self.assertTrue(
            any("GitHub personal access token" in e for e in self.validator.errors),
            f"Errors: {self.validator.errors}",
        )

    def test_hardcoded_openai_key_adds_error(self):
        raw = "sk-" + "a" * 48
        content = {"name": "CI", "on": "push", "jobs": {}}
        self.validator._validate_security("ci.yml", raw, content)
        self.assertTrue(
            any("OpenAI API key" in e for e in self.validator.errors),
            f"Errors: {self.validator.errors}",
        )

    def test_pull_request_target_adds_warning(self):
        import yaml
        content = yaml.safe_load(PULL_REQUEST_TARGET_YAML)
        self.validator._validate_security("ci.yml", PULL_REQUEST_TARGET_YAML, content)
        self.assertTrue(
            any("pull_request_target" in w for w in self.validator.warnings),
            f"Warnings: {self.validator.warnings}",
        )

    def test_no_permissions_adds_info(self):
        import yaml
        content = yaml.safe_load(VALID_WORKFLOW_YAML)
        self.validator._validate_security("ci.yml", VALID_WORKFLOW_YAML, content)
        self.assertTrue(
            any("No permissions defined" in i for i in self.validator.info),
            f"Info: {self.validator.info}",
        )

    def test_top_level_permissions_no_info(self):
        import yaml
        content = yaml.safe_load(WITH_PERMISSIONS_YAML)
        self.validator._validate_security("ci.yml", WITH_PERMISSIONS_YAML, content)
        self.assertFalse(
            any("No permissions defined" in i for i in self.validator.info),
            f"Info: {self.validator.info}",
        )

    def test_job_level_permissions_no_info(self):
        import yaml
        content = yaml.safe_load(WITH_JOB_PERMISSIONS_YAML)
        self.validator._validate_security("ci.yml", WITH_JOB_PERMISSIONS_YAML, content)
        self.assertFalse(
            any("No permissions defined" in i for i in self.validator.info),
            f"Info: {self.validator.info}",
        )

    def test_clean_workflow_no_security_errors(self):
        import yaml
        content = yaml.safe_load(WITH_PERMISSIONS_YAML)
        self.validator._validate_security("ci.yml", WITH_PERMISSIONS_YAML, content)
        self.assertEqual(self.validator.errors, [])

    def test_hardcoded_token_value_adds_error(self):
        raw = """env:\n  "token": "abc123value"\n"""
        content = {"name": "CI", "on": "push", "jobs": {}}
        self.validator._validate_security("ci.yml", raw, content)
        self.assertTrue(
            any("Hardcoded token" in e for e in self.validator.errors),
            f"Errors: {self.validator.errors}",
        )


# ---------------------------------------------------------------------------
# Tests for _validate_best_practices
# ---------------------------------------------------------------------------

class TestValidateBestPractices(unittest.TestCase):
    def setUp(self):
        self.validator = WorkflowValidator(Path("/tmp/fake"))

    def test_unsupported_python_version_adds_warning(self):
        import yaml
        content = yaml.safe_load(UNSUPPORTED_PYTHON_YAML)
        self.validator._validate_best_practices("ci.yml", content)
        self.assertTrue(
            any("3.8" in w for w in self.validator.warnings),
            f"Warnings: {self.validator.warnings}",
        )

    def test_supported_python_version_no_warning(self):
        content = {
            "name": "CI",
            "on": "push",
            "jobs": {
                "build": {
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {
                            "uses": "actions/setup-python@v4",
                            "with": {"python-version": "3.11"},
                        }
                    ],
                }
            },
        }
        self.validator._validate_best_practices("ci.yml", content)
        self.assertFalse(
            any("may not be supported" in w for w in self.validator.warnings),
            f"Warnings: {self.validator.warnings}",
        )

    def test_unpinned_action_adds_warning(self):
        import yaml
        content = yaml.safe_load(UNPINNED_ACTION_YAML)
        self.validator._validate_best_practices("ci.yml", content)
        self.assertTrue(
            any("Unpinned action" in w for w in self.validator.warnings),
            f"Warnings: {self.validator.warnings}",
        )

    def test_pinned_action_no_warning(self):
        import yaml
        content = yaml.safe_load(VALID_WORKFLOW_YAML)
        self.validator._validate_best_practices("ci.yml", content)
        self.assertFalse(
            any("Unpinned action" in w for w in self.validator.warnings),
            f"Warnings: {self.validator.warnings}",
        )

    def test_local_action_not_flagged(self):
        content = {
            "name": "CI",
            "on": "push",
            "jobs": {
                "build": {
                    "runs-on": "ubuntu-latest",
                    "steps": [{"uses": "./.github/actions/my-action"}],
                }
            },
        }
        self.validator._validate_best_practices("ci.yml", content)
        self.assertFalse(
            any("Unpinned" in w for w in self.validator.warnings),
            f"Warnings: {self.validator.warnings}",
        )

    def test_no_steps_no_error(self):
        content = {
            "name": "CI",
            "on": "push",
            "jobs": {"build": {"runs-on": "ubuntu-latest", "steps": []}},
        }
        self.validator._validate_best_practices("ci.yml", content)
        self.assertEqual(self.validator.warnings, [])

    def test_non_dict_step_skipped(self):
        content = {
            "name": "CI",
            "on": "push",
            "jobs": {
                "build": {
                    "runs-on": "ubuntu-latest",
                    "steps": [None, "invalid"],
                }
            },
        }
        # Should not raise any exception
        self.validator._validate_best_practices("ci.yml", content)


# ---------------------------------------------------------------------------
# Tests for validate_all with temp filesystem
# ---------------------------------------------------------------------------

class TestValidateAll(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.tmp_path = Path(self.tmp)
        self.workflows_dir = self.tmp_path / ".github" / "workflows"
        self.workflows_dir.mkdir(parents=True)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _make_validator(self) -> WorkflowValidator:
        return WorkflowValidator(self.tmp_path)

    def test_validate_all_valid_workflow_returns_true(self):
        _write_file(self.workflows_dir / "ci.yml", VALID_WORKFLOW_YAML)
        validator = self._make_validator()
        result = validator.validate_all()
        # Valid workflow should have no errors
        self.assertEqual(validator.errors, [], f"Errors: {validator.errors}")

    def test_validate_all_invalid_yaml_returns_false(self):
        _write_file(self.workflows_dir / "bad.yml", INVALID_YAML)
        validator = self._make_validator()
        result = validator.validate_all()
        self.assertFalse(result)
        self.assertTrue(
            any("Invalid YAML" in e for e in validator.errors),
            f"Errors: {validator.errors}",
        )

    def test_validate_all_no_workflows_returns_false(self):
        validator = self._make_validator()
        result = validator.validate_all()
        self.assertFalse(result)
        self.assertTrue(
            any("No workflow files found" in e for e in validator.errors),
            f"Errors: {validator.errors}",
        )

    def test_validate_specific_workflow_by_name(self):
        _write_file(self.workflows_dir / "ci.yml", VALID_WORKFLOW_YAML)
        validator = self._make_validator()
        result = validator.validate_all(workflow_name="ci.yml")
        self.assertEqual(validator.errors, [], f"Errors: {validator.errors}")

    def test_validate_nonexistent_specific_workflow_returns_false(self):
        validator = self._make_validator()
        result = validator.validate_all(workflow_name="nonexistent.yml")
        self.assertFalse(result)
        self.assertTrue(
            any("not found" in e for e in validator.errors),
            f"Errors: {validator.errors}",
        )

    def test_validate_empty_workflow_file_adds_warning(self):
        _write_file(self.workflows_dir / "empty.yml", "")
        validator = self._make_validator()
        validator.validate_all()
        self.assertTrue(
            any("Empty workflow file" in w for w in validator.warnings),
            f"Warnings: {validator.warnings}",
        )

    def test_validate_metadata_file_skipped(self):
        _write_file(self.workflows_dir / "meta.yml", METADATA_SDK_YAML)
        validator = self._make_validator()
        # Should not add errors for missing jobs/trigger fields
        validator.validate_all()
        self.assertEqual(
            validator.errors,
            [],
            f"Errors for metadata file: {validator.errors}",
        )

    def test_validate_missing_jobs_returns_false(self):
        _write_file(self.workflows_dir / "ci.yml", MISSING_JOBS_YAML)
        validator = self._make_validator()
        result = validator.validate_all()
        self.assertFalse(result)

    def test_get_workflow_files_returns_yml_and_yaml(self):
        _write_file(self.workflows_dir / "a.yml", VALID_WORKFLOW_YAML)
        _write_file(self.workflows_dir / "b.yaml", VALID_WORKFLOW_YAML)
        validator = self._make_validator()
        files = validator._get_workflow_files()
        names = {f.name for f in files}
        self.assertIn("a.yml", names)
        self.assertIn("b.yaml", names)

    def test_validate_all_missing_runs_on_returns_false(self):
        _write_file(self.workflows_dir / "ci.yml", MISSING_RUNS_ON_YAML)
        validator = self._make_validator()
        result = validator.validate_all()
        self.assertFalse(result)

    def test_validate_all_missing_steps_returns_false(self):
        _write_file(self.workflows_dir / "ci.yml", MISSING_STEPS_YAML)
        validator = self._make_validator()
        result = validator.validate_all()
        self.assertFalse(result)

    def test_validate_all_workflow_with_no_name_warning_not_error(self):
        _write_file(self.workflows_dir / "ci.yml", VALID_WORKFLOW_NO_NAME)
        validator = self._make_validator()
        # Missing name is a warning, not an error; should still return True
        # if no other errors
        validator.validate_all()
        self.assertTrue(
            any("Missing 'name'" in w for w in validator.warnings),
            f"Warnings: {validator.warnings}",
        )


# ---------------------------------------------------------------------------
# Tests for _get_workflow_files
# ---------------------------------------------------------------------------

class TestGetWorkflowFiles(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.tmp_path = Path(self.tmp)
        self.workflows_dir = self.tmp_path / ".github" / "workflows"
        self.workflows_dir.mkdir(parents=True)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_returns_empty_list_when_no_files(self):
        validator = WorkflowValidator(self.tmp_path)
        files = validator._get_workflow_files()
        self.assertEqual(files, [])

    def test_returns_yml_files(self):
        (self.workflows_dir / "ci.yml").write_text("a: b")
        validator = WorkflowValidator(self.tmp_path)
        files = validator._get_workflow_files()
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0].name, "ci.yml")

    def test_returns_yaml_files(self):
        (self.workflows_dir / "ci.yaml").write_text("a: b")
        validator = WorkflowValidator(self.tmp_path)
        files = validator._get_workflow_files()
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0].name, "ci.yaml")

    def test_no_duplicates(self):
        (self.workflows_dir / "ci.yml").write_text("a: b")
        validator = WorkflowValidator(self.tmp_path)
        files = validator._get_workflow_files()
        self.assertEqual(len(files), len(set(files)))

    def test_sorted_results(self):
        (self.workflows_dir / "z.yml").write_text("a: b")
        (self.workflows_dir / "a.yml").write_text("a: b")
        validator = WorkflowValidator(self.tmp_path)
        files = validator._get_workflow_files()
        names = [f.name for f in files]
        self.assertEqual(names, sorted(names))


# ---------------------------------------------------------------------------
# Tests for validate_all with hardcoded secrets in workflow content
# ---------------------------------------------------------------------------

class TestValidateSecurityIntegration(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.tmp_path = Path(self.tmp)
        self.workflows_dir = self.tmp_path / ".github" / "workflows"
        self.workflows_dir.mkdir(parents=True)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_github_pat_in_workflow_fails_validation(self):
        pat = "ghp_" + "a" * 36
        yaml_content = (
            f"name: CI\non: push\njobs:\n  build:\n"
            f"    runs-on: ubuntu-latest\n    steps:\n"
            f"      - run: echo {pat}\n"
        )
        _write_file(self.workflows_dir / "ci.yml", yaml_content)
        validator = WorkflowValidator(self.tmp_path)
        result = validator.validate_all()
        self.assertFalse(result)
        self.assertTrue(
            any("GitHub personal access token" in e for e in validator.errors),
            f"Errors: {validator.errors}",
        )

    def test_pull_request_target_warning_via_validate_all(self):
        _write_file(self.workflows_dir / "ci.yml", PULL_REQUEST_TARGET_YAML)
        validator = WorkflowValidator(self.tmp_path)
        validator.validate_all()
        self.assertTrue(
            any("pull_request_target" in w for w in validator.warnings),
            f"Warnings: {validator.warnings}",
        )


if __name__ == "__main__":
    unittest.main()
