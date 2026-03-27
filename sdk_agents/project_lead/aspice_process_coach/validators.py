"""
Domain validators for aspice_process_coach output.
Catches vague actions, missing BP references, incomplete PA 2.2 check.
"""

from sdk_agents.core.base_agent import DomainCheckError
from .schema import AspiceProcessCoachOutput

MIN_ACTION_LENGTH = 20
MIN_TOP_RISKS_LENGTH = 30


def validate(output: AspiceProcessCoachOutput) -> None:
    _check_process_areas_have_bp_references(output)
    _check_pa22_complete(output)
    _check_top_risks_specific(output)
    _check_immediate_actions_specific(output)
    _check_self_evaluation_has_evidence(output)


def _check_process_areas_have_bp_references(output: AspiceProcessCoachOutput) -> None:
    for pa in output.process_area_gaps:
        # At least one RED/AMBER work product must have a BP reference
        amber_red = [wp for wp in pa.work_products if wp.rag in ("AMBER", "RED")]
        for wp in amber_red:
            if wp.bp_at_risk == "" or wp.bp_at_risk.lower() == "none":
                raise DomainCheckError(
                    f"Work product '{wp.name}' in {pa.process_area} is {wp.rag} "
                    f"but bp_at_risk is empty. Must reference the specific BP number."
                )


def _check_pa22_complete(output: AspiceProcessCoachOutput) -> None:
    pa22 = output.pa22_check
    if len(pa22.gap_description.strip()) < 10:
        raise DomainCheckError(
            f"pa22_check.gap_description is too short ({len(pa22.gap_description)} chars). "
            f"Must describe which PA 2.2 condition(s) are missing."
        )


def _check_top_risks_specific(output: AspiceProcessCoachOutput) -> None:
    if len(output.top_3_risks.strip()) < MIN_TOP_RISKS_LENGTH:
        raise DomainCheckError(
            f"top_3_risks is too short ({len(output.top_3_risks)} chars). "
            f"Must name specific BPs and finding types (Major/Minor)."
        )
    if "BP" not in output.top_3_risks and "bp" not in output.top_3_risks.lower():
        raise DomainCheckError(
            "top_3_risks does not reference any BP numbers. "
            "Must cite specific base practice numbers (e.g., SWE.1 BP4)."
        )


def _check_immediate_actions_specific(output: AspiceProcessCoachOutput) -> None:
    if len(output.immediate_actions.strip()) < MIN_ACTION_LENGTH:
        raise DomainCheckError(
            f"immediate_actions is too short ({len(output.immediate_actions)} chars). "
            f"Must specify concrete day-by-day actions."
        )


def _check_self_evaluation_has_evidence(output: AspiceProcessCoachOutput) -> None:
    for line in output.self_evaluation:
        if line.result == "PASS" and len(line.evidence.strip()) < 10:
            raise DomainCheckError(
                f"self_evaluation item '{line.item}' claims PASS "
                f"but evidence is empty or too short: '{line.evidence}'"
            )
