"""
CodeTuneStudio - Main Application Entry Point

This module provides the main entry point for the CodeTuneStudio application,
orchestrating both Streamlit UI and Flask backend for ML model fine-tuning.
"""

import logging
import os
import sys
import time
from contextlib import contextmanager
from typing import Any, Dict, Optional

import streamlit as st
from flask import Flask

# Import components
from components.dataset_selector import dataset_browser, validate_dataset_name
from components.experiment_compare import experiment_compare
from components.parameter_config import training_parameters
from components.training_monitor import training_monitor

# Import utilities
from utils.config_validator import validate_config
from utils.database import TrainingConfig, db, init_db
from utils.plugins.registry import registry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class MLFineTuningApp:
    """
    Main application class for ML model fine-tuning.

    Orchestrates the Streamlit UI and Flask backend, manages database
    connections, and handles plugin discovery.
    """

    def __init__(self) -> None:
        """Initialize the application with Flask backend and database."""
        self.flask_app = Flask(__name__)
        self._configure_database()
        self._initialize_database_with_retry()
        self._configure_streamlit()
        self._load_plugins()

    def _configure_database(self) -> None:
        """Configure database connection with environment variables."""
        database_url = os.environ.get("DATABASE_URL", "sqlite:///database.db")
        self.flask_app.config.update(
            {
                "SQLALCHEMY_DATABASE_URI": database_url,
                "SQLALCHEMY_TRACK_MODIFICATIONS": False,
                "SQLALCHEMY_ENGINE_OPTIONS": {
                    "pool_size": 10,
                    "pool_recycle": 1800,
                    "pool_pre_ping": True,
                    "max_overflow": 20,
                    "pool_timeout": 30,
                },
            }
        )
        logger.info(f"Configured database: {database_url}")

    def _initialize_database_with_retry(
        self, max_retries: int = 3, retry_delay: int = 2
    ) -> None:
        """
        Initialize database with retry logic and fallback to SQLite.

        Args:
            max_retries: Maximum number of connection attempts
            retry_delay: Delay between retries in seconds
        """
        for attempt in range(max_retries):
            try:
                with self.flask_app.app_context():
                    init_db(self.flask_app)
                    db.create_all()
                    logger.info("Database initialized successfully")
                    return
            except Exception as e:
                logger.warning(f"Database init attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                else:
                    logger.error("Falling back to SQLite database")
                    self.flask_app.config[
                        "SQLALCHEMY_DATABASE_URI"
                    ] = "sqlite:///fallback.db"
                    with self.flask_app.app_context():
                        init_db(self.flask_app)
                        db.create_all()

    @contextmanager
    def session_scope(self):
        """
        Provide a transactional scope for database operations.

        Yields:
            Database session with automatic commit/rollback

        Raises:
            Exception: On database operation failures
        """
        session = db.session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database error: {e}", exc_info=True)
            raise
        finally:
            session.close()

    def _load_custom_css(self) -> Optional[str]:
        """
        Load custom CSS from styles.css if available.

        Returns:
            CSS content as string or None if file not found
        """
        css_file = "styles.css"
        if os.path.exists(css_file):
            try:
                with open(css_file, encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Failed to load custom CSS: {e}")
        return None

    def _configure_streamlit(self) -> None:
        """Configure Streamlit page settings and custom styling."""
        try:
            st.set_page_config(
                page_title="CodeTuneStudio - ML Fine-Tuning",
                page_icon="🎵",
                layout="wide",
                initial_sidebar_state="expanded",
            )

            # Load custom CSS if available
            custom_css = self._load_custom_css()
            if custom_css:
                st.markdown(f"<style>{custom_css}</style>", unsafe_allow_html=True)
        except Exception as e:
            logger.error(f"Failed to configure Streamlit: {e}")
            raise RuntimeError("Streamlit configuration failed") from e

    def _load_plugins(self) -> None:
        """Discover and load plugins from the plugins directory."""
        try:
            # Clear existing tools to prevent duplicates
            registry.clear_tools()

            # Get the plugins directory path
            base_dir = os.path.dirname(os.path.abspath(__file__))
            plugins_dir = os.path.join(base_dir, "plugins")

            # Discover plugins
            registry.discover_tools(plugins_dir)

            # Log loaded plugins
            tools = registry.list_tools()
            if tools:
                logger.info(f"Loaded {len(tools)} plugins: {', '.join(tools)}")
            else:
                logger.warning("No plugins found")
        except Exception as e:
            logger.error(f"Failed to load plugins: {e}", exc_info=True)

    def setup_sidebar(self) -> None:
        """Setup sidebar with navigation and plugin information."""
        with st.sidebar:
            st.title("ML Model Fine-tuning")
            st.markdown("---")

            # Display loaded plugins
            tools = registry.list_tools()
            if tools:
                st.markdown("### 🔌 Available Plugins")
                for tool in tools:
                    st.text(f"✓ {tool}")
            else:
                st.warning("No plugins available")

            st.markdown("---")
            st.markdown("### 📚 Resources")
            st.markdown(
                """
                - [Documentation](https://github.com/canstralian/CodeTuneStudio)
                - [Report Issues](https://github.com/canstralian/CodeTuneStudio/issues)
                - [Community](https://github.com/canstralian/CodeTuneStudio/discussions)
                """
            )

    def _render_navigation(self) -> None:
        """Render navigation tabs."""
        st.markdown(
            """
            <div style="padding: 1rem 0;">
                <h1>🎵 CodeTuneStudio</h1>
                <p>Optimize and fine-tune your ML models with ease</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    def save_training_config(
        self, config: Dict[str, Any], dataset_name: str
    ) -> Optional[int]:
        """
        Save training configuration to database.

        Args:
            config: Training configuration dictionary
            dataset_name: Name of the dataset

        Returns:
            Config ID if successful, None otherwise
        """
        if not isinstance(config, dict):
            logger.error("Config must be a dictionary")
            return None

        required_fields = [
            "model_type",
            "batch_size",
            "learning_rate",
            "epochs",
            "max_seq_length",
            "warmup_steps",
        ]
        if not all(field in config for field in required_fields):
            logger.error("Config missing required fields")
            return None

        try:
            with self.session_scope() as session:
                training_config = TrainingConfig(
                    model_type=config["model_type"],
                    dataset_name=dataset_name,
                    batch_size=config["batch_size"],
                    learning_rate=config["learning_rate"],
                    epochs=config["epochs"],
                    max_seq_length=config["max_seq_length"],
                    warmup_steps=config["warmup_steps"],
                )
                session.add(training_config)
                session.flush()
                config_id = training_config.id
                logger.info(f"Saved training config with ID: {config_id}")
                return config_id
        except Exception as e:
            logger.error(f"Failed to save training config: {e}", exc_info=True)
            return None

    def run(self) -> None:
        """Run the main application interface."""
        try:
            # Setup sidebar
            self.setup_sidebar()

            # Render navigation
            self._render_navigation()

            # Initialize session state for navigation
            if "page" not in st.session_state:
                st.session_state.page = "main"

            # Main content area
            st.markdown("---")

            # Dataset selection
            with st.expander("📊 Dataset Selection", expanded=True):
                dataset_name = dataset_browser()
                if not dataset_name:
                    st.warning("Please select a valid dataset to continue")
                    return

                if not validate_dataset_name(dataset_name):
                    st.warning("Invalid dataset name format")
                    return

            # Training parameters
            with st.expander("⚙️ Training Parameters", expanded=True):
                config = training_parameters()
                if not isinstance(config, dict):
                    st.error("Invalid configuration format")
                    return

                # Validate configuration
                errors = validate_config(config, dataset_name)
                if errors:
                    st.error("Configuration validation failed:")
                    for error in errors:
                        st.error(f"- {error}")
                    return

                # Save configuration
                config_id = self.save_training_config(config, dataset_name)
                if config_id:
                    st.session_state.current_config_id = config_id
                    st.success(f"✓ Configuration saved (ID: {config_id})")
                else:
                    st.error("Failed to save configuration. Please try again.")
                    return

                # Display configuration
                if st.button("📋 Show Configuration"):
                    st.json(config)

            # Training monitor
            with st.expander("📈 Training Monitor", expanded=False):
                training_monitor()

            # Experiment comparison
            with st.expander("🔬 Experiment Comparison", expanded=False):
                experiment_compare()

        except Exception as e:
            logger.error(f"Application error: {e}", exc_info=True)
            st.error(
                "An unexpected error occurred. Please try again or contact support."
            )


def main() -> None:
    """Main entry point for the application."""
    try:
        app = MLFineTuningApp()
        app.run()
    except Exception as e:
        logger.error(f"Critical error: {e}", exc_info=True)
        st.error(
            "A critical error occurred. Please reload the page or contact support."
        )


if __name__ == "__main__":
    main()
