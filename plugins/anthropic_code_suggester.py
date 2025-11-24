import os
import time
from typing import Any, Optional

from anthropic import Anthropic, APIError

from config.logging_config import get_logger
from utils.plugins.base import AgentTool, ToolMetadata

# Use centralized logging
logger = get_logger(__name__)


class AnthropicCodeSuggesterTool(AgentTool):
    """Tool for suggesting code improvements using Anthropic's Claude

    A tool for generating code improvement suggestions using Anthropic's
    Claude AI model. This class extends AgentTool to provide AI-powered
    code analysis and suggestions. It leverages Anthropic's Claude model
    to evaluate provided code snippets and offer recommendations on
    structure, optimization, best practices, and error handling.

    Attributes:
        metadata (ToolMetadata): Metadata describing the tool, including
            name, description, version, author, and tags.
        client (Anthropic): The Anthropic client instance used for API
            interactions.

    Methods:
        validate_inputs(inputs: Dict[str, Any]) -> bool:
            Validates the input dictionary to ensure it contains a valid
            'code' key with a string value.
        execute(inputs: Dict[str, Any]) -> Dict[str, Any]:
            Executes the code suggestion process by sending the code to
            Claude for analysis and returning the suggestions in a
            structured response.
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
        # Rate limiting configuration
        self.max_retries = int(os.environ.get("ANTHROPIC_MAX_RETRIES", "3"))
        self.retry_delay = float(os.environ.get("ANTHROPIC_RETRY_DELAY", "1.0"))
        self.rate_limit_delay = float(
            os.environ.get("ANTHROPIC_RATE_LIMIT_DELAY", "0.5")
        )
        self.last_request_time: float = 0.0

        # Initialize Anthropic client
        self.client: Optional[Anthropic] = None
        self._api_key = os.environ.get("ANTHROPIC_API_KEY")

    def init(self) -> None:
        """
        Initialize the Anthropic client.

        Raises:
            OSError: If ANTHROPIC_API_KEY is not set
        """
        if not self._api_key:
            msg = (
                "ANTHROPIC_API_KEY not set. Anthropic code suggestions "
                "will not be available."
            )
            logger.warning(msg)
            raise OSError(msg)

        self.client = Anthropic(api_key=self._api_key)
        super().init()
        logger.info("Anthropic Code Suggester initialized")

    def teardown(self) -> None:
        """Clean up resources."""
        self.client = None
        super().teardown()
        logger.info("Anthropic Code Suggester teardown complete")

    def validate_inputs(self, inputs: dict[str, Any]) -> bool:
        """Validate required inputs"""
        if "code" not in inputs:
            return False
        return isinstance(inputs["code"], str)

    def _apply_rate_limiting(self) -> None:
        """Apply rate limiting to avoid exceeding API limits."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last_request
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def _make_api_call_with_retry(
        self, code: str
    ) -> dict[str, Any]:
        """
        Make API call with retry logic.

        Args:
            code: Code to analyze

        Returns:
            API response dictionary

        Raises:
            APIError: If all retry attempts fail
        """
        if not self.client:
            raise RuntimeError("Client not initialized. Call init() first.")

        last_error = None

        for attempt in range(self.max_retries):
            try:
                self._apply_rate_limiting()

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
                                f"{code}"
                            ),
                        }
                    ],
                )

                # Validate response structure
                if not message.content or len(message.content) == 0:
                    logger.error("Anthropic API returned empty content")
                    return {"error": "API returned empty response", "status": "error"}

                # Extract text content
                suggestions = message.content[0].text
                return {
                    "suggestions": suggestions,
                    "model": message.model,
                    "status": "success",
                }

            except APIError as e:
                last_error = e
                logger.warning(
                    f"API call attempt {attempt + 1}/{self.max_retries} failed: {e}"
                )

                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    delay = self.retry_delay * (2 ** attempt)
                    logger.info(f"Retrying in {delay:.2f}s...")
                    time.sleep(delay)

        # All retries failed
        raise last_error

    def execute(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """
        Generate code suggestions using Anthropic with retry logic and rate limiting.

        Args:
            inputs: Dictionary containing:
                - code: String containing code to analyze

        Returns:
            Dictionary containing suggested improvements
        """
        if not self.validate_inputs(inputs):
            return {
                "error": "Invalid input. 'code' field is missing or not a string.",
                "status": "error",
            }

        if not self.client:
            return {
                "error": (
                    "ANTHROPIC_API_KEY not configured. Please set the "
                    "API key to use this tool."
                ),
                "status": "error",
            }

        try:
            return self._make_api_call_with_retry(inputs["code"])
        except APIError as e:
            logger.error(f"Anthropic code suggestion failed: {e!s}")
            return {
                "error": f"API error: {e!s}",
                "status": "error",
            }
        except Exception as e:
            logger.exception(f"Unexpected error in code suggestion: {e!s}")
            return {
                "error": f"Unexpected error: {e!s}",
                "status": "error",
            }
