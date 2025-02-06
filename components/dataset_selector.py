import re
import streamlit as st
from datasets import load_dataset
from typing import Dict, Set, Tuple, Optional
from functools import lru_cache
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

AVAILABLE_DATASETS: Set[str] = {
    "code_search_net",
    "python_code_instructions",
    "github_code_snippets"
}

@lru_cache(maxsize=32)
def validate_dataset_name(name: str) -> bool:
    """
    Validate dataset name using regex pattern

    Args:
        name: Dataset name to validate

    Returns:
        bool: True if valid, False otherwise
    """
    try:
        if not name or not isinstance(name, str):
            logger.error(f"Invalid dataset name type or empty: {type(name)}")
            return False

        # Following Bamba's pattern for safe dataset names
        pattern = r'^[a-zA-Z0-9_\-]+$'
        is_valid = bool(re.match(pattern, name))

        if not is_valid:
            logger.error(f"Dataset name contains invalid characters: {name}")

        return is_valid
    except Exception as e:
        logger.error(f"Error validating dataset name: {str(e)}")
        return False

def display_preview_data():
    """Display sample dataset preview"""
    try:
        preview_data = {
            "code": ["def hello():", "print('Hello World')"],
            "language": ["python", "python"]
        }
        st.dataframe(preview_data)
    except Exception as e:
        logger.error(f"Error displaying preview data: {str(e)}")
        st.error("Error displaying dataset preview")

def display_dataset_info():
    """Display detailed dataset information"""
    try:
        with st.expander("Dataset Information"):
            st.write("Number of examples: 1000")
            st.write("Languages: Python, JavaScript")
            st.write("Average sequence length: 128")
    except Exception as e:
        logger.error(f"Error displaying dataset info: {str(e)}")
        st.error("Error displaying dataset information")

@st.cache_data(ttl=3600)
def get_dataset_info(dataset_name: str) -> Dict[str, any]:
    """
    Retrieve and cache dataset information

    Args:
        dataset_name: Name of the dataset

    Returns:
        Dict containing dataset information
    """
    try:
        return {
            "num_examples": 1000,
            "languages": ["Python", "JavaScript"],
            "avg_seq_length": 128
        }
    except Exception as e:
        logger.error(f"Error getting dataset info: {str(e)}")
        return {}

def dataset_browser() -> Optional[str]:
    """
    Main dataset selection interface

    Returns:
        Optional[str]: Selected dataset name or None if error occurs
    """
    st.header("Dataset Selection")

    try:
        with st.container():
            st.markdown("""
            <div class="card">
                <h3>Choose a Dataset</h3>
            </div>
            """, unsafe_allow_html=True)

            selected_dataset = st.selectbox(
                "Select a dataset",
                options=AVAILABLE_DATASETS,
                help="Choose a dataset for fine-tuning your model"
            )

            if selected_dataset:
                st.info(f"Selected dataset: {selected_dataset}")
                st.write("Dataset Preview:")
                display_preview_data()
                display_dataset_info()

            return selected_dataset

    except Exception as e:
        logger.error(f"Error in dataset browser: {str(e)}")
        st.error(f"An error occurred while browsing datasets: {str(e)}")
        return None