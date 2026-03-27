"""
Domain validators for sw_project_lead output.
Catches unquantified impacts, incorrect risk scores, missing ASPICE references.
"""

from sdk_agents.core.base_agent import DomainCheckError
from .schema import SwProjectLeadOutput


def validate(output: SwProjectLeadOutput) -> None:
    _check_risk_scores_consistent(output)
    _check_impact_quantified(output)
    _check_aspice_reference_present(output)
    _check_self_evaluation_has_evidence(output)


def _check_risk_scores_consistent(output: SwProjectLeadOutput) -> None:
    for i, risk in enumerate(output.risks):
        expected = risk.probability * risk.impact
        if risk.risk_score != expected:
            raise DomainCheckError(
                f"risks[{i}].risk_score={risk.risk_score} does not match "
                f"probability({risk.probability}) x impact({risk.impact}) = {expected}. "
                f"Risk score must equal P × I."
            )
        # Check level consistency
        score = risk.risk_score
        if score <= 8 and risk.level != "LOW":
            raise DomainCheckError(
                f"risks[{i}].level='{risk.level}' but score={score} should be LOW (≤ 8)."
            )
        if score > 15 and risk.level != "HIGH":
            raise DomainCheckError(
                f"risks[{i}].level='{risk.level}' but score={score} should be HIGH (> 15)."
            )


def _check_impact_quantified(output: SwProjectLeadOutput) -> None:
    for i, item in enumerate(output.impact_assessment):
        if item.dimension == "Schedule" and not any(
            unit in item.delta for unit in ["day", "week", "working"]
        ):
            raise DomainCheckError(
                f"impact_assessment[{i}] (Schedule): delta '{item.delta}' is not quantified. "
                f"Must state impact in working days."
            )


def _check_aspice_reference_present(output: SwProjectLeadOutput) -> None:
    ref = output.aspice_reference
    if len(ref.strip()) < 5 or ref.strip().lower() == "n/a":
        # Only enforce if there are change request options or impact items
        if output.impact_assessment or output.change_request_options:
            raise DomainCheckError(
                f"aspice_reference is missing or too short: '{ref}'. "
                f"Must reference the affected ASPICE process area (SWE.x) and work product (17-xx)."
            )


def _check_self_evaluation_has_evidence(output: SwProjectLeadOutput) -> None:
    for line in output.self_evaluation:
        if line.result == "PASS" and len(line.evidence.strip()) < 10:
            raise DomainCheckError(
                f"self_evaluation item '{line.item}' claims PASS "
                f"but evidence is empty or too short: '{line.evidence}'"
            )
