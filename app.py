import logging
import os
import re
import time
from contextlib import contextmanager
from functools import lru_cache
from typing import Any, Optional

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
from components.tokenizer_builder import tokenizer_builder  # Add tokenizer builder
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
        """Provide a transactional scope with improved error handling and logging.

        Note: Flask-SQLAlchemy manages sessions automatically. This context manager
        provides explicit transaction boundaries for operations requiring it.
        """
        # Flask-SQLAlchemy's db.session is already a scoped session
        session = db.session
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database transaction failed: {e}", exc_info=True)
            raise
        # Note: No session.close() needed - Flask-SQLAlchemy handles cleanup

    @staticmethod
    @lru_cache(maxsize=1)
    def _load_custom_css() -> str | None:
        """Load and cache custom CSS with improved error handling"""
        css_path = "styles/custom.css"
        try:
            if os.path.exists(css_path):
                with open(css_path) as f:
                    return f.read()
            logger.warning(f"CSS file not found: {css_path}")
            return None
        except Exception as e:
            logger.exception(f"Failed to load CSS: {e}")
            return None

    def _configure_streamlit(self) -> None:
        """Configure Streamlit UI with cached CSS loading"""
        try:
            st.set_page_config(
                page_title="ML Model Fine-tuning",
                page_icon="🚀",
                layout="wide",
                initial_sidebar_state="expanded"
                if os.environ.get("SPACE_ID")
                else "auto",
            )
            css_content = self._load_custom_css()
            if css_content:
                st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
        except Exception as e:
            logger.error(f"Streamlit configuration failed: {e}", exc_info=True)
            msg = f"Failed to configure Streamlit: {e}"
            raise RuntimeError(msg)

    def _load_plugins(self) -> None:
        """Load plugins with improved error handling and path management"""
        try:
            # Get absolute path to plugins directory
            plugins_dir = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "plugins")
            )
            logger.info(f"Loading plugins from: {plugins_dir}")

            try:
                # Clear existing registrations to prevent duplicates
                registry.clear_tools()
            except Exception as e:
                logger.warning(f"Failed to clear tools registry: {e!s}")
                # Continue execution as this is not a critical error

            try:
                # Discover and load plugins
                registry.discover_tools(plugins_dir)
                tools = registry.list_tools()

                # Log successful plugin loading
                logger.info("=== Plugin Loading Status ===")
                if tools:
                    logger.info(f"Successfully loaded {len(tools)} tools:")
                    for tool in tools:
                        logger.info(f"- {tool}")
                else:
                    logger.info("No plugins were loaded")
                logger.info("=========================")

            except Exception as e:
                logger.error(f"Error during plugin discovery: {e!s}", exc_info=True)
                # Continue execution with empty tools list
                tools = []

        except Exception as e:
            logger.error(f"Plugin loading system error: {e!s}", exc_info=True)
            # Allow application to continue without plugins

    def setup_sidebar(self) -> None:
        """Configure sidebar with cached plugin information"""
        with st.sidebar:
            st.title("ML Model Fine-tuning")
            st.markdown("---")

            tools = registry.list_tools()
            st.markdown("### Available Plugins")
            if tools:
                for tool in tools:
                    st.text(f"✓ {tool}")
            else:
                st.warning("No plugins available")

            st.markdown("---")
            self._render_navigation()

    def _render_navigation(self) -> None:
        """Render navigation section"""
        st.markdown("""
        ### Navigation
        - [Dataset Selection](#dataset-selection)
        - [Training Configuration](#training-configuration)
        - [Training Progress](#training-progress)
        - [Experiment Comparison](#experiment-comparison)
        - [Documentation](#documentation)
        ---
        ### About
        Fine-tune ML models with advanced monitoring
        """)

    @staticmethod
    def sanitize_string(value: str, max_length: int = 200) -> str:
        """Sanitize string input to prevent injection attacks.

        Args:
            value: String to sanitize
            max_length: Maximum allowed length

        Returns:
            Sanitized string

        Raises:
            ValueError: If input is invalid
        """
        if not isinstance(value, str):
            raise ValueError(f"Expected string, got {type(value)}")

        # Remove null bytes and control characters
        value = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', value)

        # Trim to max length
        value = value[:max_length].strip()

        if not value:
            raise ValueError("String cannot be empty after sanitization")

        return value

    @staticmethod
    def validate_config_values(config: dict[str, Any]) -> list[str]:
        """Validate configuration values with comprehensive checks.

        Args:
            config: Configuration dictionary to validate

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        # Validate model_type
        if "model_type" in config:
            try:
                model_type = MLFineTuningApp.sanitize_string(config["model_type"], max_length=50)
                if not re.match(r'^[a-zA-Z0-9_\-/]+$', model_type):
                    errors.append("model_type contains invalid characters")
            except ValueError as e:
                errors.append(f"model_type validation failed: {e}")

        # Validate numeric ranges (in addition to database model validation)
        if "batch_size" in config:
            if not isinstance(config["batch_size"], int) or config["batch_size"] <= 0:
                errors.append("batch_size must be a positive integer")

        if "learning_rate" in config:
            if not isinstance(config["learning_rate"], (int, float)):
                errors.append("learning_rate must be numeric")
            elif config["learning_rate"] <= 0 or config["learning_rate"] >= 1:
                errors.append("learning_rate must be between 0 and 1")

        if "epochs" in config:
            if not isinstance(config["epochs"], int) or config["epochs"] <= 0:
                errors.append("epochs must be a positive integer")

        if "max_seq_length" in config:
            if not isinstance(config["max_seq_length"], int) or config["max_seq_length"] <= 0:
                errors.append("max_seq_length must be a positive integer")

        if "warmup_steps" in config:
            if not isinstance(config["warmup_steps"], int) or config["warmup_steps"] < 0:
                errors.append("warmup_steps must be a non-negative integer")

        return errors

    def save_training_config(self, config: dict[str, Any], dataset: str) -> int | None:
        """Save training configuration with comprehensive validation and sanitization.

        Args:
            config: Training configuration dictionary
            dataset: Dataset name

        Returns:
            Configuration ID if successful, None otherwise
        """
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

        # Validate configuration values
        validation_errors = self.validate_config_values(config)
        if validation_errors:
            for error in validation_errors:
                logger.error(f"Configuration validation error: {error}")
            return None

        try:
            # Sanitize string inputs
            model_type = self.sanitize_string(config["model_type"], max_length=50)
            dataset_name = self.sanitize_string(dataset, max_length=100)

            with self.flask_app.app_context():
                with self.session_scope() as session:
                    # Database model will perform additional validation via @validates decorators
                    training_config = TrainingConfig(
                        model_type=model_type,
                        dataset_name=dataset_name,
                        batch_size=config["batch_size"],
                        learning_rate=config["learning_rate"],
                        epochs=config["epochs"],
                        max_seq_length=config["max_seq_length"],
                        warmup_steps=config["warmup_steps"],
                    )
                    session.add(training_config)
                    session.flush()
                    logger.info(f"Saved training config {training_config.id} for {model_type}")
                    return training_config.id
        except ValueError as e:
            logger.error(f"Input validation failed: {e}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"Failed to save training configuration: {e}", exc_info=True)
            return None

    def run(self) -> None:
        """Run the application with improved error boundaries and state management"""
        try:
            self.setup_sidebar()
            st.markdown("# ML Model Fine-tuning Platform")

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


def main() -> None:
    """Application entry point with improved error handling"""
    try:
        app = MLFineTuningApp()
        app.run()
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        st.error(
            "A critical error occurred. Please reload the page or contact support."
        )


if __name__ == "__main__":
    main()
