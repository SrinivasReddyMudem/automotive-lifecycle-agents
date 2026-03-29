"""
Renders structured agent output as Streamlit UI components.
Each agent type gets a dedicated render function.
"""

import json
import streamlit as st
from sdk_agents.core.base_agent import AgentError


# ── Shared helpers ──────────────────────────────────────────────────────────────

def safe_render(render_fn, output) -> None:
    """
    Wraps any render function with a fallback raw-JSON view.
    If the render function raises AttributeError (stale field reference or
    unexpected LLM field name), the full structured output is still shown
    as formatted JSON so the user always gets the agent's answer.
    """
    if type(output).__name__ == "AgentError":
        render_agent_error(output)
        return
    try:
        render_fn(output)
    except AttributeError as e:
        st.warning(
            f"Display layout error: `{e}`. "
            f"Showing raw structured output below — all agent content is present."
        )
        if isinstance(output, AgentError):
            st.json(output.model_dump())
        else:
            try:
                st.json(json.loads(output.model_dump_json()))
            except Exception:
                st.code(str(output))


def render_agent_error(error: AgentError) -> None:
    st.error(f"**{error.error_type.replace('_', ' ').title()}**")
    st.markdown(f"Agent: `{error.agent}`")
    st.markdown(f"Message: {error.message}")
    if error.raw_response:
        with st.expander("Raw API response (for debugging)"):
            st.code(error.raw_response)


def _render_self_evaluation(self_eval: list) -> None:
    with st.expander("Self Evaluation"):
        for line in self_eval:
            icon = "✅" if line.result == "PASS" else "❌"
            st.markdown(f"{icon} **{line.item}** — {line.evidence}")


def _render_probable_causes(causes: list) -> None:
    with st.expander("Probable Causes (ranked)", expanded=True):
        for i, cause in enumerate(causes):
            rank_color = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(cause.rank, "⚪")
            is_hyp = getattr(cause, "is_hypothesis", False)
            hyp_tag = " *(hypothesis)*" if is_hyp else ""
            st.markdown(f"**{rank_color} {cause.rank} — {cause.description}**{hyp_tag}")
            # ranking_reason — available on new-style ProbableCause only
            ranking_reason = getattr(cause, "ranking_reason", "")
            if ranking_reason:
                st.caption(f"Rank rationale: {ranking_reason}")
            st.markdown(f"- **Test:** {cause.test}")
            st.markdown(f"- **Pass:** {cause.pass_criteria}")
            st.markdown(f"- **Fail:** {cause.fail_criteria}")
            # validation_test — single definitive confirm/deny test
            validation_test = getattr(cause, "validation_test", "")
            if validation_test:
                st.info(f"**Definitive test:** {validation_test}")
            if i < len(causes) - 1:
                st.markdown("---")


def _render_calc_block(lines: list | str, label: str, expanded: bool = True) -> None:
    """
    Render a step-by-step calculation block.
    All lines except the last are shown as a code block.
    The final line (the plain-English conclusion) is highlighted with st.info().
    """
    text_list = lines if isinstance(lines, list) else str(lines).splitlines()
    with st.expander(label, expanded=expanded):
        if len(text_list) > 1:
            st.code("\n".join(text_list[:-1]))
            st.info(f"**Result:** {text_list[-1].lstrip('→ ').strip()}")
        else:
            st.code("\n".join(text_list))


def _render_narrowing_questions(questions: list) -> None:
    with st.expander("Narrowing Questions"):
        for i, q in enumerate(questions, 1):
            st.markdown(f"**Q{i}: {q.question}**")
            st.markdown(f"- Yes → {q.yes_consequence}")
            st.markdown(f"- No → {q.no_consequence}")


# ── CAN Bus Analyst ─────────────────────────────────────────────────────────────

