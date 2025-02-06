import streamlit as st
from flask import Flask
from components.dataset_selector import dataset_browser
from components.parameter_config import training_parameters
from components.training_monitor import training_monitor
from components.experiment_compare import experiment_compare  # Add this import
from utils.config_validator import validate_config
from utils.database import init_db, TrainingConfig, TrainingMetric, db
import os

# Initialize Flask app for database
flask_app = Flask(__name__)

# Configure for different environments
is_huggingface = os.environ.get('SPACE_ID') is not None
if is_huggingface:
    # HuggingFace Spaces specific configuration
    st.set_page_config(
        page_title="Code Model Fine-tuning",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
else:
    # Local development configuration
    st.set_page_config(
        page_title="Code Model Fine-tuning",
        page_icon="🚀",
        layout="wide"
    )

# Initialize database
flask_app = init_db(flask_app)
app_ctx = flask_app.app_context()
app_ctx.push()

# Load custom CSS
try:
    with open("styles/custom.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("Custom CSS file not found. Using default styling.")

# Sidebar
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

# Main content
st.markdown("# Code Model Fine-tuning")

try:
    # Dataset selection
    selected_dataset = dataset_browser()

    # Training configuration
    if selected_dataset:
        config = training_parameters()

        # Validate configuration
        errors = validate_config(config)
        if errors:
            for error in errors:
                st.error(error)
        else:
            # Save configuration to database
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

                # Store config ID in session state
                st.session_state.current_config_id = training_config.id

                # Training monitor
                training_monitor()

                # Experiment comparison
                experiment_compare()

                # Model export
                from components.model_export import export_model
                export_model()

                # Export configuration  
                if st.button("Export Configuration"):
                    st.json(config)
            except Exception as e:
                st.error(f"Database error: {str(e)}")
                db.session.rollback()
    else:
        st.warning("Please select a dataset to continue")
except Exception as e:
    st.error(f"An error occurred: {str(e)}")