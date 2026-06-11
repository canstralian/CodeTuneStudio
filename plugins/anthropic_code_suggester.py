import logging
import os
from typing import Any

try:
    from anthropic import Anthropic
except ImportError:  # pragma: no cover - optional dependency fallback
    class Anthropic:  # type: ignore[no-redef]
        def __init__(self, api_key: str) -> None:
            self.api_key = api_key
            msg = "anthropic package is not installed"
            raise ImportError(msg)

from utils.plugins.base import AgentTool, ToolMetadata

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnthropicCodeSuggesterTool(AgentTool):
    """Tool for suggesting code improvements using Anthropic's Claude."""

    def __init__(self) -> None:
        super().__init__()
        self.metadata = ToolMetadata(
            name="anthropic_code_suggester",
            description="Suggests code improvements using Anthropic's Claude model",
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
        else:
            self.client = Anthropic(api_key=api_key)

    def validate_inputs(self, inputs: dict[str, Any]) -> bool:
        """Validate required inputs."""
        return "code" in inputs and isinstance(inputs["code"], str)

    def execute(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """Generate code suggestions using Anthropic."""
        if not self.validate_inputs(inputs):
            msg = "Input validation failed: 'code' must be a string"
            raise ValueError(msg)

        if not self.client:
            return {
                "error": (
                    "ANTHROPIC_API_KEY not configured. Please set the "
                    "API key to use this tool."
                ),
                "status": "error",
            }

        try:
            model = "claude-3-5-sonnet-20241022"
            message = self.client.messages.create(
                model=model,
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

            if not message.content:
                logger.error("Anthropic API returned empty content")
                return {"error": "API returned empty response", "status": "error"}

            if not hasattr(message.content[0], "text"):
                logger.error("Anthropic API response missing text attribute")
                return {"error": "Invalid API response format", "status": "error"}

            return {
                "suggestions": message.content[0].text,
                "model": model,
                "status": "success",
            }
        except Exception as e:
            logger.exception("Anthropic code suggestion failed")
            return {"error": str(e), "status": "error"}
