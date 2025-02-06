
import re
from typing import Dict, List

def sanitize_string(value: str) -> str:
    """Sanitize string inputs by removing special characters"""
    return re.sub(r'[^a-zA-Z0-9_\-]', '', value)

def validate_config(config: Dict) -> List[str]:
    """
    Validate training configuration parameters with enhanced checks
    """
    errors = []
    
    # Type validation
    if not isinstance(config.get("batch_size"), int):
        errors.append("Batch size must be an integer")
    if not isinstance(config.get("learning_rate"), float):
        errors.append("Learning rate must be a float")
        
    # Range validation
    if config.get("batch_size", 0) > 128 or config.get("batch_size", 0) < 1:
        errors.append("Batch size must be between 1 and 128")
        
    if config.get("learning_rate", 0) > 1e-2 or config.get("learning_rate", 0) < 1e-6:
        errors.append("Learning rate must be between 1e-6 and 1e-2")
        
    if config.get("max_seq_length", 0) > 512 or config.get("max_seq_length", 0) < 64:
        errors.append("Maximum sequence length must be between 64 and 512")
        
    if config.get("epochs", 0) > 100 or config.get("epochs", 0) < 1:
        errors.append("Number of epochs must be between 1 and 100")
        
    # Model type validation
    valid_models = {"CodeT5", "Replit-v1.5"}
    if config.get("model_type") not in valid_models:
        errors.append(f"Model type must be one of: {', '.join(valid_models)}")
        
    return errors
