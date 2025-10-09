import logging
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING, Any

import streamlit as st

from components.loading_animation import show_training_animation
from utils.database import TrainingMetric, db
from utils.mock_training import mock_training_step
from utils.model_inference import ModelInference
from utils.visualization import create_metrics_chart

if TYPE_CHECKING:
    import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def initialize_training_state() -> None:
    """Initialize or reset training state with proper typing"""
    if "training_active" not in st.session_state:
        st.session_state.training_active = False
        st.session_state.current_epoch = 0
        st.session_state.train_loss: list[float] = []
        st.session_state.eval_loss: list[float] = []
        st.session_state.model_inference: ModelInference | None = None
        st.session_state.distributed_trainer: DistributedTrainer | None = None
        st.session_state.training_threads: list[threading.Thread] = []


def save_training_metrics(
    train_loss: float, eval_loss: float, step: int, rank: int | None = None
) -> None:
    """
    Save training metrics to database with enhanced error handling for distributed training

    Args:
        train_loss: Training loss value
        eval_loss: Evaluation loss value
        step: Current training step
        rank: Process rank for distributed training
    """
    try:
        if hasattr(st.session_state, "current_config_id"):
            metric = TrainingMetric(
                config_id=st.session_state.current_config_id,
                epoch=st.session_state.current_epoch,
                step=step,
                train_loss=float(train_loss),
                eval_loss=float(eval_loss),
                process_rank=rank,
            )
            db.session.add(metric)
            db.session.commit()
            logger.info(
                f"Saved metrics for step {step} {'(rank ' + str(rank) + ')' if rank is not None else ''}: "
                f"train_loss={train_loss}, eval_loss={eval_loss}"
            )
    except Exception as e:
        logger.exception(f"Failed to save metrics: {e!s}")
        db.session.rollback()
        raise


def get_device_info() -> dict[str, Any]:
    """Get available device information for distributed training"""
    try:
        return DistributedTrainer.get_available_devices()
    except Exception as e:
        logger.exception(f"Error getting device information: {e!s}")
        return {"error": str(e)}


def update_training_progress(
    progress_bar: st.progress,
    metrics_chart: st.empty,
    step: int,
    rank: int | None = None,
) -> None:
    """
    Update training progress and visualizations with distributed training support

    Args:
        progress_bar: Streamlit progress bar widget
        metrics_chart: Streamlit empty container for metrics
        step: Current training step
        rank: Process rank for distributed training
    """
    try:
        train_loss, eval_loss = mock_training_step()

        # Validate loss values
        if not (
            isinstance(train_loss, (int, float)) and isinstance(eval_loss, (int, float))
        ):
            msg = "Invalid loss values received"
            raise ValueError(msg)

        st.session_state.train_loss.append(float(train_loss))
        st.session_state.eval_loss.append(float(eval_loss))

        save_training_metrics(train_loss, eval_loss, step, rank)

        progress = min(1.0, (step + 1) / 100)
        progress_bar.progress(progress)
        show_training_animation(progress)

        fig = create_metrics_chart(
            st.session_state.train_loss, st.session_state.eval_loss
        )
        metrics_chart.plotly_chart(fig, use_container_width=True)

        st.session_state.current_epoch = int(progress * 3)
        logger.info(
            f"Updated training progress: step={step}, epoch={st.session_state.current_epoch}"
        )

    except Exception as e:
        logger.exception(f"Error updating training progress: {e!s}")
        raise


def initialize_distributed_training() -> DistributedTrainer | None:
    """Initialize distributed training environment"""
    try:
        device_info = get_device_info()
        if device_info.get("cuda_available", False):
            trainer = DistributedTrainer(
                world_size=device_info["device_count"], backend="nccl"
            )
            logger.info(
                f"Initialized distributed training with {device_info['device_count']} devices"
            )
            return trainer
        logger.warning("No CUDA devices available for distributed training")
        return None
    except Exception as e:
        logger.exception(f"Failed to initialize distributed training: {e!s}")
        return None


def training_monitor() -> None:
    """Main training monitoring interface with distributed training support"""
    st.header("Training Progress")

    try:
        with st.container():
            st.markdown(
                """
            <div class="card">
                <h3>Training Metrics</h3>
            </div>
            """,
                unsafe_allow_html=True,
            )

            initialize_training_state()

            # Device information display
            device_info = get_device_info()
            if device_info.get("cuda_available", False):
                st.info(
                    f"Found {device_info['device_count']} CUDA devices available for distributed training"
                )
                for i, device in enumerate(device_info["devices"]):
                    st.text(
                        f"Device {i}: {device['name']} ({device['total_memory'] / 1024**3:.1f} GB)"
                    )

            col1, col2 = st.columns([2, 1])
            with col1:
                if not st.session_state.training_active:
                    if st.button("Start Training", type="primary"):
                        st.session_state.training_active = True
                        st.session_state.current_epoch = 0
                        st.session_state.train_loss = []
                        st.session_state.eval_loss = []

                        # Initialize distributed training if available
                        st.session_state.distributed_trainer = (
                            initialize_distributed_training()
                        )

                        # Initialize model inference
                        st.session_state.model_inference = ModelInference(
                            model_name="Replit-v1.5", device_map="auto"
                        )
                        show_training_animation()
                elif st.button("Stop Training", type="secondary"):
                    st.session_state.training_active = False
                    if st.session_state.model_inference:
                        st.session_state.model_inference.cleanup()
                    if st.session_state.distributed_trainer:
                        st.session_state.distributed_trainer.cleanup()

            with col2:
                st.metric("Current Epoch", st.session_state.current_epoch)

            progress_bar = st.progress(0)
            metrics_chart = st.empty()

            if st.session_state.training_active:
                try:
                    if st.session_state.distributed_trainer:
                        # Distributed training
                        world_size = st.session_state.distributed_trainer.world_size
                        with ThreadPoolExecutor(max_workers=world_size) as executor:
                            for i in range(100):
                                if not st.session_state.training_active:
                                    break
                                futures = []
                                for rank in range(world_size):
                                    future = executor.submit(
                                        update_training_progress,
                                        progress_bar,
                                        metrics_chart,
                                        i,
                                        rank,
                                    )
                                    futures.append(future)
                                # Wait for all processes to complete
                                for future in futures:
                                    future.result()
                    else:
                        # Single device training
                        for i in range(100):
                            if not st.session_state.training_active:
                                break
                            update_training_progress(progress_bar, metrics_chart, i)
                except Exception as e:
                    logger.exception(f"Training error: {e!s}")
                    st.error(f"Training error: {e!s}")
                    st.session_state.training_active = False
                    if st.session_state.model_inference:
                        st.session_state.model_inference.cleanup()
                    if st.session_state.distributed_trainer:
                        st.session_state.distributed_trainer.cleanup()
                finally:
                    if not st.session_state.training_active:
                        if st.session_state.model_inference:
                            st.session_state.model_inference.cleanup()
                        if st.session_state.distributed_trainer:
                            st.session_state.distributed_trainer.cleanup()

    except Exception as e:
        logger.exception(f"Fatal error in training monitor: {e!s}")
        st.error(f"An unexpected error occurred: {e!s}")
