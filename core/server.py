"""
Server module for CodeTune Studio.

This module contains the main application logic refactored from app.py,
providing a clean separation between server logic and CLI entrypoint.
"""

import logging
import os
import time
from contextlib import contextmanager
from functools import lru_cache
from typing import Any, Dict, Optional

# Third-party imports
import streamlit as st
from flask import Flask
from sqlalchemy.pool import QueuePool

# Local imports
from components.dataset_selector import dataset_browser, validate_dataset_name
from components.documentation_viewer import documentation_viewer
from components.experiment_compare import experiment_compare
from components.parameter_config import training_parameters
from components.plugin_manager import plugin_manager
from components.tokenizer_builder import tokenizer_builder
from components.training_monitor import training_monitor
from utils.config_validator import validate_config
from utils.database import TrainingConfig, db, init_db
from utils.plugins.registry import registry

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(pathname)s:%(lineno)d",
)
logger = logging.getLogger(__name__)


class MLFineTuningApp:
    """
    MLFineTuningApp: A comprehensive application for fine-tuning machine learning models.

    This class integrates Flask for backend operations, Streamlit for the user interface,
    and provides robust database management, plugin loading, and training configuration
    handling. It supports dataset selection, model training monitoring, experiment comparison,
    and plugin-based extensibility.

    Attributes:
        flask_app (Flask): The Flask application instance for backend operations.
        (Other attributes are managed internally via configuration and initialization methods.)

    Methods:
        __init__(): Initializes the app with database, Streamlit, and plugin configurations.
        _configure_database(): Sets up database connection with optimized pooling and settings.
        _initialize_database_with_retry(max_retries=3, base_delay=1.0): Initializes the database
            with retry logic and fallback to SQLite if needed.
        session_scope(): Context manager for database sessions with error handling.
        _load_custom_css(): Caches and loads custom CSS for Streamlit UI.
        _configure_streamlit(): Configures Streamlit page settings and applies custom CSS.
        _load_plugins(): Discovers and loads plugins from the plugins directory.
        setup_sidebar(): Sets up the Streamlit sidebar with plugin info and navigation.
        _render_navigation(): Renders navigation links in the sidebar.
        save_training_config(config, dataset): Validates and saves training configuration to DB.
        run(): Main method to run the Streamlit app, handling UI, validation, and training flow.

    Usage:
        Instantiate the class and call run() to start the application. Ensure environment
        variables like DATABASE_URL are set for proper configuration. Plugins should be placed
        in the 'plugins' directory for automatic loading.

    Raises:
        RuntimeError: If Streamlit configuration fails.
        Various exceptions during database or plugin operations, logged and handled gracefully.
    """

    def __init__(self) -> None:
        """Initialize the application with improved error handling and caching"""
        self.flask_app = Flask(__name__)
        self._configure_database()
        self._configure_streamlit()

        # Load plugins only once during initialization
        self._load_plugins()

        self._initialize_database_with_retry()

    def _configure_database(self) -> None:
        """Configure database with optimized settings and connection pooling"""
        database_url = os.environ.get("DATABASE_URL", "sqlite:///database.db")

        # Optimized database configuration
        self.flask_app.config.update(
            {
                "SQLALCHEMY_DATABASE_URI": database_url,
                "SQLALCHEMY_TRACK_MODIFICATIONS": False,
                "SQLALCHEMY_ENGINE_OPTIONS": {
                    "poolclass": QueuePool,
                    "pool_size": 10,
                    "max_overflow": 20,
                    "pool_timeout": 30,
                    "pool_recycle": 1800,
                    "pool_pre_ping": True,
                    "echo": bool(os.environ.get("SQL_DEBUG", False)),
                },
            }
        )
        logger.info(f"Database configured with URL: {database_url}")

    def _initialize_database_with_retry(
        self, max_retries: int = 3, base_delay: float = 1.0
    ) -> None:
        """Initialize database with exponential backoff retry strategy"""
        for attempt in range(max_retries):
            try:
                with self.flask_app.app_context():
                    init_db(self.flask_app)
                    logger.info("Database initialized successfully")
                return
            except Exception as e:
                delay = base_delay * (2**attempt)
                if attempt == max_retries - 1:
                    logger.critical(
                        f"Failed to initialize database after {max_retries} attempts: {e}"
                    )
                    # Create fallback SQLite database if main DB fails
                    try:
                        self.flask_app.config["SQLALCHEMY_DATABASE_URI"] = (
                            "sqlite:///fallback.db"
                        )
                        with self.flask_app.app_context():
                            init_db(self.flask_app)
                            logger.warning("Fallback to SQLite database successful")
                        return
                    except Exception as fallback_error:
                        logger.critical(
                            f"Fallback database initialization failed: {fallback_error}"
                        )
                        raise
                logger.warning(
                    f"Database initialization attempt {attempt + 1} failed: {e}"
                )
                time.sleep(delay)

    @contextmanager
    def session_scope(self):
        """Provide a transactional scope with improved error handling and logging"""
        session = db.session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database transaction failed: {e}", exc_info=True)
            raise
        finally:
            session.close()

    @staticmethod
    @lru_cache(maxsize=1)
    def _load_custom_css() -> str | None:
        """Load and cache custom CSS with improved error handling"""
        css_path = "styles/custom.css"
        if os.path.exists(css_path):
            try:
                with open(css_path) as f:
                    return f.read()
            except Exception as e:
                logger.warning(f"Failed to load custom CSS: {e}")
                return None
        return None

    def _configure_streamlit(self) -> None:
        """Configure Streamlit with enhanced settings and custom CSS"""
        try:
            st.set_page_config(
                page_title="CodeTune Studio - ML Fine-tuning",
                page_icon="🎵",
                layout="wide",
                initial_sidebar_state="expanded",
                menu_items={
                    "Get Help": "https://github.com/canstralian/CodeTuneStudio",
                    "Report a bug": "https://github.com/canstralian/CodeTuneStudio/issues",
                    "About": "CodeTune Studio - Advanced ML Model Fine-tuning Platform",
                },
            )

            # Load and apply custom CSS if available
            custom_css = self._load_custom_css()
            if custom_css:
                st.markdown(f"<style>{custom_css}</style>", unsafe_allow_html=True)

        except Exception as e:
            logger.error(f"Streamlit configuration failed: {e}")
            raise RuntimeError(f"Failed to configure Streamlit: {e}") from e

    def _load_plugins(self) -> None:
        """Load plugins with improved error handling and logging"""
        try:
            # Clear any existing plugins
            registry.clear_tools()

            # Discover plugins in the plugins directory
            plugin_dir = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "plugins")
            )
            registry.discover_tools(plugin_dir)

            plugins = registry.list_tools()
            logger.info(f"Loaded {len(plugins)} plugins: {', '.join(plugins)}")
        except Exception as e:
            logger.error(f"Failed to load plugins: {e}", exc_info=True)
            # Don't raise - plugins are optional

    def setup_sidebar(self) -> None:
        """Setup sidebar with enhanced plugin information and navigation"""
        with st.sidebar:
            st.title("ML Model Fine-tuning")

            st.markdown("---")
            st.markdown("### 🔌 Loaded Plugins")

            plugins = registry.list_tools()
            if plugins:
                for plugin in plugins:
                    st.text(f"✓ {plugin}")
            else:
                st.warning("No plugins available")

            st.markdown("---")
            self._render_navigation()

    def _render_navigation(self) -> None:
        """Render navigation links with improved styling"""
        st.markdown(
            """
            ### 📚 Resources
            - [Documentation](https://github.com/canstralian/CodeTuneStudio/wiki)
            - [API Reference](https://github.com/canstralian/CodeTuneStudio/blob/main/API.md)
            - [Examples](https://github.com/canstralian/CodeTuneStudio/tree/main/examples)
            - [Report Issues](https://github.com/canstralian/CodeTuneStudio/issues)
        """
        )

    def save_training_config(self, config: dict[str, Any], dataset: str) -> int | None:
        """Save training configuration with improved validation and error handling"""
        if not isinstance(config, dict):
            logger.error(f"Invalid configuration type: {type(config)}")
            return None

        required_fields = [
            "model_type",
            "batch_size",
            "learning_rate",
            "epochs",
            "max_seq_length",
            "warmup_steps",
        ]

        missing_fields = [field for field in required_fields if field not in config]
        if missing_fields:
            logger.error(f"Missing required configuration fields: {missing_fields}")
            return None

        try:
            with self.flask_app.app_context():
                with self.session_scope() as session:
                    training_config = TrainingConfig(
                        model_type=config["model_type"],
                        dataset_name=dataset,
                        batch_size=config["batch_size"],
                        learning_rate=config["learning_rate"],
                        epochs=config["epochs"],
                        max_seq_length=config["max_seq_length"],
                        warmup_steps=config["warmup_steps"],
                    )
                    session.add(training_config)
                    session.flush()
                    return training_config.id
        except Exception as e:
            logger.error(f"Failed to save training configuration: {e}", exc_info=True)
            return None

    def run(self) -> None:
        """Run the application with improved error boundaries and state management"""
        try:
            self.setup_sidebar()

            # Enhanced header with visual appeal
            st.markdown(
                """
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                            padding: 2rem; 
                            border-radius: 16px; 
                            margin-bottom: 2rem;
                            box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);">
                    <h1 style="color: white; 
                               margin: 0; 
                               text-align: center;
                               font-size: 2.5rem;
                               text-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                               -webkit-text-fill-color: white;">
                        🚀 ML Model Fine-tuning Platform
                    </h1>
                    <p style="color: rgba(255, 255, 255, 0.9); 
                              text-align: center; 
                              margin-top: 0.5rem;
                              font-size: 1.1rem;">
                        Advanced training and optimization for machine learning models
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if "page" not in st.session_state:
                st.session_state.page = "main"

            with st.expander("Documentation, Plugins & Tools", expanded=False):
                tab1, tab2, tab3 = st.tabs(
                    ["Documentation", "Plugin Management", "Tokenizer Builder"]
                )
                with tab1:
                    documentation_viewer()
                with tab2:
                    plugin_manager()
                with tab3:
                    tokenizer_builder()

            # Dataset selection with validation
            selected_dataset = dataset_browser()
            if not selected_dataset or not validate_dataset_name(selected_dataset):
                st.warning("Please select a valid dataset to continue")
                return

            # Configuration handling with validation
            config = training_parameters()
            if not isinstance(config, dict):
                st.error("Invalid configuration format")
                return

            errors = validate_config(config)
            if errors:
                for error in errors:
                    st.error(error)
                return

            # Save configuration and proceed with training
            config_id = self.save_training_config(config, selected_dataset)
            if config_id:
                st.session_state.current_config_id = config_id

                with self.flask_app.app_context():
                    # Restructured layout to avoid nested columns
                    st.subheader("Training Progress")
                    training_monitor()

                    st.subheader("Experiment Analysis")
                    experiment_compare()

                if st.button("Export Configuration"):
                    st.json(config)
            else:
                st.error("Failed to save configuration. Please try again.")

        except Exception as e:
            logger.error(f"Application error: {e}", exc_info=True)
            st.error(
                "An unexpected error occurred. Please try again or contact support."
            )
            if hasattr(st.session_state, "current_config_id"):
                del st.session_state.current_config_id


def run_app() -> None:
    """
    Main application entry point.

    This function instantiates and runs the MLFineTuningApp.
    It's the primary entry point called by the CLI and legacy app.py.
    """
    try:
        app = MLFineTuningApp()
        app.run()
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        st.error(
            "A critical error occurred. Please reload the page or contact support."
        )
