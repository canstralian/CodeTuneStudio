
import streamlit as st

def get_model_parameters(col):
    return {
        "model_type": col.selectbox(
            "Model Architecture",
            ["CodeT5", "Replit-v1.5"],
            help="Select the base model architecture"
        ),
        "batch_size": col.number_input(
            "Batch Size",
            min_value=1,
            max_value=128,
            value=16,
            help="Number of samples processed in each training step"
        ),
        "learning_rate": col.number_input(
            "Learning Rate",
            min_value=1e-6,
            max_value=1e-2,
            value=2e-5,
            format="%.0e",
            help="Step size for gradient updates"
        )
    }

def get_training_parameters(col):
    return {
        "epochs": col.number_input(
            "Number of Epochs",
            min_value=1,
            max_value=100,
            value=3,
            help="Number of complete passes through the dataset"
        ),
        "max_seq_length": col.number_input(
            "Max Sequence Length",
            min_value=64,
            max_value=512,
            value=128,
            help="Maximum length of input sequences"
        ),
        "warmup_steps": col.number_input(
            "Warmup Steps",
            min_value=0,
            max_value=1000,
            value=100,
            help="Number of warmup steps for learning rate scheduler"
        )
    }

def training_parameters():
    st.header("Training Configuration")
    
    with st.expander("Dataset Enhancement Options", expanded=False):
        include_amphigory = st.checkbox("Include Amphigory Examples", value=True, 
            help="Include nonsensical but syntactically valid code examples to enhance model robustness")
        if include_amphigory:
            amphigory_ratio = st.slider("Amphigory Ratio", 0.0, 0.3, 0.1, 0.05,
                help="Ratio of amphigory examples to include in training data")
    
    with st.container():
        st.markdown("""
        <div class="card">
            <h3>Model Parameters</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        model_params = get_model_parameters(col1)
        training_params = get_training_parameters(col2)
        
        return {**model_params, **training_params}
