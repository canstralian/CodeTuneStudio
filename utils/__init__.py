"""Utility modules for CodeTuneStudio.

The package initializer intentionally avoids importing database modules eagerly so
plugin discovery and lightweight tests do not require optional web/database
runtime dependencies before they are needed.
"""

from typing import Any

__all__ = [
    "validate_config",
    "init_db",
    "TrainingConfig",
    "TrainingMetric",
    "db",
]


def __getattr__(name: str) -> Any:
    """
    Retrieve a module-level utility symbol by name.
    
    Parameters:
        name: The attribute name to resolve. Supported values are "validate_config",
            "init_db", "TrainingConfig", "TrainingMetric", and "db".
    
    Returns:
        The requested utility symbol (a function, class, or database object).
    
    Raises:
        AttributeError: If `name` is not a supported utility name.
    """
    if name == "validate_config":
        from utils.config_validator import validate_config

        return validate_config
    if name in {"init_db", "TrainingConfig", "TrainingMetric", "db"}:
        from utils.database import TrainingConfig, TrainingMetric, db, init_db

        return {
            "init_db": init_db,
            "TrainingConfig": TrainingConfig,
            "TrainingMetric": TrainingMetric,
            "db": db,
        }[name]
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)
