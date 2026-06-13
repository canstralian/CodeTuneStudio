import importlib
import importlib.util
import logging
import os
from typing import Any

from utils.plugins.base import AgentTool, ToolMetadata

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OpenAI = None
if importlib.util.find_spec("openai") is not None:
    OpenAI = importlib.import_module("openai").OpenAI


class OpenAICodeAnalyzerTool(AgentTool):
    """
    A tool for analyzing code using OpenAI's GPT models.

    This class extends AgentTool to provide code analysis capabilities
    powered by OpenAI's GPT models. It evaluates code for quality,
    improvements, performance, and security considerations.
    """

    def __init__(self) -> None:
        """
        Initialize tool metadata and configure the OpenAI client based on environment and dependency availability.
        
        Sets the tool's metadata (name, description, author, tags), reads the `OPENAI_API_KEY` environment variable, and assigns `self.client` as follows:
        - If `OPENAI_API_KEY` is present and the OpenAI package was imported successfully, `self.client` is initialized with `OpenAI(api_key=...)`.
        - If the API key is missing or the OpenAI package is unavailable, `self.client` is set to `None` and a warning is logged.
        """
        super().__init__()
        self.metadata = ToolMetadata(
            name="openai_code_analyzer",
            description=(
                "Analyzes code using OpenAI's models for improvements "
                "and suggestions"
            ),
            author="CodeTuneStudio",
            tags=["code-analysis", "ai", "openai"],
        )
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            logger.warning(
                "OPENAI_API_KEY not set. OpenAI code analysis will not be available."
            )
            self.client = None
        elif OpenAI is None:
            logger.warning(
                "OpenAI package is not installed. OpenAI code analysis is disabled."
            )
            self.client = None
        else:
            self.client = OpenAI(api_key=api_key)

    def validate_inputs(self, inputs: dict[str, Any]) -> bool:
        """
        Check that the inputs include a 'code' entry and that its value is a string.
        
        Parameters:
            inputs (dict[str, Any]): Input mapping expected to contain a 'code' key with source code.
        
        Returns:
            bool: `True` if `inputs` contains a `'code'` key whose value is a `str`, `False` otherwise.
        """
        return isinstance(inputs.get("code"), str)

    def execute(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """
        Perform static analysis of the provided source code using the configured OpenAI client and return the structured analysis.
        
        Parameters:
            inputs (dict[str, Any]): Input dictionary that must include a 'code' key with the source code string to analyze.
        
        Returns:
            dict[str, Any]: On success, a dictionary with keys:
                - "analysis": JSON-like analysis produced by the model,
                - "model": the model name ("gpt-4o"),
                - "status": "success".
            On failure, a standardized error dictionary with keys:
                - "error": human-readable error message,
                - "status": "error".
        """
        if not self.validate_inputs(inputs):
            return {
                "error": "Invalid input. 'code' field is missing or not a string.",
                "status": "error",
            }

        if not self.client:
            return {
                "error": (
                    "OPENAI_API_KEY not configured or OpenAI package unavailable. "
                    "Please configure the API key and dependency to use this tool."
                ),
                "status": "error",
            }

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert code analyzer. Analyze the "
                            "given code and provide insights about:\n"
                            "1. Code quality\n"
                            "2. Potential improvements\n"
                            "3. Performance considerations\n"
                            "4. Security considerations\n"
                            "Provide the analysis in JSON format."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"Analyze this code:\n\n{inputs['code']}",
                    },
                ],
                response_format={"type": "json_object"},
            )

            if (
                response.choices
                and isinstance(response.choices, list)
                and len(response.choices) > 0
                and response.choices[0].message
                and response.choices[0].message.content
            ):
                analysis_content = response.choices[0].message.content
                return {
                    "analysis": analysis_content,
                    "model": "gpt-4o",
                    "status": "success",
                }
            logger.error("OpenAI API response missing expected content.")
            return {
                "error": "OpenAI API response missing expected content.",
                "status": "error",
            }
        except Exception:
            logger.exception("OpenAI code analysis failed")
            return {
                "error": "OpenAI code analysis failed. See logs for details.",
                "status": "error",
            }
