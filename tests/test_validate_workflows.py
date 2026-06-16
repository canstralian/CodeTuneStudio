

















































































































































































































































































































































































































































































































        self.assertEqual(names, sorted(set(names)))


# ---------------------------------------------------------------------------
# Additional edge-case tests strengthening coverage for PR changes
# ---------------------------------------------------------------------------


class TestValidateSecurityAdditional(unittest.TestCase):
    """Additional security tests covering patterns introduced in this PR."""

    def _v(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        return _make_validator(Path(td.name))

    def test_hardcoded_token_pattern_adds_error(self):
        """Fourth secret pattern: hardcoded 'token' key."""
        v = self._v()
        raw = '"token": "abc123"'
        v._validate_security("ci.yml", raw, {})
        self.assertTrue(any("Hardcoded token" in e for e in v.errors))

    def test_case_insensitive_github_token_detection(self):
        """Secret pattern matching is case-insensitive."""
        v = self._v()
        # Mix of upper/lower in the token prefix — regex uses re.IGNORECASE
        raw = "GHP_" + "a" * 36
        v._validate_security("ci.yml", raw, {})
        self.assertTrue(
            any("GitHub personal access token" in e for e in v.errors)
        )

    def test_secret_in_env_section_is_flagged(self):
        """A hardcoded secret embedded anywhere in raw content is detected."""
        v = self._v()
        raw = (
            "env:\n"
            '  MY_TOKEN: "ghp_' + "z" * 36 + '"\n'
        )
        v._validate_security("ci.yml", raw, {})
        self.assertTrue(
            any("GitHub personal access token" in e for e in v.errors)
        )

    def test_dollar_brace_token_value_not_flagged(self):
        """Values like '${{ secrets.TOKEN }}' should NOT trigger hardcoded token."""
        v = self._v()
        raw = '"token": "${{ secrets.MY_TOKEN }}"'
        content = {"on": "push", "jobs": {"build": {"permissions": {}}}}
        v._validate_security("ci.yml", raw, content)
        self.assertFalse(any("Hardcoded token" in e for e in v.errors))

    def test_pull_request_target_via_yaml_true_key(self):
        """YAML parses 'on:' as True; validator should handle content.get(True, {})."""
        v = self._v()
        # Simulate what PyYAML produces for 'on: {pull_request_target: {}}'
        content = {True: {"pull_request_target": {}}}
        v._validate_security("ci.yml", "echo hi", content)
        self.assertTrue(
            any("pull_request_target" in w for w in v.warnings)
        )

    def test_multiple_secret_types_each_generate_separate_error(self):
        """When multiple secret patterns match, each produces its own error."""
        v = self._v()
        raw = (
            "github_token: ghp_" + "a" * 36 + "\n"
            "openai_key: sk-" + "b" * 48 + "\n"
        )
        v._validate_security("ci.yml", raw, {})
        github_errors = [e for e in v.errors if "GitHub personal access token" in e]
        openai_errors = [e for e in v.errors if "OpenAI API key" in e]
        self.assertTrue(len(github_errors) >= 1)
        self.assertTrue(len(openai_errors) >= 1)

    def test_no_jobs_key_skips_job_permissions_check(self):
        """When content has no 'jobs', permission check should not raise."""
        v = self._v()
        content = {"on": "push"}  # no "jobs" key
        try:
            v._validate_security("ci.yml", "echo hi", content)
        except Exception as exc:
            self.fail(f"_validate_security raised unexpectedly: {exc}")


class TestValidateStructureAdditional(unittest.TestCase):
    """Extra structure tests to cover boundary cases in this PR."""

    def _v(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        return _make_validator(Path(td.name))

    def test_trigger_via_yaml_true_key_counts_as_trigger(self):
        """Content with True (YAML 'on') key should be treated as having a trigger."""
        v = self._v()
        content = {
            "name": "CI",
            True: "push",   # YAML parser converts 'on' to True
            "jobs": {
                "build": {"runs-on": "ubuntu-latest", "steps": [{"run": "echo"}]}
            },
        }
        v._validate_structure("ci.yml", content)
        # has_trigger = "on" in content or True in content → True
        self.assertFalse(any("Missing trigger" in e for e in v.errors))

    def test_multiple_jobs_all_validated(self):
        """All jobs in a workflow are validated for 'runs-on' and 'steps'."""
        v = self._v()
        content = {
            "name": "CI",
            "on": "push",
            "jobs": {
                "job1": {"runs-on": "ubuntu-latest", "steps": []},
                "job2": {"steps": []},  # missing runs-on
                "job3": {"runs-on": "ubuntu-latest"},  # missing steps
            },
        }
        v._validate_structure("ci.yml", content)
        runs_on_errors = [e for e in v.errors if "runs-on" in e]
        steps_errors = [e for e in v.errors if "steps" in e]
        self.assertEqual(len(runs_on_errors), 1)
        self.assertEqual(len(steps_errors), 1)

    def test_jobs_with_none_values_not_flagged(self):
        """Jobs with None config should not generate runs-on/steps errors."""
        v = self._v()
        content = {
            "name": "CI",
            "on": "push",
            "jobs": {"null-job": None, "valid-job": {"runs-on": "ubuntu-latest", "steps": []}},
        }
        v._validate_structure("ci.yml", content)
        # Only valid-job has runs-on and steps; null-job is skipped
        self.assertFalse(any("null-job" in e for e in v.errors))


class TestRedactAdditional(unittest.TestCase):
    """Boundary tests for the _redact helper added in this PR."""

    def _v(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        return _make_validator(Path(td.name))

    def test_redact_empty_string(self):
        v = self._v()
        self.assertEqual(v._redact(""), "")

    def test_redact_token_shorter_than_pattern_not_redacted(self):
        """A token that is shorter than the expected length should not match."""
        v = self._v()
        short_token = "ghp_" + "x" * 10  # too short (36 chars needed)
        result = v._redact(short_token)
        self.assertEqual(result, short_token)

    def test_redact_does_not_alter_safe_content(self):
        v = self._v()
        safe = "GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}"
        self.assertEqual(v._redact(safe), safe)

    def test_redact_password_pattern(self):
        v = self._v()
        raw = "'password': 'mypassword'"
        result = v._redact(raw)
        self.assertIn("[REDACTED]", result)
        self.assertNotIn("mypassword", result)


if __name__ == "__main__":
    unittest.main()
