"""
Domain validators for sil_hil_test_planner output.
Catches subjective pass criteria, missing SIL/HIL separation, vague fault injection.
"""

from sdk_agents.core.base_agent import DomainCheckError
from .schema import SilHilTestPlannerOutput

SUBJECTIVE_WORDS = ["correctly", "properly", "works", "functions", "looks good", "behaves"]
MIN_PASS_CRITERIA_LENGTH = 20
MIN_FAULT_PARAMS_LENGTH = 10


def validate(output: SilHilTestPlannerOutput) -> None:
    _check_pass_criteria_not_subjective(output)
    _check_sil_hil_separation(output)
    _check_fault_injection_specific(output)
    _check_aspice_evidence_present(output)
    _check_self_evaluation_has_evidence(output)


def _check_pass_criteria_not_subjective(output: SilHilTestPlannerOutput) -> None:
    for i, tc in enumerate(output.test_cases):
        criteria_lower = tc.pass_criteria.lower()
        for word in SUBJECTIVE_WORDS:
            if word in criteria_lower:
                raise DomainCheckError(
                    f"test_cases[{i}].pass_criteria contains subjective word '{word}': "
                    f"'{tc.pass_criteria}'. Must use numerical/measurable criteria."
                )
        if len(tc.pass_criteria.strip()) < MIN_PASS_CRITERIA_LENGTH:
            raise DomainCheckError(
                f"test_cases[{i}].pass_criteria is too short "
                f"({len(tc.pass_criteria)} chars). Must be a specific measurable criterion."
            )


def _check_sil_hil_separation(output: SilHilTestPlannerOutput) -> None:
    if len(output.sil_scope.strip()) < 10:
        raise DomainCheckError(
            "sil_scope is empty or too short. Must explain what can be tested in SIL and why."
        )
    if len(output.hil_only_scope.strip()) < 10:
        raise DomainCheckError(
            "hil_only_scope is empty or too short. Must explain what requires HIL and why SIL is insufficient."
        )


def _check_fault_injection_specific(output: SilHilTestPlannerOutput) -> None:
    for i, fi in enumerate(output.fault_injections):
        if len(fi.parameters.strip()) < MIN_FAULT_PARAMS_LENGTH:
            raise DomainCheckError(
                f"fault_injections[{i}].parameters is too vague "
                f"({len(fi.parameters)} chars). Must specify exact values: voltage, duration, timing."
            )


def _check_aspice_evidence_present(output: SilHilTestPlannerOutput) -> None:
    if len(output.aspice_evidence) == 0:
        raise DomainCheckError(
            "aspice_evidence is empty. Every test plan must produce ASPICE work products "
            "(Integration Test Specification for SWE.5, Qualification Test Specification for SWE.6)."
        )


def _check_self_evaluation_has_evidence(output: SilHilTestPlannerOutput) -> None:
    for line in output.self_evaluation:
        if line.result == "PASS" and len(line.evidence.strip()) < 10:
            raise DomainCheckError(
                f"self_evaluation item '{line.item}' claims PASS "
                f"but evidence is empty or too short: '{line.evidence}'"
            )
