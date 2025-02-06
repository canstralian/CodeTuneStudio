import streamlit as st
from datasets import list_datasets, load_dataset

def dataset_browser():
    st.header("Dataset Selection")
    
    with st.container():
        st.markdown("""
        <div class="card">
            <h3>Choose a Dataset</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Mock dataset list for code generation
        code_datasets = [
            "code_search_net",
            "python_code_instructions",
            "github_code_snippets"
        ]
        
        selected_dataset = st.selectbox(
            "Select a dataset",
            options=code_datasets,
            help="Choose a dataset for fine-tuning your model"
        )
        
        # Dataset preview
        if selected_dataset:
            try:
                st.info(f"Selected dataset: {selected_dataset}")
                st.write("Dataset Preview:")
                
                # Mock dataset preview
                preview_data = {
                    "code": ["def hello():", "print('Hello World')"],
                    "language": ["python", "python"]
                }
                st.dataframe(preview_data)
                
                dataset_info = st.expander("Dataset Information")
                with dataset_info:
                    st.write("Number of examples: 1000")
                    st.write("Languages: Python, JavaScript")
                    st.write("Average sequence length: 128")
                
            except Exception as e:
                st.error(f"Error loading dataset: {str(e)}")
                
    return selected_dataset
