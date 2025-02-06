import streamlit as st

def training_parameters():
    st.header("Training Configuration")
    
    with st.container():
        st.markdown("""
        <div class="card">
            <h3>Model Parameters</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            model_type = st.selectbox(
                "Model Architecture",
                ["CodeT5", "Replit-v1.5"],
                help="Select the base model architecture"
            )
            
            batch_size = st.number_input(
                "Batch Size",
                min_value=1,
                max_value=128,
                value=16,
                help="Number of samples processed in each training step"
            )
            
            learning_rate = st.number_input(
                "Learning Rate",
                min_value=1e-6,
                max_value=1e-2,
                value=2e-5,
                format="%.0e",
                help="Step size for gradient updates"
            )
            
        with col2:
            epochs = st.number_input(
                "Number of Epochs",
                min_value=1,
                max_value=100,
                value=3,
                help="Number of complete passes through the dataset"
            )
            
            max_seq_length = st.number_input(
                "Max Sequence Length",
                min_value=64,
                max_value=512,
                value=128,
                help="Maximum length of input sequences"
            )
            
            warmup_steps = st.number_input(
                "Warmup Steps",
                min_value=0,
                max_value=1000,
                value=100,
                help="Number of warmup steps for learning rate scheduler"
            )
    
    config = {
        "model_type": model_type,
        "batch_size": batch_size,
        "learning_rate": learning_rate,
        "epochs": epochs,
        "max_seq_length": max_seq_length,
        "warmup_steps": warmup_steps
    }
    
    return config
