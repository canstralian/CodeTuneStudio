"""
Shared dataset utilities for components.

This module provides common dataset handling logic used across
multiple components, promoting code reuse and maintainability.
"""

import logging
import re
from typing import List, Optional

logger = logging.getLogger(__name__)


class DatasetValidator:
    """
    Validator for dataset names and configurations.

    Provides centralized validation logic for dataset identifiers
    and configurations used throughout the application.
    """

    # Regex pattern for valid dataset names
    VALID_NAME_PATTERN = re.compile(r"^[a-zA-Z0-9_\-/]+$")

    # Minimum and maximum lengths for dataset names
    MIN_NAME_LENGTH = 3
    MAX_NAME_LENGTH = 200

    @classmethod
    def validate_dataset_name(cls, name: str) -> bool:
        """
        Validate dataset name format.

        Args:
            name: Dataset name to validate

        Returns:
            True if name is valid, False otherwise
        """
        if not name or not isinstance(name, str):
            return False

        name = name.strip()

        # Check length constraints
        if not (cls.MIN_NAME_LENGTH <= len(name) <= cls.MAX_NAME_LENGTH):
            logger.warning(
                f"Dataset name length {len(name)} outside valid range "
                f"[{cls.MIN_NAME_LENGTH}, {cls.MAX_NAME_LENGTH}]"
            )
            return False

        # Check pattern match
        if not cls.VALID_NAME_PATTERN.match(name):
            logger.warning(f"Dataset name '{name}' contains invalid characters")
            return False

        return True

    @classmethod
    def sanitize_dataset_name(cls, name: str) -> str:
        """
        Sanitize dataset name by removing invalid characters.

        Args:
            name: Dataset name to sanitize

        Returns:
            Sanitized dataset name
        """
        if not name:
            return ""

        # Remove invalid characters
        sanitized = re.sub(r"[^a-zA-Z0-9_\-/]", "_", name.strip())

        # Truncate to maximum length
        if len(sanitized) > cls.MAX_NAME_LENGTH:
            sanitized = sanitized[: cls.MAX_NAME_LENGTH]

        return sanitized


class DatasetRegistry:
    """
    Registry for available datasets.

    Maintains a central registry of datasets available in the application.
    """

    def __init__(self) -> None:
        """Initialize empty dataset registry."""
        self._datasets: List[str] = []

    def register_dataset(self, name: str) -> bool:
        """
        Register a dataset in the registry.

        Args:
            name: Dataset name to register

        Returns:
            True if registration succeeded, False otherwise
        """
        if not DatasetValidator.validate_dataset_name(name):
            logger.error(f"Cannot register invalid dataset name: {name}")
            return False

        if name not in self._datasets:
            self._datasets.append(name)
            logger.info(f"Registered dataset: {name}")
            return True

        logger.debug(f"Dataset already registered: {name}")
        return False

    def unregister_dataset(self, name: str) -> bool:
        """
        Unregister a dataset from the registry.

        Args:
            name: Dataset name to unregister

        Returns:
            True if unregistration succeeded, False otherwise
        """
        if name in self._datasets:
            self._datasets.remove(name)
            logger.info(f"Unregistered dataset: {name}")
            return True

        logger.warning(f"Dataset not found in registry: {name}")
        return False

    def list_datasets(self) -> List[str]:
        """
        Get list of registered datasets.

        Returns:
            List of registered dataset names
        """
        return self._datasets.copy()

    def is_registered(self, name: str) -> bool:
        """
        Check if a dataset is registered.

        Args:
            name: Dataset name to check

        Returns:
            True if dataset is registered, False otherwise
        """
        return name in self._datasets

    def clear(self) -> None:
        """Clear all registered datasets."""
        count = len(self._datasets)
        self._datasets.clear()
        logger.info(f"Cleared {count} datasets from registry")


# Global dataset registry instance
_global_registry: Optional[DatasetRegistry] = None


def get_dataset_registry() -> DatasetRegistry:
    """
    Get the global dataset registry instance.

    Returns:
        Global DatasetRegistry singleton
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = DatasetRegistry()
    return _global_registry
