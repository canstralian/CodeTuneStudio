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
