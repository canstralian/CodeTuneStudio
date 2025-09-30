"""Centralized configuration management for CodeTuneStudio."""

import os


class Config:
    """Centralized configuration management with environment variable access."""

    # Database Configuration
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "sqlite:///database.db")
    SQL_DEBUG: bool = os.environ.get("SQL_DEBUG", "").lower() == "true"

    # API Keys
    OPENAI_API_KEY: str | None = os.environ.get("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: str | None = os.environ.get("ANTHROPIC_API_KEY")

    # Argilla Configuration
    ARGILLA_WORKSPACE: str | None = os.environ.get("ARGILLA_WORKSPACE")
    ARGILLA_API_URL: str = os.environ.get("ARGILLA_API_URL", "https://api.argilla.io")
    ARGILLA_API_KEY: str | None = os.environ.get("ARGILLA_API_KEY")

    # Hugging Face
    HF_TOKEN: str | None = os.environ.get("HF_TOKEN")

    # Streamlit/Application
    SPACE_ID: str | None = os.environ.get("SPACE_ID")

    # Distributed Training
    MASTER_ADDR: str = os.environ.get("MASTER_ADDR", "localhost")
    MASTER_PORT: str = os.environ.get("MASTER_PORT", "12355")

    # Training Defaults
    VALID_MODELS: set = {"CodeT5", "Replit-v1.5"}
    AVAILABLE_DATASETS: set = {
        "code_search_net",
        "python_code_instructions",
        "github_code_snippets",
        "argilla_code_dataset",
        "google/code_x_glue_ct_code_to_text",
        "redashu/python_code_instructions",
    }

    @classmethod
    def validate(cls) -> list[str]:
        """
        Validate required configuration and return list of errors.

        Returns:
            List of error messages, empty if all valid
        """
        errors = []

        # Validate critical configuration
        if not cls.DATABASE_URL:
            errors.append("DATABASE_URL not configured")

        # Warn about missing optional API keys
        if not cls.OPENAI_API_KEY:
            errors.append("Warning: OPENAI_API_KEY not set - OpenAI plugin disabled")
        if not cls.ANTHROPIC_API_KEY:
            errors.append(
                "Warning: ANTHROPIC_API_KEY not set - Anthropic plugin disabled"
            )
        if not cls.ARGILLA_API_KEY:
            errors.append(
                "Warning: ARGILLA_API_KEY not set - Argilla integration disabled"
            )

        return errors

    @classmethod
    def get_database_config(cls) -> dict:
        """
        Get database configuration dictionary for Flask-SQLAlchemy.

        Returns:
            Dictionary with database configuration
        """
        return {
            "SQLALCHEMY_DATABASE_URI": cls.DATABASE_URL,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "SQLALCHEMY_ENGINE_OPTIONS": {
                "pool_size": 10,
                "max_overflow": 20,
                "pool_timeout": 30,
                "pool_recycle": 1800,
                "pool_pre_ping": True,
                "echo": cls.SQL_DEBUG,
            },
        }


# Create a singleton instance for convenience
config = Config()
