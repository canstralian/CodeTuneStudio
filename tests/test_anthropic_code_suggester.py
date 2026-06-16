import os
import unittest
from unittest.mock import MagicMock, patch

import pytest
from plugins.anthropic_code_suggester import AnthropicCodeSuggesterTool


class TestAnthropicCodeSuggesterTool(unittest.TestCase):
    @patch("plugins.anthropic_code_suggester.Anthropic")
    def test_init(self, mock_anthropic) -> None:
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "fake_key"}):
            tool = AnthropicCodeSuggesterTool()
            assert tool.metadata.name == "anthropic_code_suggester"
            assert (
                tool.metadata.description
                == "Suggests code improvements using Anthropic's Claude model"
            )
            assert tool.metadata.version == "0.1.0"
            assert tool.metadata.author == "CodeTuneStudio"
            assert tool.metadata.tags == ["code-suggestions", "ai", "anthropic"]
            mock_anthropic.assert_called_once_with(api_key="fake_key")

    def test_validate_inputs_valid(self) -> None:
        tool = AnthropicCodeSuggesterTool()
        assert tool.validate_inputs({"code": "print('hello')"})

    def test_validate_inputs_missing_code(self) -> None:
        tool = AnthropicCodeSuggesterTool()
        assert not tool.validate_inputs({})

    def test_validate_inputs_code_not_str(self) -> None:
        tool = AnthropicCodeSuggesterTool()
        assert not tool.validate_inputs({"code": 123})

    @patch("plugins.anthropic_code_suggester.Anthropic")
    def test_execute_success(self, mock_anthropic_class) -> None:
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        mock_message = MagicMock()
        mock_content_block = MagicMock()
        mock_content_block.text = "Some suggestions"
        mock_message.content = [mock_content_block]
        mock_client.messages.create.return_value = mock_message

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "fake_key"}):
            tool = AnthropicCodeSuggesterTool()
            result = tool.execute({"code": "def foo(): pass"})

            assert result["status"] == "success"
            assert result["suggestions"] == "Some suggestions"
            assert result["model"] == "claude-3-5-sonnet-20241022"
            mock_client.messages.create.assert_called_once_with(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                messages=[
                    {
                        "role": "user",
                        "content": (
                            "Analyze this code and suggest improvements "
                            "in JSON format.\n"
                            "Include specific recommendations for:\n"
                            "1. Code structure\n"
                            "2. Optimization opportunities\n"
                            "3. Best practices\n"
                            "4. Error handling\n\n"
                            "Code to analyze:\n"
                            "def foo(): pass"
                        ),
                    }
                ],
            )

    @patch("plugins.anthropic_code_suggester.Anthropic")
    def test_execute_invalid_inputs(self, mock_anthropic_class) -> None:
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "fake_key"}):
            tool = AnthropicCodeSuggesterTool()
            with pytest.raises(ValueError):
                tool.execute({})

    @patch("plugins.anthropic_code_suggester.Anthropic")
    def test_execute_api_error(self, mock_anthropic_class) -> None:
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        mock_client.messages.create.side_effect = Exception("API error")

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "fake_key"}):
            tool = AnthropicCodeSuggesterTool()
            result = tool.execute({"code": "def foo(): pass"})

            assert result["status"] == "error"
            assert "API error" in result["error"]

    # ------------------------------------------------------------------
    # Tests added for new behaviour introduced in this PR
    # ------------------------------------------------------------------

    def test_init_without_api_key_sets_client_to_none(self) -> None:
        """When ANTHROPIC_API_KEY is absent, client must be None (new PR behaviour)."""
        env_without_key = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
        with patch.dict(os.environ, env_without_key, clear=True):
            tool = AnthropicCodeSuggesterTool()
            assert tool.client is None

    def test_execute_returns_error_when_no_api_key(self) -> None:
        """execute() returns an error dict when client is None (no API key configured)."""
        env_without_key = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
        with patch.dict(os.environ, env_without_key, clear=True):
            tool = AnthropicCodeSuggesterTool()
            result = tool.execute({"code": "def foo(): pass"})

        assert result["status"] == "error"
        assert "ANTHROPIC_API_KEY" in result["error"]

    @patch("plugins.anthropic_code_suggester.Anthropic")
    def test_execute_empty_content_response_returns_error(self, mock_anthropic_class) -> None:
        """execute() handles the case where the API returns empty content list."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        mock_message = MagicMock()
        mock_message.content = []  # empty content
        mock_client.messages.create.return_value = mock_message

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "fake_key"}):
            tool = AnthropicCodeSuggesterTool()
            result = tool.execute({"code": "def foo(): pass"})

        assert result["status"] == "error"
        assert "empty" in result["error"].lower()

    @patch("plugins.anthropic_code_suggester.Anthropic")
    def test_execute_none_content_returns_error(self, mock_anthropic_class) -> None:
        """execute() handles the case where message.content is None/falsy."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        mock_message = MagicMock()
        mock_message.content = None
        mock_client.messages.create.return_value = mock_message

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "fake_key"}):
            tool = AnthropicCodeSuggesterTool()
            result = tool.execute({"code": "def foo(): pass"})

        assert result["status"] == "error"

    @patch("plugins.anthropic_code_suggester.Anthropic")
    def test_execute_content_block_missing_text_attribute(self, mock_anthropic_class) -> None:
        """execute() handles a content block that lacks a 'text' attribute."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        mock_message = MagicMock()
        # Create a content block that has no 'text' attribute
        mock_block = MagicMock(spec=[])  # spec=[] means no attributes
        mock_message.content = [mock_block]
        mock_client.messages.create.return_value = mock_message

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "fake_key"}):
            tool = AnthropicCodeSuggesterTool()
            result = tool.execute({"code": "def foo(): pass"})

        assert result["status"] == "error"
        assert "format" in result["error"].lower() or "invalid" in result["error"].lower()

    def test_validate_inputs_empty_string_code(self) -> None:
        """An empty string is a valid (string) code value."""
        tool = AnthropicCodeSuggesterTool()
        assert tool.validate_inputs({"code": ""})

    def test_validate_inputs_code_is_list_returns_false(self) -> None:
        tool = AnthropicCodeSuggesterTool()
        assert not tool.validate_inputs({"code": ["line1", "line2"]})

    def test_validate_inputs_code_is_none_returns_false(self) -> None:
        tool = AnthropicCodeSuggesterTool()
        assert not tool.validate_inputs({"code": None})

    @patch("plugins.anthropic_code_suggester.Anthropic")
    def test_execute_raises_value_error_for_non_string_code(self, mock_anthropic_class) -> None:
        """execute() raises ValueError when 'code' is not a string (invalid input)."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "fake_key"}):
            tool = AnthropicCodeSuggesterTool()
            with pytest.raises(ValueError):
                tool.execute({"code": 42})

    def test_metadata_tags_contains_anthropic(self) -> None:
        tool = AnthropicCodeSuggesterTool()
        assert "anthropic" in tool.metadata.tags

    def test_metadata_tags_contains_code_suggestions(self) -> None:
        tool = AnthropicCodeSuggesterTool()
        assert "code-suggestions" in tool.metadata.tags


if __name__ == "__main__":
    unittest.main()
