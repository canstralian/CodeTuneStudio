"""
Shared parameter configuration utilities.

This module provides common parameter handling logic used across
multiple components for training configuration management.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class ParameterValidator:
    """
    Validator for training parameters.

    Provides centralized validation logic for training configuration
    parameters used throughout the application.
    """

    # Parameter constraints
    CONSTRAINTS = {
        "batch_size": {"min": 1, "max": 1024, "type": int},
        "learning_rate": {"min": 1e-7, "max": 1.0, "type": float},
        "epochs": {"min": 1, "max": 1000, "type": int},
        "max_seq_length": {"min": 1, "max": 8192, "type": int},
        "warmup_steps": {"min": 0, "max": 100000, "type": int},
        "weight_decay": {"min": 0.0, "max": 1.0, "type": float},
        "gradient_accumulation_steps": {"min": 1, "max": 128, "type": int},
    }

    @classmethod
    def validate_parameter(
        cls, name: str, value: Any
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a single parameter.

        Args:
            name: Parameter name
            value: Parameter value

        Returns:
            Tuple of (is_valid, error_message)
        """
        if name not in cls.CONSTRAINTS:
            return True, None  # Unknown parameters are allowed

        constraint = cls.CONSTRAINTS[name]

        # Type check
        expected_type = constraint["type"]
        if not isinstance(value, expected_type):
            try:
                value = expected_type(value)
            except (ValueError, TypeError):
                return (
                    False,
                    f"Parameter '{name}' must be of type {expected_type.__name__}",
                )

        # Range check
        if "min" in constraint and value < constraint["min"]:
            return (
                False,
                f"Parameter '{name}' must be >= {constraint['min']}, got {value}",
            )

        if "max" in constraint and value > constraint["max"]:
            return (
                False,
                f"Parameter '{name}' must be <= {constraint['max']}, got {value}",
            )

        return True, None

    @classmethod
    def validate_parameters(
        cls, params: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Validate multiple parameters.

        Args:
            params: Dictionary of parameter name-value pairs

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        for name, value in params.items():
            is_valid, error = cls.validate_parameter(name, value)
            if not is_valid:
                errors.append(error)

        return len(errors) == 0, errors


class ParameterDefaults:
    """
    Default values for training parameters.

    Provides sensible defaults for common training configurations.
    """

    # Default parameter values for different model types
    DEFAULTS = {
        "default": {
            "batch_size": 8,
            "learning_rate": 5e-5,
            "epochs": 3,
            "max_seq_length": 512,
            "warmup_steps": 100,
            "weight_decay": 0.01,
            "gradient_accumulation_steps": 1,
        },
        "large_model": {
            "batch_size": 4,
            "learning_rate": 3e-5,
            "epochs": 3,
            "max_seq_length": 1024,
            "warmup_steps": 200,
            "weight_decay": 0.01,
            "gradient_accumulation_steps": 4,
        },
        "small_model": {
            "batch_size": 16,
            "learning_rate": 1e-4,
            "epochs": 5,
            "max_seq_length": 256,
            "warmup_steps": 50,
            "weight_decay": 0.01,
            "gradient_accumulation_steps": 1,
        },
    }

    @classmethod
    def get_defaults(cls, model_type: str = "default") -> Dict[str, Any]:
        """
        Get default parameters for a model type.

        Args:
            model_type: Type of model (default, large_model, small_model)

        Returns:
            Dictionary of default parameter values
        """
        if model_type not in cls.DEFAULTS:
            logger.warning(
                f"Unknown model type '{model_type}', using 'default' defaults"
            )
            model_type = "default"

        return cls.DEFAULTS[model_type].copy()

    @classmethod
    def merge_with_defaults(
        cls, params: Dict[str, Any], model_type: str = "default"
    ) -> Dict[str, Any]:
        """
        Merge provided parameters with defaults.

        Args:
            params: User-provided parameters
            model_type: Type of model for defaults

        Returns:
            Merged parameter dictionary
        """
        defaults = cls.get_defaults(model_type)
        defaults.update(params)
        return defaults


class ParameterPresets:
    """
    Preset configurations for common training scenarios.

    Provides pre-configured parameter sets for different use cases.
    """

    PRESETS = {
        "quick_test": {
            "name": "Quick Test",
            "description": "Fast training for testing purposes",
            "params": {
                "batch_size": 8,
                "learning_rate": 1e-4,
                "epochs": 1,
                "max_seq_length": 128,
                "warmup_steps": 10,
            },
        },
        "standard": {
            "name": "Standard Training",
            "description": "Balanced configuration for most use cases",
            "params": {
                "batch_size": 8,
                "learning_rate": 5e-5,
                "epochs": 3,
                "max_seq_length": 512,
                "warmup_steps": 100,
            },
        },
        "high_quality": {
            "name": "High Quality",
            "description": "Slower but higher quality training",
            "params": {
                "batch_size": 4,
                "learning_rate": 3e-5,
                "epochs": 5,
                "max_seq_length": 1024,
                "warmup_steps": 200,
            },
        },
    }

    @classmethod
    def get_preset(cls, preset_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a parameter preset by name.

        Args:
            preset_name: Name of the preset

        Returns:
            Preset dictionary or None if not found
        """
        return cls.PRESETS.get(preset_name)

    @classmethod
    def list_presets(cls) -> List[str]:
        """
        Get list of available preset names.

        Returns:
            List of preset names
        """
        return list(cls.PRESETS.keys())

    @classmethod
    def get_preset_descriptions(cls) -> Dict[str, str]:
        """
        Get descriptions for all presets.

        Returns:
            Dictionary mapping preset names to descriptions
        """
        return {
            name: preset["description"] for name, preset in cls.PRESETS.items()
        }