def render_can_bus_analyst(output) -> None:
    if isinstance(output, AgentError):
        render_agent_error(output)
        return

    # Protocol detection badge
    proto = getattr(output, "protocol_detection", None)
    if proto:
        conf_icon = {"HIGH": "🟢", "MEDIUM": "🟡", "LOW": "🔴"}.get(proto.confidence, "⚪")
        st.caption(f"Protocol detected: **{proto.protocol}** {conf_icon} {proto.confidence} confidence — {proto.detected_from}")

    # Input analysis + data sufficiency
    input_analysis = getattr(output, "input_analysis", None)
    data_suf = getattr(output, "data_sufficiency", None)
    if input_analysis or data_suf:
        with st.expander("Input Analysis & Data Sufficiency", expanded=False):
            if data_suf:
                suf_color = {"SUFFICIENT": "success", "PARTIAL": "warning", "INSUFFICIENT": "error"}.get(
                    data_suf.level, "info"
                )
                conf = getattr(data_suf, "confidence", "")
                conf_reason = getattr(data_suf, "confidence_reason", "")
                conf_str = f" | Confidence: **{conf}**" if conf else ""
                getattr(st, suf_color)(f"**Data: {data_suf.level}**{conf_str}")
                if conf_reason:
                    st.caption(conf_reason)
                missing = getattr(data_suf, "missing_critical_data", None)
                if missing and missing != ["None — data is complete"]:
                    st.markdown("**Missing critical data:**")
                    for item in missing:
                        st.caption(f"- {item}")
            if input_analysis:
                facts = getattr(input_analysis, "input_facts", [])
                assumptions = getattr(input_analysis, "assumptions", [])
                if facts:
                    st.markdown("**Observed facts:**")
                    for f in facts:
                        st.markdown(f"- {f}")
                if assumptions:
                    st.markdown("**Assumptions (not stated by user):**")
                    for a in assumptions:
                        st.caption(f"⚠ {a}")

    expert_diag = getattr(output, "expert_diagnosis", None)
    if expert_diag:
        st.markdown("### 💡 Key Insight")
        st.info(expert_diag)

    # Diagnosis basis — fact → implication chain
    basis = getattr(output, "diagnosis_basis", None)
    if basis:
        with st.expander("Diagnosis Basis", expanded=False):
            for line in basis:
                st.markdown(f"**{line.fact}**")
                st.caption(f"→ {line.implication}")

    col1, col2 = st.columns(2)
    col1.metric("OSI Layer", output.osi_layer)
    col2.metric("AUTOSAR Layer", output.autosar_layer)

    # Tool selection (new field — safe fallback to legacy recommended_tool)
    ts = getattr(output, "tool_selection", None)
    if ts:
        with st.expander("Recommended Tools", expanded=False):
            st.markdown(f"**Primary:** {ts.primary}")
            st.markdown(f"**Secondary:** {ts.secondary}")
            st.markdown(f"**Why:** {ts.reason}")
            st.caption(f"Fallback if unavailable: {ts.fallback}")
    elif hasattr(output, "recommended_tool"):
        st.metric("Recommended Tool", output.recommended_tool)

    st.markdown("---")

    tec = output.tec_math
    tec_text = "\n".join(tec) if isinstance(tec, list) else str(tec)
    if "N/A" not in tec_text:
        _render_calc_block(tec, "TEC (Transmit Error Counter) Math", expanded=True)
    else:
        with st.expander("TEC (Transmit Error Counter) Math", expanded=False):
            st.info(tec_text if isinstance(tec, str) else tec[0])

    bus = output.bus_load_calc
    bus_text = "\n".join(bus) if isinstance(bus, list) else str(bus)
    if "N/A" not in bus_text:
        _render_calc_block(bus, "CAN Bus Load Calculation", expanded=True)

    _render_probable_causes(output.probable_causes)

    contras = getattr(output, "contradictions", None)
    if contras and contras != ["None identified"]:
        with st.expander("Contradictions"):
            for c in contras:
                st.warning(c)

    with st.expander("Decision Flow"):
        flow = output.decision_flow
        st.code("\n".join(flow) if isinstance(flow, list) else flow)

    _render_narrowing_questions(output.narrowing_questions)
    _render_self_evaluation(output.self_evaluation)


# ── Field Debug FAE ─────────────────────────────────────────────────────────────

