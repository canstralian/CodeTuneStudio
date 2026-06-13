"""Utility modules for CodeTuneStudio.

The package initializer intentionally avoids importing database modules eagerly so
plugin discovery and lightweight tests do not require optional web/database
runtime dependencies before they are needed.
"""

__all__ = [
    "validate_config",
    "init_db",
    "TrainingConfig",
    "TrainingMetric",
    "db",
]


def __getattr__(name: str):
    """
    Lazily load and return select public utility symbols on first attribute access.
    
    This module attribute hook exposes a small set of utilities without performing
    eager imports of optional runtime dependencies. Supported attribute names are
    "validate_config", "init_db", "TrainingConfig", "TrainingMetric", and "db".
    
    Parameters:
        name (str): The attribute name being accessed.
    
    Returns:
        object: The requested module-level object corresponding to `name`.
    
    Raises:
        AttributeError: If `name` is not one of the supported attribute names.
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
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
