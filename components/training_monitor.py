from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING, Any

import streamlit as st

from core.logging_config import get_logger
from components.loading_animation import show_training_animation
from utils.database import TrainingMetric, db
from utils.distributed_trainer import DistributedTrainer
from utils.mock_training import mock_training_step
from utils.model_inference import ModelInference
from utils.visualization import create_metrics_chart

if TYPE_CHECKING:
    import threading

logger = get_logger(__name__)


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
    Save training metrics to database with enhanced error handling for
    distributed training

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
            rank_str = f"(rank {rank})" if rank is not None else ""
            logger.info(
                f"Saved metrics for step {step} {rank_str}: "
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
            f"Updated training progress: step={step}, "
            f"epoch={st.session_state.current_epoch}"
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
                "Initialized distributed training with "
                f"{device_info['device_count']} devices"
            )
            return trainer
        logger.warning("No CUDA devices available for distributed training")
        return None
    except Exception as e:
        logger.exception(f"Failed to initialize distributed training: {e!s}")
        return None


def _display_device_info() -> None:
    """Display available CUDA devices and their specifications."""
    device_info = get_device_info()
    if device_info.get("cuda_available", False):
        st.info(
            f"Found {device_info['device_count']} CUDA devices "
            "available for distributed training"
        )
        for i, device in enumerate(device_info["devices"]):
            mem_gb = device["total_memory"] / 1024**3
            st.text(f"Device {i}: {device['name']} ({mem_gb:.1f} GB)")


def _start_training() -> None:
    """Initialize and start the training process."""
    st.session_state.training_active = True
    st.session_state.current_epoch = 0
    st.session_state.train_loss = []
    st.session_state.eval_loss = []

    # Initialize distributed training if available
    st.session_state.distributed_trainer = initialize_distributed_training()

    # Initialize model inference
    st.session_state.model_inference = ModelInference(
        model_name="Replit-v1.5", device_map="auto"
    )
    show_training_animation()


def _stop_training() -> None:
    """Stop training and cleanup resources."""
    st.session_state.training_active = False
    _cleanup_training_resources()


def _cleanup_training_resources() -> None:
    """Cleanup model inference and distributed trainer resources."""
    if st.session_state.model_inference:
        st.session_state.model_inference.cleanup()
    if st.session_state.distributed_trainer:
        st.session_state.distributed_trainer.cleanup()


def _render_training_controls() -> tuple[Any, Any]:
    """
    Render training control buttons and metrics.

    Returns:
        Tuple of (progress_bar, metrics_chart) for training updates
    """
    col1, col2 = st.columns([2, 1])
    with col1:
        if not st.session_state.training_active:
            if st.button("Start Training", type="primary"):
                _start_training()
        elif st.button("Stop Training", type="secondary"):
            _stop_training()

    with col2:
        st.metric("Current Epoch", st.session_state.current_epoch)

    progress_bar = st.progress(0)
    metrics_chart = st.empty()

    return progress_bar, metrics_chart


def _run_distributed_training(progress_bar: Any, metrics_chart: Any) -> None:
    """
    Execute distributed training across multiple GPUs.

    Args:
        progress_bar: Streamlit progress bar widget
        metrics_chart: Streamlit chart widget for metrics
    """
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


def _run_single_device_training(progress_bar: Any, metrics_chart: Any) -> None:
    """
    Execute training on a single device.

    Args:
        progress_bar: Streamlit progress bar widget
        metrics_chart: Streamlit chart widget for metrics
    """
    for i in range(100):
        if not st.session_state.training_active:
            break
        update_training_progress(progress_bar, metrics_chart, i)


def _execute_training_loop(progress_bar: Any, metrics_chart: Any) -> None:
    """
    Execute the main training loop, handling both distributed and single-device training.

    Args:
        progress_bar: Streamlit progress bar widget
        metrics_chart: Streamlit chart widget for metrics
    """
    try:
        if st.session_state.distributed_trainer:
            _run_distributed_training(progress_bar, metrics_chart)
        else:
            _run_single_device_training(progress_bar, metrics_chart)
    except Exception as e:
        logger.exception(f"Training error: {e!s}")
        st.error(f"Training error: {e!s}")
        st.session_state.training_active = False
        _cleanup_training_resources()
    finally:
        if not st.session_state.training_active:
            _cleanup_training_resources()


def training_monitor() -> None:
    """Main training monitoring interface with distributed training support."""
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
            _display_device_info()

            progress_bar, metrics_chart = _render_training_controls()

            if st.session_state.training_active:
                _execute_training_loop(progress_bar, metrics_chart)

    except Exception as e:
        logger.exception(f"Fatal error in training monitor: {e!s}")
        st.error(f"An unexpected error occurred: {e!s}")
