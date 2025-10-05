import logging
import os
from typing import Any, Dict

from anthropic import Anthropic

from utils.plugins.base import AgentTool, ToolMetadata

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnthropicCodeSuggesterTool(AgentTool):
    """Tool for suggesting code improvements using Anthropic's Claude

    A tool for generating code improvement suggestions using Anthropic's Claude AI model.
    This class extends AgentTool to provide AI-powered code analysis and suggestions. It leverages
    Anthropic's Claude model to evaluate provided code snippets and offer recommendations on structure,
    optimization, best practices, and error handling.
    Attributes:
        metadata (ToolMetadata): Metadata describing the tool, including name, description, version,
            author, and tags.
        client (Anthropic): The Anthropic client instance used for API interactions.
    Methods:
        validate_inputs(inputs: Dict[str, Any]) -> bool:
            Validates the input dictionary to ensure it contains a valid 'code' key with a string value.
        execute(inputs: Dict[str, Any]) -> Dict[str, Any]:
            Executes the code suggestion process by sending the code to Claude for analysis and
            returning the suggestions in a structured response.
    Note:
        Requires an ANTHROPIC_API_KEY environment variable to be set for authentication.
        The tool uses the 'claude-3-5-sonnet-20241022' model for generating suggestions.
    Example:
        >>> tool = AnthropicCodeSuggesterTool()
        >>> result = tool.execute({"code": "def hello(): print('Hello')"})
        >>> print(result["suggestions"])
    """

    def __init__(self) -> None:
        super().__init__()
        self.metadata = ToolMetadata(
            name="anthropic_code_suggester",
            description="Suggests code improvements using Anthropic's Claude model",
            version="0.1.0",
            author="CodeTuneStudio",
            tags=["code-suggestions", "ai", "anthropic"],
        )
        # Initialize Anthropic client with validation
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            logger.warning(
                "ANTHROPIC_API_KEY not set. Anthropic code suggestions "
                "will not be available."
            )
            self.client = None
        else:
            self.client = Anthropic(api_key=api_key)

    def validate_inputs(self, inputs: dict[str, Any]) -> bool:
        """Validate required inputs"""
        if "code" not in inputs:
            return False
        return isinstance(inputs["code"], str)

    def execute(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """
        Generate code suggestions using Anthropic

        Args:
            inputs: Dictionary containing:
                - code: String containing code to analyze

        Returns:
            Dictionary containing suggested improvements
        """
        if not self.validate_inputs(inputs):
            msg = "Invalid inputs"
            raise ValueError(msg)

        if not self.client:
            return {
                "error": (
                    "ANTHROPIC_API_KEY not configured. Please set the "
                    "API key to use this tool."
                ),
                "status": "error"
            }

        try:
            # the newest Anthropic model is "claude-3-5-sonnet-20241022"
            # which was released October 22, 2024
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                messages=[
                    {
                        "role": "user",
                        "content": f"""Analyze this code and suggest improvements in JSON format.
                    Include specific recommendations for:
                    1. Code structure
                    2. Optimization opportunities
                    3. Best practices
                    4. Error handling

                    Code to analyze:
                    {inputs["code"]}
                    """,
                    }
                ],
            )

            return {
                "suggestions": message.content[0].text,
                "model": "claude-3-5-sonnet-20241022",
                "status": "success",
            }

        except Exception as e:
            logger.exception(f"Anthropic code suggestion failed: {e!s}")
            return {"error": str(e), "status": "error"}
