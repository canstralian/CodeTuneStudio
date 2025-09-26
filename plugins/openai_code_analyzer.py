from typing import Dict, Any
import os
from openai import OpenAI
import logging
from utils.plugins.base import AgentTool, ToolMetadata

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OpenAICodeAnalyzerTool(AgentTool):
    """Tool for analyzing code using OpenAI's GPT models"""

    def __init__(self):
        super().__init__()
        self.metadata = ToolMetadata(
            name="openai_code_analyzer",
            description="Analyzes code using OpenAI's models for improvements and suggestions",
            version="0.1.0",
            author="CodeTuneStudio",
            tags=["code-analysis", "ai", "openai"],
        )
        # Initialize OpenAI client
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate required inputs"""
        if "code" not in inputs:
            return False
        if not isinstance(inputs["code"], str):
            return False
        return True

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze code using OpenAI

        Args:
            inputs: Dictionary containing:
                - code: String containing code to analyze

        Returns:
            Dictionary containing analysis results
        """
        if not self.validate_inputs(inputs):
            raise ValueError("Invalid inputs")

        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert code analyzer. Analyze the given code and provide insights about:"
                        "\n1. Code quality"
                        "\n2. Potential improvements"
                        "\n3. Performance considerations"
                        "\n4. Security considerations"
                        "\nProvide the analysis in JSON format.",
                    },
                    {
                        "role": "user",
                        "content": f"Analyze this code:\n\n{inputs['code']}",
                    },
                ],
                response_format={"type": "json_object"},
            )

            return {
                "analysis": response.choices[0].message.content,
                "model": "gpt-4o",
                "status": "success",
            }

        except Exception as e:
            logger.error(f"OpenAI code analysis failed: {str(e)}")
            return {"error": str(e), "status": "error"}
