"""
Streamlit web UI for sdk_agents.
Run with: streamlit run sdk_agents/app.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

import streamlit as st
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

from sdk_agents.core.registry import get_agent, AGENT_NAMES, AGENT_DISPLAY_NAMES
from sdk_agents.core.base_agent import AgentError
from sdk_agents.core.renderer import render_can_bus_analyst, render_agent_error

# Render function map — extend as new agents are added
RENDER_MAP = {
    "can-bus-analyst": render_can_bus_analyst,
}

st.set_page_config(
    page_title="Automotive Lifecycle Agents",
    page_icon="🚗",
    layout="wide",
)

# Sidebar
with st.sidebar:
    st.title("Automotive Lifecycle Agents")
    st.caption("SDK implementation — schema-enforced structured output")
    st.markdown("---")

    selected_display = st.selectbox(
        "Select Agent",
        options=[AGENT_DISPLAY_NAMES[n] for n in AGENT_NAMES],
    )
    # Map display name back to canonical name
    selected_agent = next(
        k for k, v in AGENT_DISPLAY_NAMES.items() if v == selected_display
    )

    st.markdown("---")
    st.caption("Output structure is enforced by JSON Schema via `tool_choice`.")
    st.caption("The model cannot deviate from the defined fields.")

# Main area
st.header(selected_display)

# Chat history per agent
history_key = f"history_{selected_agent}"
if history_key not in st.session_state:
    st.session_state[history_key] = []

# Display chat history
for entry in st.session_state[history_key]:
    with st.chat_message("user"):
        st.markdown(entry["prompt"])
    with st.chat_message("assistant"):
        _render = RENDER_MAP.get(selected_agent, render_agent_error)
        _render(entry["result"])

# Chat input
if prompt := st.chat_input("Describe the fault or ask your engineering question..."):
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analysing..."):
            agent = get_agent(selected_agent)
            result = agent.run(prompt)

        render_fn = RENDER_MAP.get(selected_agent)
        if render_fn:
            render_fn(result)
        elif isinstance(result, AgentError):
            render_agent_error(result)
        else:
            st.json(result.model_dump())

    st.session_state[history_key].append({"prompt": prompt, "result": result})
