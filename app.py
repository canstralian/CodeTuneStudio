
import streamlit as st
from flask import Flask
from components.dataset_selector import dataset_browser
from components.parameter_config import training_parameters
from components.training_monitor import training_monitor
from components.experiment_compare import experiment_compare
from utils.config_validator import validate_config
from utils.database import init_db, TrainingConfig, TrainingMetric, db
import os

def init_streamlit():
    """Initialize Streamlit configuration"""
    is_huggingface = os.environ.get('SPACE_ID') is not None
    st.set_page_config(
        page_title="Code Model Fine-tuning",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded" if is_huggingface else "auto"
    )

def load_custom_css():
    """Load custom CSS styles"""
    try:
        with open("styles/custom.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("Custom CSS file not found. Using default styling.")

def setup_sidebar():
    """Setup sidebar navigation and information"""
    with st.sidebar:
        st.title("Code Model Fine-tuning")
        st.markdown("---")
        st.markdown("""
        ### Navigation
        - [Dataset Selection](#dataset-selection)
        - [Training Configuration](#training-configuration)
        - [Training Progress](#training-progress)
        """)
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        This app allows you to fine-tune code generation models
        using datasets from Hugging Face. Configure your training
        parameters and monitor the process in real-time.
        """)

def save_training_config(config, selected_dataset):
    """Save training configuration to database"""
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
    return training_config.id

def main():
    # Initialize application
    flask_app = Flask(__name__)
    flask_app = init_db(flask_app)
    app_ctx = flask_app.app_context()
    app_ctx.push()

    # Setup Streamlit UI
    init_streamlit()
    load_custom_css()
    setup_sidebar()

    # Main content
    st.markdown("# Code Model Fine-tuning")

    try:
        selected_dataset = dataset_browser()
        if selected_dataset:
            config = training_parameters()
            errors = validate_config(config)
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                try:
                    config_id = save_training_config(config, selected_dataset)
                    st.session_state.current_config_id = config_id
                    
                    training_monitor()
                    experiment_compare()
                    
                    if st.button("Export Configuration"):
                        st.json(config)
                except Exception as e:
                    st.error(f"Database error: {str(e)}")
                    db.session.rollback()
        else:
            st.warning("Please select a dataset to continue")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
