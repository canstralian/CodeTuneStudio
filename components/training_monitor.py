
import streamlit as st
import plotly.graph_objects as go
import numpy as np
from utils.visualization import create_metrics_chart
from utils.mock_training import mock_training_step
from utils.database import TrainingMetric, db

def initialize_training_state():
    if 'training_active' not in st.session_state:
        st.session_state.training_active = False
        st.session_state.current_epoch = 0
        st.session_state.train_loss = []
        st.session_state.eval_loss = []

def handle_training_step(progress_bar, metrics_chart, step):
    train_loss, eval_loss = mock_training_step()
    st.session_state.train_loss.append(train_loss)
    st.session_state.eval_loss.append(eval_loss)

    if hasattr(st.session_state, 'current_config_id'):
        metric = TrainingMetric(
            config_id=st.session_state.current_config_id,
            epoch=st.session_state.current_epoch,
            step=step,
            train_loss=train_loss,
            eval_loss=eval_loss
        )
        db.session.add(metric)
        db.session.commit()

    progress = (step + 1) / 100
    progress_bar.progress(progress)
    
    fig = create_metrics_chart(
        st.session_state.train_loss,
        st.session_state.eval_loss
    )
    metrics_chart.plotly_chart(fig, use_container_width=True)
    
    st.session_state.current_epoch = int(progress * 3)

def training_monitor():
    st.header("Training Progress")

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
            else:
                if st.button("Stop Training", type="secondary"):
                    st.session_state.training_active = False

        with col2:
            st.metric("Current Epoch", st.session_state.current_epoch)

        progress_bar = st.progress(0)
        metrics_chart = st.empty()

        if st.session_state.training_active:
            try:
                for i in range(100):
                    handle_training_step(progress_bar, metrics_chart, i)
                    if not st.session_state.training_active:
                        break
            except Exception as e:
                st.error(f"Training error: {str(e)}")
                st.session_state.training_active = False
