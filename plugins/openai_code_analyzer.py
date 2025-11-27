import logging
import os
import time
from functools import wraps
from typing import Any, Callable

from openai import OpenAI, RateLimitError, APIError

from utils.plugins.base import AgentTool, ToolMetadata

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def retry_with_exponential_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
) -> Callable:
    """
    Decorator for retrying function calls with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        exponential_base: Base for exponential backoff calculation

    Returns:
        Decorated function with retry logic
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            delay = base_delay

            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except (RateLimitError, APIError) as e:
                    retries += 1
                    if retries >= max_retries:
                        logger.error(
                            f"Max retries ({max_retries}) reached for {func.__name__}"
                        )
                        raise

                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (exponential_base**retries), max_delay)
                    logger.warning(
                        f"API error in {func.__name__}: {e}. "
                        f"Retrying in {delay:.2f}s (attempt {retries}/{max_retries})"
                    )
                    time.sleep(delay)

            return func(*args, **kwargs)

        return wrapper

    return decorator


class OpenAICodeAnalyzerTool(AgentTool):
    """
    A tool for analyzing code using OpenAI's GPT models.

    This class extends AgentTool to provide code analysis capabilities
    powered by OpenAI's GPT models. It leverages the latest available
    model (e.g., GPT-4o) to evaluate code for quality, improvements,
    performance, and security considerations.

    Attributes:
        metadata (ToolMetadata): Metadata describing the tool, including
            name, description, version, author, and tags.
        client (OpenAI): An instance of the OpenAI client initialized
            with the API key from environment variables.

    Methods:
        __init__(): Initializes the tool, sets up metadata, and creates
            the OpenAI client.
        validate_inputs(inputs: Dict[str, Any]) -> bool:
            Validates the input dictionary to ensure it contains a
            'code' key with a string value.
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
        self.client = None
        self._last_request_time = 0
        self._min_request_interval = 1.0  # Minimum 1 second between requests

    def init(self) -> None:
        """
        Initialize the OpenAI client with validation and rate limiting.

        Raises:
            OSError: If OPENAI_API_KEY is not set
        """
        if self._initialized:
            return

        # Ensure the API key is set
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            msg = (
                "The environment variable 'OPENAI_API_KEY' is not set. "
                "Please set it to your OpenAI API key."
            )
            raise OSError(msg)

        # Initialize OpenAI client
        self.client = OpenAI(api_key=api_key)
        super().init()

    def _apply_rate_limit(self) -> None:
        """
        Apply rate limiting to prevent API quota exhaustion.

        Ensures minimum interval between consecutive API requests.
        """
        current_time = time.time()
        time_since_last_request = current_time - self._last_request_time

        if time_since_last_request < self._min_request_interval:
            sleep_time = self._min_request_interval - time_since_last_request
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
            time.sleep(sleep_time)

        self._last_request_time = time.time()

    def validate_inputs(self, inputs: dict[str, Any]) -> bool:
        """Validate required inputs"""
        if "code" not in inputs:
            return False
        return isinstance(inputs["code"], str)

    @retry_with_exponential_backoff(max_retries=3, base_delay=1.0)
    def _call_openai_api(self, code: str) -> Any:
        """
        Call OpenAI API with retry logic and rate limiting.

        Args:
            code: Code string to analyze

        Returns:
            API response object

        Raises:
            RateLimitError: If rate limit is exceeded after retries
            APIError: If API call fails after retries
        """
        self._apply_rate_limit()

        return self.client.chat.completions.create(
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
                    "content": f"Analyze this code:\n\n{code}",
                },
            ],
            response_format={"type": "json_object"},
        )

    def execute(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """
        Analyze code using OpenAI with retry logic and rate limiting.

        Args:
            inputs: Dictionary containing:
                - code: String containing code to analyze

        Returns:
            Dictionary containing analysis results with status
        """
        if not self.validate_inputs(inputs):
            return {
                "error": "Invalid input. 'code' field is missing or not a string.",
                "status": "error",
            }

        if not self.client:
            return {
                "error": "OpenAI client not initialized. Call init() first.",
                "status": "error",
            }

        try:
            response = self._call_openai_api(inputs["code"])

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
        except (RateLimitError, APIError) as e:
            logger.error(f"OpenAI API error after retries: {e!s}")
            return {
                "error": f"API error: {str(e)}",
                "status": "error",
                "retry_exhausted": True,
            }
        except Exception as e:
            logger.exception(f"OpenAI code analysis failed: {e!s}")
            return {"error": str(e), "status": "error"}
