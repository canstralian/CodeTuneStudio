"""
Tests for scripts/validate_workflows.py — WorkflowValidator class.

These tests exercise the logic introduced in this PR: YAML parsing,
metadata-file detection, structure validation, security scanning,
best-practice checks, and the _redact helper.
"""

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

# Ensure the project root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.validate_workflows import WorkflowValidator


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_validator(tmp_path: Path) -> WorkflowValidator:
    """Return a WorkflowValidator whose workflows_dir is *tmp_path*."""
    # WorkflowValidator expects repo_root / ".github" / "workflows" to exist
    workflows_dir = tmp_path / ".github" / "workflows"
    workflows_dir.mkdir(parents=True, exist_ok=True)
    return WorkflowValidator(tmp_path)


def _write_workflow(workflows_dir: Path, name: str, content: str) -> Path:
    path = workflows_dir / name
    path.write_text(content)
    return path


# ---------------------------------------------------------------------------
# TestWorkflowValidatorInit
# ---------------------------------------------------------------------------


class TestWorkflowValidatorInit(unittest.TestCase):
    """Test WorkflowValidator initialisation."""

    def test_initial_lists_are_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            v = _make_validator(Path(tmp))
            self.assertEqual(v.errors, [])
            self.assertEqual(v.warnings, [])
            self.assertEqual(v.info, [])

    def test_workflows_dir_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            v = _make_validator(root)
            self.assertEqual(v.workflows_dir, root / ".github" / "workflows")


# ---------------------------------------------------------------------------
# TestRedact
# ---------------------------------------------------------------------------


