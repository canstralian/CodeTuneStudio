
import streamlit as st
from utils.model_versioning import ModelVersion

def version_manager():
    st.header("Model Version Management")
    
    version_control = ModelVersion()
    versions = version_control.list_versions()
    
    if versions:
        st.subheader("Available Versions")
        selected_version = st.selectbox(
            "Select Version",
            list(versions.keys()),
            format_func=lambda x: f"{x} - {versions[x].get('model_type', 'Unknown')}"
        )
        
        if selected_version:
            st.json(versions[selected_version])
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Load Version"):
                    config = version_control.load_version(selected_version)
                    if config:
                        st.session_state.model_config = config
                        st.success("Version loaded successfully")
            
            with col2:
                if st.button("Delete Version"):
                    # Implement version deletion
                    pass
    else:
        st.info("No model versions available")
