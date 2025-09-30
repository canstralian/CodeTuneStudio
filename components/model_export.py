import os

import streamlit as st
import torch
from huggingface_hub import HfApi, create_repo
from transformers import AutoModelForCausalLM, AutoTokenizer


def export_model() -> None:
    st.header("Model Export & Sharing")

    if "current_config_id" not in st.session_state:
        st.warning("Please train a model first")
        return

    with st.form("export_form"):
        repo_name = st.text_input(
            "Repository Name",
            help="Name for your Hugging Face repository (e.g. code-gen-small)",
        )
        model_description = st.text_area(
            "Model Description", help="Describe your fine-tuned model"
        )

        submit = st.form_submit_button("Export to Hugging Face Hub")

        if submit and repo_name:
            try:
                with st.spinner("Exporting model..."):
                    # Create repo
                    api = HfApi()
                    create_repo(repo_name, private=False)

                    # Save and upload model files
                    model_path = f"./models/{st.session_state.current_config_id}"
                    model = AutoModelForCausalLM.from_pretrained(model_path)
                    tokenizer = AutoTokenizer.from_pretrained(model_path)

                    model.push_to_hub(repo_name)
                    tokenizer.push_to_hub(repo_name)

                    # Add model card
                    model_card = f"""
                    # {repo_name}

                    {model_description}

                    ## Training Details
                    This model was fine-tuned using the ML Fine-tuning Platform.
                    """

                    api.upload_file(
                        path_or_fileobj=model_card.encode(),
                        path_in_repo="README.md",
                        repo_id=repo_name,
                    )

                st.success(
                    f"Model exported! View it at: https://huggingface.co/{repo_name}"
                )
            except Exception as e:
                st.error(f"Export failed: {e!s}")
