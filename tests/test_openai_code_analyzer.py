import os
import unittest
from unittest.mock import MagicMock, patch

import pytest

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

    def test_validate_inputs(self) -> None:
        """
        Test the validate_inputs method with various inputs.
        """
        assert self.tool.validate_inputs({"code": "print('hello')"})
        assert not self.tool.validate_inputs({})
        assert not self.tool.validate_inputs({"code": 123})
        assert not self.tool.validate_inputs({"not_code": "print('hello')"})

    def test_execute_invalid_input(self) -> None:
        """
        Test the execute method with invalid inputs.
        """
        result = self.tool.execute({"wrong_input": "some_code"})
        assert result["status"] == "error"
        assert "Invalid input" in result["error"]

    @patch("openai.OpenAI")
    def test_execute_api_exception(self, mock_openai) -> None:
        """
        Test the execute method when the OpenAI API call raises an exception.
        """
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        with patch.object(self.tool, "client", mock_client):
            result = self.tool.execute({"code": "print('hello')"})
            assert result["status"] == "error"
            assert "API Error" in result["error"]

    @patch("openai.OpenAI")
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
            assert "error" in result

    @patch("openai.OpenAI")
    def test_execute_success(self, mock_openai) -> None:
        """
        Test the execute method with a successful API call.
        """
        # Mock the OpenAI client and its response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.model = "gpt-4o"
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

    def test_payload_construction_temperature_uniqueness(self) -> None:
        """
        Test that the API payload contains temperature only once.
        This test ensures no duplicate temperature arguments.
        """
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.model = "gpt-4o"
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "analysis result"
        mock_client.chat.completions.create.return_value = mock_response

        with patch.object(self.tool, "client", mock_client):
            self.tool.execute({"code": "print('test')"})

            # Get the call arguments
            call_args = mock_client.chat.completions.create.call_args

            # Check kwargs for temperature
            if call_args.kwargs:
                temp_count = list(call_args.kwargs.keys()).count("temperature")
                assert (
                    temp_count <= 1
                ), f"Temperature appears {temp_count} times in kwargs"

            # Verify temperature is set
            assert "temperature" in call_args.kwargs
            assert call_args.kwargs["temperature"] == self.tool.temperature

    def test_payload_construction_with_custom_temperature(self) -> None:
        """
        Test that custom temperature from environment is properly used.
        """
        with patch.dict(
            os.environ, {"OPENAI_API_KEY": "test_key", "OPENAI_TEMPERATURE": "0.3"}
        ):
            tool = OpenAICodeAnalyzerTool()
            assert tool.temperature == 0.3

            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.model = "gpt-4o"
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "result"
            mock_client.chat.completions.create.return_value = mock_response

            with patch.object(tool, "client", mock_client):
                tool.execute({"code": "test"})

                call_args = mock_client.chat.completions.create.call_args
                assert call_args.kwargs["temperature"] == 0.3

    def test_payload_serialization(self) -> None:
        """
        Test that the payload can be properly serialized to JSON.
        """
        import json

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.model = "gpt-4o"
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "result"
        mock_client.chat.completions.create.return_value = mock_response

        with patch.object(self.tool, "client", mock_client):
            self.tool.execute({"code": "test_code"})

            # Get the call arguments
            call_args = mock_client.chat.completions.create.call_args

            # Try to serialize the payload to JSON (this would fail with duplicates)
            try:
                payload_dict = {
                    "model": call_args.kwargs.get("model"),
                    "temperature": call_args.kwargs.get("temperature"),
                    "messages": call_args.kwargs.get("messages"),
                }
                json_str = json.dumps(payload_dict)

                # Verify we can parse it back
                parsed = json.loads(json_str)
                assert "temperature" in parsed
                assert parsed["temperature"] == self.tool.temperature
            except (TypeError, ValueError) as e:
                pytest.fail(f"Payload serialization failed: {e}")

    def test_build_api_payload_method(self) -> None:
        """
        Test the _build_api_payload method directly.
        Ensures payload is constructed correctly with temperature set only once.
        """
        test_code = "def hello(): print('world')"
        payload = self.tool._build_api_payload(test_code)

        # Verify all required keys are present
        assert "model" in payload
        assert "temperature" in payload
        assert "messages" in payload

        # Verify temperature is set correctly
        assert payload["temperature"] == self.tool.temperature

        # Verify model is set correctly
        assert payload["model"] == self.tool.model_name

        # Verify messages structure
        assert isinstance(payload["messages"], list)
        assert len(payload["messages"]) == 2
        assert payload["messages"][0]["role"] == "system"
        assert payload["messages"][1]["role"] == "user"
        assert test_code in payload["messages"][1]["content"]

        # Count occurrences of 'temperature' key in payload
        temp_count = list(payload.keys()).count("temperature")
        assert (
            temp_count == 1
        ), f"Temperature key appears {temp_count} times, expected 1"

    @patch.dict(os.environ, {}, clear=True)
    def test_init_missing_api_key(self) -> None:
        """
        Test that init() raises OSError if the OPENAI_API_KEY is not set.
        """
        tool = OpenAICodeAnalyzerTool()
        with pytest.raises(OSError):
            tool.init()


if __name__ == "__main__":
    unittest.main()
