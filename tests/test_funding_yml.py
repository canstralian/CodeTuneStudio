"""
Tests for .github/FUNDING.yml configuration.

These tests verify that the funding configuration file is valid,
contains only explicitly configured platforms, and no placeholder
or empty entries remain after cleanup.
"""

import unittest
import yaml
from pathlib import Path


class TestFundingYml(unittest.TestCase):
    """Test the .github/FUNDING.yml configuration file."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.repo_root = Path(__file__).parent.parent
        self.funding_file = self.repo_root / ".github" / "FUNDING.yml"

    def _load_funding(self) -> dict:
        """Helper to load and return parsed FUNDING.yml content."""
        with open(self.funding_file, "r") as f:
            content = yaml.safe_load(f)
            return content if content is not None else {}

    # ------------------------------------------------------------------
    # File existence and parseability
    # ------------------------------------------------------------------

    def test_funding_file_exists(self) -> None:
        """Test that the FUNDING.yml file exists at the expected path."""
        self.assertTrue(
            self.funding_file.exists(),
            f"FUNDING.yml not found at {self.funding_file}",
        )

    def test_funding_file_is_valid_yaml(self) -> None:
        """Test that FUNDING.yml is parseable as valid YAML."""
        try:
            content = self._load_funding()
        except yaml.YAMLError as exc:
            self.fail(f"FUNDING.yml is not valid YAML: {exc}")
        self.assertIsNotNone(content, "FUNDING.yml parsed to None — file may be empty")

    def test_funding_file_is_a_mapping(self) -> None:
        """Test that the top-level YAML structure is a mapping (dict)."""
        content = self._load_funding()
        self.assertIsInstance(
            content,
            dict,
            "FUNDING.yml top-level structure should be a YAML mapping",
        )

    # ------------------------------------------------------------------
    # Configured platform values
    # ------------------------------------------------------------------

    def test_github_platform_is_configured(self) -> None:
        """Test that the github funding platform is set to canstralian."""
        content = self._load_funding()
        self.assertIn("github", content, "FUNDING.yml should contain a 'github' key")
        self.assertEqual(
            content["github"],
            "canstralian",
            "github funding username should be 'canstralian'",
        )

    def test_patreon_platform_is_configured(self) -> None:
        """Test that the patreon funding platform is set to canstralian."""
        content = self._load_funding()
        self.assertIn("patreon", content, "FUNDING.yml should contain a 'patreon' key")
        self.assertEqual(
            content["patreon"],
            "canstralian",
            "patreon funding username should be 'canstralian'",
        )

    def test_only_configured_platforms_are_present(self) -> None:
        """Test that only explicitly configured platforms exist (no extras)."""
        content = self._load_funding()
        expected_keys = {"github", "patreon"}
        actual_keys = set(content.keys())
        self.assertEqual(
            actual_keys,
            expected_keys,
            f"Unexpected keys in FUNDING.yml: {actual_keys - expected_keys}",
        )

    def test_no_none_values(self) -> None:
        """Test that no platform entry has a None/empty value (placeholder cleanup)."""
        content = self._load_funding()
        for platform, value in content.items():
            self.assertIsNotNone(
                value,
                f"Platform '{platform}' has a None value — remove it or set a real username",
            )
            self.assertNotEqual(
                value,
                "",
                f"Platform '{platform}' has an empty string value",
            )

    # ------------------------------------------------------------------
    # Removed placeholder keys (regression: must not reappear)
    # ------------------------------------------------------------------

    def test_open_collective_placeholder_removed(self) -> None:
        """Test that the open_collective placeholder entry was removed."""
        content = self._load_funding()
        self.assertNotIn(
            "open_collective",
            content,
            "open_collective placeholder should have been removed",
        )

    def test_ko_fi_placeholder_removed(self) -> None:
        """Test that the ko_fi placeholder entry was removed."""
        content = self._load_funding()
        self.assertNotIn(
            "ko_fi",
            content,
            "ko_fi placeholder should have been removed",
        )

    def test_tidelift_placeholder_removed(self) -> None:
        """Test that the tidelift placeholder entry was removed."""
        content = self._load_funding()
        self.assertNotIn(
            "tidelift",
            content,
            "tidelift placeholder should have been removed",
        )

    def test_community_bridge_placeholder_removed(self) -> None:
        """Test that the community_bridge placeholder entry was removed."""
        content = self._load_funding()
        self.assertNotIn(
            "community_bridge",
            content,
            "community_bridge placeholder should have been removed",
        )

    def test_liberapay_placeholder_removed(self) -> None:
        """Test that the liberapay placeholder entry was removed."""
        content = self._load_funding()
        self.assertNotIn(
            "liberapay",
            content,
            "liberapay placeholder should have been removed",
        )

    def test_issuehunt_placeholder_removed(self) -> None:
        """Test that the issuehunt placeholder entry was removed."""
        content = self._load_funding()
        self.assertNotIn(
            "issuehunt",
            content,
            "issuehunt placeholder should have been removed",
        )

    def test_lfx_crowdfunding_placeholder_removed(self) -> None:
        """Test that the lfx_crowdfunding placeholder entry was removed."""
        content = self._load_funding()
        self.assertNotIn(
            "lfx_crowdfunding",
            content,
            "lfx_crowdfunding placeholder should have been removed",
        )

    def test_polar_placeholder_removed(self) -> None:
        """Test that the polar placeholder entry was removed."""
        content = self._load_funding()
        self.assertNotIn(
            "polar",
            content,
            "polar placeholder should have been removed",
        )

    def test_buy_me_a_coffee_entry_removed(self) -> None:
        """Test that the buy_me_a_coffee entry (previously 'sadejager') was removed."""
        content = self._load_funding()
        self.assertNotIn(
            "buy_me_a_coffee",
            content,
            "buy_me_a_coffee entry should have been removed",
        )

    def test_thanks_dev_placeholder_removed(self) -> None:
        """Test that the thanks_dev placeholder entry was removed."""
        content = self._load_funding()
        self.assertNotIn(
            "thanks_dev",
            content,
            "thanks_dev placeholder should have been removed",
        )

    def test_custom_placeholder_removed(self) -> None:
        """Test that the custom placeholder entry was removed."""
        content = self._load_funding()
        self.assertNotIn(
            "custom",
            content,
            "custom placeholder should have been removed",
        )

    # ------------------------------------------------------------------
    # Boundary / regression: raw file content checks
    # ------------------------------------------------------------------

    def test_no_sadejager_value_in_file(self) -> None:
        """Regression: the removed buy_me_a_coffee value 'sadejager' is not present."""
        with open(self.funding_file, "r") as f:
            raw_content = f.read()
        self.assertNotIn(
            "sadejager",
            raw_content,
            "Value 'sadejager' (old buy_me_a_coffee) must not appear in FUNDING.yml",
        )

    def test_no_replace_placeholder_comments_in_values(self) -> None:
        """Test that no 'Replace with' placeholder text remains in the file."""
        with open(self.funding_file, "r") as f:
            raw_content = f.read()
        self.assertNotIn(
            "Replace with",
            raw_content,
            "Placeholder comment 'Replace with ...' should not remain in FUNDING.yml",
        )

    def test_platform_usernames_are_strings(self) -> None:
        """Test that configured platform values are plain strings, not lists or dicts."""
        content = self._load_funding()
        for platform in ("github", "patreon"):
            self.assertIn(platform, content)
            self.assertIsInstance(
                content[platform],
                str,
                f"Platform '{platform}' value should be a string, got {type(content[platform])}",
            )

    def test_file_has_expected_line_count(self) -> None:
        """Test that the file is compact — no large block of placeholder lines remain."""
        with open(self.funding_file, "r") as f:
            lines = f.readlines()
        # Original file had 15 lines; cleaned file should have at most 6
        self.assertLessEqual(
            len(lines),
            6,
            f"FUNDING.yml has {len(lines)} lines; expected at most 6 after placeholder removal",
        )


if __name__ == "__main__":
    unittest.main()