def render_field_debug_fae(output) -> None:
    if isinstance(output, AgentError):
        render_agent_error(output)
        return

    # Protocol detection badge (new field — safe fallback if absent)
    proto = getattr(output, "protocol_detection", None)
    if proto:
        conf_icon = {"HIGH": "🟢", "MEDIUM": "🟡", "LOW": "🔴"}.get(proto.confidence, "⚪")
        st.caption(f"Protocol detected: **{proto.protocol}** {conf_icon} {proto.confidence} confidence — {proto.detected_from}")

    # Input analysis + data sufficiency
    input_analysis = getattr(output, "input_analysis", None)
    data_suf = getattr(output, "data_sufficiency", None)
    if input_analysis or data_suf:
        with st.expander("Input Analysis & Data Sufficiency", expanded=False):
            if data_suf:
                suf_color = {"SUFFICIENT": "success", "PARTIAL": "warning", "INSUFFICIENT": "error"}.get(
                    data_suf.level, "info"
                )
                getattr(st, suf_color)(f"**Data: {data_suf.level}**")
                missing = getattr(data_suf, "missing_critical_data", None)
                if missing and missing != ["None — data is complete"]:
                    st.markdown("**Missing critical data:**")
                    for item in missing:
                        prefix = "🔴" if item.startswith("[CRITICAL]") else "🟡"
                        st.caption(f"{prefix} {item}")
            if input_analysis:
                facts = getattr(input_analysis, "input_facts", [])
                assumptions = getattr(input_analysis, "assumptions", [])
                if facts:
                    st.markdown("**Observed facts:**")
                    for f in facts:
                        st.markdown(f"- {f}")
                if assumptions:
                    st.markdown("**Assumptions (not stated by user):**")
                    for a in assumptions:
                        st.caption(f"⚠ {a}")

    st_tr = output.symptom_translation
    with st.expander("STEP 3 — Symptom Translation", expanded=True):
        col1, col2 = st.columns(2)
        col1.markdown(f"**Customer complaint:** {st_tr.customer_complaint}")
        col1.markdown(f"**Function affected:** {st_tr.function_affected}")
        col1.markdown(f"**Translated to:** {st_tr.translated_to}")
        col2.metric("AUTOSAR Layer", st_tr.autosar_layer)
        col2.metric("OSI Layer", st_tr.osi_layer)

    fd = output.fault_details
    safety_icon = "🔴" if fd.safety_relevant == "YES" else "🟢"
    col1, col2, col3 = st.columns(3)
    col1.metric("DTC", fd.dtc_code)
    col2.metric("Status Byte", fd.status_byte)
    col3.metric("Safety Relevant", f"{safety_icon} {fd.safety_relevant}")

    with st.expander("DTC Details", expanded=True):
        st.markdown(f"**Description:** {fd.dtc_description}")
        st.markdown(f"**System:** {fd.system}")
        st.code(fd.status_byte_decoded)
        if fd.safety_relevant == "YES":
            st.warning(f"**Safety Impact:** {fd.safety_impact}")

    st.markdown("---")
    with st.expander("Analysis", expanded=True):
        st.markdown(output.analysis)

    _render_probable_causes(output.probable_causes)

    uds = output.uds_session_analysis
    if uds.nrc_code != "N/A":
        with st.expander("UDS Session Analysis"):
            st.markdown(f"**NRC:** `{uds.nrc_code}` — {uds.nrc_name}")
            st.markdown("**Root causes:**")
            for rc in uds.nrc_root_causes:
                st.markdown(f"- {rc}")
            if uds.session_sequence_issue != "N/A":
                st.markdown(f"**Session sequence issue:** {uds.session_sequence_issue}")

    tec = output.tec_math
    tec_text = "\n".join(tec) if isinstance(tec, list) else str(tec)
    if "N/A" not in tec_text:
        _render_calc_block(tec, "TEC (Transmit Error Counter) Math", expanded=False)

    with st.expander("Debug Steps", expanded=True):
        for step in output.debug_steps:
            st.markdown(f"**Step {step.step_number} — {step.tool}**")
            st.markdown(f"- Action: {step.action}")
            st.markdown(f"- Expected: {step.expected_output}")

    _render_self_evaluation(output.self_evaluation)


# ── SW Integrator ───────────────────────────────────────────────────────────────

def render_sw_integrator(output) -> None:
    if isinstance(output, AgentError):
        render_agent_error(output)
        return

    ec = output.error_classification
    col1, col2 = st.columns(2)
    col1.metric("Error Type", ec.error_type[:30])
    col2.metric("AUTOSAR Layer", ec.autosar_layer)
    st.info(f"**Root Cause Hypothesis:** {ec.root_cause_hypothesis}")
    st.markdown(f"**Tool:** {ec.tool_view}")
    st.markdown("---")

    with st.expander("Analysis", expanded=True):
        st.markdown(output.analysis)

    _render_probable_causes(output.probable_causes)

    res = output.resource_budget_calc
    res_text = "\n".join(res) if isinstance(res, list) else str(res)
    if "N/A" not in res_text:
        with st.expander("Resource Budget — CPU / NvM", expanded=True):
            st.code(res_text)

    with st.expander("Memory Budget"):
        for sec in output.memory_budget:
            ok_icon = "✅" if sec.headroom_ok == "YES" else ("⚠️" if sec.headroom_ok == "UNKNOWN" else "❌")
            st.markdown(f"{ok_icon} **{sec.section}** — Used: {sec.used_hex} / Total: {sec.total_hex} ({sec.utilization_pct})")

    with st.expander("Resolution Steps", expanded=True):
        for step in output.resolution_steps:
            st.markdown(f"**Step {step.step_number} — {step.tool}**")
            st.markdown(f"- {step.action}")
            st.markdown(f"- Expected: {step.expected_output}")

    with st.expander("ASPICE SWE.5 Evidence"):
        for wp in output.aspice_swe5_evidence:
            icon = "✅" if wp.status == "PRESENT" else ("⚠️" if wp.status == "INCOMPLETE" else "❌")
            st.markdown(f"{icon} **{wp.work_product}** ({wp.wp_id}) — {wp.note}")

    _render_narrowing_questions(output.narrowing_questions)
    _render_self_evaluation(output.self_evaluation)


# ── AUTOSAR BSW Developer ───────────────────────────────────────────────────────

