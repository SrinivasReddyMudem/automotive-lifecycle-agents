"""
Renders structured agent output as Streamlit UI components.
Each agent type gets a dedicated render function.
"""

import streamlit as st
from sdk_agents.core.base_agent import AgentError


def render_agent_error(error: AgentError) -> None:
    st.error(f"**{error.error_type.replace('_', ' ').title()}**")
    st.markdown(f"Agent: `{error.agent}`")
    st.markdown(f"Message: {error.message}")
    if error.raw_response:
        with st.expander("Raw API response (for debugging)"):
            st.code(error.raw_response)


def render_can_bus_analyst(output) -> None:
    from sdk_agents.integrator.can_bus_analyst.schema import CanBusAnalystOutput
    if isinstance(output, AgentError):
        render_agent_error(output)
        return

    # Expert diagnosis — always visible at top
    st.info(f"**Expert Diagnosis**\n\n{output.expert_diagnosis}")

    col1, col2, col3 = st.columns(3)
    col1.metric("OSI Layer", output.osi_layer)
    col2.metric("AUTOSAR Layer", output.autosar_layer)
    col3.metric("Recommended Tool", output.recommended_tool)

    st.markdown("---")

    with st.expander("TEC Math", expanded=True):
        st.code(output.tec_math)

    with st.expander("Probable Causes (3 ranked)", expanded=True):
        for i, cause in enumerate(output.probable_causes):
            rank_color = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(cause.rank, "⚪")
            st.markdown(f"**{rank_color} {cause.rank} — {cause.description}**")
            st.markdown(f"- **Test:** {cause.test}")
            st.markdown(f"- **Pass:** {cause.pass_criteria}")
            st.markdown(f"- **Fail:** {cause.fail_criteria}")
            if i < len(output.probable_causes) - 1:
                st.markdown("---")

    with st.expander("Decision Flow"):
        st.code(output.decision_flow)

    with st.expander("Narrowing Questions"):
        for i, q in enumerate(output.narrowing_questions, 1):
            st.markdown(f"**Q{i}: {q.question}**")
            st.markdown(f"- Yes → {q.yes_consequence}")
            st.markdown(f"- No → {q.no_consequence}")

    with st.expander("Self Evaluation"):
        for line in output.self_evaluation:
            icon = "✅" if line.result == "PASS" else "❌"
            st.markdown(f"{icon} **{line.item}** — {line.evidence}")
