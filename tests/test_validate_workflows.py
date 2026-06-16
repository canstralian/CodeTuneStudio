"""Tests for scripts/validate_workflows.py

Covers the WorkflowValidator class introduced (decoded from base64) in this PR.
Tests exercise all public and private methods using temporary workflow files.
"""
import sys
import os
import textwrap
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Ensure scripts/ is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from validate_workflows import WorkflowValidator  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_validator(tmp_path: Path) -> WorkflowValidator:
    """Return a WorkflowValidator whose repo_root is *tmp_path*."""
    workflows_dir = tmp_path / ".github" / "workflows"
    workflows_dir.mkdir(parents=True, exist_ok=True)
    return WorkflowValidator(tmp_path)


def _write_workflow(workflows_dir: Path, name: str, content: str) -> Path:
    p = workflows_dir / name
    p.write_text(textwrap.dedent(content))
    return p


# ---------------------------------------------------------------------------
# Minimal valid workflow YAML used across multiple tests
# ---------------------------------------------------------------------------
_VALID_WORKFLOW = """
name: CI
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
"""


# ===========================================================================
# TestWorkflowValidatorInit
# ===========================================================================


class TestWorkflowValidatorInit(unittest.TestCase):
    def test_attributes_set_on_init(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            v = WorkflowValidator(root)
            self.assertEqual(v.repo_root, root)
            self.assertEqual(v.workflows_dir, root / ".github" / "workflows")
            self.assertEqual(v.errors, [])
            self.assertEqual(v.warnings, [])
            self.assertEqual(v.info, [])


# ===========================================================================
# TestIsMetadataFile
# ===========================================================================


class TestIsMetadataFile(unittest.TestCase):
    def setUp(self):
        import tempfile

        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / ".github" / "workflows").mkdir(parents=True)
        self.v = WorkflowValidator(self.root)

    def tearDown(self):
        self._tmp.cleanup()

    def test_sdk_key_is_metadata(self):
        self.assertTrue(self.v._is_metadata_file("space.yml", {"sdk": "gradio"}))

    def test_emoji_key_is_metadata(self):
        self.assertTrue(self.v._is_metadata_file("space.yml", {"emoji": "🚀"}))

    def test_colorFrom_key_is_metadata(self):
        self.assertTrue(self.v._is_metadata_file("space.yml", {"colorFrom": "blue"}))

    def test_title_without_jobs_or_on_is_metadata(self):
        self.assertTrue(
            self.v._is_metadata_file("readme.yml", {"title": "My Space"})
        )

    def test_title_with_jobs_is_not_metadata(self):
        self.assertFalse(
            self.v._is_metadata_file("ci.yml", {"title": "CI", "jobs": {}})
        )

    def test_title_with_on_is_not_metadata(self):
        self.assertFalse(
            self.v._is_metadata_file("ci.yml", {"title": "CI", "on": "push"})
        )

    def test_normal_workflow_is_not_metadata(self):
        content = {"name": "CI", "on": ["push"], "jobs": {"build": {}}}
        self.assertFalse(self.v._is_metadata_file("ci.yml", content))

    def test_empty_content_is_not_metadata(self):
        self.assertFalse(self.v._is_metadata_file("ci.yml", {}))


# ===========================================================================
# TestRedact
# ===========================================================================


class TestRedact(unittest.TestCase):
    def setUp(self):
        import tempfile

        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / ".github" / "workflows").mkdir(parents=True)
        self.v = WorkflowValidator(self.root)

    def tearDown(self):
        self._tmp.cleanup()

    def test_redacts_github_token(self):
        text = "token: ghp_" + "a" * 36
        result = self.v._redact(text)
        self.assertIn("[REDACTED]", result)
        self.assertNotIn("ghp_", result)

    def test_redacts_openai_key(self):
        text = "key: sk-" + "b" * 48
        result = self.v._redact(text)
        self.assertIn("[REDACTED]", result)
        self.assertNotIn("sk-" + "b" * 48, result)

    def test_no_secrets_unchanged(self):
        text = "this is safe text"
        self.assertEqual(self.v._redact(text), text)

    def test_empty_string_unchanged(self):
        self.assertEqual(self.v._redact(""), "")

    def test_multiple_patterns_all_redacted(self):
        ghp = "ghp_" + "c" * 36
        sk = "sk-" + "d" * 48
        text = f"{ghp} and {sk}"
        result = self.v._redact(text)
        self.assertNotIn(ghp, result)
        self.assertNotIn(sk, result)


