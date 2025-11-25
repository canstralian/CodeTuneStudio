"""
Shared Parameter Utilities

This module provides common utilities for parameter configuration and validation
across components, promoting code reuse and consistency.
"""

from typing import Any, Dict, List, Optional

from config.logging_config import get_logger

logger = get_logger(__name__)

# Model architecture options
SUPPORTED_MODELS = [
    "CodeT5",
    "Replit-v1.5",
    "CodeBERT",
    "GPT-2",
]

# Default parameter ranges
PARAM_RANGES = {
    "batch_size": {"min": 1, "max": 128, "default": 16},
    "learning_rate": {"min": 1e-6, "max": 1e-2, "default": 5e-5},
    "epochs": {"min": 1, "max": 100, "default": 3},
    "max_seq_length": {"min": 64, "max": 2048, "default": 512},
    "warmup_steps": {"min": 0, "max": 10000, "default": 500},
    "weight_decay": {"min": 0.0, "max": 1.0, "default": 0.01},
    "gradient_accumulation_steps": {"min": 1, "max": 32, "default": 1},
}


def get_model_architectures() -> List[str]:
    """
    Get list of supported model architectures.

    Returns:
        List of model architecture names
    """
    return SUPPORTED_MODELS.copy()


def get_parameter_range(param_name: str) -> Optional[Dict[str, Any]]:
    """
    Get the valid range for a specific parameter.

    Args:
        param_name: Name of the parameter

    Returns:
        Dictionary with min, max, and default values, or None if not found
    """
    return PARAM_RANGES.get(param_name)


def validate_parameter_value(
    param_name: str, value: Any
) -> tuple[bool, Optional[str]]:
    """
    Validate a parameter value against its expected range.

    Args:
        param_name: Name of the parameter
        value: Value to validate

    Returns:
        Tuple of (is_valid, error_message)

    Example:
        >>> validate_parameter_value("batch_size", 16)
        (True, None)
        >>> validate_parameter_value("batch_size", 200)
        (False, "batch_size must be between 1 and 128")
    """
    param_range = get_parameter_range(param_name)

    if param_range is None:
        # Unknown parameter - allow it but log warning
        logger.warning(f"Unknown parameter: {param_name}")
        return True, None

    min_val = param_range["min"]
    max_val = param_range["max"]

    # Type checking
    if isinstance(min_val, int) and isinstance(max_val, int):
        if not isinstance(value, (int, float)):
            return False, f"{param_name} must be numeric"
        value = int(value)
    elif isinstance(min_val, float) or isinstance(max_val, float):
        if not isinstance(value, (int, float)):
            return False, f"{param_name} must be numeric"
        value = float(value)

    # Range checking
    if value < min_val or value > max_val:
        return False, f"{param_name} must be between {min_val} and {max_val}"

    return True, None


def get_default_config() -> Dict[str, Any]:
    """
    Get default training configuration.

    Returns:
        Dictionary with default parameter values
    """
    config = {
        "model_type": SUPPORTED_MODELS[0],
    }

    for param_name, param_range in PARAM_RANGES.items():
        config[param_name] = param_range["default"]

    return config


def validate_config(config: Dict[str, Any]) -> List[str]:
    """
    Validate a complete configuration dictionary.

    Args:
        config: Configuration dictionary to validate

    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []

    # Check required fields
    required_fields = ["model_type", "batch_size", "learning_rate", "epochs"]
    for field in required_fields:
        if field not in config:
            errors.append(f"Missing required field: {field}")

    # Validate model type
    if "model_type" in config:
        if config["model_type"] not in SUPPORTED_MODELS:
            errors.append(
                f"Invalid model_type: {config['model_type']}. "
                f"Must be one of: {', '.join(SUPPORTED_MODELS)}"
            )

    # Validate parameter values
    for param_name, value in config.items():
        if param_name == "model_type":
            continue

        is_valid, error_msg = validate_parameter_value(param_name, value)
        if not is_valid:
            errors.append(error_msg)

    return errors


def apply_constraints(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply constraints and clamp values to valid ranges.

    This function modifies the config in-place to ensure all values are
    within valid ranges.

    Args:
        config: Configuration dictionary to constrain

    Returns:
        Constrained configuration dictionary
    """
    for param_name, value in config.items():
        if param_name == "model_type":
            continue

        param_range = get_parameter_range(param_name)
        if param_range:
            min_val = param_range["min"]
            max_val = param_range["max"]

            # Clamp value to range
            if isinstance(value, (int, float)):
                config[param_name] = max(min_val, min(max_val, value))

                if config[param_name] != value:
                    logger.warning(
                        f"Clamped {param_name} from {value} to {config[param_name]}"
                    )

    return config
