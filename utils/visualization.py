import plotly.graph_objects as go
import streamlit as st


@st.cache_data(ttl=30)  # Cache metrics chart for 30 seconds
def create_metrics_chart(train_loss, eval_loss):
    """
    Create a plotly chart for training metrics with caching
    """
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            y=train_loss,
            name="Training Loss",
            line=dict(color="#FF4B4B"),
            hovertemplate=(
                "<b>Training Loss</b><br>"
                + "Step: %{x}<br>"
                + "Loss: %{y:.4f}<br>"
                + "<extra></extra>"
            ),
        )
    )

    fig.add_trace(
        go.Scatter(
            y=eval_loss,
            name="Validation Loss",
            line=dict(color="#0068C9"),
            hovertemplate=(
                "<b>Validation Loss</b><br>"
                + "Step: %{x}<br>"
                + "Loss: %{y:.4f}<br>"
                + "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title="Training Progress",
        xaxis_title="Steps",
        yaxis_title="Loss",
        template="plotly_white",
        height=400,
        margin=dict(l=0, r=0, t=40, b=0),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="white", font_size=14, font_family="Roboto"),
    )

    return fig
