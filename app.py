"""
CodeTuneStudio - ML Model Fine-tuning Application

Main entry point for the Streamlit/Flask hybrid application providing
ML model fine-tuning with PEFT/LoRA, plugin architecture, and experiment tracking.
"""

import logging
import os
import time
from contextlib import contextmanager
from typing import Any, Dict, Optional

import streamlit as st
from flask import Flask

from components.dataset_selector import dataset_browser, validate_dataset_name
from components.experiment_compare import experiment_compare
from components.parameter_config import training_parameters
from components.training_monitor import training_monitor
from utils.config_validator import validate_config
from utils.database import TrainingConfig, db, init_db
from utils.plugins.registry import registry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MLFineTuningApp:
    """
    Main application class for ML model fine-tuning with Streamlit UI and Flask backend.
    
    This class orchestrates the hybrid Streamlit/Flask application, managing database
    connections, plugin loading, and the complete training workflow.
    """
    
    def __init__(self):
        """Initialize the ML fine-tuning application with database and plugins."""
        self.flask_app = Flask(__name__)
        self._configure_database()
        self._initialize_database_with_retry()
        self._configure_streamlit()
        self._load_plugins()
        logger.info("MLFineTuningApp initialized successfully")
    
    def _configure_database(self) -> None:
        """Configure database connection with environment-based settings."""
        database_url = os.environ.get("DATABASE_URL", "sqlite:///database.db")
        
        self.flask_app.config.update({
            "SQLALCHEMY_DATABASE_URI": database_url,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "SQLALCHEMY_ENGINE_OPTIONS": {
                "pool_size": 10,
                "pool_recycle": 1800,
                "pool_pre_ping": True,
                "max_overflow": 20,
                "pool_timeout": 30
            }
        })
        
        logger.info(f"Database configured: {database_url}")
    
    def _initialize_database_with_retry(self, max_retries: int = 1) -> None:
        """
        Initialize database with exponential backoff retry logic.
        
        Args:
            max_retries: Maximum number of retry attempts before fallback
        """
        for attempt in range(max_retries):
            try:
                with self.flask_app.app_context():
                    init_db(self.flask_app)
                    db.create_all()
                logger.info("Database initialized successfully")
                return
            except Exception as e:
                logger.warning(
                    f"Database initialization attempt {attempt + 1}/{max_retries} failed: {e}"
                )
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
        
        # If we get here, all retries failed - fall back to SQLite
        logger.error("Max retries reached, falling back to SQLite")
        self.flask_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///fallback.db"
        try:
            with self.flask_app.app_context():
                init_db(self.flask_app)
                db.create_all()
        except Exception as fallback_error:
            logger.error(f"Fallback database also failed: {fallback_error}")
    
    @contextmanager
    def session_scope(self):
        """
        Provide a transactional scope for database operations.
        
        Yields:
            Database session with automatic commit/rollback
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
        Load custom CSS styles from styles.css if available.
        
        Returns:
            CSS content as string or None if not found
        """
        css_path = "styles.css"
        if os.path.exists(css_path):
            try:
                with open(css_path) as f:
                    return f.read()
            except Exception as e:
                logger.warning(f"Failed to load custom CSS: {e}")
                return None
        return None
    
    def _configure_streamlit(self) -> None:
        """Configure Streamlit page settings and custom styling."""
        try:
            st.set_page_config(
                page_title="CodeTuneStudio - ML Fine-tuning",
                page_icon="🎵💻",
                layout="wide",
                initial_sidebar_state="expanded"
            )
            
            # Load custom CSS
            custom_css = self._load_custom_css()
            if custom_css:
                st.markdown(f"<style>{custom_css}</style>", unsafe_allow_html=True)
            
            logger.info("Streamlit configured successfully")
        except Exception as e:
            logger.error(f"Failed to configure Streamlit: {e}")
            raise RuntimeError(f"Streamlit configuration failed: {e}")
    
    def _load_plugins(self) -> None:
        """Discover and load plugins from the plugins directory."""
        try:
            # Clear existing tools to prevent duplicates
            registry.clear_tools()
            
            # Discover plugins
            plugin_dir = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "plugins"
            )
            registry.discover_tools("plugins")
            
            tools = registry.list_tools()
            logger.info(f"Loaded {len(tools)} plugins: {tools}")
        except Exception as e:
            logger.error(f"Plugin loading error: {e}", exc_info=True)
    
    def setup_sidebar(self) -> None:
        """Setup the Streamlit sidebar with plugin information."""
        with st.sidebar:
            st.title("ML Model Fine-tuning")
            st.markdown("---")
            
            # Display loaded plugins
            tools = registry.list_tools()
            if tools:
                st.markdown("### Available Plugins")
                for tool in tools:
                    st.text(f"✓ {tool}")
            else:
                st.warning("No plugins available")
            
            st.markdown("---")
            st.markdown("### About")
            st.markdown(
                "CodeTuneStudio provides parameter-efficient fine-tuning "
                "for ML models with experiment tracking and plugin support."
            )
    
    def _render_navigation(self) -> None:
        """Render the main navigation/header."""
        st.markdown(
            """
            <div style='text-align: center; padding: 20px;'>
                <h1>🎵💻 CodeTuneStudio</h1>
                <p>ML Model Fine-tuning with PEFT/LoRA</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    def save_training_config(
        self, 
        config: Dict[str, Any], 
        dataset_name: str
    ) -> Optional[int]:
        """
        Save training configuration to database.
        
        Args:
            config: Training configuration dictionary
            dataset_name: Name of the dataset
            
        Returns:
            Configuration ID if successful, None otherwise
        """
        # Validate config type
        if not isinstance(config, dict):
            logger.error("Configuration must be a dictionary")
            return None
        
        # Check required fields
        required_fields = [
            "model_type", "batch_size", "learning_rate", 
            "epochs", "max_seq_length", "warmup_steps"
        ]
        if not all(field in config for field in required_fields):
            logger.error(f"Missing required fields: {required_fields}")
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
                    warmup_steps=config["warmup_steps"]
                )
                session.add(training_config)
                session.flush()  # Get ID before commit
                config_id = training_config.id
                logger.info(f"Saved training configuration with ID: {config_id}")
                return config_id
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}", exc_info=True)
            return None
    
    def run(self) -> None:
        """Main application loop - render the Streamlit interface."""
        try:
            # Setup sidebar
            self.setup_sidebar()
            
            # Render header
            self._render_navigation()
            
            # Check session state
            if "current_page" not in st.session_state:
                st.session_state.current_page = "main"
            
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
            with st.expander("⚙️ Training Configuration", expanded=True):
                config = training_parameters()
                
                if not isinstance(config, dict):
                    st.error("Invalid configuration format")
                    return
                
                # Validate configuration
                errors = validate_config(config)
                if errors:
                    for error in errors:
                        st.error(error)
                    return
                
                # Save configuration
                if st.button("Save Configuration"):
                    config_id = self.save_training_config(config, dataset_name)
                    if config_id:
                        st.success(f"Configuration saved with ID: {config_id}")
                        st.session_state.current_config_id = config_id
                        st.json(config)
                    else:
                        st.error("Failed to save configuration. Please try again.")
            
            # Training monitor
            with st.expander("📈 Training Monitor", expanded=False):
                training_monitor()
            
            # Experiment comparison
            with st.expander("🔍 Experiment Comparison", expanded=False):
                experiment_compare()
                
        except Exception as e:
            logger.error(f"Application error: {e}", exc_info=True)
            st.error("An unexpected error occurred. Please try again or contact support.")


def main() -> None:
    """Application entry point."""
    try:
        app = MLFineTuningApp()
        app.run()
    except Exception as e:
        logger.error(f"Critical application error: {e}", exc_info=True)
        st.error("A critical error occurred. Please reload the page or contact support.")


if __name__ == "__main__":
    main()
