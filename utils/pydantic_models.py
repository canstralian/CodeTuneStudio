"""
Pydantic models for configuration validation and data structures.

This module provides type-safe configuration models using Pydantic.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict, validator
import re


class TrainingConfigModel(BaseModel):
    """Pydantic model for training configuration validation."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",  # Prevent extra fields
    )

    model_type: str = Field(
        ..., description="Type of model to train (e.g., CodeT5, Replit-v1.5)"
    )
    dataset_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Name of the dataset to use for training",
    )
    batch_size: int = Field(..., ge=1, le=128, description="Training batch size")
    learning_rate: float = Field(
        ..., gt=0.0, le=1.0, description="Learning rate for training"
    )
    epochs: int = Field(..., ge=1, le=100, description="Number of training epochs")
    max_seq_length: int = Field(
        ..., ge=64, le=2048, description="Maximum sequence length"
    )
    warmup_steps: int = Field(..., ge=0, le=10000, description="Number of warmup steps")
    include_amphigory: Optional[bool] = Field(
        default=False, description="Whether to include amphigory data enhancement"
    )
    amphigory_ratio: Optional[float] = Field(
        default=0.1, ge=0.0, le=0.3, description="Ratio of amphigory data to include"
    )

    @validator("model_type")
    def validate_model_type(cls, v):
        """Validate model type against allowed values."""
        allowed_models = {"CodeT5", "Replit-v1.5", "CodeGen", "InCoder"}
        if v not in allowed_models:
            raise ValueError(f"Model type must be one of: {', '.join(allowed_models)}")
        return v

    @validator("dataset_name")
    def validate_dataset_name(cls, v):
        """Validate dataset name format."""
        # Allow alphanumeric, hyphens, underscores, and forward slashes for HF datasets
        if not re.match(r"^[\w\-\/\.]+$", v):
            raise ValueError(
                "Dataset name can only contain alphanumeric characters, "
                "hyphens, underscores, dots, and forward slashes"
            )
        return v

    @validator("learning_rate")
    def validate_learning_rate(cls, v):
        """Validate learning rate is in reasonable range."""
        if not (1e-6 <= v <= 1e-2):
            raise ValueError("Learning rate must be between 1e-6 and 1e-2")
        return v

    @validator("amphigory_ratio", always=True)
    def validate_amphigory_ratio(cls, v, values):
        """Validate amphigory ratio when amphigory is enabled."""
        if values.get("include_amphigory", False) and v is None:
            raise ValueError(
                "amphigory_ratio is required when include_amphigory is True"
            )
        return v


class PluginMetadataModel(BaseModel):
    """Pydantic model for plugin metadata validation."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")  # Semantic versioning
    author: Optional[str] = Field(default=None, max_length=100)
    tags: List[str] = Field(default_factory=list)
    requires_api_key: bool = Field(default=False)
    api_key_env_var: Optional[str] = Field(default=None)

    @validator("tags")
    def validate_tags(cls, v):
        """Validate and clean up tags."""
        # Remove duplicates and empty strings
        clean_tags = list(set(tag.strip() for tag in v if tag.strip()))
        return clean_tags[:10]  # Limit to 10 tags


class DatasetConfigModel(BaseModel):
    """Pydantic model for dataset configuration."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(..., min_length=1)
    source: str = Field(..., pattern=r"^(huggingface|argilla|local)$")
    subset: Optional[str] = Field(default=None)
    split: str = Field(default="train")
    max_samples: Optional[int] = Field(default=None, gt=0)
    cache_dir: Optional[str] = Field(default=None)

    @validator("name")
    def validate_dataset_name(cls, v):
        """Validate dataset name format."""
        if not re.match(r"^[\w\-\/\.]+$", v):
            raise ValueError(
                "Dataset name can only contain alphanumeric characters, "
                "hyphens, underscores, dots, and forward slashes"
            )
        return v


class SecurityConfigModel(BaseModel):
    """Pydantic model for security configuration."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    allow_code_execution: bool = Field(default=False)
    sandbox_plugins: bool = Field(default=True)
    max_plugin_runtime: int = Field(default=30, ge=1, le=300)  # seconds
    allowed_file_extensions: List[str] = Field(
        default_factory=lambda: [".py", ".txt", ".json", ".yaml", ".yml"]
    )
    max_file_size: int = Field(default=10485760, ge=1)  # 10MB default

    @validator("allowed_file_extensions")
    def validate_file_extensions(cls, v):
        """Validate file extensions format."""
        clean_extensions = []
        for ext in v:
            if not ext.startswith("."):
                ext = "." + ext
            if not re.match(r"^\.[a-zA-Z0-9]+$", ext):
                raise ValueError(f"Invalid file extension: {ext}")
            clean_extensions.append(ext.lower())
        return list(set(clean_extensions))


def validate_config_dict(config_dict: Dict[str, Any]) -> TrainingConfigModel:
    """
    Validate a configuration dictionary using Pydantic model.

    Args:
        config_dict: Dictionary containing configuration parameters

    Returns:
        Validated TrainingConfigModel instance

    Raises:
        ValidationError: If validation fails
    """
    return TrainingConfigModel(**config_dict)


def validate_plugin_metadata(metadata_dict: Dict[str, Any]) -> PluginMetadataModel:
    """
    Validate plugin metadata using Pydantic model.

    Args:
        metadata_dict: Dictionary containing plugin metadata

    Returns:
        Validated PluginMetadataModel instance

    Raises:
        ValidationError: If validation fails
    """
    return PluginMetadataModel(**metadata_dict)
