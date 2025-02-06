import streamlit as st
from flask import Flask
from components.dataset_selector import dataset_browser, validate_dataset_name
from components.parameter_config import training_parameters
from components.training_monitor import training_monitor
from components.experiment_compare import experiment_compare
from utils.config_validator import validate_config
from utils.database import init_db, TrainingConfig, db
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_streamlit():
    is_huggingface = bool(os.environ.get('SPACE_ID'))
    st.set_page_config(
        page_title="Code Model Fine-tuning",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded" if is_huggingface else "auto"
    )

def load_custom_css():
    try:
        with open("styles/custom.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        logger.warning("Custom CSS file not found")

def setup_sidebar():
    with st.sidebar:
        st.title("Code Model Fine-tuning")
        st.markdown("---")
        st.markdown("""
        ### Navigation
        - [Dataset Selection](#dataset-selection)
        - [Training Configuration](#training-configuration)
        - [Training Progress](#training-progress)
        ---
        ### About
        Fine-tune code generation models using Hugging Face datasets.
        Configure training parameters and monitor progress.
        """)

def save_training_config(config, selected_dataset):
    try:
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
        logger.error(f"Failed to save config: {e}")
        raise

def main():
    try:
        # Initialize application
        flask_app = Flask(__name__)
        init_db(flask_app)
        with flask_app.app_context():
            init_streamlit()
            load_custom_css()
            setup_sidebar()

            st.markdown("# Code Model Fine-tuning")

            # Dataset selection
            selected_dataset = dataset_browser()
            if not selected_dataset or not validate_dataset_name(selected_dataset):
                st.warning("Please select a valid dataset")
                return

            # Training configuration
            config = training_parameters()
            if not isinstance(config, dict):
                st.error("Invalid configuration format")
                return

            errors = validate_config(config)
            if errors:
                for error in errors:
                    st.error(error)
                return

            # Save configuration and monitor training
            try:
                config_id = save_training_config(config, selected_dataset)
                st.session_state.current_config_id = config_id
                training_monitor()
                experiment_compare()

                if st.button("Export Configuration"):
                    st.json(config)
            except Exception as e:
                logger.error(f"Database error: {e}")
                st.error(f"Database error: {e}")
                db.session.rollback()

    except Exception as e:
        logger.error(f"Application error: {e}")
        st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()