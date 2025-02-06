from typing import Optional, Dict, Any, List
import os
import logging
import time
from contextlib import contextmanager

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
from utils.config_validator import validate_config
from utils.database import init_db, TrainingConfig, db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MLFineTuningApp:
    def __init__(self):
        self.flask_app = Flask(__name__)
        self._configure_database()
        self._configure_streamlit()

        retries = 3
        while retries > 0:
            try:
                with self.flask_app.app_context():
                    self._init_database()
                break
            except Exception as e:
                retries -= 1
                if retries == 0:
                    logger.critical(f"Failed to initialize application: {e}")
                    raise
                logger.warning(f"Retrying database initialization: {e}")
                time.sleep(2)

    def _configure_database(self):
        """Configure database settings with optimized connection pooling"""
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is not set")

        self.flask_app.config.update({
            'SQLALCHEMY_DATABASE_URI': database_url,
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'SQLALCHEMY_ENGINE_OPTIONS': {
                'poolclass': QueuePool,
                'pool_size': 5,  # Reduced from 10 for better resource management
                'max_overflow': 10,  # Reduced from 20
                'pool_timeout': 20,  # Reduced from 30
                'pool_recycle': 900,  # Reduced from 1800 for more frequent recycling
                'pool_pre_ping': True  # Added for connection health checks
            }
        })

    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around operations with improved error handling"""
        session = db.session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database transaction failed: {e}")
            raise
        finally:
            session.close()

    def _configure_streamlit(self):
        """Configure Streamlit UI settings with error handling"""
        try:
            st.set_page_config(
                page_title="ML Model Fine-tuning",
                page_icon="🚀",
                layout="wide",
                initial_sidebar_state="expanded" if os.environ.get('SPACE_ID') else "auto"
            )
            self._load_custom_css()
        except Exception as e:
            logger.error(f"Streamlit configuration failed: {e}")
            raise RuntimeError(f"Failed to configure Streamlit: {e}")

    def _load_custom_css(self):
        """Load custom CSS styles with improved error handling"""
        css_path = "styles/custom.css"
        try:
            if os.path.exists(css_path):
                with open(css_path) as f:
                    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
            else:
                logger.warning(f"CSS file not found: {css_path}")
        except Exception as e:
            logger.error(f"Failed to load CSS: {e}")

    def _init_database(self):
        """Initialize database with improved retry logic"""
        try:
            init_db(self.flask_app)
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise

    def setup_sidebar(self):
        """Configure sidebar navigation"""
        with st.sidebar:
            st.title("ML Model Fine-tuning")
            st.markdown("---")
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
        """Save training configuration to database with improved error handling"""
        if not config:  # Early return if config is None
            logger.error("Configuration is None")
            return None

        if not isinstance(config, dict):
            logger.error("Invalid configuration format")
            return None

        required_fields = ['model_type', 'batch_size', 'learning_rate', 'epochs', 
                         'max_seq_length', 'warmup_steps']
        if not all(field in config for field in required_fields):
            logger.error("Missing required configuration fields")
            return None

        retries = 3
        for attempt in range(retries):
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
                        config_id = training_config.id
                        return config_id
            except Exception as e:
                if attempt == retries - 1:
                    logger.error(f"Config save failed after {retries} attempts: {e}")
                    return None
                logger.warning(f"Config save attempt {attempt + 1} failed: {e}")
                time.sleep(2 ** attempt)

    def run(self):
        """Run the main application with improved error handling and validation"""
        try:
            self.setup_sidebar()
            st.markdown("# ML Model Fine-tuning Platform")

            selected_dataset = dataset_browser()
            if not selected_dataset or not validate_dataset_name(selected_dataset):
                st.warning("Please select a valid dataset")
                return

            config = training_parameters()
            errors = validate_config(config) if isinstance(config, dict) else ["Invalid configuration format"]

            if errors:
                for error in errors:
                    st.error(error)
                return

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
            logger.error(f"Application error: {e}")
            st.error("An unexpected error occurred. Please try again or contact support.")
            if hasattr(st.session_state, 'current_config_id'):
                del st.session_state.current_config_id

def main():
    """Application entry point with improved error handling"""
    try:
        app = MLFineTuningApp()
        app.run()
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        st.error("A critical error occurred. Please reload the page or contact support.")

if __name__ == "__main__":
    main()