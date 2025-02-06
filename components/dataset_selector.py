import streamlit as st
from datasets import load_dataset

AVAILABLE_DATASETS = [
    "code_search_net",
    "python_code_instructions",
    "github_code_snippets"
]

def show_dataset_preview(selected_dataset):
    """Display dataset preview without caching since it contains widgets"""
    preview_data = {
        "code": ["def hello():", "print('Hello World')"],
        "language": ["python", "python"]
    }
    st.dataframe(preview_data)

    with st.expander("Dataset Information"):
        st.write("Number of examples: 1000")
        st.write("Languages: Python, JavaScript")
        st.write("Average sequence length: 128")

@st.cache_data(ttl=3600)
def get_dataset_info(dataset_name):
    """Cache only the dataset information retrieval"""
    return {
        "num_examples": 1000,
        "languages": ["Python", "JavaScript"],
        "avg_seq_length": 128
    }

def dataset_browser():
    """Main dataset browser function without caching due to widget usage"""
    st.header("Dataset Selection")

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
            try:
                st.info(f"Selected dataset: {selected_dataset}")
                st.write("Dataset Preview:")
                show_dataset_preview(selected_dataset)
            except Exception as e:
                st.error(f"Error loading dataset: {str(e)}")

        return selected_dataset