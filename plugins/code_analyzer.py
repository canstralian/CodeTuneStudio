from typing import Dict, Any, List
import ast
from utils.plugins.base import AgentTool, ToolMetadata

class CodeAnalyzerTool(AgentTool):
    """Tool for analyzing Python code structure"""
    
    def __init__(self):
        super().__init__()
        self.metadata = ToolMetadata(
            name="code_analyzer",
            description="Analyzes Python code structure and complexity",
            version="0.1.0",
            author="CodeTuneStudio",
            tags=["code-analysis", "python"]
        )
        
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate that required inputs are present"""
        if "code" not in inputs:
            return False
        if not isinstance(inputs["code"], str):
            return False
        return True
        
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze Python code structure
        
        Args:
            inputs: Dictionary containing:
                - code: String containing Python code to analyze
                
        Returns:
            Dictionary containing:
                - num_functions: Number of functions
                - num_classes: Number of classes
                - imports: List of imported modules
                - complexity: Estimated code complexity
        """
        if not self.validate_inputs(inputs):
            raise ValueError("Invalid inputs")
            
        try:
            tree = ast.parse(inputs["code"])
            
            # Count functions and classes
            num_functions = len([node for node in ast.walk(tree) 
                              if isinstance(node, ast.FunctionDef)])
            num_classes = len([node for node in ast.walk(tree) 
                             if isinstance(node, ast.ClassDef)])
            
            # Get imports
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.extend(n.name for n in node.names)
                elif isinstance(node, ast.ImportFrom):
                    imports.append(node.module)
                    
            # Simple complexity metric based on number of nodes
            complexity = len([node for node in ast.walk(tree)])
            
            return {
                "num_functions": num_functions,
                "num_classes": num_classes,
                "imports": imports,
                "complexity": complexity
            }
            
        except Exception as e:
            raise RuntimeError(f"Failed to analyze code: {str(e)}")