def render_autosar_bsw_developer(output) -> None:
    if isinstance(output, AgentError):
        render_agent_error(output)
        return

    col1, col2, col3 = st.columns(3)
    col1.metric("AUTOSAR Version", output.autosar_version)
    col2.metric("ASIL Level", output.asil_level)
    col3.metric("SWC Type", output.swc_type)
    st.markdown(f"**SWC Name:** `{output.swc_name}`")
    st.markdown("---")

    def _render_ports(ports, label):
        if ports:
            with st.expander(label, expanded=True):
                for port in ports:
                    st.markdown(f"**{port.port_name}** ({port.port_direction} / {port.interface_type})")
                    st.markdown(f"- Interface: `{port.interface_name}`")
                    st.markdown(f"- Data/Op: {port.data_element_or_operation}")
                    st.code(port.rte_api, language="c")
                    if port.asil_constraint != "N/A":
                        st.warning(f"ASIL constraint: {port.asil_constraint}")

    _render_ports(output.provider_ports, "Provider Ports (P-Port)")
    _render_ports(output.consumer_ports, "Consumer Ports (R-Port)")

    if output.runnables:
        with st.expander("Runnables"):
            for r in output.runnables:
                st.markdown(f"**{r.name}** — Trigger: {r.trigger} | Task: {r.os_task}")
                if r.timing_protection != "N/A":
                    st.markdown(f"  Timing protection: {r.timing_protection}")

    if output.bsw_parameters:
        with st.expander("BSW Parameters"):
            for p in output.bsw_parameters:
                st.markdown(f"**{p.module}** — `{p.parameter_path}`")
                st.markdown(f"  Value: {p.value} | Impact: {p.impact}")
                st.caption(f"Common mistake: {p.common_mistake}")

    with st.expander("MISRA Notes"):
        st.markdown(output.misra_notes)

    if output.asil_notes != "N/A":
        with st.expander("ASIL Notes"):
            st.warning(output.asil_notes)

    _render_self_evaluation(output.self_evaluation)


# ── Embedded C Developer ────────────────────────────────────────────────────────

def render_embedded_c_developer(output) -> None:
    if isinstance(output, AgentError):
        render_agent_error(output)
        return

    st.info(f"**Problem Classification:** {output.problem_classification}")

    # Input analysis + data sufficiency
    input_analysis = getattr(output, "input_analysis", None)
    data_suf = getattr(output, "data_sufficiency", None)
    if input_analysis or data_suf:
        with st.expander("Input Analysis & Data Sufficiency", expanded=False):
            if data_suf:
                suf_color = {"SUFFICIENT": "success", "PARTIAL": "warning", "INSUFFICIENT": "error"}.get(
                    data_suf.level, "info"
                )
                getattr(st, suf_color)(f"**Data: {data_suf.level}**")
                missing = getattr(data_suf, "missing_critical_data", None)
                if missing and missing != ["None — data is complete"]:
                    st.markdown("**Missing critical data:**")
                    for item in missing:
                        prefix = "🔴" if item.startswith("[CRITICAL]") else "🟡"
                        st.caption(f"{prefix} {item}")
            if input_analysis:
                facts = getattr(input_analysis, "input_facts", [])
                assumptions = getattr(input_analysis, "assumptions", [])
                if facts:
                    st.markdown("**Observed facts:**")
                    for f in facts:
                        st.markdown(f"- {f}")
                if assumptions:
                    st.markdown("**Assumptions (not stated by user):**")
                    for a in assumptions:
                        st.caption(f"⚠ {a}")
    st.markdown("---")

    with st.expander("Layer Diagnosis", expanded=True):
        for layer in output.layer_diagnosis:
            icon = {"SUSPECT": "🔴", "CLEAR": "🟢", "UNKNOWN": "🟡"}.get(layer.status, "⚪")
            st.markdown(f"{icon} **{layer.layer}** — {layer.status}")
            st.markdown(f"  Evidence: {layer.evidence}")
            st.markdown(f"  Tool: {layer.tool} | Check: {layer.check}")

    if output.cfsr_decode.cfsr_value != "N/A":
        with st.expander("CFSR Register Decode"):
            st.code(
                f"CFSR = {output.cfsr_decode.cfsr_value}\n"
                f"Bit:  {output.cfsr_decode.bit_set}\n"
                f"Meaning: {output.cfsr_decode.meaning}\n"
                f"Action:  {output.cfsr_decode.action}"
            )

    st.markdown(f"**Root Cause:** {output.root_cause}")

    with st.expander("Code Pattern", expanded=True):
        st.code(output.code_pattern, language="c")

    if output.misra_notes:
        with st.expander("MISRA Notes"):
            for note in output.misra_notes:
                st.markdown(f"**{note.rule}** ({note.category}) — {note.violation_pattern}")
                st.code(note.compliant_fix, language="c")

    cpu = output.cpu_load_calc
    cpu_text = "\n".join(cpu) if isinstance(cpu, list) else str(cpu)
    if "N/A" not in cpu_text:
        _render_calc_block(cpu, "CPU Load Calculation", expanded=True)

    rtos = output.rtos_calc
    rtos_text = "\n".join(rtos) if isinstance(rtos, list) else str(rtos)
    if "N/A" not in rtos_text:
        _render_calc_block(rtos, "RTOS Timing Calculations", expanded=True)

    _render_narrowing_questions(output.narrowing_questions)
    _render_self_evaluation(output.self_evaluation)


# ── MISRA Reviewer ──────────────────────────────────────────────────────────────

