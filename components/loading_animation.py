import time
from typing import Optional

import streamlit as st


def show_training_animation(progress: float | None = None) -> None:
    """
    Display a playful loading animation during model training

    Args:
        progress (float, optional): Training progress from 0 to 1
    """
    # Enhanced CSS for the animation
    st.markdown(
        """
    <style>
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-15px); }
    }

    @keyframes glow {
        0%, 100% { box-shadow: 0 0 10px rgba(102, 126, 234, 0.5); }
        50% { box-shadow: 0 0 20px rgba(118, 75, 162, 0.8); }
    }

    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }

    .training-container {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }

    .training-emoji {
        display: inline-block;
        font-size: 3rem;
        animation: bounce 1.5s infinite ease-in-out;
        margin: 0 10px;
        filter: drop-shadow(0 4px 8px rgba(102, 126, 234, 0.3));
    }

    .progress-circle {
        display: inline-block;
        width: 120px;
        height: 120px;
        border-radius: 50%;
        background: conic-gradient(
            from 0deg,
            #667eea 0%,
            #764ba2 var(--progress),
            #e5e7eb var(--progress),
            #e5e7eb 100%
        );
        animation: glow 2s infinite;
        position: relative;
        margin: 1rem auto;
    }

    .progress-inner {
        position: absolute;
        top: 10px;
        left: 10px;
        right: 10px;
        bottom: 10px;
        background: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .training-message {
        margin-top: 1.5rem;
        text-align: center;
        font-size: 1.3rem;
        font-weight: 600;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: 0.5px;
    }

    .training-stats {
        margin-top: 1rem;
        display: flex;
        justify-content: center;
        gap: 2rem;
        flex-wrap: wrap;
    }

    .stat-item {
        padding: 0.75rem 1.5rem;
        background: white;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        font-size: 0.9rem;
        color: #64748b;
    }

    .stat-value {
        font-size: 1.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Display emoji and progress
    progress_display = progress * 100 if progress is not None else 0
    progress_deg = progress_display * 3.6 if progress is not None else 0

    st.markdown(
        f"""
        <div class="training-container">
            <div class="training-emoji">🤖</div>
            <div class="training-emoji">⚡</div>
            <div class="training-emoji">🚀</div>

            <div class="progress-circle" style="--progress: {progress_deg}deg;">
                <div class="progress-inner">
                    {progress_display:.1f}%
                </div>
            </div>

            <div class="training-message">
                Training in Progress...
            </div>

            <div class="training-stats">
                <div class="stat-item">
                    <div>Progress</div>
                    <div class="stat-value">{progress_display:.1f}%</div>
                </div>
                <div class="stat-item">
                    <div>Status</div>
                    <div class="stat-value">Active</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
