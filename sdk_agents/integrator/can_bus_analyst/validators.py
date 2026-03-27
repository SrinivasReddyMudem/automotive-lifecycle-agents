"""
Domain-specific validators for can_bus_analyst output.
These checks catch semantic errors that JSON schema cannot — e.g. vague
test descriptions, missing numeric values, unknown AUTOSAR layer names.
"""

from sdk_agents.core.base_agent import DomainCheckError
from .schema import CanBusAnalystOutput

KNOWN_AUTOSAR_LAYERS = [
    "MCAL", "CanIf", "CanSM", "COM", "PduR", "SWC", "RTE", "DCM",
    "EthIf", "TcpIp", "SoAd", "CanTp", "OS", "CanDrv", "EthDrv",
]

MIN_TEST_LENGTH = 25       # test must describe an action + tool: "check ground" (12) is too vague
MIN_CRITERIA_LENGTH = 12  # pass/fail criteria can be a short threshold: "Ripple < 200 mV" is fine


def validate(output: CanBusAnalystOutput) -> None:
    """Run all domain checks. Raises DomainCheckError on first failure."""

    _check_tec_math_has_numbers(output)
    _check_autosar_layer_known(output)
    _check_probable_causes_specific(output)
    _check_self_evaluation_has_evidence(output)


def _check_tec_math_has_numbers(output: CanBusAnalystOutput) -> None:
    digits = sum(c.isdigit() for c in output.tec_math)
    if digits < 3:
        raise DomainCheckError(
            f"tec_math contains fewer than 3 numeric characters — "
            f"model returned a vague description instead of a calculation. "
            f"Got: '{output.tec_math[:80]}'"
        )


def _check_autosar_layer_known(output: CanBusAnalystOutput) -> None:
    layer = output.autosar_layer
    if not any(known in layer for known in KNOWN_AUTOSAR_LAYERS):
        raise DomainCheckError(
            f"autosar_layer '{layer}' does not match any known AUTOSAR layer. "
            f"Expected one of: {KNOWN_AUTOSAR_LAYERS}"
        )


def _check_probable_causes_specific(output: CanBusAnalystOutput) -> None:
    for i, cause in enumerate(output.probable_causes):
        for field_name, field_value, minimum in [
            ("test", cause.test, MIN_TEST_LENGTH),
            ("pass_criteria", cause.pass_criteria, MIN_CRITERIA_LENGTH),
            ("fail_criteria", cause.fail_criteria, MIN_CRITERIA_LENGTH),
        ]:
            if len(field_value.strip()) < minimum:
                raise DomainCheckError(
                    f"probable_causes[{i}].{field_name} is too vague "
                    f"({len(field_value)} chars, minimum {minimum}). "
                    f"Got: '{field_value}'"
                )


def _check_self_evaluation_has_evidence(output: CanBusAnalystOutput) -> None:
    for line in output.self_evaluation:
        if line.result == "PASS" and len(line.evidence.strip()) < 10:
            raise DomainCheckError(
                f"self_evaluation item '{line.item}' claims PASS "
                f"but evidence field is empty or too short: '{line.evidence}'"
            )