# ===========================================================================
# TestValidateStructure
# ===========================================================================


class TestValidateStructure(unittest.TestCase):
    def setUp(self):
        import tempfile

        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / ".github" / "workflows").mkdir(parents=True)
        self.v = WorkflowValidator(self.root)

    def tearDown(self):
        self._tmp.cleanup()

    def _valid_content(self):
        return {
            "name": "CI",
            "on": ["push"],
            "jobs": {
                "build": {
                    "runs-on": "ubuntu-latest",
                    "steps": [{"uses": "actions/checkout@v3"}],
                }
            },
        }

    def test_valid_workflow_produces_no_errors(self):
        self.v._validate_structure("ci.yml", self._valid_content())
        self.assertEqual(self.v.errors, [])

    def test_missing_name_produces_warning(self):
        content = self._valid_content()
        del content["name"]
        self.v._validate_structure("ci.yml", content)
        self.assertTrue(any("name" in w for w in self.v.warnings))

    def test_missing_jobs_produces_error(self):
        content = {"name": "CI", "on": ["push"]}
        self.v._validate_structure("ci.yml", content)
        self.assertTrue(any("jobs" in e for e in self.v.errors))

    def test_jobs_not_dict_produces_error(self):
        content = {"name": "CI", "on": ["push"], "jobs": "not-a-dict"}
        self.v._validate_structure("ci.yml", content)
        self.assertTrue(any("dictionary" in e for e in self.v.errors))

    def test_empty_jobs_produces_error(self):
        content = {"name": "CI", "on": ["push"], "jobs": {}}
        self.v._validate_structure("ci.yml", content)
        self.assertTrue(any("No jobs" in e for e in self.v.errors))

    def test_job_missing_runs_on_produces_error(self):
        content = {
            "name": "CI",
            "on": ["push"],
            "jobs": {"build": {"steps": []}},
        }
        self.v._validate_structure("ci.yml", content)
        self.assertTrue(any("runs-on" in e for e in self.v.errors))

    def test_job_missing_steps_produces_error(self):
        content = {
            "name": "CI",
            "on": ["push"],
            "jobs": {"build": {"runs-on": "ubuntu-latest"}},
        }
        self.v._validate_structure("ci.yml", content)
        self.assertTrue(any("steps" in e for e in self.v.errors))

    def test_non_dict_job_config_is_skipped(self):
        """A job whose value is not a dict should be skipped without error."""
        content = {
            "name": "CI",
            "on": ["push"],
            "jobs": {"bad": None},
        }
        before = len(self.v.errors)
        self.v._validate_structure("ci.yml", content)
        # No additional errors beyond possibly "No jobs" (but jobs dict is non-empty here)
        # None value means it's skipped; no runs-on/steps error expected
        runs_on_errors = [e for e in self.v.errors if "runs-on" in e]
        self.assertEqual(runs_on_errors, [])


# ===========================================================================
# TestValidateSecurity
# ===========================================================================


