import pytest
from utils import (
    TrainingConfig,
    TrainingMetric,
    __all__,
    db,
    init_db,
    validate_config,
)


def test_imports():
    """Test that all expected items are imported correctly."""
    assert TrainingConfig is not None
    assert TrainingMetric is not None
    assert db is not None
    assert init_db is not None
    assert validate_config is not None


def test_all_list():
    """Test that __all__ contains the expected items."""
    expected_all = [
        "TrainingConfig",
        "TrainingMetric",
        "db",
        "init_db",
        "validate_config",
    ]
    assert __all__ == expected_all


def test_package_import():
    """Test importing the package and accessing items."""
    import utils

    assert hasattr(utils, "TrainingConfig")
    assert hasattr(utils, "TrainingMetric")
    assert hasattr(utils, "db")
    assert hasattr(utils, "init_db")
    assert hasattr(utils, "validate_config")
    assert utils.__all__ == [
        "TrainingConfig",
        "TrainingMetric",
        "db",
        "init_db",
        "validate_config",
    ]
