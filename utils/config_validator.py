import re
from typing import Dict, List, Union, Any
import logging
from pydantic import ValidationError
from .pydantic_models import TrainingConfigModel, validate_config_dict

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def sanitize_string(value: str) -> str:
    """
    Sanitize string inputs by removing special characters and whitespace

    Args:
        value: Input string to sanitize

    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        raise ValueError("Input must be a string")
    return re.sub(r"[^a-zA-Z0-9_\-\.]", "", value.strip())


def validate_numeric_range(
    value: Union[int, float],
    min_val: Union[int, float],
    max_val: Union[int, float],
    param_name: str,
) -> List[str]:
    """
    Validate numeric parameter within specified range

    Args:
        value: Value to validate
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        param_name: Name of parameter being validated

    Returns:
        List of validation errors, empty if valid
    """
    errors = []
    try:
        if not isinstance(value, (int, float)):
            errors.append(f"{param_name} must be a number")
        elif value < min_val or value > max_val:
            errors.append(f"{param_name} must be between {min_val} and {max_val}")
    except Exception as e:
        logger.error(f"Error validating {param_name}: {str(e)}")
        errors.append(f"Invalid value for {param_name}")
    return errors


def validate_config(config: Dict[str, Any]) -> List[str]:
    """
    Validate training configuration parameters using Pydantic models.

    Args:
        config: Dictionary containing configuration parameters

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    try:
        # Use Pydantic model for comprehensive validation
        validated_model = validate_config_dict(config)
        logger.info(f"Configuration validated successfully: {validated_model.model_type}")
        return []  # No errors if Pydantic validation passes
    
    except ValidationError as e:
        # Extract errors from Pydantic validation
        for error in e.errors():
            field = error.get('loc', ['unknown'])[0]
            message = error.get('msg', 'Validation error')
            errors.append(f"{field}: {message}")
        
        logger.warning(f"Configuration validation failed with {len(errors)} errors")
        return errors
    
    except Exception as e:
        # Fallback to legacy validation for unexpected errors
        logger.warning(f"Pydantic validation failed, using legacy validation: {e}")
        return _legacy_validate_config(config)


def _legacy_validate_config(config: Dict[str, Any]) -> List[str]:
    """
    Legacy configuration validation (kept as fallback).
    
    Args:
        config: Dictionary containing configuration parameters
        
    Returns:
        List of validation errors
    """
    errors = []

    try:
        # Required fields check
        required_fields = {
            "model_type": str,
            "batch_size": int,
            "learning_rate": float,
            "epochs": int,
            "max_seq_length": int,
            "warmup_steps": int,
        }

        for field, expected_type in required_fields.items():
            if field not in config:
                errors.append(f"Missing required field: {field}")
            elif not isinstance(config[field], expected_type):
                errors.append(f"{field} must be of type {expected_type.__name__}")

        # Model type validation
        valid_models = {"CodeT5", "Replit-v1.5"}
        if config.get("model_type") not in valid_models:
            errors.append(f"Model type must be one of: {', '.join(valid_models)}")

        # Numeric range validations
        validations = [
            ("batch_size", 1, 128),
            ("learning_rate", 1e-6, 1e-2),
            ("epochs", 1, 100),
            ("max_seq_length", 64, 512),
            ("warmup_steps", 0, 1000),
        ]

        for param, min_val, max_val in validations:
            if param in config:
                errors.extend(
                    validate_numeric_range(config[param], min_val, max_val, param)
                )

        # Dataset enhancement options validation
        if "include_amphigory" in config:
            if not isinstance(config["include_amphigory"], bool):
                errors.append("include_amphigory must be a boolean")

        if "amphigory_ratio" in config:
            if config["include_amphigory"]:
                errors.extend(
                    validate_numeric_range(
                        config["amphigory_ratio"], 0.0, 0.3, "amphigory_ratio"
                    )
                )

        logger.info(f"Configuration validation completed with {len(errors)} errors")
        return errors

    except Exception as e:
        logger.error(f"Error during configuration validation: {str(e)}")
        errors.append(f"Configuration validation error: {str(e)}")
        return errors
