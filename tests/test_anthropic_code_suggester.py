import os
import unittest
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

from plugins.anthropic_code_suggester import AnthropicCodeSuggesterTool

if TYPE_CHECKING:
    from unittest.mock import Mock


class TestAnthropicCodeSuggesterTool(unittest.TestCase):
    @patch("plugins.anthropic_code_suggester.Anthropic")
    def test_init(self, mock_anthropic: "Mock") -> None:
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
    def test_execute_success(self, mock_anthropic_class: "Mock") -> None:
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        mock_message = MagicMock()
        # Mock the content structure - Anthropic returns list with text objects
        mock_content_block = MagicMock()
        mock_content_block.text = (
            '"code_structure": [], '
            '"optimization_opportunities": [], '
            '"best_practices": [], '
            '"error_handling": []}'
        )
        mock_message.content = [mock_content_block]
        mock_client.messages.create.return_value = mock_message

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "fake_key"}):
            tool = AnthropicCodeSuggesterTool()
            result = tool.execute({"code": "def foo(): pass"})

            assert result["status"] == "success"
            assert result["suggestions"].startswith("{")
            assert result["model"] == "claude-3-5-sonnet-20241022"
            # Verify the API was called with proper JSON mode parameters
            call_args = mock_client.messages.create.call_args
            assert call_args[1]["model"] == "claude-3-5-sonnet-20241022"
            assert call_args[1]["max_tokens"] == 4096
            assert "JSON" in call_args[1]["system"]
            # Verify assistant prefill for JSON mode
            assert any(
                msg.get("role") == "assistant"
                for msg in call_args[1]["messages"]
            )

    @patch("plugins.anthropic_code_suggester.Anthropic")
    def test_execute_invalid_inputs(self, _mock_anthropic_class: "Mock") -> None:
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "fake_key"}):
            tool = AnthropicCodeSuggesterTool()
            with self.assertRaises(ValueError):
                tool.execute({})

    @patch("plugins.anthropic_code_suggester.Anthropic")
    def test_execute_api_error(self, mock_anthropic_class: "Mock") -> None:
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        mock_client.messages.create.side_effect = Exception("API error")

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "fake_key"}):
            tool = AnthropicCodeSuggesterTool()
            result = tool.execute({"code": "def foo(): pass"})

            assert result["status"] == "error"
            assert "API error" in result["error"]


if __name__ == "__main__":
    unittest.main()