def render_misra_reviewer(output) -> None:
    if isinstance(output, AgentError):
        render_agent_error(output)
        return

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total", output.total_violations)
    col2.metric("Mandatory", output.mandatory_count)
    col3.metric("Required", output.required_count)
    col4.metric("Advisory", output.advisory_count)
    st.markdown(f"**ASIL:** {output.asil_level} | **Tool:** {output.tool} | **Context:** {output.file_context}")
    st.markdown("---")

    with st.expander("Violations", expanded=True):
        for v in output.violations:
            st.markdown(f"**{v.rule}**")
            vp = v.violation_pattern
            st.code("\n".join(vp) if isinstance(vp, list) else vp, language="c")
            st.markdown(f"*Why:* {v.explanation}")
            st.markdown("**Compliant rewrite:**")
            cr = v.compliant_rewrite
            st.code("\n".join(cr) if isinstance(cr, list) else cr, language="c")
            st.markdown("---")

    with st.expander("Root Cause Clusters"):
        for cluster in output.root_cause_clusters:
            st.markdown(f"**{cluster.cluster_name}** ({cluster.violation_count} violations)")
            st.markdown(f"- Rules: {cluster.rule_numbers}")
            st.markdown(f"- Root cause: {cluster.root_cause}")
            st.markdown(f"- Fix: {cluster.fix_approach}")

    with st.expander("Action Plan"):
        for row in output.action_plan:
            st.markdown(f"**{row.priority}** — {row.action} | Effort: {row.effort_days} | Owner: {row.owner}")

    st.warning(f"**ASIL Note:** {output.asil_note}")
    _render_self_evaluation(output.self_evaluation)


# ── ASPICE Process Coach ────────────────────────────────────────────────────────

def render_aspice_process_coach(output) -> None:
    if isinstance(output, AgentError):
        render_agent_error(output)
        return

    # Input analysis + data sufficiency
    input_analysis = getattr(output, "input_analysis", None)
    data_suf = getattr(output, "data_sufficiency", None)
    if input_analysis or data_suf:
        with st.expander("Input Analysis & Data Sufficiency", expanded=False):
            if data_suf:
                suf_color = {"SUFFICIENT": "success", "PARTIAL": "warning", "INSUFFICIENT": "error"}.get(
                    data_suf.level, "info"
                )
                getattr(st, suf_color)(f"**Data: {data_suf.level}**")
                missing = getattr(data_suf, "missing_critical_data", None)
                if missing and missing != ["None — data is complete"]:
                    st.markdown("**Missing critical data:**")
                    for item in missing:
                        prefix = "🔴" if item.startswith("[CRITICAL]") else "🟡"
                        st.caption(f"{prefix} {item}")
            if input_analysis:
                facts = getattr(input_analysis, "input_facts", [])
                assumptions = getattr(input_analysis, "assumptions", [])
                if facts:
                    st.markdown("**Observed facts:**")
                    for f in facts:
                        st.markdown(f"- {f}")
                if assumptions:
                    st.markdown("**Assumptions (not stated by user):**")
                    for a in assumptions:
                        st.caption(f"⚠ {a}")

    rag_icon = {"GREEN": "🟢", "AMBER": "🟡", "RED": "🔴"}.get(output.overall_readiness, "⚪")
    st.markdown(f"**Project:** {output.project_context} | **Target:** {output.target_level} | **Weeks to assessment:** {output.weeks_to_assessment}")
    st.metric("Overall Readiness", f"{rag_icon} {output.overall_readiness}")
    st.markdown("---")

    for pa in output.process_area_gaps:
        with st.expander(f"{pa.process_area} — {pa.top_risk[:50]}"):
            for wp in pa.work_products:
                rag = {"GREEN": "🟢", "AMBER": "🟡", "RED": "🔴"}.get(wp.rag, "⚪")
                st.markdown(f"{rag} **{wp.name}** ({wp.wp_id}) — {wp.finding_type} risk | BP: {wp.bp_at_risk}")
                st.caption(wp.status)
            st.markdown(f"**Action:** {pa.recommended_action}")

    pa22 = output.pa22_check
    with st.expander("PA 2.2 Check (hidden Level 2 trap)"):
        icons = {"YES": "✅", "NO": "❌", "PARTIAL": "⚠️"}
        st.markdown(f"{icons[pa22.review_record_exists]} Review record exists")
        st.markdown(f"{icons[pa22.review_record_approved]} Review record approved")
        st.markdown(f"{icons[pa22.document_in_cm_baseline]} Document in CM baseline")
        rag = {"GREEN": "🟢", "AMBER": "🟡", "RED": "🔴"}.get(pa22.overall_pa22_status, "⚪")
        st.markdown(f"**PA 2.2 status:** {rag} {pa22.overall_pa22_status}")
        if pa22.gap_description:
            st.warning(pa22.gap_description)

    with st.expander("Top 3 Risks"):
        st.markdown(output.top_3_risks)

    with st.expander("Action Plan", expanded=True):
        st.markdown(f"**Immediate (this week):**\n{output.immediate_actions}")
        st.markdown(f"**Short-term (2 weeks):**\n{output.short_term_actions}")
        st.markdown(f"**Finding response template:**\n{output.finding_response_template}")

    _render_self_evaluation(output.self_evaluation)


