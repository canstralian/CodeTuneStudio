import streamlit as st
from components.dataset_selector import dataset_browser
from components.parameter_config import training_parameters
from components.training_monitor import training_monitor
from utils.config_validator import validate_config

# Page configuration
st.set_page_config(
    page_title="Code Model Fine-tuning",
    page_icon="🚀",
    layout="wide"
)

# Load custom CSS
with open("styles/custom.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

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
        # Training monitor
        training_monitor()
        
        # Export configuration
        if st.button("Export Configuration"):
            st.json(config)
else:
    st.warning("Please select a dataset to continue")
