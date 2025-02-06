import streamlit as st
import plotly.graph_objects as go
import numpy as np
from typing import List, Optional, Tuple
from utils.visualization import create_metrics_chart
from utils.mock_training import mock_training_step
from utils.database import TrainingMetric, db
from utils.model_inference import ModelInference
from components.loading_animation import show_training_animation
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_training_state() -> None:
    """Initialize or reset training state with proper typing"""
    if 'training_active' not in st.session_state:
        st.session_state.training_active = False
        st.session_state.current_epoch = 0
        st.session_state.train_loss: List[float] = []
        st.session_state.eval_loss: List[float] = []
        st.session_state.model_inference: Optional[ModelInference] = None

def save_training_metrics(train_loss: float, eval_loss: float, step: int) -> None:
    """
    Save training metrics to database with error handling

    Args:
        train_loss: Training loss value
        eval_loss: Evaluation loss value
        step: Current training step
    """
    try:
        if hasattr(st.session_state, 'current_config_id'):
            metric = TrainingMetric(
                config_id=st.session_state.current_config_id,
                epoch=st.session_state.current_epoch,
                step=step,
                train_loss=float(train_loss),
                eval_loss=float(eval_loss)
            )
            db.session.add(metric)
            db.session.commit()
            logger.info(f"Saved metrics for step {step}: train_loss={train_loss}, eval_loss={eval_loss}")
    except Exception as e:
        logger.error(f"Failed to save metrics: {str(e)}")
        db.session.rollback()
        raise

def update_training_progress(
    progress_bar: st.progress,
    metrics_chart: st.empty,
    step: int
) -> None:
    """
    Update training progress and visualizations with proper error handling

    Args:
        progress_bar: Streamlit progress bar widget
        metrics_chart: Streamlit empty container for metrics
        step: Current training step
    """
    try:
        train_loss, eval_loss = mock_training_step()

        # Validate loss values
        if not (isinstance(train_loss, (int, float)) and isinstance(eval_loss, (int, float))):
            raise ValueError("Invalid loss values received")

        st.session_state.train_loss.append(float(train_loss))
        st.session_state.eval_loss.append(float(eval_loss))

        save_training_metrics(train_loss, eval_loss, step)

        progress = min(1.0, (step + 1) / 100)
        progress_bar.progress(progress)
        show_training_animation(progress)

        fig = create_metrics_chart(
            st.session_state.train_loss,
            st.session_state.eval_loss
        )
        metrics_chart.plotly_chart(fig, use_container_width=True)

        st.session_state.current_epoch = int(progress * 3)
        logger.info(f"Updated training progress: step={step}, epoch={st.session_state.current_epoch}")

    except Exception as e:
        logger.error(f"Error updating training progress: {str(e)}")
        raise

def training_monitor() -> None:
    """Main training monitoring interface with enhanced error handling"""
    st.header("Training Progress")

    try:
        with st.container():
            st.markdown("""
            <div class="card">
                <h3>Training Metrics</h3>
            </div>
            """, unsafe_allow_html=True)

            initialize_training_state()

            col1, col2 = st.columns([2, 1])
            with col1:
                if not st.session_state.training_active:
                    if st.button("Start Training", type="primary"):
                        st.session_state.training_active = True
                        st.session_state.current_epoch = 0
                        st.session_state.train_loss = []
                        st.session_state.eval_loss = []
                        # Initialize model inference
                        st.session_state.model_inference = ModelInference(
                            model_name="Replit-v1.5",
                            device_map="auto"
                        )
                        show_training_animation()
                else:
                    if st.button("Stop Training", type="secondary"):
                        st.session_state.training_active = False
                        if st.session_state.model_inference:
                            st.session_state.model_inference.cleanup()

            with col2:
                st.metric("Current Epoch", st.session_state.current_epoch)

            progress_bar = st.progress(0)
            metrics_chart = st.empty()

            if st.session_state.training_active:
                try:
                    for i in range(100):
                        if not st.session_state.training_active:
                            break
                        update_training_progress(progress_bar, metrics_chart, i)
                except Exception as e:
                    logger.error(f"Training error: {str(e)}")
                    st.error(f"Training error: {str(e)}")
                    st.session_state.training_active = False
                    if st.session_state.model_inference:
                        st.session_state.model_inference.cleanup()
                finally:
                    if not st.session_state.training_active and st.session_state.model_inference:
                        st.session_state.model_inference.cleanup()

    except Exception as e:
        logger.error(f"Fatal error in training monitor: {str(e)}")
        st.error(f"An unexpected error occurred: {str(e)}")