import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Mock the anthropic module before importing the tool
sys.modules['anthropic'] = MagicMock()

# Add parent directory to path to import plugins
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from plugins.anthropic_code_suggester import AnthropicCodeSuggesterTool


class TestAnthropicCodeSuggesterTool(unittest.TestCase):
    @patch("anthropic.Anthropic")
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

    @patch("anthropic.Anthropic")
    def test_execute_success(self, mock_anthropic_class) -> None:
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        mock_message = MagicMock()
        # Mock the content as a list with a text block (matching Anthropic API structure)
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
                messages=[
                    {
                        "role": "user",
                        "content": """Analyze this code and suggest improvements in JSON format.
                    Include specific recommendations for:
                    1. Code structure
                    2. Optimization opportunities
                    3. Best practices
                    4. Error handling

                    Code to analyze:
                    def foo(): pass
                    """,
                    }
                ],
            )

    @patch("anthropic.Anthropic")
    def test_execute_invalid_inputs(self, mock_anthropic_class) -> None:
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "fake_key"}):
            tool = AnthropicCodeSuggesterTool()
            with self.assertRaises(ValueError):
                tool.execute({})

    @patch("anthropic.Anthropic")
    def test_execute_api_error(self, mock_anthropic_class) -> None:
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        mock_client.messages.create.side_effect = Exception("API error")

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "fake_key"}):
            tool = AnthropicCodeSuggesterTool()
            result = tool.execute({"code": "def foo(): pass"})

            assert result["status"] == "error"
            assert "API error" in result["error"]

    @patch("anthropic.Anthropic")
    def test_execute_empty_content(self, mock_anthropic_class) -> None:
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        mock_message = MagicMock()
        # Mock empty content list
        mock_message.content = []
        mock_client.messages.create.return_value = mock_message

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "fake_key"}):
            tool = AnthropicCodeSuggesterTool()
            result = tool.execute({"code": "def foo(): pass"})

            assert result["status"] == "error"
            assert "missing expected content" in result["error"]


if __name__ == "__main__":
    unittest.main()
