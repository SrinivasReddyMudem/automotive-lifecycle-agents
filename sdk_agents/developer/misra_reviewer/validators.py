"""
Domain validators for misra_reviewer output.
Catches generic rule explanations, missing code patterns, unclustered violations.
"""

from sdk_agents.core.base_agent import DomainCheckError
from .schema import MisraReviewerOutput

MIN_VIOLATION_PATTERN_LENGTH = 20
MIN_EXPLANATION_LENGTH = 30
MIN_REWRITE_LENGTH = 20
MIN_ASIL_NOTE_LENGTH = 30


def validate(output: MisraReviewerOutput) -> None:
    _check_violations_have_code(output)
    _check_violation_counts_consistent(output)
    _check_clusters_present(output)
    _check_action_plan_has_effort(output)
    _check_asil_note_specific(output)
    _check_self_evaluation_has_evidence(output)


def _check_violation_counts_consistent(output: MisraReviewerOutput) -> None:
    declared_total = output.mandatory_count + output.required_count + output.advisory_count
    if output.total_violations != declared_total:
        raise DomainCheckError(
            f"total_violations={output.total_violations} does not match "
            f"mandatory({output.mandatory_count}) + required({output.required_count}) + "
            f"advisory({output.advisory_count}) = {declared_total}."
        )


def _check_violations_have_code(output: MisraReviewerOutput) -> None:
    for i, v in enumerate(output.violations):
        pattern_text = "\n".join(v.violation_pattern)
        if len(pattern_text.strip()) < MIN_VIOLATION_PATTERN_LENGTH:
            raise DomainCheckError(
                f"violations[{i}].violation_pattern is too short "
                f"({len(pattern_text)} chars). Must show C code pattern."
            )
        rewrite_text = "\n".join(v.compliant_rewrite)
        if len(rewrite_text.strip()) < MIN_REWRITE_LENGTH:
            raise DomainCheckError(
                f"violations[{i}].compliant_rewrite is too short "
                f"({len(rewrite_text)} chars). Must show compliant C code."
            )
        if "Rule" not in v.rule and len(v.rule) < 3:
            raise DomainCheckError(
                f"violations[{i}].rule '{v.rule}' is not a valid MISRA rule number. "
                f"Expected format: 'Rule X.Y'"
            )


def _check_clusters_present(output: MisraReviewerOutput) -> None:
    if len(output.root_cause_clusters) == 0:
        raise DomainCheckError(
            "root_cause_clusters is empty. Violations must be grouped into clusters. "
            "Even a single violation must have one cluster entry."
        )


def _check_action_plan_has_effort(output: MisraReviewerOutput) -> None:
    for i, row in enumerate(output.action_plan):
        if not row.effort_days.strip():
            raise DomainCheckError(
                f"action_plan[{i}].effort_days is empty. "
                f"Must state specific effort in person-days (e.g. '1', '0.5', '2-3')."
            )


def _check_asil_note_specific(output: MisraReviewerOutput) -> None:
    if len(output.asil_note.strip()) < MIN_ASIL_NOTE_LENGTH:
        raise DomainCheckError(
            f"asil_note is too short ({len(output.asil_note)} chars). "
            f"Must specify what this ASIL level requires for this violation set."
        )


def _check_self_evaluation_has_evidence(output: MisraReviewerOutput) -> None:
    for line in output.self_evaluation:
        if line.result == "PASS" and len(line.evidence.strip()) < 10:
            raise DomainCheckError(
                f"self_evaluation item '{line.item}' claims PASS "
                f"but evidence is empty or too short: '{line.evidence}'"
            )
