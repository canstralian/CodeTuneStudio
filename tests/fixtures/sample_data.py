"""
Test fixtures for CodeTuneStudio tests.

Provides common test data and utilities.
"""

import pytest
from utils.pydantic_models import TrainingConfigModel


@pytest.fixture
def valid_training_config():
    """Fixture providing a valid training configuration."""
    return {
        "model_type": "CodeT5",
        "dataset_name": "test_dataset",
        "batch_size": 16,
        "learning_rate": 0.001,
        "epochs": 5,
        "max_seq_length": 512,
        "warmup_steps": 100,
        "include_amphigory": False,
        "amphigory_ratio": 0.1
    }


@pytest.fixture
def invalid_training_config():
    """Fixture providing an invalid training configuration."""
    return {
        "model_type": "InvalidModel",
        "dataset_name": "",
        "batch_size": 0,
        "learning_rate": -1.0,
        "epochs": 0,
        "max_seq_length": 32,
        "warmup_steps": -1
    }


@pytest.fixture
def sample_plugin_metadata():
    """Fixture providing sample plugin metadata."""
    return {
        "name": "test_plugin",
        "description": "A test plugin for validation",
        "version": "1.0.0",
        "author": "Test Author",
        "tags": ["test", "validation"],
        "requires_api_key": False
    }