# ── Gate Review Approver ────────────────────────────────────────────────────────

def render_gate_review_approver(output) -> None:
    if isinstance(output, AgentError):
        render_agent_error(output)
        return

    overall_color = {"PASS": "success", "AMBER": "warning", "FAIL": "error"}.get(output.overall, "info")
    getattr(st, overall_color)(f"**GATE REVIEW — {output.gate_type} | {output.project_ecu}**\n\nOverall: {output.overall} | {output.score}")
    st.markdown("---")

    with st.expander("Criteria Assessment", expanded=True):
        for c in output.criteria_assessment:
            icon = {"PASS": "✅", "AMBER": "⚠️", "FAIL": "❌"}.get(c.status, "⚪")
            st.markdown(f"{icon} **{c.criterion}** — {c.evidence}")
            if c.finding != "None":
                st.caption(f"Finding: {c.finding}")

    if output.open_findings:
        with st.expander("Open Findings"):
            for f in output.open_findings:
                risk_icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(f.risk, "⚪")
                st.markdown(f"{risk_icon} **{f.finding}**")
                st.caption(f"Required action: {f.required_action}")

    st.warning(output.mandatory_closing_note)
    _render_self_evaluation(output.self_evaluation)


# ── Safety & Cyber Lead ─────────────────────────────────────────────────────────

def render_safety_and_cyber_lead(output) -> None:
    if isinstance(output, AgentError):
        render_agent_error(output)
        return

    # Input analysis + data sufficiency
    input_analysis = getattr(output, "input_analysis", None)
    data_suf = getattr(output, "data_sufficiency", None)
    if input_analysis or data_suf:
        with st.expander("Input Analysis & Data Sufficiency", expanded=False):
            if data_suf:
                suf_color = {"SUFFICIENT": "success", "PARTIAL": "warning", "INSUFFICIENT": "error"}.get(
                    data_suf.level, "info"
                )
                getattr(st, suf_color)(f"**Data: {data_suf.level}**")
                missing = getattr(data_suf, "missing_critical_data", None)
                if missing and missing != ["None — data is complete"]:
                    st.markdown("**Missing critical data:**")
                    for item in missing:
                        prefix = "🔴" if item.startswith("[CRITICAL]") else "🟡"
                        st.caption(f"{prefix} {item}")
            if input_analysis:
                facts = getattr(input_analysis, "input_facts", [])
                assumptions = getattr(input_analysis, "assumptions", [])
                if facts:
                    st.markdown("**Observed facts:**")
                    for f in facts:
                        st.markdown(f"- {f}")
                if assumptions:
                    st.markdown("**Assumptions (not stated by user):**")
                    for a in assumptions:
                        st.caption(f"⚠ {a}")

    st.markdown(f"**Item:** {output.item_name} | **Analysis:** {output.analysis_type}")
    st.markdown(f"**Boundary:** {output.item_definition}")
    st.markdown("---")

    if output.hazardous_events:
        with st.expander("Hazardous Events (HARA)", expanded=True):
            for he in output.hazardous_events:
                asil_color = {"ASIL-D": "🔴", "ASIL-C": "🟠", "ASIL-B": "🟡", "ASIL-A": "🟢", "QM": "⚪"}.get(he.asil, "⚪")
                st.markdown(f"**{he.he_id}** {asil_color} {he.asil} — {he.malfunctioning_behavior}")
                st.caption(f"OS: {he.operational_situation} | S={he.severity} E={he.exposure} C={he.controllability}")

        with st.expander("S/E/C Justifications"):
            st.markdown(output.sec_justifications)

    if output.safety_goals:
        with st.expander("Safety Goals"):
            for sg in output.safety_goals:
                st.markdown(f"**{sg.sg_id}** ({sg.asil}) — {sg.goal_statement}")
                st.caption(f"Safe state: {sg.safe_state} | FTTI: {sg.ftti}")

    if output.threat_scenarios:
        with st.expander("Threat Scenarios (TARA)", expanded=True):
            for ts in output.threat_scenarios:
                st.markdown(f"**{ts.ts_id}** — {ts.scenario}")
                st.caption(f"Actor: {ts.actor} | Vector: {ts.attack_vector} | Asset: {ts.target_asset}")

        with st.expander("Attack Feasibility"):
            for af in output.attack_feasibility:
                st.markdown(f"**{af.ts_id}** — Total: {af.total} → **{af.feasibility}**")
                st.caption(f"Time={af.time_factor} Expertise={af.expertise_factor} Knowledge={af.knowledge_factor} Opportunity={af.opportunity_factor} Equipment={af.equipment_factor}")

    if output.cybersecurity_goals:
        with st.expander("Cybersecurity Goals"):
            for cg in output.cybersecurity_goals:
                st.markdown(f"**{cg.cg_id}** ({cg.cal}) — {cg.goal_statement}")
                st.caption(f"Control: {cg.control}")

    if output.hw_metrics_note != "N/A":
        st.info(f"**Hardware Metrics:** {output.hw_metrics_note}")

    if output.co_engineering_interface != "N/A":
        with st.expander("Co-Engineering Interface"):
            st.markdown(output.co_engineering_interface)

    st.warning(output.mandatory_review_note)
    _render_self_evaluation(output.self_evaluation)


