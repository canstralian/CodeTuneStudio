"""Utility modules for CodeTuneStudio.

This module serves as the entry point for utility functions and classes used throughout the CodeTuneStudio application. It provides convenient access to configuration validation tools and database-related components.

Imported and exported items include:
- TrainingConfig: A database model class for storing training configurations.
- TrainingMetric: A database model class for storing training metrics.
- db: The SQLAlchemy database instance for managing database connections and operations.
- init_db: A function to initialize the database schema and connections.
- validate_config: A function to validate configuration dictionaries against predefined schemas.

These utilities support the core functionality of training data management and configuration handling in CodeTuneStudio.
"""

from utils.config_validator import validate_config
from utils.database import TrainingConfig, TrainingMetric, db, init_db

__all__ = [
    "TrainingConfig",
    "TrainingMetric",
    "db",
    "init_db",
    "validate_config",
]