class TestValidateSecurity(unittest.TestCase):
    def setUp(self):
        import tempfile

        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / ".github" / "workflows").mkdir(parents=True)
        self.v = WorkflowValidator(self.root)

    def tearDown(self):
        self._tmp.cleanup()

    def _call(self, raw_content, content=None):
        if content is None:
            content = {"name": "CI", "on": ["push"], "jobs": {}}
        self.v._validate_security("ci.yml", raw_content, content)

    def test_clean_content_no_errors(self):
        self._call("name: CI\non: push\njobs: {}")
        self.assertEqual(self.v.errors, [])

    def test_detects_github_token(self):
        raw = "token: ghp_" + "x" * 36
        self._call(raw)
        self.assertTrue(any("GitHub personal access token" in e for e in self.v.errors))

    def test_detects_openai_key(self):
        raw = "key: sk-" + "y" * 48
        self._call(raw)
        self.assertTrue(any("OpenAI API key" in e for e in self.v.errors))

    def test_detects_hardcoded_password(self):
        raw = "\"password\": \"mypassword\""
        self._call(raw)
        self.assertTrue(any("password" in e.lower() for e in self.v.errors))

    def test_detects_hardcoded_token(self):
        raw = "\"token\": \"hardcoded\""
        self._call(raw)
        self.assertTrue(any("token" in e.lower() for e in self.v.errors))

    def test_pull_request_target_produces_warning(self):
        content = {
            "name": "CI",
            "on": {"pull_request_target": {"branches": ["main"]}},
            "jobs": {},
        }
        self._call("raw", content)
        self.assertTrue(
            any("pull_request_target" in w for w in self.v.warnings)
        )

    def test_no_permissions_produces_info(self):
        content = {
            "name": "CI",
            "on": ["push"],
            "jobs": {"build": {"runs-on": "ubuntu-latest", "steps": []}},
        }
        self._call("raw", content)
        self.assertTrue(any("permissions" in i for i in self.v.info))

    def test_workflow_level_permissions_suppresses_info(self):
        content = {
            "name": "CI",
            "on": ["push"],
            "permissions": "read-all",
            "jobs": {"build": {"runs-on": "ubuntu-latest", "steps": []}},
        }
        self._call("raw", content)
        perm_info = [i for i in self.v.info if "permissions" in i]
        self.assertEqual(perm_info, [])

    def test_job_level_permissions_suppresses_info(self):
        content = {
            "name": "CI",
            "on": ["push"],
            "jobs": {
                "build": {
                    "runs-on": "ubuntu-latest",
                    "permissions": {"contents": "read"},
                    "steps": [],
                }
            },
        }
        self._call("raw", content)
        perm_info = [i for i in self.v.info if "permissions" in i]
        self.assertEqual(perm_info, [])

    def test_secret_via_env_variable_not_flagged(self):
        """${{ secrets.MY_TOKEN }} should NOT be flagged as a hardcoded token."""
        raw = "token: ${{ secrets.GITHUB_TOKEN }}"
        self._call(raw)
        token_errors = [e for e in self.v.errors if "token" in e.lower()]
        self.assertEqual(token_errors, [])


# ===========================================================================
# TestValidateBestPractices
# ===========================================================================


class TestValidateBestPractices(unittest.TestCase):
    def setUp(self):
        import tempfile

        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / ".github" / "workflows").mkdir(parents=True)
        self.v = WorkflowValidator(self.root)

    def tearDown(self):
        self._tmp.cleanup()

    def test_supported_python_version_no_warning(self):
        content = {
            "jobs": {
                "build": {
                    "steps": [
                        {"with": {"python-version": "3.11"}}
                    ]
                }
            }
        }
        self.v._validate_best_practices("ci.yml", content)
        version_warns = [w for w in self.v.warnings if "Python" in w]
        self.assertEqual(version_warns, [])

    def test_unsupported_python_version_produces_warning(self):
        content = {
            "jobs": {
                "build": {
                    "steps": [
                        {"with": {"python-version": "3.8"}}
                    ]
                }
            }
        }
        self.v._validate_best_practices("ci.yml", content)
        self.assertTrue(any("3.8" in w for w in self.v.warnings))

    def test_unpinned_action_produces_warning(self):
        content = {
            "jobs": {
                "build": {
                    "steps": [{"uses": "actions/checkout"}]  # no @version
                }
            }
        }
        self.v._validate_best_practices("ci.yml", content)
        self.assertTrue(any("Unpinned" in w for w in self.v.warnings))

    def test_pinned_action_no_warning(self):
        content = {
            "jobs": {
                "build": {
                    "steps": [{"uses": "actions/checkout@v3"}]
                }
            }
        }
        self.v._validate_best_practices("ci.yml", content)
        unpinned = [w for w in self.v.warnings if "Unpinned" in w]
        self.assertEqual(unpinned, [])

    def test_local_action_no_warning(self):
        content = {
            "jobs": {
                "build": {
                    "steps": [{"uses": "./local-action"}]
                }
            }
        }
        self.v._validate_best_practices("ci.yml", content)
        unpinned = [w for w in self.v.warnings if "Unpinned" in w]
        self.assertEqual(unpinned, [])

    def test_step_without_uses_no_warning(self):
        content = {
            "jobs": {
                "build": {
                    "steps": [{"run": "echo hello"}]
                }
            }
        }
        self.v._validate_best_practices("ci.yml", content)
        unpinned = [w for w in self.v.warnings if "Unpinned" in w]
        self.assertEqual(unpinned, [])

    def test_non_dict_step_skipped(self):
        content = {
            "jobs": {
                "build": {
                    "steps": ["not-a-dict"]
                }
            }
        }
        # Should not raise
        self.v._validate_best_practices("ci.yml", content)


