import os
import time
from typing import Any, Optional

from openai import OpenAI, OpenAIError

from config.logging_config import get_logger
from utils.plugins.base import AgentTool, ToolMetadata

# Use centralized logging
logger = get_logger(__name__)


class OpenAICodeAnalyzerTool(AgentTool):
    """
    A tool for analyzing code using OpenAI's GPT models.

    This class extends AgentTool to provide code analysis capabilities
    powered by OpenAI's GPT models. It leverages the latest available
    model (e.g., GPT-4o) to evaluate code for quality, improvements,
    performance, and security considerations.

    The implementation ensures that API payloads are constructed properly
    with no duplicate parameters, particularly for the temperature setting.

    Attributes:
        metadata (ToolMetadata): Metadata describing the tool, including
            name, description, version, author, and tags.
        client (OpenAI): An instance of the OpenAI client initialized
            with the API key from environment variables.
        temperature (float): Temperature setting for API calls, loaded
            from OPENAI_TEMPERATURE environment variable (default: 0.7).
        model_name (str): Model to use for API calls, loaded from
            OPENAI_MODEL environment variable (default: "gpt-4o").

    Methods:
        __init__(): Initializes the tool, sets up metadata, and creates
            the OpenAI client.
        init(): Initialize the OpenAI client with API key.
        teardown(): Clean up resources.
        validate_inputs(inputs: Dict[str, Any]) -> bool:
            Validates the input dictionary to ensure it contains a
            'code' key with a string value.
        _build_api_payload(code: str) -> Dict[str, Any]:
            Constructs the API payload ensuring no duplicate parameters.
        _make_api_call_with_retry(code: str) -> Dict[str, Any]:
            Makes API calls with retry logic and exponential backoff.
        execute(inputs: Dict[str, Any]) -> Dict[str, Any]:
            Executes the code analysis using OpenAI's API.
    """

    def __init__(self) -> None:
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
        # Rate limiting configuration
        self.max_retries = int(os.environ.get("OPENAI_MAX_RETRIES", "3"))
        self.retry_delay = float(os.environ.get("OPENAI_RETRY_DELAY", "1.0"))
        self.rate_limit_delay = float(os.environ.get("OPENAI_RATE_LIMIT_DELAY", "0.5"))
        self.last_request_time: float = 0.0

        # Model configuration
        self.model_name = os.environ.get("OPENAI_MODEL", "gpt-4o")
        self.temperature = float(os.environ.get("OPENAI_TEMPERATURE", "0.7"))

        # Initialize OpenAI client
        self.client: Optional[OpenAI] = None
        self._api_key = os.environ.get("OPENAI_API_KEY")

    def init(self) -> None:
        """
        Initialize the OpenAI client.

        Raises:
            OSError: If OPENAI_API_KEY is not set
        """
        if not self._api_key:
            msg = (
                "The environment variable 'OPENAI_API_KEY' is not set. "
                "Please set it to your OpenAI API key."
            )
            raise OSError(msg)

        self.client = OpenAI(api_key=self._api_key)
        super().init()
        logger.info("OpenAI Code Analyzer initialized")

    def teardown(self) -> None:
        """Clean up resources."""
        self.client = None
        super().teardown()
        logger.info("OpenAI Code Analyzer teardown complete")

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

    def _build_api_payload(self, code: str) -> dict[str, Any]:
        """
        Build the API payload for OpenAI chat completion.

        This method ensures that all parameters are explicitly set once
        and only once, preventing any duplicate parameter issues.

        Args:
            code: Code to analyze

        Returns:
            Dictionary containing the API payload with:
                - model: Model name
                - temperature: Temperature setting (set only once)
                - messages: List of message dictionaries
        """
        payload = {
            "model": self.model_name,
            "temperature": self.temperature,
            "messages": [
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
                {"role": "user", "content": f"Analyze this code:\n\n{code}"},
            ],
        }

        # Log payload for debugging (without the code content for brevity)
        logger.debug(
            f"API payload constructed: model={payload['model']}, "
            f"temperature={payload['temperature']}"
        )

        return payload

    def _make_api_call_with_retry(self, code: str) -> dict[str, Any]:
        """
        Make API call with retry logic.

        Args:
            code: Code to analyze

        Returns:
            API response dictionary

        Raises:
            OpenAIError: If all retry attempts fail
        """
        if not self.client:
            raise RuntimeError("Client not initialized. Call init() first.")

        last_error = None

        for attempt in range(self.max_retries):
            try:
                self._apply_rate_limiting()

                # Build payload using explicit method to ensure no duplicates
                payload = self._build_api_payload(code)

                # Use **payload to unpack the dictionary
                response = self.client.chat.completions.create(**payload)

                return {
                    "analysis": response.choices[0].message.content,
                    "model": response.model,
                    "status": "success",
                }

            except OpenAIError as e:
                last_error = e
                logger.warning(
                    f"API call attempt {attempt + 1}/{self.max_retries} failed: {e}"
                )

                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    delay = self.retry_delay * (2**attempt)
                    logger.info(f"Retrying in {delay:.2f}s...")
                    time.sleep(delay)

        # All retries failed
        raise last_error

    def execute(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """
        Analyze code using OpenAI with retry logic and rate limiting.

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
            return self._make_api_call_with_retry(inputs["code"])
        except OpenAIError as e:
            logger.error(f"OpenAI code analysis failed: {e!s}")
            return {
                "error": f"API error: {e!s}",
                "status": "error",
            }
        except Exception as e:
            logger.exception(f"Unexpected error in code analysis: {e!s}")
            return {
                "error": f"Unexpected error: {e!s}",
                "status": "error",
            }
