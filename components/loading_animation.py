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
    
    .training-progress {
        margin-top: 1rem;
        text-align: center;
        font-size: 1.2rem;
        color: #4CAF50;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Animated emojis
    emojis = ["🤖", "📚", "💡", "🔄"]
    
    # Display emojis with animation
    cols = st.columns(len(emojis))
    for idx, (emoji, col) in enumerate(zip(emojis, cols)):
        # Add delay to create a wave effect
        col.markdown(
            f"""<div class="training-emoji" style="animation-delay: {idx * 0.2}s">
            {emoji}
            </div>""",
            unsafe_allow_html=True
        )
    
    # Display progress message
    if progress is not None:
        progress_percentage = int(progress * 100)
        st.markdown(
            f"""<div class="training-progress">
            Training Progress: {progress_percentage}%
            </div>""",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """<div class="training-progress">
            Preparing for training...
            </div>""",
            unsafe_allow_html=True
        )
