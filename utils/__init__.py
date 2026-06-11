"""Utility modules for CodeTuneStudio.

Database-backed symbols are loaded lazily so subpackages such as
``utils.plugins`` remain importable in lightweight analysis environments where
Flask database dependencies are not installed.
"""

from utils.config_validator import validate_config

__all__ = [
    "TrainingConfig",
    "TrainingMetric",
    "db",
    "init_db",
    "validate_config",
]


def __getattr__(name: str) -> object:
    """
    Lazily resolve and return selected database-backed attributes when accessed on the module.
    
    Parameters:
        name (str): Attribute name requested from the module; supported values are "TrainingConfig", "TrainingMetric", "db", and "init_db".
    
    Returns:
        object: The requested attribute object corresponding to name.
    
    Raises:
        AttributeError: If name is not one of the supported attributes.
    """
    if name in {"TrainingConfig", "TrainingMetric", "db", "init_db"}:
        from utils.database import (  # noqa: PLC0415
            TrainingConfig,
            TrainingMetric,
            db,
            init_db,
        )

        return {
            "TrainingConfig": TrainingConfig,
            "TrainingMetric": TrainingMetric,
            "db": db,
            "init_db": init_db,
        }[name]
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)
