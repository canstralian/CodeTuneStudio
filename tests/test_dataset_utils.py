"""
Tests for shared dataset utilities.
"""

import pytest

from utils.dataset_utils import (
    DatasetRegistry,
    DatasetValidator,
    get_dataset_registry,
)


class TestDatasetValidator:
    """Test cases for DatasetValidator class."""

    def test_validate_valid_name(self):
        """Test validation of valid dataset names."""
        valid_names = [
            "my-dataset",
            "dataset_123",
            "org/dataset-name",
            "Dataset123",
        ]
        for name in valid_names:
            assert DatasetValidator.validate_dataset_name(name)

    def test_validate_invalid_name(self):
        """Test validation rejects invalid dataset names."""
        invalid_names = [
            "",  # Empty
            "a",  # Too short
            "name with spaces",  # Spaces
            "name@special",  # Special chars
            "a" * 201,  # Too long
        ]
        for name in invalid_names:
            assert not DatasetValidator.validate_dataset_name(name)

    def test_validate_none_name(self):
        """Test validation rejects None."""
        assert not DatasetValidator.validate_dataset_name(None)

    def test_sanitize_dataset_name(self):
        """Test sanitizing dataset names."""
        assert DatasetValidator.sanitize_dataset_name("valid-name") == "valid-name"
        assert (
            DatasetValidator.sanitize_dataset_name("name with spaces")
            == "name_with_spaces"
        )
        assert (
            DatasetValidator.sanitize_dataset_name("name@special#chars")
            == "name_special_chars"
        )

    def test_sanitize_empty_name(self):
        """Test sanitizing empty name."""
        assert DatasetValidator.sanitize_dataset_name("") == ""

    def test_sanitize_truncates_long_name(self):
        """Test that sanitization truncates long names."""
        long_name = "a" * 300
        sanitized = DatasetValidator.sanitize_dataset_name(long_name)
        assert len(sanitized) <= DatasetValidator.MAX_NAME_LENGTH


class TestDatasetRegistry:
    """Test cases for DatasetRegistry class."""

    def test_initialization(self):
        """Test registry initialization."""
        registry = DatasetRegistry()
        assert len(registry.list_datasets()) == 0

    def test_register_dataset(self):
        """Test registering a dataset."""
        registry = DatasetRegistry()
        assert registry.register_dataset("test-dataset")
        assert "test-dataset" in registry.list_datasets()

    def test_register_invalid_dataset(self):
        """Test that invalid dataset cannot be registered."""
        registry = DatasetRegistry()
        assert not registry.register_dataset("")

    def test_register_duplicate_dataset(self):
        """Test registering duplicate dataset."""
        registry = DatasetRegistry()
        registry.register_dataset("test-dataset")
        # Should return False for duplicate
        assert not registry.register_dataset("test-dataset")
        # But dataset should still be in registry
        assert "test-dataset" in registry.list_datasets()

    def test_unregister_dataset(self):
        """Test unregistering a dataset."""
        registry = DatasetRegistry()
        registry.register_dataset("test-dataset")
        assert registry.unregister_dataset("test-dataset")
        assert "test-dataset" not in registry.list_datasets()

    def test_unregister_nonexistent_dataset(self):
        """Test unregistering non-existent dataset."""
        registry = DatasetRegistry()
        assert not registry.unregister_dataset("nonexistent")

    def test_is_registered(self):
        """Test checking if dataset is registered."""
        registry = DatasetRegistry()
        registry.register_dataset("test-dataset")
        assert registry.is_registered("test-dataset")
        assert not registry.is_registered("other-dataset")

    def test_list_datasets(self):
        """Test listing datasets."""
        registry = DatasetRegistry()
        datasets = ["dataset1", "dataset2", "dataset3"]
        for dataset in datasets:
            registry.register_dataset(dataset)
        listed = registry.list_datasets()
        assert len(listed) == len(datasets)
        for dataset in datasets:
            assert dataset in listed

    def test_clear(self):
        """Test clearing all datasets."""
        registry = DatasetRegistry()
        registry.register_dataset("dataset1")
        registry.register_dataset("dataset2")
        registry.clear()
        assert len(registry.list_datasets()) == 0

    def test_global_singleton(self):
        """Test that get_dataset_registry returns singleton."""
        registry1 = get_dataset_registry()
        registry2 = get_dataset_registry()
        assert registry1 is registry2
