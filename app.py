import os
import logging
import time
from typing import Optional, Dict, Any
import streamlit as st
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.pool import QueuePool
from components.dataset_selector import dataset_browser, validate_dataset_name
from components.parameter_config import training_parameters
from components.training_monitor import training_monitor
from components.experiment_compare import experiment_compare
from utils.config_validator import validate_config
from utils.database import init_db, TrainingConfig, db
from functools import wraps
from contextlib import contextmanager

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MLFineTuningApp:
    """Main application class for ML model fine-tuning platform with enhanced error handling"""

    def __init__(self):
        """Initialize application components and database with connection pooling"""
        self.flask_app = Flask(__name__)

        # Enhanced database configuration
        self.flask_app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
        self.flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.flask_app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'poolclass': QueuePool,
            'pool_size': 10,
            'max_overflow': 20,
            'pool_timeout': 30,
            'pool_recycle': 1800,
        }

        self._configure_streamlit()
        with self.flask_app.app_context():
            self._init_database()

    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        try:
            yield db.session
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Database transaction failed: {str(e)}")
            raise
        finally:
            db.session.close()

    def _configure_streamlit(self) -> None:
        """Configure Streamlit UI settings with error handling"""
        try:
            is_huggingface = bool(os.environ.get('SPACE_ID'))
            st.set_page_config(
                page_title="ML Model Fine-tuning",
                page_icon="🚀",
                layout="wide",
                initial_sidebar_state="expanded" if is_huggingface else "auto"
            )
            self._load_custom_css()
        except Exception as e:
            logger.error(f"Failed to configure Streamlit: {str(e)}")
            raise

    def _load_custom_css(self) -> None:
        """Load custom CSS styles with proper error handling"""
        try:
            css_path = "styles/custom.css"
            if os.path.exists(css_path):
                with open(css_path) as f:
                    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
            else:
                logger.warning(f"Custom CSS file not found at {css_path}")
        except Exception as e:
            logger.error(f"Failed to load custom CSS: {str(e)}")
            # Continue without custom styling

    def _init_database(self) -> None:
        """Initialize database connection with retry logic"""
        max_retries = 3
        retry_delay = 1

        for attempt in range(max_retries):
            try:
                init_db(self.flask_app)
                logger.info("Database initialized successfully")
                return
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"Database initialization failed after {max_retries} attempts: {str(e)}")
                    raise
                logger.warning(f"Database initialization attempt {attempt + 1} failed: {str(e)}")
                time.sleep(retry_delay)
                retry_delay *= 2

    def setup_sidebar(self) -> None:
        """Configure sidebar navigation with error handling"""
        try:
            with st.sidebar:
                st.title("ML Model Fine-tuning")
                st.markdown("---")
                st.markdown("""
                ### Navigation
                - [Dataset Selection](#dataset-selection)
                - [Training Configuration](#training-configuration)
                - [Training Progress](#training-progress)
                ---
                ### About
                Fine-tune machine learning models with advanced monitoring 
                and configuration capabilities.
                """)
        except Exception as e:
            logger.error(f"Failed to setup sidebar: {str(e)}")
            raise

    def save_training_config(self, config: Dict[str, Any], 
                           selected_dataset: str) -> Optional[int]:
        """
        Save training configuration to database with enhanced error handling and retries

        Args:
            config: Training configuration parameters
            selected_dataset: Selected dataset name

        Returns:
            Configuration ID if successful, None otherwise
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                with self.flask_app.app_context():
                    with self.session_scope() as session:
                        training_config = TrainingConfig(
                            model_type=config['model_type'],
                            dataset_name=selected_dataset,
                            batch_size=config['batch_size'],
                            learning_rate=config['learning_rate'],
                            epochs=config['epochs'],
                            max_seq_length=config['max_seq_length'],
                            warmup_steps=config['warmup_steps']
                        )
                        session.add(training_config)
                        session.flush()
                        config_id = training_config.id
                        logger.info(f"Saved config for dataset: {selected_dataset}")
                        return config_id
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"Failed to save config after {max_retries} attempts: {str(e)}")
                    return None
                logger.warning(f"Save config attempt {attempt + 1} failed: {str(e)}")
                time.sleep(2 ** attempt)  # Exponential backoff

    def run(self) -> None:
        """Run the main application loop with comprehensive error handling"""
        try:
            self.setup_sidebar()
            st.markdown("# ML Model Fine-tuning Platform")

            # Dataset selection with validation
            selected_dataset = dataset_browser()
            if not selected_dataset or not validate_dataset_name(selected_dataset):
                st.warning("Please select a valid dataset")
                return

            # Training configuration with validation
            config = training_parameters()
            if not isinstance(config, dict):
                st.error("Invalid configuration format")
                return

            errors = validate_config(config)
            if errors:
                for error in errors:
                    st.error(error)
                return

            # Save configuration and initialize training
            config_id = self.save_training_config(config, selected_dataset)
            if config_id:
                st.session_state.current_config_id = config_id
                with self.flask_app.app_context():
                    training_monitor()
                    experiment_compare()

                if st.button("Export Configuration"):
                    st.json(config)
            else:
                st.error("Failed to save configuration")

        except Exception as e:
            logger.error(f"Application error: {str(e)}")
            st.error(f"An unexpected error occurred: {str(e)}")
            # Attempt to cleanup any incomplete state
            if hasattr(st.session_state, 'current_config_id'):
                del st.session_state.current_config_id

def main():
    """Application entry point with error handling"""
    try:
        app = MLFineTuningApp()
        app.run()
    except Exception as e:
        logger.critical(f"Fatal application error: {str(e)}")
        st.error("The application encountered a critical error. Please try reloading the page.")

if __name__ == "__main__":
    main()