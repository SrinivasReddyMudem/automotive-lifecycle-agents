"""
Domain validators for sw_integrator output.
Catches vague resolution steps, missing AUTOSAR layer classification, unknown memory sections.
"""

from sdk_agents.core.base_agent import DomainCheckError
from .schema import SwIntegratorOutput

KNOWN_AUTOSAR_LAYERS = [
    "RTE", "BSW", "Linker", "OS", "MCAL", "ComStack",
    "CanIf", "COM", "PduR", "CanSM", "SWC", "Build",
]

MIN_ACTION_LENGTH = 15
MIN_ANALYSIS_LENGTH = 40


def validate(output: SwIntegratorOutput) -> None:
    _check_autosar_layer_known(output)
    _check_analysis_specific(output)
    _check_resolution_steps_specific(output)
    _check_resource_budget_calc(output)
    _check_self_evaluation_has_evidence(output)


def _check_autosar_layer_known(output: SwIntegratorOutput) -> None:
    layer = output.error_classification.autosar_layer
    if not any(known in layer for known in KNOWN_AUTOSAR_LAYERS):
        raise DomainCheckError(
            f"error_classification.autosar_layer '{layer}' does not match any known "
            f"AUTOSAR layer. Expected one of: {KNOWN_AUTOSAR_LAYERS}"
        )


def _check_analysis_specific(output: SwIntegratorOutput) -> None:
    if len(output.analysis.strip()) < MIN_ANALYSIS_LENGTH:
        raise DomainCheckError(
            f"analysis field is too short ({len(output.analysis)} chars, "
            f"minimum {MIN_ANALYSIS_LENGTH}). Must explain the error at AUTOSAR layer level."
        )


def _check_resolution_steps_specific(output: SwIntegratorOutput) -> None:
    for i, step in enumerate(output.resolution_steps):
        if len(step.action.strip()) < MIN_ACTION_LENGTH:
            raise DomainCheckError(
                f"resolution_steps[{i}].action is too vague "
                f"({len(step.action)} chars, minimum {MIN_ACTION_LENGTH}). "
                f"Got: '{step.action}'"
            )


def _check_resource_budget_calc(output: SwIntegratorOutput) -> None:
    calc = output.resource_budget_calc
    text = "\n".join(calc) if isinstance(calc, list) else str(calc)
    if "N/A" in text:
        return  # fallback path is valid — symptom did not indicate resource constraint
    digits = sum(c.isdigit() for c in text)
    if digits < 3:
        raise DomainCheckError(
            f"resource_budget_calc contains fewer than 3 numeric characters but N/A was not declared. "
            f"Either show step-by-step arithmetic or write 'N/A — [reason]'. "
            f"Got: '{text[:80]}'"
        )


def _check_self_evaluation_has_evidence(output: SwIntegratorOutput) -> None:
    for line in output.self_evaluation:
        if line.result == "PASS" and len(line.evidence.strip()) < 10:
            raise DomainCheckError(
                f"self_evaluation item '{line.item}' claims PASS "
                f"but evidence is empty or too short: '{line.evidence}'"
            )
