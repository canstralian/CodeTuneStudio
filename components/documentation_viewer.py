import os
from typing import Optional

import streamlit as st

# Lazy import for DocumentationGenerator to optimize performance
_doc_gen_cache: Optional[object] = None


def _get_documentation_generator():
    """
    Lazy-load the DocumentationGenerator.

    This function implements lazy loading to optimize application startup time
    by only importing and initializing the documentation generator when needed.

    Returns:
        DocumentationGenerator instance
    """
    global _doc_gen_cache

    if _doc_gen_cache is None:
        from utils.documentation import DocumentationGenerator
        _doc_gen_cache = DocumentationGenerator(
            os.path.dirname(os.path.dirname(__file__))
        )

    return _doc_gen_cache


def render_parameters(params: list[dict[str, str]]) -> None:
    """Render function parameters in a table"""
    if params:
        st.markdown("**Parameters:**")
        params_data = []
        for param in params:
            param_type = param.get("type", "Any")
            params_data.append([param["name"], param_type])
        st.table(
            {
                "Parameter": [p[0] for p in params_data],
                "Type": [p[1] for p in params_data],
            }
        )


def render_doc_item(item, level: int = 0) -> None:
    """Render a documentation item with proper formatting"""
    prefix = "#" * (level + 2)

    st.markdown(f"{prefix} {item.name}")

    if item.signature:
        st.code(item.signature, language="python")

    if item.docstring:
        st.markdown(item.docstring)

    if item.parameters:
        render_parameters(item.parameters)

    if item.methods:
        st.markdown("**Methods:**")
        for method in item.methods:
            render_doc_item(method, level + 1)


def documentation_viewer() -> None:
    """
    Streamlit component for viewing project documentation.

    Uses lazy loading to optimize performance by only loading the
    documentation generator when the component is actually rendered.
    """
    st.header("📚 Documentation")

    # Lazy-load documentation generator
    doc_gen = _get_documentation_generator()

    try:
        with st.spinner("Generating documentation..."):
            documentation = doc_gen.generate_documentation()

        # Sidebar navigation
        st.sidebar.markdown("### Documentation Navigation")
        selected_file = st.sidebar.selectbox(
            "Select File",
            options=sorted(documentation.keys()),
            format_func=lambda x: x.replace("/", " → "),
        )

        if selected_file:
            st.subheader(f"File: {selected_file}")

            # Display documentation for selected file
            doc_items = documentation[selected_file]

            # Categorize items
            modules = [item for item in doc_items if item.type == "module"]
            classes = [item for item in doc_items if item.type == "class"]
            functions = [item for item in doc_items if item.type == "function"]

            # Display items by category
            if modules:
                st.markdown("## Module Documentation")
                for item in modules:
                    st.markdown(item.docstring)

            if classes:
                st.markdown("## Classes")
                for item in classes:
                    render_doc_item(item)

            if functions:
                st.markdown("## Functions")
                for item in functions:
                    render_doc_item(item)

    except Exception as e:
        st.error(f"Failed to generate documentation: {e!s}")