class TestRedact(unittest.TestCase):
    """Test WorkflowValidator._redact strips secret patterns."""

    def _v(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        return _make_validator(Path(td.name))

    def test_redacts_github_token(self):
        v = self._v()
        token = "ghp_" + "a" * 36
        result = v._redact(f"some text {token} end")
        self.assertNotIn(token, result)
        self.assertIn("[REDACTED]", result)

    def test_redacts_openai_key(self):
        v = self._v()
        key = "sk-" + "b" * 48
        result = v._redact(f"key={key}")
        self.assertNotIn(key, result)
        self.assertIn("[REDACTED]", result)

    def test_plain_text_unchanged(self):
        v = self._v()
        text = "nothing sensitive here"
        self.assertEqual(v._redact(text), text)

    def test_multiple_patterns_all_redacted(self):
        v = self._v()
        token = "ghp_" + "c" * 36
        key = "sk-" + "d" * 48
        result = v._redact(f"{token} and {key}")
        self.assertNotIn(token, result)
        self.assertNotIn(key, result)


# ---------------------------------------------------------------------------
# TestIsMetadataFile
# ---------------------------------------------------------------------------


class TestIsMetadataFile(unittest.TestCase):

    def _v(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        return _make_validator(Path(td.name))

    def test_sdk_key_is_metadata(self):
        v = self._v()
        self.assertTrue(v._is_metadata_file("space.yml", {"sdk": "gradio"}))

    def test_emoji_key_is_metadata(self):
        v = self._v()
        self.assertTrue(v._is_metadata_file("space.yml", {"emoji": "🚀"}))

    def test_colorFrom_key_is_metadata(self):
        v = self._v()
        self.assertTrue(v._is_metadata_file("space.yml", {"colorFrom": "blue"}))

    def test_title_without_jobs_and_on_is_metadata(self):
        v = self._v()
        content = {"title": "My Space", "description": "cool"}
        self.assertTrue(v._is_metadata_file("meta.yml", content))

    def test_title_with_jobs_is_not_metadata(self):
        v = self._v()
        content = {"title": "CI", "jobs": {"build": {}}, "on": "push"}
        self.assertFalse(v._is_metadata_file("ci.yml", content))

    def test_normal_workflow_is_not_metadata(self):
        v = self._v()
        content = {"name": "CI", "on": "push", "jobs": {"build": {}}}
        self.assertFalse(v._is_metadata_file("ci.yml", content))

    def test_empty_dict_is_not_metadata(self):
        v = self._v()
        self.assertFalse(v._is_metadata_file("empty.yml", {}))


# ---------------------------------------------------------------------------
# TestValidateStructure
# ---------------------------------------------------------------------------


class TestValidateStructure(unittest.TestCase):

    def _v(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        return _make_validator(Path(td.name))

    def _minimal_valid(self):
        return {
            "name": "CI",
            "on": "push",
            "jobs": {
                "build": {
                    "runs-on": "ubuntu-latest",
                    "steps": [{"run": "echo hi"}],
                }
            },
        }

    def test_valid_structure_no_errors(self):
        v = self._v()
        v._validate_structure("ci.yml", self._minimal_valid())
        self.assertEqual(v.errors, [])
        self.assertEqual(v.warnings, [])

    def test_missing_name_adds_warning(self):
        v = self._v()
        content = self._minimal_valid()
        del content["name"]
        v._validate_structure("ci.yml", content)
        self.assertTrue(any("name" in w for w in v.warnings))

    def test_missing_jobs_adds_error(self):
        v = self._v()
        content = {"name": "CI", "on": "push"}
        v._validate_structure("ci.yml", content)
        self.assertTrue(any("jobs" in e for e in v.errors))

    def test_jobs_not_dict_adds_error(self):
        v = self._v()
        content = {"name": "CI", "on": "push", "jobs": "invalid"}
        v._validate_structure("ci.yml", content)
        self.assertTrue(any("dictionary" in e for e in v.errors))

    def test_empty_jobs_adds_error(self):
        v = self._v()
        content = {"name": "CI", "on": "push", "jobs": {}}
        v._validate_structure("ci.yml", content)
        self.assertTrue(any("No jobs" in e for e in v.errors))

    def test_job_missing_runs_on_adds_error(self):
        v = self._v()
        content = {
            "name": "CI",
            "on": "push",
            "jobs": {"build": {"steps": [{"run": "echo"}]}},
        }
        v._validate_structure("ci.yml", content)
        self.assertTrue(any("runs-on" in e for e in v.errors))

    def test_job_missing_steps_adds_error(self):
        v = self._v()
        content = {
            "name": "CI",
            "on": "push",
            "jobs": {"build": {"runs-on": "ubuntu-latest"}},
        }
        v._validate_structure("ci.yml", content)
        self.assertTrue(any("steps" in e for e in v.errors))

    def test_non_dict_job_config_is_skipped(self):
        """A job whose config is not a dict should not cause errors."""
        v = self._v()
        content = {
            "name": "CI",
            "on": "push",
            "jobs": {"build": None},
        }
        v._validate_structure("ci.yml", content)
        # No errors about runs-on/steps for null job config
        self.assertFalse(any("runs-on" in e for e in v.errors))


# ---------------------------------------------------------------------------
# TestValidateSecurity
# ---------------------------------------------------------------------------


class TestValidateSecurity(unittest.TestCase):

    def _v(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        return _make_validator(Path(td.name))

    def test_github_token_in_raw_content_adds_error(self):
        v = self._v()
        raw = "token: ghp_" + "x" * 36
        v._validate_security("ci.yml", raw, {})
        self.assertTrue(any("GitHub personal access token" in e for e in v.errors))

    def test_openai_key_in_raw_content_adds_error(self):
        v = self._v()
        raw = "key: sk-" + "y" * 48
        v._validate_security("ci.yml", raw, {})
        self.assertTrue(any("OpenAI API key" in e for e in v.errors))

    def test_hardcoded_password_adds_error(self):
        v = self._v()
        raw = '"password": "mysecret"'
        v._validate_security("ci.yml", raw, {})
        self.assertTrue(any("password" in e.lower() for e in v.errors))

    def test_no_secrets_no_errors(self):
        v = self._v()
        raw = "echo hello"
        content = {
            "on": "push",
            "jobs": {"build": {"permissions": {"contents": "read"}}},
        }
        v._validate_security("ci.yml", raw, content)
        self.assertEqual(v.errors, [])

    def test_pull_request_target_adds_warning(self):
        v = self._v()
        content = {"on": {"pull_request_target": {}}}
        v._validate_security("ci.yml", "echo hi", content)
        self.assertTrue(any("pull_request_target" in w for w in v.warnings))

    def test_no_permissions_adds_info(self):
        v = self._v()
        content = {
            "on": "push",
            "jobs": {"build": {"runs-on": "ubuntu-latest", "steps": []}},
        }
        v._validate_security("ci.yml", "echo hi", content)
        self.assertTrue(any("permissions" in i for i in v.info))

    def test_job_level_permissions_suppresses_info(self):
        v = self._v()
        content = {
            "on": "push",
            "jobs": {
                "build": {
                    "permissions": {"contents": "read"},
                    "runs-on": "ubuntu-latest",
                    "steps": [],
                }
            },
        }
        v._validate_security("ci.yml", "echo hi", content)
        self.assertFalse(any("No permissions" in i for i in v.info))


# ---------------------------------------------------------------------------
# TestValidateBestPractices
# ---------------------------------------------------------------------------


class TestValidateBestPractices(unittest.TestCase):

    def _v(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        return _make_validator(Path(td.name))

    def _content_with_python_version(self, version: str):
        return {
            "name": "CI",
            "on": "push",
            "jobs": {
                "build": {
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {
                            "uses": "actions/setup-python@v4",
                            "with": {f"python-version": version},
                        }
                    ],
                }
            },
        }

    def test_supported_python_version_no_warning(self):
        v = self._v()
        content = self._content_with_python_version("3.11")
        v._validate_best_practices("ci.yml", content)
        self.assertFalse(any("3.11" in w for w in v.warnings))

    def test_unsupported_python_version_adds_warning(self):
        v = self._v()
        content = self._content_with_python_version("3.8")
        v._validate_best_practices("ci.yml", content)
        self.assertTrue(any("3.8" in w for w in v.warnings))

    def test_unpinned_action_adds_warning(self):
        v = self._v()
        content = {
            "on": "push",
            "jobs": {
                "build": {
                    "runs-on": "ubuntu-latest",
                    "steps": [{"uses": "actions/checkout"}],  # no @ pin
                }
            },
        }
        v._validate_best_practices("ci.yml", content)
        self.assertTrue(any("Unpinned" in w for w in v.warnings))

    def test_pinned_action_no_warning(self):
        v = self._v()
        content = {
            "on": "push",
            "jobs": {
                "build": {
                    "runs-on": "ubuntu-latest",
                    "steps": [{"uses": "actions/checkout@v4"}],
                }
            },
        }
        v._validate_best_practices("ci.yml", content)
        self.assertFalse(any("Unpinned" in w for w in v.warnings))

    def test_local_action_not_flagged_as_unpinned(self):
        v = self._v()
        content = {
            "on": "push",
            "jobs": {
                "build": {
                    "runs-on": "ubuntu-latest",
                    "steps": [{"uses": "./local-action"}],
                }
            },
        }
        v._validate_best_practices("ci.yml", content)
        self.assertFalse(any("Unpinned" in w for w in v.warnings))


# ---------------------------------------------------------------------------
# TestValidateAll
# ---------------------------------------------------------------------------


class TestValidateAll(unittest.TestCase):
    """Integration-level tests for validate_all."""

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmpdir.name)
        self.validator = _make_validator(self.tmp)
        self.workflows_dir = self.tmp / ".github" / "workflows"

    def tearDown(self):
        self._tmpdir.cleanup()

    def test_no_workflow_files_returns_false(self):
        result = self.validator.validate_all()
        self.assertFalse(result)
        self.assertTrue(any("No workflow" in e for e in self.validator.errors))

    def test_nonexistent_specific_workflow_returns_false(self):
        result = self.validator.validate_all(workflow_name="missing.yml")
        self.assertFalse(result)
        self.assertTrue(any("not found" in e for e in self.validator.errors))

    def test_valid_workflow_returns_true(self):
        content = (
            "name: CI\n"
            "on: push\n"
            "permissions:\n"
            "  contents: read\n"
            "jobs:\n"
            "  build:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n"
        )
        _write_workflow(self.workflows_dir, "ci.yml", content)
        result = self.validator.validate_all()
        self.assertTrue(result)

    def test_invalid_yaml_workflow_returns_false(self):
        _write_workflow(self.workflows_dir, "bad.yml", ":\ninvalid: yaml: [unclosed")
        result = self.validator.validate_all()
        self.assertFalse(result)
        self.assertTrue(any("Invalid YAML" in e for e in self.validator.errors))

    def test_empty_workflow_adds_warning(self):
        _write_workflow(self.workflows_dir, "empty.yml", "")
        self.validator.validate_all()
        self.assertTrue(any("Empty" in w for w in self.validator.warnings))

    def test_metadata_file_is_skipped(self):
        content = "sdk: gradio\ntitle: My Space\n"
        _write_workflow(self.workflows_dir, "meta.yml", content)
        # Should not add errors for missing jobs/trigger
        self.validator.validate_all()
        self.assertFalse(any("jobs" in e for e in self.validator.errors))

    def test_validate_specific_workflow_by_name(self):
        content = (
            "name: CI\n"
            "on: push\n"
            "permissions:\n"
            "  contents: read\n"
            "jobs:\n"
            "  build:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n"
        )
        _write_workflow(self.workflows_dir, "ci.yml", content)
        result = self.validator.validate_all(workflow_name="ci.yml")
        self.assertTrue(result)

    def test_workflow_missing_jobs_returns_false(self):
        content = "name: CI\non: push\n"
        _write_workflow(self.workflows_dir, "no_jobs.yml", content)
        result = self.validator.validate_all()
        self.assertFalse(result)


# ---------------------------------------------------------------------------
# TestGetWorkflowFiles
# ---------------------------------------------------------------------------


class TestGetWorkflowFiles(unittest.TestCase):

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmpdir.name)
        self.validator = _make_validator(self.tmp)
        self.workflows_dir = self.tmp / ".github" / "workflows"

    def tearDown(self):
        self._tmpdir.cleanup()

    def test_finds_yml_files(self):
        _write_workflow(self.workflows_dir, "ci.yml", "name: CI")
        files = self.validator._get_workflow_files()
        names = [f.name for f in files]
        self.assertIn("ci.yml", names)

    def test_finds_yaml_files(self):
        _write_workflow(self.workflows_dir, "deploy.yaml", "name: Deploy")
        files = self.validator._get_workflow_files()
        names = [f.name for f in files]
        self.assertIn("deploy.yaml", names)

    def test_returns_sorted_unique_list(self):
        _write_workflow(self.workflows_dir, "a.yml", "name: A")
        _write_workflow(self.workflows_dir, "b.yml", "name: B")
        files = self.validator._get_workflow_files()
        names = [f.name for f in files]
        self.assertEqual(names, sorted(set(names)))


if __name__ == "__main__":
    unittest.main()
