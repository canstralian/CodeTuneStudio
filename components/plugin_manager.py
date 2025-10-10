import logging

import streamlit as st

from utils.plugins.registry import registry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def plugin_manager() -> None:
    """
    Display and manage loaded plugins in the Streamlit interface
    """
    st.header("🔌 Plugin Manager")

    try:
        tools = registry.list_tools()
        if not tools:
            st.warning("No plugins currently loaded")
            return

        # Plugin Overview
        st.markdown(
            """
        <style>
        .plugin-card {
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px;
            margin: 10px 0;
        }
        .plugin-title {
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 10px;
        }
        </style>
        """,
            unsafe_allow_html=True,
        )

        for tool_name in tools:
            tool_class = registry.get_tool(tool_name)
            if tool_class:
                tool = tool_class()

                with st.container():
                    st.markdown(
                        f"""
                    <div class="plugin-card">
                        <div class="plugin-title">{tool.metadata.name}</div>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**Description:** {tool.metadata.description}")
                        st.markdown(f"**Version:** {tool.metadata.version}")
                        if tool.metadata.author:
                            st.markdown(f"**Author:** {tool.metadata.author}")
                        if tool.metadata.tags:
                            st.markdown(f"**Tags:** {', '.join(tool.metadata.tags)}")

                    with col2:
                        # Store plugin state in session state
                        if f"plugin_{tool_name}_enabled" not in st.session_state:
                            st.session_state[f"plugin_{tool_name}_enabled"] = True

                        enabled = st.toggle(
                            "Enabled",
                            key=f"plugin_{tool_name}_enabled",
                            help=f"Enable/disable the {tool_name} plugin",
                        )

                        if enabled:
                            st.success("Active")
                        else:
                            st.error("Inactive")

    except Exception as e:
        logger.exception(f"Error in plugin manager: {e!s}")
        st.error(f"Failed to load plugin manager: {e!s}")