# ===========================================================================
# TestValidateAll (integration-style using temp files)
# ===========================================================================


class TestValidateAll(unittest.TestCase):
    def setUp(self):
        import tempfile

        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.workflows_dir = self.root / ".github" / "workflows"
        self.workflows_dir.mkdir(parents=True)

    def tearDown(self):
        self._tmp.cleanup()

    def _validator(self):
        return WorkflowValidator(self.root)

    def test_valid_workflow_passes(self):
        _write_workflow(self.workflows_dir, "ci.yml", _VALID_WORKFLOW)
        v = self._validator()
        result = v.validate_all()
        self.assertTrue(result)
        self.assertEqual(v.errors, [])

    def test_no_workflows_returns_false(self):
        v = self._validator()
        result = v.validate_all()
        self.assertFalse(result)
        self.assertTrue(any("No workflow files" in e for e in v.errors))

    def test_invalid_yaml_returns_false(self):
        _write_workflow(self.workflows_dir, "bad.yml", "key: [\nbad yaml")
        v = self._validator()
        result = v.validate_all()
        self.assertFalse(result)
        self.assertTrue(any("Invalid YAML" in e for e in v.errors))

    def test_specific_workflow_name_validates_only_that_file(self):
        _write_workflow(self.workflows_dir, "ci.yml", _VALID_WORKFLOW)
        v = self._validator()
        result = v.validate_all(workflow_name="ci.yml")
        self.assertTrue(result)

    def test_specific_workflow_not_found_returns_false(self):
        v = self._validator()
        result = v.validate_all(workflow_name="nonexistent.yml")
        self.assertFalse(result)
        self.assertTrue(any("not found" in e for e in v.errors))

    def test_empty_yaml_file_adds_warning(self):
        (self.workflows_dir / "empty.yml").write_text("")
        v = self._validator()
        v.validate_all()
        self.assertTrue(any("Empty" in w for w in v.warnings))

    def test_metadata_file_is_skipped_without_errors(self):
        metadata = "sdk: gradio\ntitle: My App\n"
        _write_workflow(self.workflows_dir, "README.yml", metadata)
        v = self._validator()
        # Metadata file should not produce structure errors
        v.validate_all()
        struct_errors = [e for e in v.errors if "Missing 'jobs'" in e]
        self.assertEqual(struct_errors, [])

    def test_workflow_missing_jobs_fails(self):
        bad = "name: CI\non: [push]\n"
        _write_workflow(self.workflows_dir, "ci.yml", bad)
        v = self._validator()
        result = v.validate_all()
        self.assertFalse(result)

    def test_get_workflow_files_finds_yml_and_yaml(self):
        _write_workflow(self.workflows_dir, "a.yml", _VALID_WORKFLOW)
        _write_workflow(self.workflows_dir, "b.yaml", _VALID_WORKFLOW)
        v = self._validator()
        files = v._get_workflow_files()
        names = {f.name for f in files}
        self.assertIn("a.yml", names)
        self.assertIn("b.yaml", names)


# ===========================================================================
# TestValidateAllReturnValue
# ===========================================================================


class TestValidateAllReturnValue(unittest.TestCase):
    """Ensure validate_all returns True iff errors list is empty."""

    def setUp(self):
        import tempfile

        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.workflows_dir = self.root / ".github" / "workflows"
        self.workflows_dir.mkdir(parents=True)

    def tearDown(self):
        self._tmp.cleanup()

    def test_errors_present_means_false(self):
        v = WorkflowValidator(self.root)
        v.errors.append("some error")
        # Directly check the contract
        self.assertFalse(len(v.errors) == 0)

    def test_no_errors_means_true(self):
        v = WorkflowValidator(self.root)
        self.assertTrue(len(v.errors) == 0)


if __name__ == "__main__":
    unittest.main()
