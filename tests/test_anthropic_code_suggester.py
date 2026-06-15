import os
import unittest
import unittest.mock
from unittest.mock import MagicMock, patch

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
            result = tool.execute({})
            assert result["status"] == "error"
            assert "Invalid input" in result["error"]

    @patch("plugins.anthropic_code_suggester.Anthropic")
    def test_execute_api_error(self, mock_anthropic_class) -> None:
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        mock_client.messages.create.side_effect = Exception("API error")

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "fake_key"}):
            tool = AnthropicCodeSuggesterTool()
            result = tool.execute({"code": "def foo(): pass"})

            assert result["status"] == "error"
            assert (
                result["error"]
                == "Anthropic code suggestion failed. See logs for details."
            )



    def test_init_no_api_key_client_is_none(self) -> None:
        """Missing API key must set client to None without raising."""
        import os
        env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
        with unittest.mock.patch.dict(os.environ, env, clear=True):
            tool = AnthropicCodeSuggesterTool()
            assert tool.client is None

    @patch("plugins.anthropic_code_suggester.Anthropic")
    def test_execute_no_client_returns_error(self, mock_anthropic_class) -> None:
        """When client is None (no API key), execute returns an error dict without calling API."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "fake_key"}):
            tool = AnthropicCodeSuggesterTool()
        tool.client = None  # force no-client state
        result = tool.execute({"code": "def foo(): pass"})
        assert result["status"] == "error"
        assert "ANTHROPIC_API_KEY" in result["error"] or "unavailable" in result["error"]
        mock_anthropic_class.return_value.messages.create.assert_not_called()

    @patch("plugins.anthropic_code_suggester.Anthropic")
    def test_execute_empty_content_returns_error(self, mock_anthropic_class) -> None:
        """Empty content list from API returns an error dict."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        mock_message = MagicMock()
        mock_message.content = []
        mock_client.messages.create.return_value = mock_message

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "fake_key"}):
            tool = AnthropicCodeSuggesterTool()
            result = tool.execute({"code": "def foo(): pass"})

        assert result["status"] == "error"
        assert "empty" in result["error"].lower() or "API" in result["error"]

    @patch("plugins.anthropic_code_suggester.Anthropic")
    def test_execute_response_without_text_attribute_returns_error(self, mock_anthropic_class) -> None:
        """Content block missing .text returns an error dict."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        mock_message = MagicMock()
        # Remove the 'text' attribute from the first content block
        del mock_message.content[0].text
        mock_client.messages.create.return_value = mock_message

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "fake_key"}):
            tool = AnthropicCodeSuggesterTool()
            result = tool.execute({"code": "def foo(): pass"})

        assert result["status"] == "error"

    @patch("plugins.anthropic_code_suggester.Anthropic", None)
    def test_init_package_unavailable_client_is_none(self) -> None:
        """When the anthropic package module-level variable is None, client stays None."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "fake_key"}):
            tool = AnthropicCodeSuggesterTool()
            assert tool.client is None


if __name__ == "__main__":
    unittest.main()
