"""
Domain validators for gate_review_approver output.
Ensures closing note present, score matches criteria, no criteria skipped.
"""

from sdk_agents.core.base_agent import DomainCheckError
from .schema import GateReviewApproverOutput

MANDATORY_NOTE_KEYWORDS = ["formal release approval", "sign-off", "Project Lead"]
SOR_CRITERIA_COUNT = 6
SOP_CRITERIA_COUNT = 6


def validate(output: GateReviewApproverOutput) -> None:
    _check_criteria_count(output)
    _check_mandatory_closing_note(output)
    _check_overall_consistent(output)
    _check_open_findings_complete(output)
    _check_self_evaluation_has_evidence(output)


def _check_criteria_count(output: GateReviewApproverOutput) -> None:
    expected = SOR_CRITERIA_COUNT if output.gate_type == "SOR" else SOP_CRITERIA_COUNT
    actual = len(output.criteria_assessment)
    if actual < expected:
        raise DomainCheckError(
            f"criteria_assessment has {actual} entries but {output.gate_type} gate "
            f"requires {expected} criteria. All criteria must be assessed."
        )


def _check_mandatory_closing_note(output: GateReviewApproverOutput) -> None:
    note = output.mandatory_closing_note
    if not any(kw in note for kw in MANDATORY_NOTE_KEYWORDS):
        raise DomainCheckError(
            f"mandatory_closing_note is missing required content. "
            f"Must reference: {MANDATORY_NOTE_KEYWORDS}. "
            f"Got: '{note[:100]}'"
        )


def _check_overall_consistent(output: GateReviewApproverOutput) -> None:
    statuses = [c.status for c in output.criteria_assessment]
    has_fail = "FAIL" in statuses
    has_amber = "AMBER" in statuses
    if has_fail and output.overall != "FAIL":
        raise DomainCheckError(
            f"Overall is '{output.overall}' but at least one criterion is FAIL. "
            f"Overall must be FAIL when any criterion is FAIL."
        )
    if not has_fail and has_amber and output.overall == "PASS":
        raise DomainCheckError(
            f"Overall is PASS but AMBER criteria exist. "
            f"Overall must be AMBER when any criterion is AMBER."
        )


def _check_open_findings_complete(output: GateReviewApproverOutput) -> None:
    amber_fail = [c for c in output.criteria_assessment if c.status in ("AMBER", "FAIL")]
    if len(amber_fail) > 0 and len(output.open_findings) == 0:
        raise DomainCheckError(
            f"There are {len(amber_fail)} AMBER/FAIL criteria but open_findings is empty. "
            f"Every AMBER/FAIL criterion must have a corresponding open finding."
        )


def _check_self_evaluation_has_evidence(output: GateReviewApproverOutput) -> None:
    for line in output.self_evaluation:
        if line.result == "PASS" and len(line.evidence.strip()) < 10:
            raise DomainCheckError(
                f"self_evaluation item '{line.item}' claims PASS "
                f"but evidence is empty or too short: '{line.evidence}'"
            )
