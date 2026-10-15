"""Copy the rendered response, including collapsed sections, in the browser."""

from pathlib import Path


def render_copy_button(key):
    """Mount a response-local control; no regenerated text or model calls."""
    from streamlit.components.v1 import declare_component

    component = declare_component(
        "copy_full_response", path=str(Path(__file__).with_name("copy_component"))
    )
    component(key=key, default=None)
