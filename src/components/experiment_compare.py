import plotly.graph_objects as go
import streamlit as st

from src.utils.database import TrainingConfig, TrainingMetric, db


@st.cache_data(ttl=60)  # Cache experiment data for 1 minute
def fetch_experiment_data(exp_id):
    metrics = db.session.query(TrainingMetric).filter_by(config_id=exp_id).all()
    return {
        "epochs": [m.epoch for m in metrics],
        "train_loss": [m.train_loss for m in metrics],
        "eval_loss": [m.eval_loss for m in metrics],
    }


@st.cache_data(ttl=300)  # Cache experiment list for 5 minutes
def fetch_experiments():
    return db.session.query(TrainingConfig).all()


def experiment_compare() -> None:
    st.header("Experiment Comparison")

    # Get all experiments with caching
    experiments = fetch_experiments()
    selected_experiments = st.multiselect(
        "Select experiments to compare",
        options=[
            (exp.id, f"Experiment {exp.id} - {exp.model_type}") for exp in experiments
        ],
        format_func=lambda x: x[1],
    )

    if selected_experiments:
        fig = go.Figure()
        for exp_id, exp_name in selected_experiments:
            # Fetch cached experiment data
            data = fetch_experiment_data(exp_id)

            # Enhanced hover data for training loss
            fig.add_trace(
                go.Scatter(
                    x=data["epochs"],
                    y=data["train_loss"],
                    name=f"{exp_name} - Train",
                    hovertemplate=(
                        "<b>%{fullData.name}</b><br>"
                        "Epoch: %{x}<br>"
                        "Loss: %{y:.4f}<br>"
                        "<extra></extra>"
                    ),
                    line={"width": 2},
                )
            )

            # Enhanced hover data for evaluation loss
            fig.add_trace(
                go.Scatter(
                    x=data["epochs"],
                    y=data["eval_loss"],
                    name=f"{exp_name} - Eval",
                    hovertemplate=(
                        "<b>%{fullData.name}</b><br>"
                        "Epoch: %{x}<br>"
                        "Loss: %{y:.4f}<br>"
                        "<extra></extra>"
                    ),
                    line={"width": 2, "dash": "dash"},
                )
            )

        fig.update_layout(
            title="Training Loss Comparison",
            xaxis_title="Epoch",
            yaxis_title="Loss",
            hovermode="x unified",
            hoverlabel={"bgcolor": "white", "font_size": 14, "font_family": "Roboto"},
        )
        st.plotly_chart(fig, use_container_width=True)
