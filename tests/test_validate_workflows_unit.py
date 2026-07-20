"""
Unit tests for the WorkflowValidator class in scripts/validate_workflows.py.

These tests isolate the validator from real workflow files on disk by creating
temporary YAML fixtures via the tempfile module. They cover:
  - WorkflowValidator.__init__ state
  - _is_metadata_file detection
  - _validate_structure (name, on, jobs)
  - _validate_security (hardcoded secrets, pull_request_target, permissions)
  - _validate_best_practices (action pinning – SHA vs tag)
  - _validate_workflow (file-not-found, invalid YAML, empty file, non-dict root)
  - validate_all (no workflows, security_only flag, single workflow selection)
"""

import tempfile
import textwrap
import unittest
from pathlib import Path


def _make_validator(tmp_dir: Path):
    """Return a fresh WorkflowValidator whose workflows_dir is tmp_dir/.github/workflows."""
    from scripts.validate_workflows import WorkflowValidator

    workflows_dir = tmp_dir / ".github" / "workflows"
    workflows_dir.mkdir(parents=True, exist_ok=True)
    return WorkflowValidator(tmp_dir)


def _write_workflow(workflows_dir: Path, name: str, content: str) -> Path:
    """
    Write a workflow configuration to a file in the specified directory.

    Parameters:
        workflows_dir (Path): The directory where the workflow file will be written.
        name (str): The filename for the workflow.
        content (str): The workflow content to write.

    Returns:
        Path: The path to the written workflow file.
    """
    path = workflows_dir / name
    path.write_text(textwrap.dedent(content), encoding="utf-8")
    return path


class TestWorkflowValidatorInit(unittest.TestCase):
    def test_attributes_initialised(self):
        with tempfile.TemporaryDirectory() as tmp:
            v = _make_validator(Path(tmp))
            self.assertEqual(v.errors, [])
            self.assertEqual(v.warnings, [])
            self.assertEqual(v.info, [])
            self.assertEqual(v.workflows_dir, Path(tmp) / ".github" / "workflows")


