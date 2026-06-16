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


    def test_execute_no_client_returns_error(self) -> None:
        """When ANTHROPIC_API_KEY is missing, execute returns an error dict."""
        with patch.dict(os.environ, {}, clear=True):
            # Ensure the env var is not set
            os.environ.pop("ANTHROPIC_API_KEY", None)
            tool = AnthropicCodeSuggesterTool()
            assert tool.client is None
            result = tool.execute({"code": "def foo(): pass"})
            assert result["status"] == "error"
            assert "ANTHROPIC_API_KEY" in result["error"]

    @patch("plugins.anthropic_code_suggester.Anthropic")
    def test_execute_empty_content_returns_error(self, mock_anthropic_class) -> None:
        """When the API returns empty content, execute returns an error dict."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        mock_message = MagicMock()
        mock_message.content = []  # empty content list
        mock_client.messages.create.return_value = mock_message

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "fake_key"}):
            tool = AnthropicCodeSuggesterTool()
            result = tool.execute({"code": "def foo(): pass"})
            assert result["status"] == "error"
            assert "empty" in result["error"].lower()

    @patch("plugins.anthropic_code_suggester.Anthropic")
    def test_execute_missing_text_attr_returns_error(
        self, mock_anthropic_class
    ) -> None:
        """When API response content block has no 'text' attr, execute returns error."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        mock_message = MagicMock()
        # content block without a 'text' attribute
        content_block = MagicMock(spec=[])  # empty spec -> no attributes
        mock_message.content = [content_block]
        mock_client.messages.create.return_value = mock_message

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "fake_key"}):
            tool = AnthropicCodeSuggesterTool()
            result = tool.execute({"code": "def foo(): pass"})
            assert result["status"] == "error"
            assert "Invalid" in result["error"] or "format" in result["error"].lower()

    @patch("plugins.anthropic_code_suggester.Anthropic")
    def test_execute_invalid_code_type_raises_value_error(
        self, mock_anthropic_class
    ) -> None:
        """execute raises ValueError when 'code' value is not a string."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "fake_key"}):
            tool = AnthropicCodeSuggesterTool()
            with self.assertRaises(ValueError):
                tool.execute({"code": 42})

    def test_validate_inputs_empty_string_code(self) -> None:
        """validate_inputs returns True for empty string — it is still a string."""
        tool = AnthropicCodeSuggesterTool()
        assert tool.validate_inputs({"code": ""})

    def test_str_representation(self) -> None:
        """__str__ returns name and version."""
        tool = AnthropicCodeSuggesterTool()
        result = str(tool)
        assert "anthropic_code_suggester" in result
        assert "0.1.0" in result


if __name__ == "__main__":
    unittest.main()
