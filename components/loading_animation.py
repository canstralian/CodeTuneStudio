import streamlit as st
import time
from typing import Optional

def show_training_animation(progress: Optional[float] = None):
    """
    Display a playful loading animation during model training
    
    Args:
        progress (float, optional): Training progress from 0 to 1
    """
    # Custom CSS for the animation
    st.markdown("""
    <style>
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    .training-emoji {
        display: inline-block;
        font-size: 2rem;
        animation: bounce 1s infinite;
        margin: 0 5px;
    }
    
    .training-message {
        margin-top: 1rem;
        text-align: center;
        font-size: 1.2rem;
        color: #4CAF50;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Single animated emoji counting up
    emoji = "🤖"
    
    # Display emoji and progress
    progress_display = progress * 100 if progress is not None else 0
    st.markdown(
        f"""<div class="training-emoji">
        {emoji} {progress_display:.2f}%
        </div>""",
        unsafe_allow_html=True
    )
    
    # Display a static message
    st.markdown(
        """<div class="training-message">
        Model is training, please be patient...
        </div>""",
        unsafe_allow_html=True
    )