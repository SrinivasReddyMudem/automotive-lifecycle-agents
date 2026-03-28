"""
Domain validators for sw_unit_tester output.
Catches missing boundary tests, absent MC/DC pairs for ASIL-C/D, non-code test_code.
"""

from sdk_agents.core.base_agent import DomainCheckError
from .schema import SwUnitTesterOutput

MIN_TEST_CODE_LENGTH = 50
MIN_PASS_CRITERIA_LENGTH = 10
ASIL_CD = ["ASIL-C", "ASIL-D"]


def validate(output: SwUnitTesterOutput) -> None:
    _check_test_code_present(output)
    _check_mcdc_for_asil_cd(output)
    _check_pass_criteria_specific(output)
    _check_coverage_summary_complete(output)
    _check_self_evaluation_has_evidence(output)


def _check_test_code_present(output: SwUnitTesterOutput) -> None:
    joined = "\n".join(output.test_code)
    if len(joined.strip()) < MIN_TEST_CODE_LENGTH:
        raise DomainCheckError(
            f"test_code is too short ({len(joined)} chars). "
            f"Must show actual test code in framework syntax (minimum {MIN_TEST_CODE_LENGTH} chars). "
            f"Not just a comment or table."
        )


def _check_mcdc_for_asil_cd(output: SwUnitTesterOutput) -> None:
    asil = output.asil_level.upper()
    if any(level in asil for level in ASIL_CD):
        if len(output.mcdc_pairs) == 0:
            raise DomainCheckError(
                f"ASIL level is '{output.asil_level}' which requires MC/DC coverage, "
                f"but mcdc_pairs is empty. Must define independence pairs for each condition."
            )


def _check_pass_criteria_specific(output: SwUnitTesterOutput) -> None:
    for i, tc in enumerate(output.test_cases):
        if len(tc.pass_criteria.strip()) < MIN_PASS_CRITERIA_LENGTH:
            raise DomainCheckError(
                f"test_cases[{i}].pass_criteria is too short "
                f"({len(tc.pass_criteria)} chars). Must state explicit pass condition."
            )


def _check_coverage_summary_complete(output: SwUnitTesterOutput) -> None:
    if len(output.coverage_summary) == 0:
        raise DomainCheckError(
            "coverage_summary is empty. Must include at least Statement coverage summary."
        )
    for cs in output.coverage_summary:
        if not cs.achieving_tcs.strip():
            raise DomainCheckError(
                f"coverage_summary[{cs.coverage_type}].achieving_tcs is empty. "
                f"Must name the specific test case IDs that achieve this coverage."
            )


def _check_self_evaluation_has_evidence(output: SwUnitTesterOutput) -> None:
    for line in output.self_evaluation:
        if line.result == "PASS" and len(line.evidence.strip()) < 10:
            raise DomainCheckError(
                f"self_evaluation item '{line.item}' claims PASS "
                f"but evidence is empty or too short: '{line.evidence}'"
            )
