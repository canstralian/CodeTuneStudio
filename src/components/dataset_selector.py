import logging
import re
from functools import lru_cache

import streamlit as st

from src.utils.argilla_dataset import ArgillaDatasetManager

logger = logging.getLogger(__name__)

AVAILABLE_DATASETS = {
    "code_search_net",
    "python_code_instructions",
    "github_code_snippets",
    "argilla_code_dataset",
    "google/code_x_glue_ct_code_to_text",
    "redashu/python_code_instructions",
}


@lru_cache(maxsize=32)
def validate_dataset_name(name: str) -> bool:
    if not name or not isinstance(name, str):
        logger.error(f"Invalid dataset name: {name}")
        return False
    pattern = r"^[a-zA-Z0-9_\-]+$"
    return bool(re.match(pattern, name))


def get_argilla_dataset_manager() -> ArgillaDatasetManager | None:
    try:
        return ArgillaDatasetManager()
    except Exception as e:
        logger.exception(f"Argilla initialization error: {e}")
        return None


def display_preview_data(dataset_name: str) -> None:
    try:
        if dataset_name.startswith("argilla_"):
            argilla_manager = get_argilla_dataset_manager()
            if argilla_manager:
                dataset = argilla_manager.load_dataset(dataset_name)
                if dataset:
                    st.dataframe(dataset[:5])
                else:
                    st.warning("No preview available")
            else:
                st.warning("Argilla connection failed")
        else:
            preview_data = {
                "code": ["def hello():", "print('Hello World')"],
                "language": ["python", "python"],
            }
            st.dataframe(preview_data)
    except Exception as e:
        logger.exception(f"Preview error: {e}")
        st.error("Error displaying preview")


def display_dataset_info(dataset_name: str) -> None:
    try:
        with st.expander("Dataset Information"):
            if dataset_name.startswith("argilla_"):
                argilla_manager = get_argilla_dataset_manager()
                if argilla_manager:
                    dataset = argilla_manager.load_dataset(dataset_name)
                    if dataset:
                        st.write(f"Number of examples: {len(dataset)}")
                        st.write("Source: Argilla")
                        st.write("Type: Code Generation Dataset")
                    else:
                        st.warning("No dataset information available")
                else:
                    st.warning("Argilla connection failed")
            else:
                st.write("Number of examples: 1000")
                st.write("Languages: Python, JavaScript")
                st.write("Average sequence length: 128")
    except Exception as e:
        logger.exception(f"Info display error: {e}")
        st.error("Error displaying information")


@st.cache_data(ttl=3600)
def get_dataset_info(dataset_name: str) -> dict:
    try:
        if dataset_name.startswith("argilla_"):
            argilla_manager = get_argilla_dataset_manager()
            if argilla_manager:
                dataset = argilla_manager.load_dataset(dataset_name)
                if dataset:
                    return {
                        "num_examples": len(dataset),
                        "source": "Argilla",
                        "type": "Code Generation",
                    }
            logger.warning("Argilla connection failed or no dataset available")
            return {}
        return {
            "num_examples": 1000,
            "languages": ["Python", "JavaScript"],
            "avg_seq_length": 128,
        }
    except Exception as e:
        logger.exception(f"Dataset info error: {e}")
        return {}


def dataset_browser() -> str | None:
    st.header("Dataset Selection")

    try:
        with st.container():
            st.markdown(
                """
            <div class="card">
                <h3>Choose a Dataset</h3>
                <p>Select from available datasets or connect to Argilla</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

            source = st.radio(
                "Dataset Source",
                ["Standard Datasets", "Argilla Datasets"],
                help="Choose dataset source",
            )

            if source == "Argilla Datasets":
                argilla_manager = get_argilla_dataset_manager()
                if not argilla_manager:
                    st.error("Argilla connection failed")
                    return None
                available_datasets = argilla_manager.list_datasets() or []
                if not available_datasets:
                    st.warning("No Argilla datasets found")
                    return None
            else:
                available_datasets = list(AVAILABLE_DATASETS)

            selected_dataset = st.selectbox("Select a dataset", available_datasets)
            if selected_dataset:
                st.info(f"Selected: {selected_dataset}")
                display_preview_data(selected_dataset)
                display_dataset_info(selected_dataset)

            return selected_dataset

    except Exception as e:
        logger.exception(f"Dataset browser error: {e}")
        st.error(f"Dataset selection error: {e}")
        return None
