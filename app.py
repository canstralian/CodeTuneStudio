from typing import Optional, Dict, Any, List
import os
import logging
import time
from contextlib import contextmanager
from functools import lru_cache

# Third-party imports
import streamlit as st
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.pool import QueuePool

# Local imports
from components.dataset_selector import dataset_browser, validate_dataset_name
from components.parameter_config import training_parameters
from components.training_monitor import training_monitor
from components.experiment_compare import experiment_compare
from components.version_manager import version_manager
from components.plugin_manager import plugin_manager
from utils.config_validator import validate_config
from utils.database import init_db, TrainingConfig, db
from utils.plugins.registry import registry

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(pathname)s:%(lineno)d'
)
logger = logging.getLogger(__name__)

class MLFineTuningApp:
    def __init__(self):
        """Initialize the application with improved error handling and caching"""
        self.flask_app = Flask(__name__)
        self._configure_database()
        self._configure_streamlit()

        # Load plugins only once during initialization
        self._load_plugins()

        self._initialize_database_with_retry()

    def _configure_database(self) -> None:
        """Configure database with optimized settings and connection pooling"""
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is not set")

        # Optimized database configuration
        self.flask_app.config.update({
            'SQLALCHEMY_DATABASE_URI': database_url,
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'SQLALCHEMY_ENGINE_OPTIONS': {
                'poolclass': QueuePool,
                'pool_size': 10,
                'max_overflow': 20,
                'pool_timeout': 30,
                'pool_recycle': 1800,
                'pool_pre_ping': True,
                'echo': bool(os.environ.get('SQL_DEBUG', False))
            }
        })

    def _initialize_database_with_retry(self, max_retries: int = 3, base_delay: float = 1.0) -> None:
        """Initialize database with exponential backoff retry strategy"""
        for attempt in range(max_retries):
            try:
                with self.flask_app.app_context():
                    init_db(self.flask_app)
                    logger.info("Database initialized successfully")
                return
            except Exception as e:
                delay = base_delay * (2 ** attempt)
                if attempt == max_retries - 1:
                    logger.critical(f"Failed to initialize database after {max_retries} attempts: {e}")
                    raise
                logger.warning(f"Database initialization attempt {attempt + 1} failed: {e}")
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
    def _load_custom_css() -> Optional[str]:
        """Load and cache custom CSS with improved error handling"""
        css_path = "styles/custom.css"
        try:
            if os.path.exists(css_path):
                with open(css_path) as f:
                    return f.read()
            logger.warning(f"CSS file not found: {css_path}")
            return None
        except Exception as e:
            logger.error(f"Failed to load CSS: {e}")
            return None

    def _configure_streamlit(self) -> None:
        """Configure Streamlit UI with cached CSS loading"""
        try:
            st.set_page_config(
                page_title="ML Model Fine-tuning",
                page_icon="🚀",
                layout="wide",
                initial_sidebar_state="expanded" if os.environ.get('SPACE_ID') else "auto"
            )
            css_content = self._load_custom_css()
            if css_content:
                st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
        except Exception as e:
            logger.error(f"Streamlit configuration failed: {e}", exc_info=True)
            raise RuntimeError(f"Failed to configure Streamlit: {e}")

    def _load_plugins(self) -> None:
        """Load plugins with deduplication and improved error handling"""
        try:
            plugins_dir = os.path.join(os.path.dirname(__file__), "plugins")
            logger.info(f"Loading plugins from: {plugins_dir}")

            try:
                # Clear existing registrations to prevent duplicates
                registry.clear_tools()
            except Exception as e:
                logger.warning(f"Failed to clear tools registry: {str(e)}")
                # Continue execution as this is not a critical error

            try:
                registry.discover_tools(plugins_dir)
                tools = registry.list_tools()
                logger.info("=== Plugin Loading Status ===")
                logger.info(f"Successfully loaded {len(tools)} tools:")
                for tool in tools:
                    logger.info(f"- {tool}")
                logger.info("=========================")
            except Exception as e:
                logger.error(f"Error during plugin discovery: {str(e)}", exc_info=True)
                # Continue execution to allow application to run without plugins
                tools = []

        except Exception as e:
            logger.error(f"Plugin loading system error: {str(e)}", exc_info=True)
            # Allow application to continue without plugins
            pass

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

    @staticmethod
    def _render_navigation() -> None:
        """Render navigation section"""
        st.markdown("""
        ### Navigation
        - [Dataset Selection](#dataset-selection)
        - [Training Configuration](#training-configuration)
        - [Training Progress](#training-progress)
        - [Experiment Comparison](#experiment-comparison)
        ---
        ### About
        Fine-tune ML models with advanced monitoring
        """)

    def save_training_config(self, config: Dict[str, Any], dataset: str) -> Optional[int]:
        """Save training configuration with improved validation and error handling"""
        if not isinstance(config, dict):
            logger.error(f"Invalid configuration type: {type(config)}")
            return None

        required_fields = ['model_type', 'batch_size', 'learning_rate', 'epochs', 
                         'max_seq_length', 'warmup_steps']

        missing_fields = [field for field in required_fields if field not in config]
        if missing_fields:
            logger.error(f"Missing required configuration fields: {missing_fields}")
            return None

        try:
            with self.flask_app.app_context():
                with self.session_scope() as session:
                    training_config = TrainingConfig(
                        model_type=config['model_type'],
                        dataset_name=dataset,
                        batch_size=config['batch_size'],
                        learning_rate=config['learning_rate'],
                        epochs=config['epochs'],
                        max_seq_length=config['max_seq_length'],
                        warmup_steps=config['warmup_steps']
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
            st.markdown("# ML Model Fine-tuning Platform")

            # Add plugin manager section
            with st.expander("Plugin Management", expanded=False):
                plugin_manager()

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
                    col1, col2 = st.columns(2)
                    with col1:
                        training_monitor()
                    with col2:
                        experiment_compare()

                if st.button("Export Configuration"):
                    st.json(config)
            else:
                st.error("Failed to save configuration. Please try again.")

        except Exception as e:
            logger.error(f"Application error: {e}", exc_info=True)
            st.error("An unexpected error occurred. Please try again or contact support.")
            if hasattr(st.session_state, 'current_config_id'):
                del st.session_state.current_config_id

def main():
    """Application entry point with improved error handling"""
    try:
        app = MLFineTuningApp()
        app.run()
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        st.error("A critical error occurred. Please reload the page or contact support.")

if __name__ == "__main__":
    main()