class TestIsMetadataFile(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.v = _make_validator(Path(self._tmp.name))

    def tearDown(self):
        """
        Remove the temporary test directory.
        """
        self._tmp.cleanup()

    def test_sdk_key_is_metadata(self):
        self.assertTrue(self.v._is_metadata_file({"sdk": "gradio"}))

    def test_emoji_key_is_metadata(self):
        self.assertTrue(self.v._is_metadata_file({"emoji": "🚀"}))

    def test_color_from_key_is_metadata(self):
        self.assertTrue(self.v._is_metadata_file({"colorFrom": "blue"}))

    def test_title_without_jobs_or_on_is_metadata(self):
        self.assertTrue(self.v._is_metadata_file({"title": "My Space"}))

    def test_title_with_jobs_is_not_metadata(self):
        self.assertFalse(self.v._is_metadata_file({"title": "CI", "jobs": {}}))

    def test_title_with_on_is_not_metadata(self):
        self.assertFalse(self.v._is_metadata_file({"title": "CI", "on": "push"}))

    def test_normal_workflow_is_not_metadata(self):
        content = {"name": "CI", "on": "push", "jobs": {"build": {}}}
        self.assertFalse(self.v._is_metadata_file(content))


class TestValidateStructure(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.v = _make_validator(Path(self._tmp.name))

    def tearDown(self):
        """
        Remove the temporary test directory.
        """
        self._tmp.cleanup()

    def _fresh(self):
        """Reset collected messages."""
        self.v.errors.clear()
        self.v.warnings.clear()
        self.v.info.clear()

    def test_valid_minimal_workflow_produces_no_errors(self):
        content = {
            "name": "CI",
            "on": "push",
            "jobs": {"build": {"runs-on": "ubuntu-latest", "steps": []}},
        }
        self.v._validate_structure("ci.yml", content)
        self.assertEqual(self.v.errors, [])
        self.assertEqual(self.v.warnings, [])

    def test_missing_name_adds_warning(self):
        content = {"on": "push", "jobs": {"build": {}}}
        self.v._validate_structure("ci.yml", content)
        self.assertTrue(any("name" in w for w in self.v.warnings))

    def test_missing_jobs_adds_error(self):
        content = {"name": "CI", "on": "push"}
        self.v._validate_structure("ci.yml", content)
        self.assertTrue(any("jobs" in e for e in self.v.errors))

    def test_empty_jobs_dict_adds_error(self):
        content = {"name": "CI", "on": "push", "jobs": {}}
        self.v._validate_structure("ci.yml", content)
        self.assertTrue(any("jobs" in e for e in self.v.errors))

    def test_jobs_not_dict_adds_error(self):
        content = {"name": "CI", "on": "push", "jobs": ["build"]}
        self.v._validate_structure("ci.yml", content)
        self.assertTrue(any("jobs" in e for e in self.v.errors))


class TestValidateSecurity(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.v = _make_validator(Path(self._tmp.name))

    def tearDown(self):
        """
        Remove the temporary test directory.
        """
        self._tmp.cleanup()

    def _run(self, raw, content=None):
        self.v.errors.clear()
        self.v.warnings.clear()
        self.v.info.clear()
        if content is None:
            import yaml

            content = yaml.safe_load(raw)
        self.v._validate_security("wf.yml", raw, content)

    def test_clean_workflow_no_errors(self):
        raw = textwrap.dedent(
            """\
            name: CI
            on: push
            permissions:
              contents: read
            jobs:
              build:
                runs-on: ubuntu-latest
                steps: []
            """
        )
        self._run(raw)
        self.assertEqual(self.v.errors, [])

    def test_hardcoded_password_flagged(self):
        raw = textwrap.dedent(
            """\
            name: CI
            on: push
            jobs:
              build:
                runs-on: ubuntu-latest
                env:
                  DB_PASS: "hardcoded123"
                steps: []
            """
        )
        # The raw text contains password: "..." pattern
        raw_with_password = raw.replace(
            'DB_PASS: "hardcoded123"', 'password: "hardcoded123"'
        )
        import yaml

        self._run(raw_with_password, yaml.safe_load(raw_with_password))
        self.assertTrue(
            any("hardcoded password" in e for e in self.v.errors),
            f"Expected hardcoded password error, got: {self.v.errors}",
        )

    def test_github_token_pattern_flagged(self):
        token = "ghp_" + "A" * 36
        raw = f"name: CI\non: push\nenv:\n  TOKEN: {token}\njobs:\n  b:\n    runs-on: ubuntu-latest\n    steps: []\n"
        self._run(raw)
        self.assertTrue(any("GitHub token" in e for e in self.v.errors))

    def test_openai_key_pattern_flagged(self):
        key = "sk-" + "B" * 48
        raw = f"name: CI\non: push\nenv:\n  KEY: {key}\njobs:\n  b:\n    runs-on: ubuntu-latest\n    steps: []\n"
        self._run(raw)
        self.assertTrue(any("OpenAI" in e for e in self.v.errors))

    def test_pull_request_target_is_an_error(self):
        raw = textwrap.dedent(
            """\
            name: PR
            on:
              pull_request_target:
                types: [opened]
            jobs:
              build:
                runs-on: ubuntu-latest
                steps: []
            """
        )
        self._run(raw)
        self.assertTrue(
            any("pull_request_target" in e for e in self.v.errors),
            f"Expected pull_request_target error, got errors={self.v.errors}",
        )

    def test_no_permissions_adds_info(self):
        raw = textwrap.dedent(
            """\
            name: CI
            on: push
            jobs:
              build:
                runs-on: ubuntu-latest
                steps: []
            """
        )
        self._run(raw)
        self.assertTrue(
            any("permissions" in i for i in self.v.info),
            f"Expected permissions info, got: {self.v.info}",
        )

    def test_job_level_permissions_suppresses_info(self):
        raw = textwrap.dedent(
            """\
            name: CI
            on: push
            jobs:
              build:
                permissions:
                  contents: read
                runs-on: ubuntu-latest
                steps: []
            """
        )
        self._run(raw)
        self.assertFalse(any("permissions" in i for i in self.v.info))

    def test_api_key_variant_flagged(self):
        raw = textwrap.dedent(
            """\
            name: CI
            on: push
            jobs:
              b:
                runs-on: ubuntu-latest
                env:
                  api_key: "mysecretkey"
                steps: []
            """
        )
        self._run(raw)
        self.assertTrue(
            any("api key" in e.lower() for e in self.v.errors),
            f"Expected api key error, got: {self.v.errors}",
        )


class TestValidateBestPractices(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.v = _make_validator(Path(self._tmp.name))

    def tearDown(self):
        """
        Remove the temporary test directory.
        """
        self._tmp.cleanup()

    def _run(self, content):
        """
        Clear warnings and validate best practices for a workflow.

        Parameters:
            content (dict): The parsed workflow content to validate.
        """
        self.v.warnings.clear()
        self.v._validate_best_practices("wf.yml", content)

    def test_sha_pinned_action_no_warning(self):
        sha = "a" * 40
        content = {
            "jobs": {
                "build": {
                    "steps": [{"uses": f"actions/checkout@{sha}"}],
                }
            }
        }
        self._run(content)
        self.assertEqual(self.v.warnings, [])

    def test_tag_pinned_action_adds_warning(self):
        content = {
            "jobs": {
                "build": {
                    "steps": [{"uses": "actions/checkout@v4"}],
                }
            }
        }
        self._run(content)
        self.assertTrue(
            any("not pinned" in w for w in self.v.warnings),
            f"Expected unpinned warning, got: {self.v.warnings}",
        )

    def test_local_action_no_warning(self):
        content = {
            "jobs": {
                "build": {
                    "steps": [{"uses": "./my-action"}],
                }
            }
        }
        self._run(content)
        self.assertEqual(self.v.warnings, [])

    def test_docker_action_no_warning(self):
        content = {
            "jobs": {
                "build": {
                    "steps": [{"uses": "docker://alpine:3.18"}],
                }
            }
        }
        self._run(content)
        self.assertEqual(self.v.warnings, [])

    def test_action_without_at_adds_warning(self):
        content = {
            "jobs": {
                "build": {
                    "steps": [{"uses": "actions/checkout"}],
                }
            }
        }
        self._run(content)
        self.assertTrue(any("not pinned" in w for w in self.v.warnings))

    def test_branch_pin_adds_warning(self):
        content = {
            "jobs": {
                "build": {
                    "steps": [{"uses": "actions/checkout@main"}],
                }
            }
        }
        self._run(content)
        self.assertTrue(any("not pinned" in w for w in self.v.warnings))


class TestValidateWorkflow(unittest.TestCase):
    """Tests for _validate_workflow called via a real YAML file on disk."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.v = _make_validator(self.tmp)
        self.wf_dir = self.tmp / ".github" / "workflows"

    def tearDown(self):
        """
        Remove the temporary test directory.
        """
        self._tmp.cleanup()

    def test_empty_yaml_file_adds_warning(self):
        path = self.wf_dir / "empty.yml"
        path.write_text("", encoding="utf-8")
        self.v._validate_workflow(path, security_only=False)
        self.assertTrue(any("Empty" in w for w in self.v.warnings))

    def test_invalid_yaml_adds_error(self):
        path = self.wf_dir / "bad.yml"
        path.write_text("key: [unclosed bracket", encoding="utf-8")
        self.v._validate_workflow(path, security_only=False)
        self.assertTrue(any("YAML" in e for e in self.v.errors))

    def test_non_mapping_root_adds_error(self):
        path = self.wf_dir / "list.yml"
        path.write_text("- item1\n- item2\n", encoding="utf-8")
        self.v._validate_workflow(path, security_only=False)
        self.assertTrue(any("mapping" in e for e in self.v.errors))

    def test_metadata_file_is_skipped(self):
        path = self.wf_dir / "meta.yml"
        path.write_text("sdk: gradio\ntitle: My Space\n", encoding="utf-8")
        self.v._validate_workflow(path, security_only=False)
        self.assertTrue(any("Metadata" in i for i in self.v.info))
        self.assertEqual(self.v.errors, [])

    def test_security_only_skips_structure_check(self):
        path = self.wf_dir / "nojobs.yml"
        # Missing 'jobs' would normally cause a structure error
        path.write_text("name: CI\non: push\n", encoding="utf-8")
        self.v._validate_workflow(path, security_only=True)
        # Structure errors not reported because security_only=True
        self.assertFalse(any("jobs" in e for e in self.v.errors))

    def test_valid_workflow_no_errors(self):
        sha = "a" * 40
        content = textwrap.dedent(
            f"""\
            name: CI
            on: push
            permissions:
              contents: read
            jobs:
              build:
                runs-on: ubuntu-latest
                steps:
                  - uses: actions/checkout@{sha}
            """
        )
        path = self.wf_dir / "valid.yml"
        path.write_text(content, encoding="utf-8")
        self.v._validate_workflow(path, security_only=False)
        self.assertEqual(self.v.errors, [])


class TestSelectWorkflows(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.v = _make_validator(self.tmp)
        self.wf_dir = self.tmp / ".github" / "workflows"

    def tearDown(self):
        """
        Remove the temporary test directory.
        """
        self._tmp.cleanup()

    def test_nonexistent_named_workflow_records_error(self):
        result = self.v._select_workflows("ghost.yml")
        self.assertEqual(result, [])
        self.assertTrue(any("not found" in e for e in self.v.errors))

    def test_existing_named_workflow_returns_single_path(self):
        path = self.wf_dir / "ci.yml"
        path.write_text("name: CI\n", encoding="utf-8")
        result = self.v._select_workflows("ci.yml")
        self.assertEqual(result, [path])

    def test_glob_returns_all_yml_files(self):
        for name in ("a.yml", "b.yaml", "c.yml"):
            (self.wf_dir / name).write_text("x: 1\n", encoding="utf-8")
        result = self.v._select_workflows(None)
        names = {p.name for p in result}
        self.assertIn("a.yml", names)
        self.assertIn("b.yaml", names)
        self.assertIn("c.yml", names)

    def test_empty_workflows_dir_returns_empty_list(self):
        result = self.v._select_workflows(None)
        self.assertEqual(result, [])


class TestValidateSecurityExtended(unittest.TestCase):
    """Additional edge-case coverage for _validate_security added in 0.2.1."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.v = _make_validator(Path(self._tmp.name))

    def tearDown(self):
        self._tmp.cleanup()

    def _run(self, raw, content=None):
        self.v.errors.clear()
        self.v.warnings.clear()
        self.v.info.clear()
        if content is None:
            import yaml

            content = yaml.safe_load(raw)
        self.v._validate_security("wf.yml", raw, content)

    def test_pull_request_target_as_string_trigger_is_error(self):
        """When 'on' is a plain string 'pull_request_target', it should be flagged as an error."""
        raw = "name: PR\non: pull_request_target\njobs:\n  b:\n    runs-on: ubuntu-latest\n    steps: []\n"
        import yaml

        content = yaml.safe_load(raw)
        self._run(raw, content)
        self.assertTrue(
            any("pull_request_target" in e for e in self.v.errors),
            f"Expected pull_request_target error for string trigger, got: {self.v.errors}",
        )

    def test_pull_request_target_in_list_trigger_is_error(self):
        """When 'on' is a list containing 'pull_request_target', it should be flagged."""
        raw = textwrap.dedent(
            """\
            name: PR
            on:
              - push
              - pull_request_target
            jobs:
              b:
                runs-on: ubuntu-latest
                steps: []
            """
        )
        import yaml

        content = yaml.safe_load(raw)
        self._run(raw, content)
        self.assertTrue(
            any("pull_request_target" in e for e in self.v.errors),
            f"Expected pull_request_target error for list trigger, got: {self.v.errors}",
        )

    def test_hardcoded_token_key_is_flagged(self):
        """A literal 'token: \"value\"' pattern in raw YAML is treated as a hardcoded secret."""
        raw = textwrap.dedent(
            """\
            name: CI
            on: push
            jobs:
              b:
                runs-on: ubuntu-latest
                env:
                  token: "myrawtoken"
                steps: []
            """
        )
        import yaml

        self._run(raw, yaml.safe_load(raw))
        self.assertTrue(
            any("token" in e.lower() for e in self.v.errors),
            f"Expected hardcoded token error, got: {self.v.errors}",
        )

    def test_api_dash_key_variant_is_flagged(self):
        """'api-key: value' (dash variant) should be detected as a hardcoded secret."""
        raw = textwrap.dedent(
            """\
            name: CI
            on: push
            jobs:
              b:
                runs-on: ubuntu-latest
                env:
                  api-key: "supersecret"
                steps: []
            """
        )
        import yaml

        self._run(raw, yaml.safe_load(raw))
        self.assertTrue(
            any("api key" in e.lower() for e in self.v.errors),
            f"Expected api key error for 'api-key' variant, got: {self.v.errors}",
        )

    def test_github_secret_reference_not_flagged_as_hardcoded_token(self):
        """'token: ${{ secrets.GITHUB_TOKEN }}' must not be flagged as a hardcoded secret."""
        raw = textwrap.dedent(
            """\
            name: CI
            on: push
            permissions:
              contents: read
            jobs:
              b:
                runs-on: ubuntu-latest
                env:
                  TOKEN: ${{ secrets.GITHUB_TOKEN }}
                steps: []
            """
        )
        import yaml

        self._run(raw, yaml.safe_load(raw))
        self.assertFalse(
            any("hardcoded token" in e.lower() for e in self.v.errors),
            f"Secret reference should not trigger hardcoded-token error, got: {self.v.errors}",
        )


class TestValidateBestPracticesExtended(unittest.TestCase):
    """Additional coverage for _validate_best_practices (action SHA pinning)."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.v = _make_validator(Path(self._tmp.name))

    def tearDown(self):
        self._tmp.cleanup()

    def _run(self, content):
        self.v.warnings.clear()
        self.v._validate_best_practices("wf.yml", content)

    def test_sha_39_chars_adds_warning(self):
        """A 39-character hex string is not a full SHA-40 and must be flagged."""
        short_sha = "a" * 39
        content = {
            "jobs": {
                "build": {
                    "steps": [{"uses": f"actions/checkout@{short_sha}"}],
                }
            }
        }
        self._run(content)
        self.assertTrue(
            any("not pinned" in w for w in self.v.warnings),
            f"39-char SHA should be flagged as unpinned, got: {self.v.warnings}",
        )

    def test_sha_41_chars_adds_warning(self):
        """A 41-character string after @ is also not a valid 40-char SHA."""
        long_sha = "a" * 41
        content = {
            "jobs": {
                "build": {
                    "steps": [{"uses": f"actions/checkout@{long_sha}"}],
                }
            }
        }
        self._run(content)
        self.assertTrue(
            any("not pinned" in w for w in self.v.warnings),
            f"41-char SHA should be flagged as unpinned, got: {self.v.warnings}",
        )

    def test_step_without_uses_key_is_ignored(self):
        """Steps that use 'run' instead of 'uses' must not generate warnings."""
        content = {
            "jobs": {
                "build": {
                    "steps": [{"run": "echo hello"}],
                }
            }
        }
        self._run(content)
        self.assertEqual(self.v.warnings, [])

    def test_non_dict_step_is_skipped_gracefully(self):
        """Non-dict step entries must not raise and must produce no warnings."""
        content = {
            "jobs": {
                "build": {
                    "steps": ["just-a-string"],
                }
            }
        }
        self._run(content)
        self.assertEqual(self.v.warnings, [])

    def test_non_dict_job_is_skipped_gracefully(self):
        """Non-dict job configs must not raise and must produce no warnings."""
        content = {
            "jobs": {
                "build": "not-a-dict",
            }
        }
        self._run(content)
        self.assertEqual(self.v.warnings, [])


class TestValidateAll(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.wf_dir = self.tmp / ".github" / "workflows"
        self.wf_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        """
        Remove the temporary test directory.
        """
        self._tmp.cleanup()

    def _validator(self):
        from scripts.validate_workflows import WorkflowValidator

        return WorkflowValidator(self.tmp)

    def test_no_workflows_returns_false(self):
        v = self._validator()
        result = v.validate_all()
        self.assertFalse(result)
        self.assertTrue(any("No workflow" in e for e in v.errors))

    def test_valid_workflow_returns_true(self):
        sha = "b" * 40
        content = textwrap.dedent(
            f"""\
            name: CI
            on: push
            permissions:
              contents: read
            jobs:
              build:
                runs-on: ubuntu-latest
                steps:
                  - uses: actions/checkout@{sha}
            """
        )
        (self.wf_dir / "ci.yml").write_text(content, encoding="utf-8")
        v = self._validator()
        result = v.validate_all()
        self.assertTrue(result, f"Expected success but got errors: {v.errors}")

    def test_workflow_with_error_returns_false(self):
        (self.wf_dir / "bad.yml").write_text("name: CI\non: push\n", encoding="utf-8")
        v = self._validator()
        result = v.validate_all()
        self.assertFalse(result)

    def test_security_only_flag_propagated(self):
        # A workflow missing 'jobs' would fail structure, but security_only skips it
        (self.wf_dir / "nojobs.yml").write_text(
            "name: CI\non: push\n", encoding="utf-8"
        )
        v = self._validator()
        # security_only=True → no structure error for missing jobs
        v.validate_all(security_only=True)
        self.assertFalse(any("jobs" in e for e in v.errors))

    def test_named_workflow_only_validates_that_file(self):
        sha = "c" * 40
        good = textwrap.dedent(
            f"""\
            name: Good
            on: push
            permissions:
              contents: read
            jobs:
              build:
                runs-on: ubuntu-latest
                steps:
                  - uses: actions/checkout@{sha}
            """
        )
        bad = "invalid_yaml: [broken"
        (self.wf_dir / "good.yml").write_text(good, encoding="utf-8")
        (self.wf_dir / "bad.yml").write_text(bad, encoding="utf-8")
        v = self._validator()
        result = v.validate_all(workflow_name="good.yml")
        self.assertTrue(result, f"Expected good.yml to pass; errors: {v.errors}")


if __name__ == "__main__":
    unittest.main()
