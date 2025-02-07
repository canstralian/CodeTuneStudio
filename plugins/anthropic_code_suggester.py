from typing import Dict, Any
import os
from anthropic import Anthropic
import logging
from utils.plugins.base import AgentTool, ToolMetadata

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnthropicCodeSuggesterTool(AgentTool):
    """Tool for suggesting code improvements using Anthropic's Claude"""
    
    def __init__(self):
        super().__init__()
        self.metadata = ToolMetadata(
            name="anthropic_code_suggester",
            description="Suggests code improvements using Anthropic's Claude model",
            version="0.1.0",
            author="CodeTuneStudio",
            tags=["code-suggestions", "ai", "anthropic"]
        )
        # Initialize Anthropic client
        self.client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate required inputs"""
        if "code" not in inputs:
            return False
        if not isinstance(inputs["code"], str):
            return False
        return True
        
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate code suggestions using Anthropic
        
        Args:
            inputs: Dictionary containing:
                - code: String containing code to analyze
                
        Returns:
            Dictionary containing suggested improvements
        """
        if not self.validate_inputs(inputs):
            raise ValueError("Invalid inputs")
            
        try:
            # the newest Anthropic model is "claude-3-5-sonnet-20241022" which was released October 22, 2024
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                messages=[{
                    "role": "user",
                    "content": f"""Analyze this code and suggest improvements in JSON format. 
                    Include specific recommendations for:
                    1. Code structure
                    2. Optimization opportunities
                    3. Best practices
                    4. Error handling
                    
                    Code to analyze:
                    {inputs['code']}
                    """
                }]
            )
            
            return {
                "suggestions": message.content,
                "model": "claude-3-5-sonnet-20241022",
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Anthropic code suggestion failed: {str(e)}")
            return {
                "error": str(e),
                "status": "error"
            }
