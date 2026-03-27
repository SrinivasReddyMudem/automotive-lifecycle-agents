"""
Domain validators for safety_and_cyber_lead output.
Catches missing S/E/C justifications, ASIL assigned to hazards instead of goals,
missing review note, infeasible feasibility totals.
"""

from sdk_agents.core.base_agent import DomainCheckError
from .schema import SafetyAndCyberLeadOutput

VALID_ASIL = {"QM", "ASIL-A", "ASIL-B", "ASIL-C", "ASIL-D", "QM-A", "N/A"}
MANDATORY_REVIEW_KEYWORDS = ["qualified engineer", "review and approval"]
MIN_SEC_JUSTIFICATION_LENGTH = 20


def validate(output: SafetyAndCyberLeadOutput) -> None:
    _check_safety_goals_have_asil(output)
    _check_sec_justifications_present(output)
    _check_feasibility_totals(output)
    _check_mandatory_review_note(output)
    _check_self_evaluation_has_evidence(output)


def _check_safety_goals_have_asil(output: SafetyAndCyberLeadOutput) -> None:
    for i, goal in enumerate(output.safety_goals):
        if not any(valid in goal.asil for valid in VALID_ASIL):
            raise DomainCheckError(
                f"safety_goals[{i}].asil '{goal.asil}' is not a valid ASIL level. "
                f"Expected one of: {VALID_ASIL}"
            )
        if len(goal.safe_state.strip()) < 5:
            raise DomainCheckError(
                f"safety_goals[{i}].safe_state is empty or too short. "
                f"Every safety goal must define a safe state."
            )


def _check_sec_justifications_present(output: SafetyAndCyberLeadOutput) -> None:
    if output.hazardous_events and len(output.sec_justifications.strip()) < MIN_SEC_JUSTIFICATION_LENGTH:
        raise DomainCheckError(
            f"sec_justifications is too short ({len(output.sec_justifications)} chars). "
            f"Every S, E, C rating requires a written justification sentence."
        )


def _check_feasibility_totals(output: SafetyAndCyberLeadOutput) -> None:
    for i, af in enumerate(output.attack_feasibility):
        expected_total = (
            af.time_factor + af.expertise_factor + af.knowledge_factor +
            af.opportunity_factor + af.equipment_factor
        )
        if af.total != expected_total:
            raise DomainCheckError(
                f"attack_feasibility[{i}] ts_id={af.ts_id}: "
                f"total={af.total} does not match sum of factors ({expected_total}). "
                f"Total must equal time + expertise + knowledge + opportunity + equipment."
            )


def _check_mandatory_review_note(output: SafetyAndCyberLeadOutput) -> None:
    note = output.mandatory_review_note
    if not any(kw in note for kw in MANDATORY_REVIEW_KEYWORDS):
        raise DomainCheckError(
            f"mandatory_review_note is missing required content. "
            f"Must contain: {MANDATORY_REVIEW_KEYWORDS}. Got: '{note[:100]}'"
        )


def _check_self_evaluation_has_evidence(output: SafetyAndCyberLeadOutput) -> None:
    for line in output.self_evaluation:
        if line.result == "PASS" and len(line.evidence.strip()) < 10:
            raise DomainCheckError(
                f"self_evaluation item '{line.item}' claims PASS "
                f"but evidence is empty or too short: '{line.evidence}'"
            )
