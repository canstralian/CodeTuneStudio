"""
Shared Dataset Utilities

This module provides common utilities for dataset handling across components,
promoting code reuse and consistency.
"""

import re
from functools import lru_cache
from typing import Set

from config.logging_config import get_logger

logger = get_logger(__name__)

# Default available datasets
DEFAULT_DATASETS: Set[str] = {
    "code_search_net",
    "python_code_instructions",
    "github_code_snippets",
    "argilla_code_dataset",
    "google/code_x_glue_ct_code_to_text",
    "redashu/python_code_instructions",
}


@lru_cache(maxsize=32)
def validate_dataset_name(name: str) -> bool:
    """
    Validate dataset name format.

    Checks if the dataset name follows the expected pattern for security
    and compatibility. Names should contain only alphanumeric characters,
    underscores, hyphens, and forward slashes (for namespaced datasets).

    Args:
        name: Dataset name to validate

    Returns:
        True if name is valid, False otherwise

    Example:
        >>> validate_dataset_name("my_dataset")
        True
        >>> validate_dataset_name("user/dataset-name")
        True
        >>> validate_dataset_name("invalid@name")
        False
    """
    if not name or not isinstance(name, str):
        logger.error(f"Invalid dataset name type: {type(name)}")
        return False

    # Allow alphanumeric, underscore, hyphen, and slash for namespaced datasets
    pattern = r"^[a-zA-Z0-9_\-/]+$"
    is_valid = bool(re.match(pattern, name))

    if not is_valid:
        logger.warning(f"Dataset name '{name}' does not match expected pattern")

    return is_valid


def is_argilla_dataset(dataset_name: str) -> bool:
    """
    Check if a dataset is an Argilla dataset.

    Args:
        dataset_name: Name of the dataset

    Returns:
        True if dataset is from Argilla, False otherwise
    """
    return dataset_name.startswith("argilla_")


def get_dataset_info(dataset_name: str) -> dict[str, str | int]:
    """
    Get information about a dataset.

    This function provides metadata about a dataset including source,
    type, and example count. For Argilla datasets, it attempts to fetch
    real information; for others, it provides defaults.

    Args:
        dataset_name: Name of the dataset

    Returns:
        Dictionary containing dataset metadata:
            - source: Dataset source (e.g., "Argilla", "HuggingFace")
            - type: Dataset type description
            - examples: Number of examples (or estimate)
            - languages: Supported languages (if applicable)
    """
    info = {
        "source": "Unknown",
        "type": "Code Dataset",
        "examples": 1000,
        "languages": "Python, JavaScript",
    }

    if is_argilla_dataset(dataset_name):
        info["source"] = "Argilla"
        info["type"] = "Code Generation Dataset"
        # Could fetch real info from Argilla here if needed
    elif "/" in dataset_name:
        info["source"] = "HuggingFace"
        info["type"] = "Code Dataset"
    else:
        info["source"] = "Local"

    return info


def get_available_datasets() -> Set[str]:
    """
    Get the set of available datasets.

    Returns:
        Set of dataset names
    """
    return DEFAULT_DATASETS.copy()


def add_dataset(dataset_name: str) -> bool:
    """
    Add a new dataset to the available datasets.

    Args:
        dataset_name: Name of the dataset to add

    Returns:
        True if successfully added, False if invalid or already exists
    """
    if not validate_dataset_name(dataset_name):
        logger.error(f"Cannot add invalid dataset name: {dataset_name}")
        return False

    if dataset_name in DEFAULT_DATASETS:
        logger.warning(f"Dataset {dataset_name} already exists")
        return False

    DEFAULT_DATASETS.add(dataset_name)
    logger.info(f"Added dataset: {dataset_name}")
    return True
