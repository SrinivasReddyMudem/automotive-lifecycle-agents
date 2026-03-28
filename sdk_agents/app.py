"""
Streamlit web UI for sdk_agents.
Run with: streamlit run sdk_agents/app.py
"""

import re as _re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))  # noqa: E402

import streamlit as st  # noqa: E402
from dotenv import load_dotenv  # noqa: E402

load_dotenv(Path(__file__).parent / ".env")

from sdk_agents.core.registry import get_agent, AGENT_NAMES, AGENT_DISPLAY_NAMES  # noqa: E402
from sdk_agents.core.base_agent import AgentError  # noqa: E402
from sdk_agents.core.renderer import (  # noqa: E402
    safe_render,
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

# ── Auto-routing: weighted keyword scoring ─────────────────────────────────────
# Each agent has (keyword → score) pairs.
# Score values:  4 = uniquely identifies this agent (almost never ambiguous)
#                3 = strong signal — nearly always this domain
#                2 = medium signal — usually this domain, sometimes shared
#                1 = weak signal — corroborating evidence only
# Routing: score all agents → pick highest → require minimum total ≥ 3 to fire.

AGENT_SCORES: dict[str, dict[str, int]] = {
    "can-bus-analyst": {
        "bus-off": 4, "babbling idiot": 4, "candump": 4, "error counter": 4,
        "tec counter": 4, "rec counter": 4, "bit stuffing": 4, "error passive": 4,
        "error active": 4, "oscilloscope can": 4, "can-fd": 3, "error frame": 3,
        "bit timing": 3, "can trace": 3, "120 ohm": 3, "can matrix": 3,
        "dbc file": 3, "canalyzer": 3, "canoe": 2, "can node": 2, "baud rate": 2,
        "termination": 2, "transceiver": 2, "can bus": 2, "bus load": 2,
        "can high": 2, "can low": 2, "tec": 1, "rec": 1, "can": 1,
    },
    "field-debug-fae": {
        "nrc": 4, "negative response code": 4, "conditionsnotcorrect": 4,
        "securityaccessdenied": 4, "requestoutofrange": 4, "freeze frame": 4,
        "dtc status byte": 4, "seed key": 4, "service 0x27": 4, "service 0x22": 4,
        "customer says": 4, "customer reports": 4,
        "service 0x10": 3, "service 0x19": 3, "security access": 3,
        "programming session": 3, "extended session": 3, "flash programming": 3,
        "uds session": 3, "ecu not responding": 3, "negative response": 3,
        "workshop": 3, "vehicle complaint": 3, "field return": 3, "field failure": 3,
        "won't start": 3, "warning light": 2,
        "tester present": 2, "dtc": 2, "fault code": 2, "diagnostic session": 2,
        "field issue": 2, "customer complaint": 2, "0x22": 2, "0x31": 2,
        "diagnostic": 1,
    },
    "sw-integrator": {
        "port not connected": 4, "rte generation fail": 4, "rte generation error": 4,
        "linker error": 4, "memory map conflict": 4, "bsw wiring": 4,
        "port prototype mismatch": 4, "arxml error": 4, "composition error": 4,
        "rte inconsistency": 4, "integration issue": 3, "build error": 3,
        "integration plan": 3, "sw baseline": 3, "delivery package": 3,
        "bsw module version": 3, "undefined reference": 3, "integration test": 2,
        "build system": 2, "cmake": 2, "makefile": 2, "integration": 1,
    },
    "autosar-bsw-developer": {
        "arxml": 4, "p-port": 4, "r-port": 4, "rte api": 4, "rte_read": 4,
        "rte_write": 4, "rte_call": 4, "davinci": 4, "eb tresos": 4,
        "runnable entity": 4, "sender-receiver": 4, "client-server": 4,
        "bsw configuration": 4, "software component type": 4,
        "autosar classic": 3, "bsw module": 3, "swc design": 3,
        "composition swc": 3, "port interface": 3, "data element": 3,
        "autosar r4": 3, "autosar r22": 3, "swc port": 3,
        "autosar": 2, "swc": 2, "runnable": 2, "bsw": 2, "rte": 1,
    },
    "embedded-c-developer": {
        "cfsr": 4, "hard fault": 4, "stack overflow": 4, "mpu fault": 4,
        "hardfault": 4, "nvic": 4, "memory barrier": 4, "cortex-m": 4,
        "cortex-r": 4, "bare metal": 4, "isr": 3, "watchdog reset": 3,
        "dma transfer": 3, "volatile": 3, "freertos": 3, "context switch": 3,
        "linker script": 3, "startup code": 3, "stack depth": 3,
        "interrupt priority": 3, "mutex": 2, "semaphore": 2, "rtos": 2,
        "watchdog": 2, "interrupt": 2, "embedded c": 2, "microcontroller": 2,
        "cortex": 2, "embedded": 1,
    },
    "misra-reviewer": {
        "misra": 4, "misra c": 4, "misra c:2012": 4, "polyspace": 4,
        "qac": 4, "pc-lint": 4, "coverity": 4, "deviation justification": 4,
        "compliant rewrite": 4, "mandatory rule": 4, "required rule": 4,
        "advisory rule": 4, "rule violation": 3, "static analysis finding": 3,
        "deviation request": 3, "coding standard": 3, "dead code": 2,
        "undefined behaviour": 2, "implicit cast": 2, "static analysis": 2,
        "deviation": 1,
    },
    "aspice-process-coach": {
        "aspice": 4, "automotive spice": 4, "swe.1": 4, "swe.2": 4,
        "swe.3": 4, "swe.4": 4, "swe.5": 4, "swe.6": 4, "pa 2.1": 4,
        "pa 2.2": 4, "capability level": 4, "process area": 4,
        "gap analysis": 3, "work product missing": 3, "base practice": 3,
        "major finding": 3, "minor finding": 3, "assessment": 3,
        "aspice level": 3, "process attribute": 3, "traceability matrix": 3,
        "review record": 2, "baseline freeze": 2, "work product": 2,
        "process compliance": 2, "audit": 2,
    },
    "gate-review-approver": {
        "gate review": 4, "go/no-go": 4, "sop readiness": 4, "sor readiness": 4,
        "release gate": 4, "formal release approval": 4, "gate decision": 4,
        "gate criteria": 3, "release approval": 3, "milestone gate": 3,
        "release readiness": 3, "gate": 2,
    },
    "safety-and-cyber-lead": {
        "hara": 4, "hazardous event": 4, "tara": 4, "iso 26262": 4,
        "iso 21434": 4, "asil-d": 4, "asil-c": 4, "cybersecurity goal": 4,
        "attack feasibility": 4, "ftti": 4, "damage scenario": 4,
        "safety goal": 3, "threat scenario": 3, "controllability": 3,
        "severity": 3, "exposure": 3, "unece r155": 3, "cal-": 3,
        "asil-b": 2, "asil-a": 2, "asil": 2, "functional safety": 2,
        "safe state": 2, "safety mechanism": 2, "hazard": 2,
        "cybersecurity": 2, "safety": 1,
    },
    "sw-project-lead": {
        "change request": 4, "cr impact": 4, "schedule impact": 4,
        "ota update requirement": 4, "scope change": 4, "statement of work": 4,
        "risk register": 3, "milestone delay": 3, "resource plan": 3,
        "schedule delta": 3, "feasibility study": 3, "project risk": 3,
        "stakeholder": 2, "milestone": 2, "project plan": 2, "nre": 2,
        "schedule": 1, "project": 1,
    },
    "regression-analyst": {
        "regression analysis": 4, "test delta": 4, "baseline comparison": 4,
        "new test failures": 4, "pass rate dropped": 4, "pass rate change": 4,
        "flaky test": 4, "test comparison": 4, "test instability": 3,
        "coverage decreased": 3, "test history": 3, "failed tests after change": 3,
        "new failures": 3, "tests failed": 2, "test report": 2,
        "regression": 2, "test failures": 2, "test failure": 3, "baseline": 2,
    },
    "sil-hil-test-planner": {
        "hardware in the loop": 4, "software in the loop": 4, "dspace": 4,
        "scalexio": 4, "microautobox": 4, "hil rack": 4, "test bench setup": 4,
        "fault injection test": 4, "plant model": 4, "canoe capl": 3,
        "hil test": 3, "sil test": 3, "test environment": 3,
        "ni teststand": 3, "automation framework": 3, "test bench": 3,
        "hil": 2, "sil": 2, "test plan": 2,
    },
    "sw-unit-tester": {
        "mc/dc": 4, "mcdc": 4, "modified condition decision": 4,
        "equivalence partition": 4, "boundary value analysis": 4,
        "googletest": 4, "unity test": 4, "vectorcast": 4, "ldra": 4,
        "cpputest": 4, "test case design": 4, "stub function": 4,
        "independence pair": 4, "unit test": 3, "branch coverage": 3,
        "statement coverage": 3, "function under test": 3, "test harness": 3,
        "mock": 2, "test coverage": 2, "unit tester": 2, "stub": 2,
    },
}

# Minimum total score needed to trigger auto-routing (avoids noise from single weak keywords)
_MIN_ROUTE_SCORE = 3

# ── Typo and variant normalization applied before scoring ──────────────────────

_NORMALIZATIONS: list[tuple[str, str]] = [
    # CAN bus variants
    (r"\bbus\s*off\b",               "bus-off"),
    (r"\bcanbus\b",                   "can bus"),
    (r"\bcan[\s_-]fd\b",             "can-fd"),
    (r"\bcandump\b",                  "candump"),
    (r"\bbabl(ing)?\b",              "babbling"),
    (r"\bbit[\s_]tim(ing)?\b",       "bit timing"),
    (r"\berror[\s_]counter\b",       "error counter"),
    (r"\btec[\s_]counter\b",         "tec counter"),
    (r"\brec[\s_]counter\b",         "rec counter"),
    # ASIL variants
    (r"\basil[\s_]([a-dA-D])\b",     r"asil-\1"),
    # SWE.x variants: swe4 / swe 4 / swe_4 → swe.4
    (r"\bswe[\s_]?([1-6])\b",        r"swe.\1"),
    # UDS/NRC service codes: 0x22 stays, service22 → service 0x22
    (r"\bservice[\s_]?0?x?([0-9a-fA-F]{2})\b", r"service 0x\1"),
    (r"\bnrc[\s_]?0?x?([0-9a-fA-F]{2})\b",     r"nrc"),
    # Hard fault variants
    (r"\bhard[\s_]fault\b",          "hard fault"),
    (r"\bhardfault\b",               "hard fault"),
    (r"\bstack[\s_]overflow\b",      "stack overflow"),
    # MISRA variants
    (r"\bmisra[\s_]c\b",             "misra"),
    (r"\bmisra[\s]?c:?2012\b",       "misra"),
    # AUTOSAR variants
    (r"\bautosar[\s_]classic\b",     "autosar classic"),
    (r"\bp[\s_]port\b",             "p-port"),
    (r"\br[\s_]port\b",             "r-port"),
    (r"\bsender[\s_]receiver\b",    "sender-receiver"),
    (r"\bclient[\s_]server\b",      "client-server"),
    # RTE variants
    (r"\brte[\s_]generation[\s_]?(fail|error|issue)\b", "rte generation fail"),
    (r"\bport[\s_]not[\s_]connected\b", "port not connected"),
    # dSPACE / HIL / SIL
    (r"\bd[\s_]?space\b",           "dspace"),
    (r"\bhardware[\s_]in[\s_]the[\s_]loop\b", "hardware in the loop"),
    (r"\bsoftware[\s_]in[\s_]the[\s_]loop\b", "software in the loop"),
    (r"\btest[\s_]bench\b",         "test bench"),
    # Unit test / MC/DC
    (r"\bunit[\s_]test(ing|s)?\b",  "unit test"),
    (r"\bmc[\s_/]?dc\b",            "mc/dc"),
    (r"\bboundary[\s_]value\b",     "boundary value analysis"),
    (r"\bequivalence[\s_]part\w*\b", "equivalence partition"),
    # Project lead
    (r"\bchange[\s_]request\b",     "change request"),
    (r"\bschedule[\s_]impact\b",    "schedule impact"),
    (r"\brisk[\s_]register\b",      "risk register"),
    # Safety/HARA
    (r"\biso[\s_]?26262\b",         "iso 26262"),
    (r"\biso[\s_]?21434\b",         "iso 21434"),
    (r"\bsafety[\s_]goal\b",        "safety goal"),
    (r"\bhazardous[\s_]event\b",    "hazardous event"),
    # ASPICE
    (r"\bgap[\s_]analysis\b",       "gap analysis"),
    (r"\bprocess[\s_]area\b",       "process area"),
    (r"\bwork[\s_]product\b",       "work product"),
    # Regression
    (r"\btest[\s_]delta\b",         "test delta"),
    (r"\bbaseline[\s_]comp\w*\b",   "baseline comparison"),
    (r"\bpass[\s_]rate\b",          "pass rate"),
    (r"\bflaky[\s_]test\b",         "flaky test"),
    # Gate review
    (r"\bgate[\s_]review\b",        "gate review"),
    (r"\bgo[\s_/]no[\s_/]go\b",    "go/no-go"),
    (r"\bsop[\s_]readiness\b",      "sop readiness"),
    # Diagnostics
    (r"\bdiagnostic[\s_]trouble[\s_]code\b", "dtc"),
    (r"\bnegative[\s_]response\b",  "negative response"),
    (r"\bfreeze[\s_]frame\b",       "freeze frame"),
    # Simple plural/suffix stripping for key terms
    (r"\bfailures\b",               "failure"),
    (r"\btests\b",                  "test"),
    (r"\bhazards\b",                "hazard"),
]


def _normalize(text: str) -> str:
    """Apply all normalization patterns, return cleaned lowercase string."""
    s = text.lower()
    for pattern, replacement in _NORMALIZATIONS:
        s = _re.sub(pattern, replacement, s)
    return s


def detect_agents(text: str) -> list[str]:
    """
    Score all agents and return a ranked list of relevant agents.

    Primary:    highest scorer above _MIN_ROUTE_SCORE (ties broken by max keyword weight).
    Secondaries: any other agent scoring >= 60 % of primary AND >= _MIN_ROUTE_SCORE.
                 These represent genuinely overlapping domains (e.g. CAN bus-off + UDS
                 diagnostic session; ASPICE gap + MISRA violation; HARA + TARA).

    Returns [] when nothing scores above the threshold (general/off-topic query).
    """
    normalized = _normalize(text)
    scores: dict[str, int] = {}
    for agent, kw_map in AGENT_SCORES.items():
        total = sum(w for kw, w in kw_map.items() if kw in normalized)
        if total > 0:
            scores[agent] = total
    if not scores:
        return []
    best_score = max(scores.values())
    if best_score < _MIN_ROUTE_SCORE:
        return []

    # Primary — break ties by highest single-keyword weight (more specific vocabulary wins)
    top = [a for a, s in scores.items() if s == best_score]
    primary = max(top, key=lambda a: max(AGENT_SCORES[a].values()))

    # Secondaries — floor is capped at 7 so dominant primaries don't crowd out
    # genuinely overlapping domains (e.g. AUTOSAR score 20 + MISRA score 7)
    secondary_floor = max(_MIN_ROUTE_SCORE, min(best_score * 0.4, 7))
    secondaries = [
        a for a, s in sorted(scores.items(), key=lambda x: -x[1])
        if a != primary and s >= secondary_floor
    ]

    return [primary] + secondaries


def auto_detect_agent(text: str) -> str | None:
    """Return primary detected agent or None (backward-compatible wrapper)."""
    agents = detect_agents(text)
    return agents[0] if agents else None


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
    page_icon=":car:",
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
        _AUTO_LABEL = "Auto — detect from input"
        selected_display = st.selectbox(
            "Agent",
            options=[_AUTO_LABEL] + [AGENT_DISPLAY_NAMES[n] for n in AGENT_NAMES],
            index=0,
            key="agent_selector",
        )
        if selected_display == _AUTO_LABEL:
            selected_agent = None   # resolved per query from user input keywords
        else:
            selected_agent = next(
                k for k, v in AGENT_DISPLAY_NAMES.items() if v == selected_display
            )
        if selected_agent is None:
            st.caption("Describe your problem — the agent is selected automatically from your words.")
        else:
            st.caption(f"Fixed to **{selected_display}**. Clear the dropdown to return to Auto.")

# ── About page ─────────────────────────────────────────────────────────────────
if page == "About":
    st.title("Automotive Lifecycle Agents")
    st.subheader("Structured, actionable AI for automotive ECU development, integration, and diagnostics")
    st.markdown("---")

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Tests Passing", "✅ 78")
    col_m2.metric("Agents", "✅ 13")
    col_m3.metric("Skills", "✅ 8")
    col_m4.metric("CI Checks", "✅ 5")

    st.markdown("---")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
Built from real automotive ECU experience across development, integration, testing,
and project leadership. These agents do not replace engineering judgment — they
replicate the methodical analysis a domain expert applies, producing structured,
traceable, and safety-compliant outputs. The system is developed using professional
software practices, including automated testing, CI/CD pipelines, and versioned
model validation, ensuring reliability, reproducibility, and production-ready performance.

**Expert-level reasoning, not suggestions**

Generic AI gives broad suggestions. These agents classify the problem first —
by OSI layer, AUTOSAR layer, or process area — then apply the relevant standard
to produce output an engineer can directly act on.

*Question: "CAN node goes bus-off after 3 minutes, only when engine running"*
""")

        ex_col1, ex_col2 = st.columns(2)
        with ex_col1:
            st.caption("Generic AI")
            st.code('''"Check your CAN bus wiring
 and termination. Verify
 baud rate settings are
 consistent across all
 nodes..."''', language="text")
        with ex_col2:
            st.caption("This agent")
            st.code("""OSI Layer:     L1 Physical
AUTOSAR Layer: MCAL (CanDrv)
Tool:          Oscilloscope

TEC Math:
  Net climb = 256 / 180s
              = 1.41 TEC/s
  Bus-off: ~181s — 3 min ✓

Causes:
  [HIGH]   Alternator ripple
           Vcc AC-coupled
           Pass < 200mV
           Fail > 500mV

  [MEDIUM] GND offset
           ECU GND vs bat-
           Pass < 50mV
           Fail > 200mV

Decision Flow:
  Vcc + GND OK?
  +-- No  --> Fix supply
  +-- Yes --> Error frames?
      +-- No  --> Heat gun
      +-- Yes --> L1/L7""", language="text")

        st.markdown("""
**What engineers get**

- Root cause classification before diagnosis — never jumps to solutions
- Calculations shown with full working (TEC math, ASIL determination, CAL scoring)
- Specific tool, probe point, and numeric pass/fail threshold per probable cause
- Standards-compliant reasoning — not pattern-matched suggestions

**How output quality is ensured**

Every response passes through a layered validation system — covering structure,
domain correctness, and content completeness. Calculations are verified, domain
rules enforced, and decision flows cross-checked against automotive standards.

The result: consistent, reproducible outputs — not pattern-matched suggestions.

**Standards**

ISO 26262 · ASPICE v3.1 · MISRA C:2012 · AUTOSAR Classic ·
ISO 21434 · ISO 14229 (UDS) · ISO 11898 (CAN) · IEEE 802.3bw

*All examples use synthetic data only.*
""")

    with col2:
        st.markdown("**Built by**")
        st.markdown("Srinivas Reddy Mudem")
        st.markdown(
            "Automotive ECU engineer across development, integration, "
            "testing, and project leadership."
        )
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
- CAN bus / error counters / TEC math
- ISO 26262 / HARA / ASIL table
- ASPICE SWE.1–6 · SUP.8 · SUP.10 · MAN.3
- MISRA C:2012 rules + deviations
- AUTOSAR Classic BSW/RTE/COM
- UDS/diagnostics / NRC codes
- ISO 21434 / TARA / attack feasibility
- Embedded RTOS / ISR / watchdog
        """)

        st.markdown("---")
        st.info("Use **Try the Agent** in the sidebar to run a live query.")

