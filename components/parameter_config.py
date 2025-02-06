import streamlit as st
from typing import Dict, Any, Optional
from utils.config_validator import validate_config, sanitize_string
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_model_parameters(col) -> Dict[str, Any]:
    """
    Get model architecture and training parameters with enhanced validation

    Args:
        col: Streamlit column object for layout

    Returns:
        Dictionary containing validated model parameters
    """
    try:
        model_type = col.selectbox(
            "Model Architecture",
            ["CodeT5", "Replit-v1.5"],
            help="Select the base model architecture for fine-tuning. Each architecture is optimized for different tasks."
        )

        batch_size = col.number_input(
            "Batch Size",
            min_value=1,
            max_value=128,
            value=16,
            help="Number of samples processed in each training step. Larger values use more memory but can train faster."
        )

        learning_rate = col.number_input(
            "Learning Rate",
            min_value=1e-6,
            max_value=1e-2,
            value=2e-5,
            format="%.0e",
            help="Step size for gradient updates. Too high can cause unstable training, too low can make training very slow."
        )

        return {
            "model_type": sanitize_string(model_type),
            "batch_size": int(batch_size),
            "learning_rate": float(learning_rate)
        }
    except Exception as e:
        logger.error(f"Error getting model parameters: {str(e)}")
        raise

def get_training_parameters(col) -> Dict[str, Any]:
    """
    Get training configuration parameters with enhanced validation

    Args:
        col: Streamlit column object for layout

    Returns:
        Dictionary containing validated training parameters
    """
    try:
        epochs = col.number_input(
            "Number of Epochs",
            min_value=1,
            max_value=100,
            value=3,
            help="Number of complete passes through the dataset. More epochs can improve results but take longer to train."
        )

        max_seq_length = col.number_input(
            "Max Sequence Length",
            min_value=64,
            max_value=512,
            value=128,
            help="Maximum length of input sequences. Longer sequences provide more context but require more memory."
        )

        warmup_steps = col.number_input(
            "Warmup Steps",
            min_value=0,
            max_value=1000,
            value=100,
            help="Number of steps for learning rate warmup. Helps stabilize early training."
        )

        return {
            "epochs": int(epochs),
            "max_seq_length": int(max_seq_length),
            "warmup_steps": int(warmup_steps)
        }
    except Exception as e:
        logger.error(f"Error getting training parameters: {str(e)}")
        raise

def get_dataset_enhancement_options() -> Dict[str, Any]:
    """
    Get dataset enhancement configuration with validation

    Returns:
        Dictionary containing dataset enhancement options
    """
    try:
        include_amphigory = st.checkbox(
            "Include Amphigory Examples",
            value=True,
            help="Include nonsensical but syntactically valid code examples to enhance model robustness"
        )

        amphigory_ratio = 0.1
        if include_amphigory:
            amphigory_ratio = st.slider(
                "Amphigory Ratio",
                min_value=0.0,
                max_value=0.3,
                value=0.1,
                step=0.05,
                help="Ratio of amphigory examples to include in training data"
            )

        return {
            "include_amphigory": include_amphigory,
            "amphigory_ratio": float(amphigory_ratio)
        }
    except Exception as e:
        logger.error(f"Error getting enhancement options: {str(e)}")
        raise

def training_parameters() -> Optional[Dict[str, Any]]:
    """
    Configure and validate training parameters with enhanced error handling

    Returns:
        Dictionary containing all validated parameters or None if validation fails
    """
    st.header("Training Configuration")

    try:
        # Dataset enhancement options
        enhancement_options = get_dataset_enhancement_options()

        with st.container():
            st.markdown("""
            <div class="card">
                <h3>Model Parameters</h3>
                <p>Configure the core model and training parameters below.</p>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)

            # Get parameters with validation
            model_params = get_model_parameters(col1)
            training_params = get_training_parameters(col2)

            # Combine all parameters
            config = {
                **model_params,
                **training_params,
                **enhancement_options
            }

            # Validate complete configuration
            errors = validate_config(config)
            if errors:
                for error in errors:
                    st.error(error)
                return None

            logger.info("Training parameters configured successfully")
            return config

    except Exception as e:
        logger.error(f"Error in training parameter configuration: {str(e)}")
        st.error(f"Configuration error: {str(e)}")
        return None