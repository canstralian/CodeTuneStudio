import importlib
import importlib.util
import logging
import os
from typing import Any

from utils.plugins.base import AgentTool, ToolMetadata

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Anthropic = None
if importlib.util.find_spec("anthropic") is not None:
    Anthropic = importlib.import_module("anthropic").Anthropic


class AnthropicCodeSuggesterTool(AgentTool):
    """Tool for suggesting code improvements using Anthropic's Claude."""

    def __init__(self) -> None:
        super().__init__()
        self.metadata = ToolMetadata(
            name="anthropic_code_suggester",
            description="Suggests code improvements using Anthropic's Claude model",
            version="0.1.0",
            author="CodeTuneStudio",
            tags=["code-suggestions", "ai", "anthropic"],
        )
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            logger.warning(
                "ANTHROPIC_API_KEY not set. Anthropic code suggestions "
                "will not be available."
            )
            self.client = None
        elif Anthropic is None:
            logger.warning(
                "Anthropic package is not installed. Anthropic code suggestions are disabled."
            )
            self.client = None
        else:
            self.client = Anthropic(api_key=api_key)

    def validate_inputs(self, inputs: dict[str, Any]) -> bool:
        """Validate required inputs."""
        return isinstance(inputs.get("code"), str)

    def execute(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """
        Generate code suggestions using Anthropic.

        Args:
            inputs: Dictionary containing a ``code`` string to analyze.

        Returns:
            Dictionary containing suggested improvements or a standardized error.
        """
        if not self.validate_inputs(inputs):
            return {
                "error": "Invalid input. 'code' field is missing or not a string.",
                "status": "error",
            }

        if not self.client:
            return {
                "error": (
                    "ANTHROPIC_API_KEY not configured or Anthropic package unavailable. "
                    "Please configure the API key and dependency to use this tool."
                ),
                "status": "error",
            }

        try:
            message = self.client.messages.create(
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
                            f"{inputs['code']}"
                        ),
                    }
                ],
            )

            if not message.content or len(message.content) == 0:
                logger.error("Anthropic API returned empty content")
                return {"error": "API returned empty response", "status": "error"}

            if not hasattr(message.content[0], "text"):
                logger.error("Anthropic API response missing text attribute")
                return {"error": "Invalid API response format", "status": "error"}

            return {
                "suggestions": message.content[0].text,
                "model": "claude-3-5-sonnet-20241022",
                "status": "success",
            }

        except Exception:
            logger.exception("Anthropic code suggestion failed")
            return {
                "error": "Anthropic code suggestion failed. See logs for details.",
                "status": "error",
            }