# ── Agent chat page ────────────────────────────────────────────────────────────
elif page == "Try the Agent":
    st.header(selected_display)

    history_key = f"history_{selected_agent or 'auto'}"
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
    if selected_agent is None:
        example = "CAN node goes bus-off after 3 minutes only when engine running — or any other engineering problem"
    else:
        example = EXAMPLE_PROMPTS.get(selected_agent, "Describe your engineering problem...")
    st.caption(f"Example: *{example}*")

    # Display chat history
    for entry in st.session_state[history_key]:
        with st.chat_message("user"):
            st.markdown(entry["prompt"])
        with st.chat_message("assistant"):
            if entry.get("result") is None:
                st.warning("No agent matched for this input.")
                continue
            entry_agent = entry.get("agent", selected_agent)
            _render = RENDER_MAP.get(entry_agent, render_agent_error)
            _render(entry["result"])

    # Chat input
    if prompt := st.chat_input("Describe the fault or ask your engineering question..."):
        # Multi-agent routing: detect primary + any strongly overlapping secondaries
        detected_agents = detect_agents(prompt)
        primary_agent = detected_agents[0] if detected_agents else None
        secondaries = detected_agents[1:] if len(detected_agents) > 1 else []
        # active_agent: use auto-detected primary, fall back to manual selection
        active_agent = primary_agent if primary_agent else selected_agent

        with st.chat_message("user"):
            st.markdown(prompt)
            if primary_agent and primary_agent != selected_agent:
                st.caption(f"Auto-routed to: **{AGENT_DISPLAY_NAMES[primary_agent]}**")
            if secondaries:
                names = ", ".join(f"**{AGENT_DISPLAY_NAMES[a]}**" for a in secondaries)
                st.info(
                    f"Multi-skill query detected. Also relevant: {names}. "
                    f"Switch agents in the sidebar to get each perspective.",
                )

        # If Auto mode and no agent could be detected, prompt the user
        if active_agent is None:
            with st.chat_message("assistant"):
                st.warning(
                    "No agent matched for this input. Try adding domain terms like "
                    "*bus-off, NRC 0x22, ASIL-B, ASPICE SWE.4, hard fault, MISRA rule* — "
                    "or pick an agent manually from the sidebar."
                )
            st.session_state[history_key].append({
                "prompt": prompt, "result": None, "agent": None,
            })
            st.stop()

        with st.chat_message("assistant"):
            with st.spinner("Analysing..."):
                agent = get_agent(active_agent)
                result = agent.run(prompt)

            render_fn = RENDER_MAP.get(active_agent)
            if render_fn:
                safe_render(render_fn, result)
            elif isinstance(result, AgentError):
                render_agent_error(result)
            else:
                st.json(result.model_dump())

        st.session_state[history_key].append({
            "prompt": prompt,
            "result": result,
            "agent": active_agent,
        })
