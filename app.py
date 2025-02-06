from typing import Optional, Dict, Any
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

        with self.flask_app.app_context():
            self._init_database()

    def _configure_database(self):
        """Configure database settings with connection pooling"""
        self.flask_app.config.update({
            'SQLALCHEMY_DATABASE_URI': os.environ.get('DATABASE_URL'),
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'SQLALCHEMY_ENGINE_OPTIONS': {
                'poolclass': QueuePool,
                'pool_size': 10,
                'max_overflow': 20,
                'pool_timeout': 30,
                'pool_recycle': 1800,
            }
        })

    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around operations"""
        try:
            yield db.session
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Database transaction failed: {e}")
            raise
        finally:
            db.session.close()

    def _configure_streamlit(self):
        """Configure Streamlit UI settings"""
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
            raise

    def _load_custom_css(self):
        """Load custom CSS styles"""
        css_path = "styles/custom.css"
        if os.path.exists(css_path):
            with open(css_path) as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        else:
            logger.warning(f"CSS file not found: {css_path}")

    def _init_database(self):
        """Initialize database with retry logic"""
        retries, delay = 3, 1
        for attempt in range(retries):
            try:
                init_db(self.flask_app)
                logger.info("Database initialized")
                return
            except Exception as e:
                if attempt == retries - 1:
                    logger.error(f"Database initialization failed after {retries} attempts: {e}")
                    raise
                logger.warning(f"Database initialization attempt {attempt + 1} failed: {e}")
                time.sleep(delay)
                delay *= 2

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
            ---
            ### About
            Fine-tune ML models with advanced monitoring
            """)

    def save_training_config(self, config: Dict[str, Any], dataset: str) -> Optional[int]:
        """Save training configuration to database"""
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
                        return training_config.id
            except Exception as e:
                if attempt == retries - 1:
                    logger.error(f"Config save failed after {retries} attempts: {e}")
                    return None
                logger.warning(f"Config save attempt {attempt + 1} failed: {e}")
                time.sleep(2 ** attempt)

    def run(self):
        """Run the main application"""
        try:
            self.setup_sidebar()
            st.markdown("# ML Model Fine-tuning Platform")

            selected_dataset = dataset_browser()
            if not selected_dataset or not validate_dataset_name(selected_dataset):
                st.warning("Please select a valid dataset")
                return

            config = training_parameters()
            if not isinstance(config, dict) or (errors := validate_config(config)):
                if errors:
                    for error in errors:
                        st.error(error)
                return

            if config_id := self.save_training_config(config, selected_dataset):
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
            st.error(f"An unexpected error occurred: {e}")
            if hasattr(st.session_state, 'current_config_id'):
                del st.session_state.current_config_id

def main():
    """Application entry point"""
    try:
        app = MLFineTuningApp()
        app.run()
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        st.error("Critical error occurred. Please reload the page.")

if __name__ == "__main__":
    main()