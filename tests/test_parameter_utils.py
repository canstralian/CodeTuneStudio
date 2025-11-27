"""
Tests for shared parameter configuration utilities.
"""

import pytest

from utils.parameter_utils import (
    ParameterDefaults,
    ParameterPresets,
    ParameterValidator,
)


class TestParameterValidator:
    """Test cases for ParameterValidator class."""

    def test_validate_batch_size_valid(self):
        """Test validation of valid batch size."""
        is_valid, error = ParameterValidator.validate_parameter("batch_size", 16)
        assert is_valid
        assert error is None

    def test_validate_batch_size_too_small(self):
        """Test validation rejects batch size too small."""
        is_valid, error = ParameterValidator.validate_parameter("batch_size", 0)
        assert not is_valid
        assert "must be >=" in error

    def test_validate_batch_size_too_large(self):
        """Test validation rejects batch size too large."""
        is_valid, error = ParameterValidator.validate_parameter("batch_size", 2000)
        assert not is_valid
        assert "must be <=" in error

    def test_validate_learning_rate_valid(self):
        """Test validation of valid learning rate."""
        is_valid, error = ParameterValidator.validate_parameter(
            "learning_rate", 5e-5
        )
        assert is_valid
        assert error is None

    def test_validate_learning_rate_too_small(self):
        """Test validation rejects learning rate too small."""
        is_valid, error = ParameterValidator.validate_parameter(
            "learning_rate", 1e-10
        )
        assert not is_valid

    def test_validate_epochs_valid(self):
        """Test validation of valid epochs."""
        is_valid, error = ParameterValidator.validate_parameter("epochs", 5)
        assert is_valid
        assert error is None

    def test_validate_unknown_parameter(self):
        """Test that unknown parameters are allowed."""
        is_valid, error = ParameterValidator.validate_parameter(
            "unknown_param", "value"
        )
        assert is_valid
        assert error is None

    def test_validate_type_conversion(self):
        """Test that type conversion works."""
        # String that can be converted to int
        is_valid, error = ParameterValidator.validate_parameter("batch_size", "16")
        assert is_valid

    def test_validate_invalid_type(self):
        """Test that invalid types are rejected."""
        is_valid, error = ParameterValidator.validate_parameter(
            "batch_size", "not_a_number"
        )
        assert not is_valid
        assert "type" in error.lower()

    def test_validate_parameters_all_valid(self):
        """Test validating multiple valid parameters."""
        params = {
            "batch_size": 8,
            "learning_rate": 5e-5,
            "epochs": 3,
        }
        is_valid, errors = ParameterValidator.validate_parameters(params)
        assert is_valid
        assert len(errors) == 0

    def test_validate_parameters_some_invalid(self):
        """Test validating with some invalid parameters."""
        params = {
            "batch_size": 0,  # Invalid - too small
            "learning_rate": 5e-5,  # Valid
            "epochs": 2000,  # Invalid - too large
        }
        is_valid, errors = ParameterValidator.validate_parameters(params)
        assert not is_valid
        assert len(errors) == 2


class TestParameterDefaults:
    """Test cases for ParameterDefaults class."""

    def test_get_defaults_default(self):
        """Test getting default parameters."""
        defaults = ParameterDefaults.get_defaults("default")
        assert "batch_size" in defaults
        assert "learning_rate" in defaults
        assert "epochs" in defaults

    def test_get_defaults_large_model(self):
        """Test getting defaults for large model."""
        defaults = ParameterDefaults.get_defaults("large_model")
        assert defaults["batch_size"] < ParameterDefaults.get_defaults("default")[
            "batch_size"
        ]

    def test_get_defaults_small_model(self):
        """Test getting defaults for small model."""
        defaults = ParameterDefaults.get_defaults("small_model")
        assert defaults["batch_size"] > ParameterDefaults.get_defaults("default")[
            "batch_size"
        ]

    def test_get_defaults_unknown_type(self):
        """Test getting defaults for unknown model type falls back."""
        defaults = ParameterDefaults.get_defaults("unknown_type")
        default_defaults = ParameterDefaults.get_defaults("default")
        assert defaults == default_defaults

    def test_merge_with_defaults(self):
        """Test merging user parameters with defaults."""
        user_params = {"batch_size": 32}
        merged = ParameterDefaults.merge_with_defaults(user_params)
        assert merged["batch_size"] == 32  # User value
        assert "learning_rate" in merged  # Default value
        assert "epochs" in merged  # Default value

    def test_merge_with_defaults_preserves_defaults(self):
        """Test that original defaults are not modified."""
        user_params = {"batch_size": 32}
        ParameterDefaults.merge_with_defaults(user_params)
        # Check original defaults unchanged
        defaults = ParameterDefaults.get_defaults("default")
        assert defaults["batch_size"] != 32


class TestParameterPresets:
    """Test cases for ParameterPresets class."""

    def test_get_preset_quick_test(self):
        """Test getting quick test preset."""
        preset = ParameterPresets.get_preset("quick_test")
        assert preset is not None
        assert "name" in preset
        assert "params" in preset
        assert preset["params"]["epochs"] == 1

    def test_get_preset_standard(self):
        """Test getting standard preset."""
        preset = ParameterPresets.get_preset("standard")
        assert preset is not None
        assert preset["params"]["epochs"] > 1

    def test_get_preset_high_quality(self):
        """Test getting high quality preset."""
        preset = ParameterPresets.get_preset("high_quality")
        assert preset is not None
        assert preset["params"]["epochs"] >= 5

    def test_get_preset_nonexistent(self):
        """Test getting non-existent preset."""
        preset = ParameterPresets.get_preset("nonexistent")
        assert preset is None

    def test_list_presets(self):
        """Test listing available presets."""
        presets = ParameterPresets.list_presets()
        assert "quick_test" in presets
        assert "standard" in presets
        assert "high_quality" in presets

    def test_get_preset_descriptions(self):
        """Test getting preset descriptions."""
        descriptions = ParameterPresets.get_preset_descriptions()
        assert "quick_test" in descriptions
        assert "standard" in descriptions
        assert isinstance(descriptions["quick_test"], str)
