"""
Domain validators for embedded_c_developer output.
Catches vague layer diagnosis, missing CFSR interpretation, generic code patterns.
"""

from sdk_agents.core.base_agent import DomainCheckError
from .schema import EmbeddedCDeveloperOutput

MIN_CODE_LENGTH = 30
MIN_ROOT_CAUSE_LENGTH = 20
MIN_CHECK_LENGTH = 15


def validate(output: EmbeddedCDeveloperOutput) -> None:
    _check_layer_diagnosis_complete(output)
    _check_cfsr_decode_present(output)
    _check_code_pattern_specific(output)
    _check_root_cause_specific(output)
    _check_rtos_calc_structure(output)
    _check_self_evaluation_has_evidence(output)


def _check_layer_diagnosis_complete(output: EmbeddedCDeveloperOutput) -> None:
    layers = {d.layer for d in output.layer_diagnosis}
    required = {"Physical", "RTOS", "Application"}
    missing = required - layers
    if missing:
        raise DomainCheckError(
            f"layer_diagnosis is missing layers: {missing}. "
            f"All three layers (Physical, RTOS, Application) must be present."
        )
    # At least one must be SUSPECT
    suspects = [d for d in output.layer_diagnosis if d.status == "SUSPECT"]
    if not suspects:
        raise DomainCheckError(
            "No layer is marked SUSPECT in layer_diagnosis. "
            "At least one layer must be identified as the fault candidate."
        )


def _check_cfsr_decode_present(output: EmbeddedCDeveloperOutput) -> None:
    cfsr = output.cfsr_decode
    if len(cfsr.meaning.strip()) < 10:
        raise DomainCheckError(
            f"cfsr_decode.meaning is too short ({len(cfsr.meaning)} chars). "
            f"Must explain what the CFSR value means or explicitly state N/A with reason."
        )


def _check_code_pattern_specific(output: EmbeddedCDeveloperOutput) -> None:
    if len(output.code_pattern.strip()) < MIN_CODE_LENGTH:
        raise DomainCheckError(
            f"code_pattern is too short ({len(output.code_pattern)} chars, "
            f"minimum {MIN_CODE_LENGTH}). Must show actual C code pattern."
        )


def _check_root_cause_specific(output: EmbeddedCDeveloperOutput) -> None:
    if len(output.root_cause.strip()) < MIN_ROOT_CAUSE_LENGTH:
        raise DomainCheckError(
            f"root_cause is too short ({len(output.root_cause)} chars, "
            f"minimum {MIN_ROOT_CAUSE_LENGTH}). Must be a specific diagnosis."
        )


def _check_rtos_calc_structure(output: EmbeddedCDeveloperOutput) -> None:
    calc = output.rtos_calc
    text = "\n".join(calc) if isinstance(calc, list) else str(calc)
    if "N/A" in text:
        return  # fallback path is valid
    digits = sum(c.isdigit() for c in text)
    if digits < 3:
        raise DomainCheckError(
            f"rtos_calc contains fewer than 3 numeric characters but N/A was not declared. "
            f"Either show step-by-step arithmetic or write 'N/A — [reason]'. "
            f"Got: '{text[:80]}'"
        )


def _check_self_evaluation_has_evidence(output: EmbeddedCDeveloperOutput) -> None:
    for line in output.self_evaluation:
        if line.result == "PASS" and len(line.evidence.strip()) < 10:
            raise DomainCheckError(
                f"self_evaluation item '{line.item}' claims PASS "
                f"but evidence is empty or too short: '{line.evidence}'"
            )
