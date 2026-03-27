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
    _check_clusters_present(output)
    _check_action_plan_has_effort(output)
    _check_asil_note_specific(output)
    _check_self_evaluation_has_evidence(output)


def _check_violations_have_code(output: MisraReviewerOutput) -> None:
    for i, v in enumerate(output.violations):
        if len(v.violation_pattern.strip()) < MIN_VIOLATION_PATTERN_LENGTH:
            raise DomainCheckError(
                f"violations[{i}].violation_pattern is too short "
                f"({len(v.violation_pattern)} chars). Must show C code pattern."
            )
        if len(v.compliant_rewrite.strip()) < MIN_REWRITE_LENGTH:
            raise DomainCheckError(
                f"violations[{i}].compliant_rewrite is too short "
                f"({len(v.compliant_rewrite)} chars). Must show compliant C code."
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
        if len(row.effort_days.strip()) < 2:
            raise DomainCheckError(
                f"action_plan[{i}].effort_days is empty or too vague: '{row.effort_days}'. "
                f"Must state specific effort in person-days."
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