# ── SW Project Lead ─────────────────────────────────────────────────────────────

def render_sw_project_lead(output) -> None:
    if isinstance(output, AgentError):
        render_agent_error(output)
        return

    st.markdown(f"**Type:** {output.request_type}")
    st.info(output.summary)
    if output.decision_required_by != "N/A":
        st.warning(f"Decision required by: {output.decision_required_by}")
    st.markdown("---")

    if output.impact_assessment:
        with st.expander("Impact Assessment", expanded=True):
            for item in output.impact_assessment:
                cp_icon = "🔴" if item.critical_path_affected == "YES" else ""
                st.markdown(f"{cp_icon} **{item.dimension}:** {item.delta}")
                st.caption(item.detail)

    if output.change_request_options:
        with st.expander("CR Options"):
            for opt in output.change_request_options:
                st.markdown(f"**{opt.option}**")
                st.markdown(f"- Condition: {opt.condition}")
                st.markdown(f"- Cost: {opt.cost_person_days} | Schedule: {opt.schedule_consequence}")
                st.caption(f"Risk: {opt.risk_of_this_option}")

    if output.risks:
        with st.expander("Risk Register"):
            for risk in output.risks:
                level_icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(risk.level, "⚪")
                st.markdown(f"{level_icon} **{risk.risk_statement}** (P={risk.probability} × I={risk.impact} = {risk.risk_score})")
                st.caption(f"Mitigation: {risk.mitigation} | Residual: {risk.residual_risk}")

    st.markdown(f"**Recommendation:** {output.recommendation}")
    with st.expander("Action Plan"):
        st.markdown(f"**Immediate:** {output.immediate_actions}")
        st.markdown(f"**Short-term:** {output.short_term_actions}")
    st.caption(f"ASPICE reference: {output.aspice_reference}")
    _render_self_evaluation(output.self_evaluation)


# ── Regression Analyst ──────────────────────────────────────────────────────────

def render_regression_analyst(output) -> None:
    if isinstance(output, AgentError):
        render_agent_error(output)
        return

    # Input analysis + data sufficiency
    input_analysis = getattr(output, "input_analysis", None)
    data_suf = getattr(output, "data_sufficiency", None)
    if input_analysis or data_suf:
        with st.expander("Input Analysis & Data Sufficiency", expanded=False):
            if data_suf:
                suf_color = {"SUFFICIENT": "success", "PARTIAL": "warning", "INSUFFICIENT": "error"}.get(
                    data_suf.level, "info"
                )
                getattr(st, suf_color)(f"**Data: {data_suf.level}**")
                missing = getattr(data_suf, "missing_critical_data", None)
                if missing and missing != ["None — data is complete"]:
                    st.markdown("**Missing critical data:**")
                    for item in missing:
                        prefix = "🔴" if item.startswith("[CRITICAL]") else "🟡"
                        st.caption(f"{prefix} {item}")
            if input_analysis:
                facts = getattr(input_analysis, "input_facts", [])
                assumptions = getattr(input_analysis, "assumptions", [])
                if facts:
                    st.markdown("**Observed facts:**")
                    for f in facts:
                        st.markdown(f"- {f}")
                if assumptions:
                    st.markdown("**Assumptions (not stated by user):**")
                    for a in assumptions:
                        st.caption(f"⚠ {a}")

    rec_icon = {"HOLD": "🔴", "PROCEED_WITH_EXCEPTIONS": "🟡", "PROCEED": "🟢"}.get(output.hold_proceed_recommendation, "⚪")
    st.metric("Recommendation", f"{rec_icon} {output.hold_proceed_recommendation}")
    st.markdown(f"**Builds:** {output.build_baseline} → {output.build_current}")

    s = output.summary
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("New Failures", s.new_failures)
    col2.metric("ASIL-D Affected", s.asil_d_affected)
    col3.metric("Coverage", s.current_coverage_pct, delta=None)
    col4.metric("Pass Rate", f"{s.current_pass}/{s.current_pass + s.current_fail}")
    st.markdown("---")

    with st.expander("Failure Clusters (risk-ranked)", expanded=True):
        for cluster in output.failure_clusters:
            icon = {"ASIL-D": "🔴", "ASIL-B": "🟡", "QM": "🟢", "ENVIRONMENT": "🔵"}.get(cluster.risk_level, "⚪")
            st.markdown(f"{icon} **{cluster.cluster_name}** — {cluster.failure_count} failures | {cluster.risk_level}")
            st.markdown(f"  Probable cause: {cluster.probable_cause}")
            st.caption(f"  Check: {cluster.confirming_check}")

    if output.coverage_deltas:
        with st.expander("Coverage Deltas"):
            for cd in output.coverage_deltas:
                blocker_icon = "❌" if cd.is_blocker == "YES" else "⚠️"
                st.markdown(f"{blocker_icon} **{cd.module}** — {cd.previous_pct} → {cd.current_pct} ({cd.delta_pct})")
                st.caption(f"Lost: {cd.lost_function}")

    with st.expander("Investigation Sequence"):
        st.markdown(output.investigation_sequence)

    st.markdown(f"**ASPICE Impact:** {output.aspice_impact}")
    st.info(f"**HOLD/PROCEED Rationale:** {output.hold_proceed_rationale}")
    _render_self_evaluation(output.self_evaluation)


