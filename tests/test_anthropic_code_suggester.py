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


class TestAnthropicCodeSuggesterEdgeCases(unittest.TestCase):
    """Additional edge-case tests for the PR-changed behavior."""

    # ------------------------------------------------------------------
    # __init__: no API key
    # ------------------------------------------------------------------

    def test_init_no_api_key_sets_client_to_none(self) -> None:
        """When ANTHROPIC_API_KEY is absent, client must be None."""
        env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
        with patch.dict(os.environ, env, clear=True):
            tool = AnthropicCodeSuggesterTool()
            assert tool.client is None

    @patch("plugins.anthropic_code_suggester.Anthropic")
    def test_init_with_api_key_creates_client(self, mock_anthropic) -> None:
        """When ANTHROPIC_API_KEY is present, client is instantiated."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "real-looking-key"}):
            tool = AnthropicCodeSuggesterTool()
            assert tool.client is not None
            mock_anthropic.assert_called_once_with(api_key="real-looking-key")

    # ------------------------------------------------------------------
    # validate_inputs: edge cases
    # ------------------------------------------------------------------

    def test_validate_inputs_empty_string_is_valid(self) -> None:
        """An empty string is still a str, so validate_inputs returns True."""
        tool = AnthropicCodeSuggesterTool()
        assert tool.validate_inputs({"code": ""})

    def test_validate_inputs_none_code_returns_false(self) -> None:
        tool = AnthropicCodeSuggesterTool()
        assert not tool.validate_inputs({"code": None})

    def test_validate_inputs_list_code_returns_false(self) -> None:
        tool = AnthropicCodeSuggesterTool()
        assert not tool.validate_inputs({"code": ["print('hi')"]})

    def test_validate_inputs_extra_keys_allowed(self) -> None:
        """Extra keys beyond 'code' should not invalidate the input."""
        tool = AnthropicCodeSuggesterTool()
        assert tool.validate_inputs({"code": "x = 1", "language": "python"})

    def test_validate_inputs_returns_bool(self) -> None:
        tool = AnthropicCodeSuggesterTool()
        result = tool.validate_inputs({"code": "pass"})
        assert isinstance(result, bool)

    # ------------------------------------------------------------------
    # execute: no client (missing API key)
    # ------------------------------------------------------------------

    def test_execute_no_client_returns_error_dict(self) -> None:
        """When client is None, execute returns an error dict (not raises)."""
        env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
        with patch.dict(os.environ, env, clear=True):
            tool = AnthropicCodeSuggesterTool()
            assert tool.client is None
            result = tool.execute({"code": "def foo(): pass"})
            assert result["status"] == "error"
            assert "ANTHROPIC_API_KEY" in result["error"]

    def test_execute_no_client_does_not_raise(self) -> None:
        """execute with no client must return a dict, never raise."""
        env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
        with patch.dict(os.environ, env, clear=True):
            tool = AnthropicCodeSuggesterTool()
            try:
                result = tool.execute({"code": "x = 1"})
            except Exception as exc:
                self.fail(f"execute raised unexpectedly: {exc}")
            assert isinstance(result, dict)

    # ------------------------------------------------------------------
    # execute: invalid inputs (PR changed behaviour – now raises ValueError)
    # ------------------------------------------------------------------

    def test_execute_invalid_inputs_raises_value_error(self) -> None:
        """PR change: execute raises ValueError for invalid inputs."""
        tool = AnthropicCodeSuggesterTool()
        with pytest.raises(ValueError):
            tool.execute({"code": 999})

    def test_execute_missing_code_key_raises_value_error(self) -> None:
        tool = AnthropicCodeSuggesterTool()
        with pytest.raises(ValueError):
            tool.execute({"not_code": "x = 1"})

    # ------------------------------------------------------------------
    # execute: API response edge cases
    # ------------------------------------------------------------------

    @patch("plugins.anthropic_code_suggester.Anthropic")
    def test_execute_empty_content_returns_error(self, mock_anthropic_class) -> None:
        """Empty message.content should produce an error response."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        mock_message = MagicMock()
        mock_message.content = []
        mock_client.messages.create.return_value = mock_message

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "fake_key"}):
            tool = AnthropicCodeSuggesterTool()
            result = tool.execute({"code": "def foo(): pass"})
            assert result["status"] == "error"
            assert "empty" in result["error"].lower()

    @patch("plugins.anthropic_code_suggester.Anthropic")
    def test_execute_content_without_text_attr_returns_error(
        self, mock_anthropic_class
    ) -> None:
        """Content block without .text attribute should return an error response."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        mock_message = MagicMock()
        # Create a content block that explicitly lacks the 'text' attribute
        mock_block = MagicMock(spec=[])  # spec=[] means no attributes available
        mock_message.content = [mock_block]
        mock_client.messages.create.return_value = mock_message

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "fake_key"}):
            tool = AnthropicCodeSuggesterTool()
            result = tool.execute({"code": "def foo(): pass"})
            assert result["status"] == "error"

    @patch("plugins.anthropic_code_suggester.Anthropic")
    def test_execute_success_returns_correct_model_name(
        self, mock_anthropic_class
    ) -> None:
        """Successful execute must report the claude-3-5-sonnet model."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        mock_message = MagicMock()
        mock_block = MagicMock()
        mock_block.text = "Use type hints."
        mock_message.content = [mock_block]
        mock_client.messages.create.return_value = mock_message

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "fake_key"}):
            tool = AnthropicCodeSuggesterTool()
            result = tool.execute({"code": "x = 1"})
            assert result["model"] == "claude-3-5-sonnet-20241022"
            assert result["status"] == "success"

    @patch("plugins.anthropic_code_suggester.Anthropic")
    def test_execute_passes_code_in_prompt(self, mock_anthropic_class) -> None:
        """The user's code must appear verbatim in the API request content."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        mock_message = MagicMock()
        mock_block = MagicMock()
        mock_block.text = "suggestions"
        mock_message.content = [mock_block]
        mock_client.messages.create.return_value = mock_message

        code_snippet = "def complex_function(x, y):\n    return x ** y\n"
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "fake_key"}):
            tool = AnthropicCodeSuggesterTool()
            tool.execute({"code": code_snippet})

        call_kwargs = mock_client.messages.create.call_args
        sent_content = call_kwargs[1]["messages"][0]["content"]
        assert code_snippet in sent_content

    @patch("plugins.anthropic_code_suggester.Anthropic")
    def test_execute_uses_max_tokens_4096(self, mock_anthropic_class) -> None:
        """The API call must use max_tokens=4096."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        mock_message = MagicMock()
        mock_block = MagicMock()
        mock_block.text = "ok"
        mock_message.content = [mock_block]
        mock_client.messages.create.return_value = mock_message

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "fake_key"}):
            tool = AnthropicCodeSuggesterTool()
            tool.execute({"code": "pass"})

        call_kwargs = mock_client.messages.create.call_args
        assert call_kwargs[1]["max_tokens"] == 4096

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    def test_metadata_tags_list(self) -> None:
        tool = AnthropicCodeSuggesterTool()
        assert isinstance(tool.metadata.tags, list)
        assert "anthropic" in tool.metadata.tags

    def test_metadata_version_format(self) -> None:
        import re
        tool = AnthropicCodeSuggesterTool()
        assert re.match(r"^\d+\.\d+\.\d+$", tool.metadata.version)


if __name__ == "__main__":
    unittest.main()
