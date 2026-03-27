"""
Domain validators for autosar_bsw_developer output.
Catches non-standard naming, missing RTE APIs, vague BSW parameters.
"""

from sdk_agents.core.base_agent import DomainCheckError
from .schema import AutosarBswDeveloperOutput

KNOWN_AUTOSAR_VERSIONS = ["R4.4", "R4.3", "R4.2", "R4.1", "R22", "Adaptive"]
KNOWN_SWC_TYPES = ["Application", "Sensor-Actuator", "Service", "Parameter", "Composition"]
MIN_RTE_API_LENGTH = 20  # "Rte_Write_X_Y(z);" must be at least this
MIN_MISRA_NOTE_LENGTH = 15


def validate(output: AutosarBswDeveloperOutput) -> None:
    _check_autosar_version_known(output)
    _check_swc_naming_convention(output)
    _check_rte_apis_present(output)
    _check_misra_notes_specific(output)
    _check_self_evaluation_has_evidence(output)


def _check_autosar_version_known(output: AutosarBswDeveloperOutput) -> None:
    version = output.autosar_version
    if not any(known in version for known in KNOWN_AUTOSAR_VERSIONS):
        raise DomainCheckError(
            f"autosar_version '{version}' does not match known versions. "
            f"Expected one of: {KNOWN_AUTOSAR_VERSIONS}"
        )


def _check_swc_naming_convention(output: AutosarBswDeveloperOutput) -> None:
    # SWC name should follow PascalCase — at minimum must be non-empty and not generic
    name = output.swc_name
    if len(name.strip()) < 3 or name.lower() in ("swc", "component", "module"):
        raise DomainCheckError(
            f"swc_name '{name}' is too generic or too short. "
            f"Must follow AUTOSAR naming convention (PascalCase, meaningful name)."
        )


def _check_rte_apis_present(output: AutosarBswDeveloperOutput) -> None:
    all_ports = output.provider_ports + output.consumer_ports
    for i, port in enumerate(all_ports):
        if len(port.rte_api.strip()) < MIN_RTE_API_LENGTH:
            raise DomainCheckError(
                f"Port[{i}].rte_api '{port.rte_api}' is too short or missing. "
                f"Must show exact RTE API signature (minimum {MIN_RTE_API_LENGTH} chars)."
            )
        if "Rte_" not in port.rte_api and "N/A" not in port.rte_api:
            raise DomainCheckError(
                f"Port[{i}].rte_api does not start with 'Rte_'. "
                f"Must use actual AUTOSAR RTE API. Got: '{port.rte_api[:60]}'"
            )


def _check_misra_notes_specific(output: AutosarBswDeveloperOutput) -> None:
    if len(output.misra_notes.strip()) < MIN_MISRA_NOTE_LENGTH:
        raise DomainCheckError(
            f"misra_notes is too short ({len(output.misra_notes)} chars). "
            f"Must reference specific MISRA rules by number."
        )


def _check_self_evaluation_has_evidence(output: AutosarBswDeveloperOutput) -> None:
    for line in output.self_evaluation:
        if line.result == "PASS" and len(line.evidence.strip()) < 10:
            raise DomainCheckError(
                f"self_evaluation item '{line.item}' claims PASS "
                f"but evidence is empty or too short: '{line.evidence}'"
            )
