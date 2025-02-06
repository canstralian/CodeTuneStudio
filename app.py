import os
import logging
from typing import Optional, Dict, Any
import streamlit as st
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from components.dataset_selector import dataset_browser, validate_dataset_name
from components.parameter_config import training_parameters
from components.training_monitor import training_monitor
from components.experiment_compare import experiment_compare
from utils.config_validator import validate_config
from utils.database import init_db, TrainingConfig, db

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MLFineTuningApp:
    """Main application class for ML model fine-tuning platform"""

    def __init__(self):
        """Initialize application components and database"""
        self.flask_app = Flask(__name__)
        self.flask_app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
        self.flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self._configure_streamlit()
        with self.flask_app.app_context():
            self._init_database()

    def _configure_streamlit(self) -> None:
        """Configure Streamlit UI settings"""
        is_huggingface = bool(os.environ.get('SPACE_ID'))
        st.set_page_config(
            page_title="ML Model Fine-tuning",
            page_icon="🚀",
            layout="wide",
            initial_sidebar_state="expanded" if is_huggingface else "auto"
        )
        self._load_custom_css()

    def _load_custom_css(self) -> None:
        """Load custom CSS styles"""
        try:
            with open("styles/custom.css") as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        except FileNotFoundError:
            logger.warning("Custom CSS file not found")

    def _init_database(self) -> None:
        """Initialize database connection"""
        try:
            init_db(self.flask_app)
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {str(e)}")
            raise

    def setup_sidebar(self) -> None:
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
            Fine-tune machine learning models with advanced monitoring 
            and configuration capabilities.
            """)

    def save_training_config(self, config: Dict[str, Any], 
                           selected_dataset: str) -> Optional[int]:
        """
        Save training configuration to database

        Args:
            config: Training configuration parameters
            selected_dataset: Selected dataset name

        Returns:
            Configuration ID if successful, None otherwise
        """
        try:
            with self.flask_app.app_context():
                training_config = TrainingConfig(
                    model_type=config['model_type'],
                    dataset_name=selected_dataset,
                    batch_size=config['batch_size'],
                    learning_rate=config['learning_rate'],
                    epochs=config['epochs'],
                    max_seq_length=config['max_seq_length'],
                    warmup_steps=config['warmup_steps']
                )
                db.session.add(training_config)
                db.session.commit()
                logger.info(f"Saved config for dataset: {selected_dataset}")
                return training_config.id
        except Exception as e:
            logger.error(f"Failed to save config: {str(e)}")
            db.session.rollback()
            return None

    def run(self) -> None:
        """Run the main application loop"""
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

def main():
    """Application entry point"""
    app = MLFineTuningApp()
    app.run()

if __name__ == "__main__":
    main()