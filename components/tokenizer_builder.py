import logging
import os

import streamlit as st
from transformers import AutoTokenizer

logger = logging.getLogger(__name__)


def tokenizer_builder() -> None:
    """
    Streamlit component for building and uploading tokenizers to Hugging Face
    """
    st.header("🔤 Tokenizer Builder")
    st.markdown("""
    Build and upload a tokenizer to your Hugging Face model repository.
    This component allows you to create a tokenizer.json file and other necessary
    tokenizer configuration files.
    """)

    # Base model selection
    st.subheader("1. Select Base Tokenizer")
    base_model_options = [
        "Salesforce/codet5-small",
        "gpt2",
        "bert-base-uncased",
        "roberta-base",
        "EleutherAI/gpt-neox-20b",
        "microsoft/phi-2",
        "google/flan-t5-base",
    ]

    # Allow custom input for base model
    use_custom_model = st.checkbox("Use custom base model")
    if use_custom_model:
        base_model = st.text_input("Enter custom model name/path:", "")
    else:
        base_model = st.selectbox(
            "Select base tokenizer model:", options=base_model_options
        )

    # HuggingFace repository information
    st.subheader("2. Target Repository")
    hf_username = st.text_input("Your Hugging Face username:")
    model_repo = st.text_input("Target model repository name:")
    full_repo_path = f"{hf_username}/{model_repo}" if hf_username and model_repo else ""

    if full_repo_path:
        st.success(f"Target repository: {full_repo_path}")

    # Special tokens customization
    st.subheader("3. Customize Special Tokens")
    with st.expander("Special Tokens Configuration", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            bos_token = st.text_input("BOS Token:", "<s>")
            eos_token = st.text_input("EOS Token:", "</s>")
            unk_token = st.text_input("UNK Token:", "<unk>")
        with col2:
            pad_token = st.text_input("PAD Token:", "<pad>")
            mask_token = st.text_input("MASK Token:", "<mask>")

    # Build tokenizer
    if st.button("Build Tokenizer") and base_model:
        with st.spinner("Building tokenizer..."):
            try:
                # Create special tokens dict
                special_tokens = {
                    "bos_token": bos_token,
                    "eos_token": eos_token,
                    "unk_token": unk_token,
                    "pad_token": pad_token,
                    "mask_token": mask_token,
                }

                # Load base tokenizer
                tokenizer = AutoTokenizer.from_pretrained(base_model)

                # Add special tokens
                tokenizer.add_special_tokens(special_tokens)

                # Create output directory
                output_dir = "tokenizer_output"
                os.makedirs(output_dir, exist_ok=True)

                # Save tokenizer locally
                tokenizer.save_pretrained(output_dir)

                st.success(
                    f"✅ Tokenizer built successfully and saved to {output_dir}/"
                )

                # Display the files created
                files = os.listdir(output_dir)
                st.write("Files created:")
                for file in files:
                    st.code(f"{output_dir}/{file}")

                # Option to upload to HuggingFace
                if full_repo_path:
                    upload = st.radio(
                        "Upload tokenizer to Hugging Face?",
                        options=["No", "Yes"],
                        horizontal=True,
                    )

                    if upload == "Yes":
                        try:
                            tokenizer.push_to_hub(full_repo_path)
                            st.success(
                                f"🚀 Tokenizer successfully uploaded to "
                                f"{full_repo_path}"
                            )
                            hf_url = (
                                f"https://huggingface.co/{full_repo_path}"
                            )
                            st.markdown(
                                f"[View your tokenizer on Hugging Face]({hf_url})"
                            )
                        except Exception as e:
                            st.error(f"⚠️ Upload failed: {e!s}")
                            st.info("""
                            To upload to Hugging Face, make sure you are logged in.
                            Run this in your terminal: `huggingface-cli login`
                            """)
                else:
                    st.warning(
                        "HuggingFace repository information is required for uploading."
                    )

            except Exception as e:
                logger.exception(f"Tokenizer building error: {e!s}")
                st.error(f"Error building tokenizer: {e!s}")

    # Documentation and help
    with st.expander("Help & Documentation"):
        st.markdown("""
        ### How to use this tool

        1. **Select a base tokenizer** - Choose from popular pre-trained
           tokenizers or specify a custom one
        2. **Enter your Hugging Face details** - Provide your username
           and repository name
        3. **Customize special tokens** - Modify the special tokens if
           needed
        4. **Build the tokenizer** - Generate tokenizer files locally
        5. **Upload to Hugging Face** - Optionally push the tokenizer to
           your model repository

        ### Hugging Face Login

        To upload your tokenizer to Hugging Face, you need to be logged in.
        Run the following command in your terminal:
        ```
        huggingface-cli login
        ```

        You'll be prompted for your Hugging Face token, which you can generate at:
        [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
        """)
