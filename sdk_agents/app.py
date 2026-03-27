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
    page_icon="",
    layout="wide",
)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("Automotive Lifecycle Agents")
    st.caption("by Srinivas Reddy Mudem")
    st.markdown("---")

    page = st.radio("", ["About", "Try the Agent"], label_visibility="collapsed")

    st.markdown("---")
    if page == "Try the Agent":
        selected_display = st.selectbox(
            "Select Agent",
            options=[AGENT_DISPLAY_NAMES[n] for n in AGENT_NAMES],
        )
        selected_agent = next(
            k for k, v in AGENT_DISPLAY_NAMES.items() if v == selected_display
        )
        st.caption("Output structure is enforced by JSON Schema — the model cannot return free text or skip any field.")

# ── About page ─────────────────────────────────────────────────────────────────
if page == "About":
    st.title("Automotive Lifecycle Agents")
    st.subheader("AI agents purpose-built for automotive software engineering")
    st.markdown("---")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
**The problem this solves**

Generic AI assistants know *about* automotive standards.
These agents work *within* them — they apply ISO 26262, ASPICE, MISRA C,
AUTOSAR, and CAN/Ethernet protocol knowledge to produce structured,
actionable engineering output that a real engineer can act on directly.

**What makes the output different**

Ask a generic AI: *"CAN node goes bus-off after 3 minutes, only when engine running"*

You get: *"Check your CAN bus wiring and termination. Verify baud rate settings..."*

Ask this agent, and you get:
""")

        st.code("""OSI Layer:     L1 Physical
AUTOSAR Layer: MCAL (CanDrv)
Tool:          Oscilloscope

TEC Math:
  Required net climb = 256 / 180s = 1.41 TEC/s
  Solving: error_rate = 2.4/9 = 26.7%
  At 1 msg/s: net TEC = 1.41 TEC/s => 181s to bus-off ~ 3 min

Probable Causes (ranked):
  [HIGH]   Alternator ripple on transceiver Vcc
           Test: Oscilloscope AC-coupled on Vcc pin at ECU connector
           Pass: Ripple < 200 mV | Fail: Ripple > 500 mV

  [MEDIUM] Chassis GND offset under engine load
           Test: DMM DC between ECU GND pin and battery negative
           Pass: Offset < 50 mV | Fail: Offset > 200 mV

Decision Flow:
  L1 Physical: Vcc ripple and GND offset OK?
  +-- No  --> Fix supply / GND, retest
  +-- Yes --> L2 Data Link: Error frames in CANoe?
      +-- No  --> Check thermal drift with heat gun
      +-- Yes --> Bit error = L1; ACK error = check L7""", language="text")

        st.markdown("""
**Architecture**

The output structure is enforced at the API level using **JSON Schema via
structured output** — the model cannot return free text, skip required fields,
or invent a different format. Every response is then validated by domain-specific
checks (TEC math has numbers, AUTOSAR layer is known, test descriptions are specific).

**Standards covered**

ISO 26262 · ASPICE v3.1 · MISRA C:2012 · AUTOSAR Classic ·
ISO 21434 · ISO 14229 (UDS) · ISO 11898 (CAN) · IEEE 802.3bw (100BASE-T1)

**Built from**

11 years of hands-on automotive ECU development — developer, tester,
integrator, and SW project lead roles. All examples use synthetic data only.
""")

    with col2:
        st.markdown("**Author**")
        st.markdown("Srinivas Reddy Mudem")
        st.markdown("SW Project Lead | Integration Engineer")
        st.markdown("11 years automotive ECU development")
        st.markdown("---")

        st.markdown("**Agents implemented**")
        st.markdown("""
- CAN Bus Analyst
- *(11 more expanding)*
        """)

        st.markdown("**Domain knowledge**")
        st.markdown("""
8 skill files loaded automatically:
- CAN bus analysis
- ISO 26262 / HARA
- ASPICE process
- MISRA C:2012
- AUTOSAR Classic
- UDS diagnostics
- ISO 21434 / TARA
- Embedded patterns
        """)

        st.markdown("---")
        st.info("Use the **Try the Agent** page to run a live query.")

# ── Agent chat page ────────────────────────────────────────────────────────────
elif page == "Try the Agent":
    st.header(selected_display)

    history_key = f"history_{selected_agent}"
    if history_key not in st.session_state:
        st.session_state[history_key] = []

    # Example prompts
    st.caption("Example: *CAN node goes bus-off after 3 minutes, only when engine running. Other nodes are fine.*")

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