# ── SIL/HIL Test Planner ────────────────────────────────────────────────────────

def render_sil_hil_test_planner(output) -> None:
    if isinstance(output, AgentError):
        render_agent_error(output)
        return

    col1, col2, col3 = st.columns(3)
    col1.metric("ECU", output.ecu_name)
    col2.metric("ASPICE Scope", output.aspice_scope)
    col3.metric("ASIL", output.asil_level)
    st.markdown("---")

    te = output.test_environment
    with st.expander("Test Environment"):
        st.markdown(f"**SIL:** {te.sil_setup}")
        st.markdown(f"**HIL:** {te.hil_setup}")
        st.markdown(f"**Bus:** {te.bus_configuration}")
        st.markdown(f"**Measurement:** {te.measurement_tools}")

    with st.expander("Test Cases", expanded=True):
        for tc in output.test_cases:
            env_icon = {"SIL": "🖥️", "HIL": "🔧", "SIL+HIL": "🖥️🔧"}.get(tc.environment, "")
            fault_note = f" | Fault: {tc.fault_injected}" if tc.fault_injected != "N/A" else ""
            st.markdown(f"**{tc.tc_id}** {env_icon} — {tc.objective}{fault_note}")
            st.caption(f"Pass: {tc.pass_criteria}")
            if tc.asil_note != "N/A":
                st.caption(f"ASIL: {tc.asil_note}")

    with st.expander("SIL vs HIL Allocation"):
        st.markdown(f"**SIL:** {output.sil_scope}")
        st.markdown(f"**HIL only:** {output.hil_only_scope}")

    if output.fault_injections:
        with st.expander("Fault Injection Specification"):
            for fi in output.fault_injections:
                st.markdown(f"**{fi.fault_type}** — {fi.parameters}")
                st.caption(f"Expected DTC: {fi.expected_dtc} | Timing: {fi.timing}")

    with st.expander("ASPICE Evidence"):
        for ae in output.aspice_evidence:
            st.markdown(f"**{ae.process_area}** — {ae.work_product} ({ae.wp_id}): {ae.content}")

    _render_self_evaluation(output.self_evaluation)


# ── SW Unit Tester ──────────────────────────────────────────────────────────────

def render_sw_unit_tester(output) -> None:
    if isinstance(output, AgentError):
        render_agent_error(output)
        return

    st.code(output.function_signature, language="c")
    col1, col2, col3 = st.columns(3)
    col1.metric("ASIL Level", output.asil_level)
    col2.metric("Framework", output.framework)
    col3.metric("Coverage Required", output.coverage_required[:20])
    st.markdown(f"**{output.swe4_work_product}** | Traceability: {output.design_traceability}")
    st.markdown("---")

    if output.stubs_required:
        with st.expander("Stubs Required"):
            for stub in output.stubs_required:
                st.markdown(f"- **{stub.stub_name}** — {stub.purpose} → returns `{stub.return_value}`")

    with st.expander("Test Cases", expanded=True):
        for tc in output.test_cases:
            st.markdown(f"**{tc.tc_id}** — {tc.objective}")
            st.markdown(f"  Input: `{tc.input_values}` → Expected: `{tc.expected_result}`")
            st.caption(f"Pass: {tc.pass_criteria}")

    if output.mcdc_pairs:
        with st.expander("MC/DC Independence Pairs"):
            for pair in output.mcdc_pairs:
                st.markdown(f"**{pair.tc_id}** — {pair.independently_tests}")
                st.caption(f"Conditions: {pair.condition_values} → Decision: {pair.decision_result}")

    with st.expander("Test Code", expanded=True):
        tc = output.test_code
        st.code("\n".join(tc) if isinstance(tc, list) else tc, language="c")

    with st.expander("Coverage Summary"):
        for cs in output.coverage_summary:
            try:
                icon = "✅" if float(cs.achieved_pct.rstrip('%')) >= float(cs.target_pct.rstrip('%')) else "⚠️"
            except (ValueError, AttributeError):
                icon = "📊"
            st.markdown(f"{icon} **{cs.coverage_type}** — {cs.achieved_pct} / {cs.target_pct} target | TCs: {cs.achieving_tcs}")

    _render_self_evaluation(output.self_evaluation)
