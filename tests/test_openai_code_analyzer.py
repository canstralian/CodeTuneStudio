import os
import unittest
from unittest.mock import MagicMock, patch

from plugins.openai_code_analyzer import OpenAICodeAnalyzerTool


class TestOpenAICodeAnalyzerTool(unittest.TestCase):
    """
    Unit tests for the OpenAICodeAnalyzerTool class.
    """

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_api_key"})
    def setUp(self) -> None:
        """
        Set up the test environment before each test.
        """
        self.tool = OpenAICodeAnalyzerTool()

    @patch.dict(os.environ, {}, clear=True)
    def test_init_missing_api_key(self) -> None:
        """
        Test that a missing OPENAI_API_KEY disables the client without raising.
        """
        tool = OpenAICodeAnalyzerTool()
        assert tool.client is None

    def test_validate_inputs(self) -> None:
        """
        Test the validate_inputs method with various inputs.
        """
        assert self.tool.validate_inputs({"code": "print('hello')"})
        assert not self.tool.validate_inputs({})
        assert not self.tool.validate_inputs({"code": 123})
        assert not self.tool.validate_inputs({"not_code": "print('hello')"})

    @patch("plugins.openai_code_analyzer.OpenAI")
    def test_execute_success(self, mock_openai) -> None:
        """
        Test the execute method with a successful API call.
        """
        # Mock the OpenAI client and its response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"quality": "good"}'
        mock_client.chat.completions.create.return_value = mock_response

        # Temporarily replace the client instance with the mock
        with patch.object(self.tool, "client", mock_client):
            result = self.tool.execute({"code": "print('hello')"})

            assert result["status"] == "success"
            assert result["analysis"] == '{"quality": "good"}'
            assert result["model"] == "gpt-4o"
            mock_client.chat.completions.create.assert_called_once()

    def test_execute_invalid_input(self) -> None:
        """
        Test the execute method with invalid inputs.
        """
        with patch.object(self.tool, "client") as mock_client:
            result = self.tool.execute({"wrong_input": "some_code"})
            assert result["status"] == "error"
            assert "Invalid input" in result["error"]
            mock_client.chat.completions.create.assert_not_called()

    @patch("plugins.openai_code_analyzer.OpenAI")
    def test_execute_api_exception(self, mock_openai) -> None:
        """
        Test the execute method when the OpenAI API call raises an exception.
        """
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        with patch.object(self.tool, "client", mock_client):
            result = self.tool.execute({"code": "print('hello')"})
            assert result["status"] == "error"
            assert (
                result["error"] == "OpenAI code analysis failed. See logs for details."
            )

    @patch("plugins.openai_code_analyzer.OpenAI")
    def test_execute_malformed_response(self, mock_openai) -> None:
        """
        Test the execute method with a malformed response from the OpenAI API.
        """
        mock_client = MagicMock()
        mock_response = MagicMock()
        # Simulate a response that doesn't have the expected structure
        mock_response.choices = []
        mock_client.chat.completions.create.return_value = mock_response

        with patch.object(self.tool, "client", mock_client):
            result = self.tool.execute({"code": "print('hello')"})
            assert result["status"] == "error"
            assert result["error"] == "OpenAI API response missing expected content."


    def test_execute_no_client_returns_error(self) -> None:
        """When client is None (no API key / package unavailable), execute returns an error dict."""
        import os
        env = {k: v for k, v in os.environ.items() if k != "OPENAI_API_KEY"}
        with patch.dict(os.environ, env, clear=True):
            tool = OpenAICodeAnalyzerTool()
        assert tool.client is None
        result = tool.execute({"code": "print('hello')"})
        assert result["status"] == "error"
        assert "OPENAI_API_KEY" in result["error"] or "unavailable" in result["error"]

    @patch("plugins.openai_code_analyzer.OpenAI", None)
    def test_init_package_unavailable_client_is_none(self) -> None:
        """When the openai package module-level variable is None, client stays None."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "fake_key"}):
            tool = OpenAICodeAnalyzerTool()
            assert tool.client is None

    def test_execute_none_code_returns_error(self) -> None:
        """None as code value returns error dict without calling API."""
        with patch.object(self.tool, "client") as mock_client:
            result = self.tool.execute({"code": None})
            assert result["status"] == "error"
            mock_client.chat.completions.create.assert_not_called()


if __name__ == "__main__":
    unittest.main()
