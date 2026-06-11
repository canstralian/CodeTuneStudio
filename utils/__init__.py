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
    """Lazily expose common utility symbols without eager optional imports."""
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
