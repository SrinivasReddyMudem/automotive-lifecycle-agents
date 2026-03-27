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
from sdk_agents.core.renderer import (
    render_can_bus_analyst,
    render_field_debug_fae,
    render_sw_integrator,
    render_autosar_bsw_developer,
    render_embedded_c_developer,
    render_misra_reviewer,
    render_aspice_process_coach,
    render_gate_review_approver,
    render_safety_and_cyber_lead,
    render_sw_project_lead,
    render_regression_analyst,
    render_sil_hil_test_planner,
    render_sw_unit_tester,
    render_agent_error,
)

# Render function map — one entry per agent
RENDER_MAP = {
    "can-bus-analyst":       render_can_bus_analyst,
    "field-debug-fae":       render_field_debug_fae,
    "sw-integrator":         render_sw_integrator,
    "autosar-bsw-developer": render_autosar_bsw_developer,
    "embedded-c-developer":  render_embedded_c_developer,
    "misra-reviewer":        render_misra_reviewer,
    "aspice-process-coach":  render_aspice_process_coach,
    "gate-review-approver":  render_gate_review_approver,
    "safety-and-cyber-lead": render_safety_and_cyber_lead,
    "sw-project-lead":       render_sw_project_lead,
    "regression-analyst":    render_regression_analyst,
    "sil-hil-test-planner":  render_sil_hil_test_planner,
    "sw-unit-tester":        render_sw_unit_tester,
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
    st.subheader("AI agents grounded in practical automotive embedded engineering")
    st.markdown("---")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
**What this is**

A personal project exploring how AI can support day-to-day automotive software
engineering work — not by replacing engineering judgement, but by providing a
structured starting point based on domain knowledge that takes years to build.

The agents are built from hands-on experience working across development,
testing, integration, and project roles in automotive ECU projects. The domain
knowledge comes from that practical background, not from reading documentation.

**Why the output looks different from a generic AI**

Generic AI gives broad suggestions. These agents classify the problem first —
by OSI layer, AUTOSAR layer, or process area — then apply the right standard
or method to produce output an engineer can directly act on.

Example — same question, different output:

*Question: "CAN node goes bus-off after 3 minutes, only when engine running"*
""")

        st.code("""Generic AI:
  "Check your CAN bus wiring and termination.
   Verify the baud rate settings are consistent across all nodes..."

This agent:
  OSI Layer:     L1 Physical
  AUTOSAR Layer: MCAL (CanDrv)
  Tool:          Oscilloscope

  TEC Math:
    Net climb needed = 256 / 180s = 1.41 TEC/s
    Error rate required = 26.7% at 1 msg/s => 181s to bus-off ~ 3 min

  Probable Causes:
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
**How the output is enforced**

The response structure is enforced at the API level using JSON Schema — the
model cannot return free text or skip any required field. A second layer of
domain checks validates that the content is specific: TEC math must contain
numbers, AUTOSAR layer must be a known value, test descriptions must name a
tool and probe point. This is what separates structured output from a
well-formatted guess.

**Standards the agents work within**

ISO 26262 · ASPICE v3.1 · MISRA C:2012 · AUTOSAR Classic ·
ISO 21434 · ISO 14229 (UDS) · ISO 11898 (CAN) · IEEE 802.3bw (100BASE-T1)

*All examples in this project use synthetic data only.*
""")

    with col2:
        st.markdown("**Built by**")
        st.markdown("Srinivas Reddy Mudem")
        st.markdown("Automotive embedded engineer with hands-on experience across ECU development, integration, and testing.")
        st.markdown("---")

        st.markdown("**Agents — all live**")
        st.markdown("""
**Integrator**
- CAN Bus Analyst
- Field Debug FAE
- SW Integrator

**Developer**
- AUTOSAR BSW Developer
- Embedded C Developer
- MISRA Reviewer

**Project Lead**
- ASPICE Process Coach
- Gate Review Approver
- Safety & Cyber Lead
- SW Project Lead

**Tester**
- Regression Analyst
- SIL/HIL Test Planner
- SW Unit Tester
        """)

        st.markdown("**Domain knowledge loaded**")
        st.markdown("""
- CAN bus / error counters
- ISO 26262 / HARA / ASIL
- ASPICE SWE.1 – SWE.6
- MISRA C:2012
- AUTOSAR Classic
- UDS / diagnostics
- ISO 21434 / TARA
- Embedded patterns
        """)

        st.markdown("---")
        st.info("Use **Try the Agent** in the sidebar to run a live query.")

# ── Agent chat page ────────────────────────────────────────────────────────────
elif page == "Try the Agent":
    st.header(selected_display)

    history_key = f"history_{selected_agent}"
    if history_key not in st.session_state:
        st.session_state[history_key] = []

    # Per-agent example prompts
    EXAMPLE_PROMPTS = {
        "can-bus-analyst":       "CAN node goes bus-off after 3 minutes, only when engine running. Other nodes are fine.",
        "field-debug-fae":       "ECU returns NRC 0x22 on service 0x27 seed request in extended session only. Programming session works fine.",
        "sw-integrator":         "RTE generation fails with 'port not connected' error after adding a new sender-receiver interface for vehicle speed.",
        "autosar-bsw-developer": "Design a sender-receiver SWC for brake pedal position, ASIL-B, 10 ms cyclic, uint16 data element.",
        "embedded-c-developer":  "Hard fault on Cortex-M4, CFSR = 0x00000400, occurs only after 2 hours runtime. Stack usage looks normal.",
        "misra-reviewer":        "Polyspace flagged Rule 11.3 (cast from pointer to integer) in our CAN driver receive handler. How do I write a deviation?",
        "aspice-process-coach":  "Assessment in 3 weeks, SWE.4 unit test specs are not formally reviewed, and SWE.2 traceability is partial.",
        "gate-review-approver":  "Use /gate-review command to trigger this agent.",
        "safety-and-cyber-lead": "Perform HARA for autonomous emergency braking — loss of braking function at highway speed.",
        "sw-project-lead":       "Customer added OTA update requirement at Milestone 3. Assess schedule impact and change request options.",
        "regression-analyst":    "After SW baseline 2.4, 14 tests failed that passed in 2.3. Three are ASIL-D brake functions. Should we proceed?",
        "sil-hil-test-planner":  "Plan SIL and HIL tests for the new ASIL-B torque limiter function. We use dSPACE SCALEXIO and CANoe.",
        "sw-unit-tester":        "Write unit tests for a saturating uint16 adder, ASIL-B function. Need branch coverage and boundary value tests.",
    }
    example = EXAMPLE_PROMPTS.get(selected_agent, "Describe your engineering problem...")
    st.caption(f"Example: *{example}*")

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
