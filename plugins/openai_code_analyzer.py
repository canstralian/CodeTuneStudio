import logging
import os
from typing import Any, Dict

from openai import OpenAI

from utils.plugins.base import AgentTool, ToolMetadata

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OpenAICodeAnalyzerTool(AgentTool):
    """
    A tool for analyzing code using OpenAI's GPT models.

    This class extends AgentTool to provide code analysis capabilities powered by OpenAI's
    GPT models. It leverages the latest available model (e.g., GPT-4o) to evaluate code
    for quality, improvements, performance, and security considerations.

    Attributes:
        metadata (ToolMetadata): Metadata describing the tool, including name, description,
            version, author, and tags.
        client (OpenAI): An instance of the OpenAI client initialized with the API key
            from environment variables.

    Methods:
        __init__(): Initializes the tool, sets up metadata, and creates the OpenAI client.
        validate_inputs(inputs: Dict[str, Any]) -> bool:
            Validates the input dictionary to ensure it contains a 'code' key with a string value.
        execute(inputs: Dict[str, Any]) -> Dict[str, Any]:
            Executes the code analysis using OpenAI's API.
    """

    def __init__(self) -> None:
        super().__init__()
        self.metadata = ToolMetadata(
            name="openai_code_analyzer",
            description="Analyzes code using OpenAI's models for improvements and suggestions",
            author="CodeTuneStudio",
            tags=["code-analysis", "ai", "openai"],
        )
        # Initialize OpenAI client
        # Ensure the API key is set
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            msg = "The environment variable 'OPENAI_API_KEY' is not set. Please set it to your OpenAI API key."
            raise OSError(msg)
        # Initialize OpenAI client
        self.client = OpenAI(api_key=api_key)

    def validate_inputs(self, inputs: dict[str, Any]) -> bool:
        """Validate required inputs"""
        if "code" not in inputs:
            return False
        return isinstance(inputs["code"], str)

    def execute(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """
        Analyze code using OpenAI

        Args:
            inputs: Dictionary containing:
                - code: String containing code to analyze

        Returns:
            Dictionary containing analysis results
        """
        if not self.validate_inputs(inputs):
            return {
                "error": "Invalid input. 'code' field is missing or not a string.",
                "status": "error",
            }

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert code analyzer. Analyze the given code and provide insights about:\n"
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

            # Validate response structure before accessing
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
        except Exception as e:
            logger.exception(f"OpenAI code analysis failed: {e!s}")
            return {"error": str(e), "status": "error"}
