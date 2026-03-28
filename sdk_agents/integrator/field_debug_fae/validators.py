"""
Domain validators for field_debug_fae output.
Catches semantic errors that JSON schema cannot: vague tests, missing bit decode,
incomplete NRC analysis, non-specific debug steps.
"""

from sdk_agents.core.base_agent import DomainCheckError
from .schema import FieldDebugFaeOutput

MIN_TEST_LENGTH = 25
MIN_CRITERIA_LENGTH = 12
MIN_ANALYSIS_LENGTH = 40


def validate(output: FieldDebugFaeOutput) -> None:
    _check_protocol_tec_consistency(output)
    _check_status_byte_decoded(output)
    _check_safety_relevant_consistent(output)
    _check_analysis_has_lab_vs_field(output)
    _check_probable_causes_specific(output)
    _check_nrc_root_causes(output)
    _check_debug_steps_specific(output)
    _check_self_evaluation_has_evidence(output)


def _check_protocol_tec_consistency(output: FieldDebugFaeOutput) -> None:
    """
    If protocol_detection says CAN or CAN-FD and confidence is HIGH,
    tec_math must not be N/A — the agent must show TEC accumulation math.
    """
    protocol = output.protocol_detection.protocol
    confidence = output.protocol_detection.confidence
    if protocol in ("CAN", "CAN-FD") and confidence == "HIGH":
        tec = output.tec_math
        text = "\n".join(tec) if isinstance(tec, list) else str(tec)
        if "N/A" in text:
            raise DomainCheckError(
                f"protocol_detection identifies '{protocol}' with HIGH confidence "
                f"but tec_math is set to N/A. "
                f"CAN faults require TEC accumulation math — show the net_TEC/s calculation "
                f"or lower protocol confidence if CAN is not confirmed."
            )


def _check_safety_relevant_consistent(output: FieldDebugFaeOutput) -> None:
    fd = output.fault_details
    if fd.safety_relevant == "YES" and "not safety" in fd.safety_impact.lower():
        raise DomainCheckError(
            f"fault_details contradiction: safety_relevant='YES' but safety_impact says "
            f"'{fd.safety_impact}'. These are mutually exclusive."
        )
    if fd.safety_relevant == "NO" and fd.safety_impact.strip() and \
            "not safety" not in fd.safety_impact.lower() and "n/a" not in fd.safety_impact.lower():
        raise DomainCheckError(
            f"fault_details contradiction: safety_relevant='NO' but safety_impact describes "
            f"a safety concern: '{fd.safety_impact[:60]}'. Set safety_relevant='YES' or "
            f"safety_impact='Not safety-critical'."
        )


def _check_analysis_has_lab_vs_field(output: FieldDebugFaeOutput) -> None:
    analysis_lower = output.analysis.lower()
    if "lab" not in analysis_lower and "field" not in analysis_lower and \
            "workshop" not in analysis_lower and "repro" not in analysis_lower:
        raise DomainCheckError(
            "analysis field must include a lab-vs-field assessment. "
            "State whether field trace is sufficient or lab reproduction is needed, and why."
        )


def _check_status_byte_decoded(output: FieldDebugFaeOutput) -> None:
    decoded = output.fault_details.status_byte_decoded
    # Must contain bit reference OR explicit N/A
    if "N/A" not in decoded and "Bit" not in decoded and "0x" not in decoded:
        raise DomainCheckError(
            f"status_byte_decoded does not contain bit-level interpretation. "
            f"Expected 'Bit X = ...' or explicit 'N/A'. Got: '{decoded[:80]}'"
        )


def _check_probable_causes_specific(output: FieldDebugFaeOutput) -> None:
    for i, cause in enumerate(output.probable_causes):
        for field_name, value, minimum in [
            ("test", cause.test, MIN_TEST_LENGTH),
            ("pass_criteria", cause.pass_criteria, MIN_CRITERIA_LENGTH),
            ("fail_criteria", cause.fail_criteria, MIN_CRITERIA_LENGTH),
        ]:
            if len(value.strip()) < minimum:
                raise DomainCheckError(
                    f"probable_causes[{i}].{field_name} is too vague "
                    f"({len(value)} chars, minimum {minimum}). Got: '{value}'"
                )


def _check_nrc_root_causes(output: FieldDebugFaeOutput) -> None:
    uds = output.uds_session_analysis
    if uds.nrc_code != "N/A" and len(uds.nrc_root_causes) < 2:
        raise DomainCheckError(
            f"nrc_root_causes has only {len(uds.nrc_root_causes)} entries "
            f"but nrc_code is '{uds.nrc_code}' — at least 2 root causes required "
            f"when a specific NRC is identified."
        )


def _check_debug_steps_specific(output: FieldDebugFaeOutput) -> None:
    for i, step in enumerate(output.debug_steps):
        if len(step.action.strip()) < MIN_TEST_LENGTH:
            raise DomainCheckError(
                f"debug_steps[{i}].action is too vague "
                f"({len(step.action)} chars, minimum {MIN_TEST_LENGTH}). "
                f"Got: '{step.action}'"
            )


def _check_self_evaluation_has_evidence(output: FieldDebugFaeOutput) -> None:
    for line in output.self_evaluation:
        if line.result == "PASS" and len(line.evidence.strip()) < 10:
            raise DomainCheckError(
                f"self_evaluation item '{line.item}' claims PASS "
                f"but evidence is empty or too short: '{line.evidence}'"
            )
