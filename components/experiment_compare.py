import streamlit as st
import plotly.graph_objects as go
from utils.database import TrainingConfig, TrainingMetric, db

def experiment_compare():
    st.header("Experiment Comparison")

    # Get all experiments
    experiments = db.session.query(TrainingConfig).all()
    selected_experiments = st.multiselect(
        "Select experiments to compare",
        options=[(exp.id, f"Experiment {exp.id} - {exp.model_type}") for exp in experiments],
        format_func=lambda x: x[1]
    )

    if selected_experiments:
        fig = go.Figure()
        for exp_id, exp_name in selected_experiments:
            metrics = db.session.query(TrainingMetric).filter_by(config_id=exp_id).all()
            epochs = [m.epoch for m in metrics]
            train_loss = [m.train_loss for m in metrics]
            eval_loss = [m.eval_loss for m in metrics]

            # Enhanced hover data for training loss
            fig.add_trace(go.Scatter(
                x=epochs,
                y=train_loss,
                name=f"{exp_name} - Train",
                hovertemplate=(
                    "<b>%{fullData.name}</b><br>" +
                    "Epoch: %{x}<br>" +
                    "Loss: %{y:.4f}<br>" +
                    "<extra></extra>"
                ),
                line=dict(width=2)
            ))

            # Enhanced hover data for evaluation loss
            fig.add_trace(go.Scatter(
                x=epochs,
                y=eval_loss,
                name=f"{exp_name} - Eval",
                hovertemplate=(
                    "<b>%{fullData.name}</b><br>" +
                    "Epoch: %{x}<br>" +
                    "Loss: %{y:.4f}<br>" +
                    "<extra></extra>"
                ),
                line=dict(width=2, dash='dash')
            ))

        fig.update_layout(
            title="Training Loss Comparison",
            xaxis_title="Epoch",
            yaxis_title="Loss",
            hovermode='x unified',
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Roboto"
            )
        )
        st.plotly_chart(fig, use_container_width=True)