"""
Domain-specific validators for can_bus_analyst output.
These checks catch semantic errors that JSON schema cannot — e.g. vague
test descriptions, missing numeric values, unknown AUTOSAR layer names,
wrong tool for detected protocol, and decision flow not starting at L1.
"""

from sdk_agents.core.base_agent import DomainCheckError
from sdk_agents.core.tool_constants import get_tools_for
from .schema import CanBusAnalystOutput

KNOWN_AUTOSAR_LAYERS = [
    "MCAL", "CanIf", "CanSM", "COM", "PduR", "SWC", "RTE", "DCM",
    "EthIf", "TcpIp", "SoAd", "CanTp", "OS", "CanDrv", "EthDrv",
]

MIN_TEST_LENGTH = 25       # test must describe an action + tool: "check ground" (12) is too vague
MIN_CRITERIA_LENGTH = 12  # pass/fail criteria can be a short threshold: "Ripple < 200 mV" is fine

# L1 Physical must be the entry point of the decision flow
L1_ANCHOR_WORDS = ["l1", "physical", "vcc", "gnd", "ground", "supply", "voltage", "scope"]


def validate(output: CanBusAnalystOutput) -> None:
    """Run all domain checks. Raises DomainCheckError on first failure."""
    _check_tec_math_has_numbers(output)
    _check_bus_load_calc_has_numbers(output)
    _check_autosar_layer_known(output)
    _check_tool_selection(output)
    _check_decision_flow_starts_l1(output)
    _check_probable_causes_specific(output)
    _check_self_evaluation_has_evidence(output)


def _check_tec_math_has_numbers(output: CanBusAnalystOutput) -> None:
    tec = output.tec_math
    text = "\n".join(tec) if isinstance(tec, list) else str(tec)
    digits = sum(c.isdigit() for c in text)
    if digits < 3:
        raise DomainCheckError(
            f"tec_math contains fewer than 3 numeric characters — "
            f"model returned a vague description instead of a calculation. "
            f"Got: '{text[:80]}'"
        )


def _check_bus_load_calc_has_numbers(output: CanBusAnalystOutput) -> None:
    calc = output.bus_load_calc
    text = "\n".join(calc) if isinstance(calc, list) else str(calc)
    if "N/A" in text:
        return  # fallback path is valid
    digits = sum(c.isdigit() for c in text)
    if digits < 3:
        raise DomainCheckError(
            f"bus_load_calc contains fewer than 3 numeric characters but N/A was not declared. "
            f"Either show step-by-step arithmetic or write 'N/A — [reason]'. "
            f"Got: '{text[:80]}'"
        )


def _check_autosar_layer_known(output: CanBusAnalystOutput) -> None:
    layer = output.autosar_layer
    if not any(known in layer for known in KNOWN_AUTOSAR_LAYERS):
        raise DomainCheckError(
            f"autosar_layer '{layer}' does not match any known AUTOSAR layer. "
            f"Expected one of: {KNOWN_AUTOSAR_LAYERS}"
        )


def _check_tool_selection(output: CanBusAnalystOutput) -> None:
    """
    Verify that tool_selection.primary is in LAYER_TOOL_MAP for the detected
    protocol + OSI layer combination.
    If the combination is not in the map (Unknown protocol or unusual layer),
    the check is skipped — we only enforce what is known.
    """
    protocol = output.protocol_detection.protocol
    osi_layer = output.osi_layer
    primary = output.tool_selection.primary

    expected_tools = get_tools_for(protocol, osi_layer)
    if not expected_tools:
        return  # unknown combination — skip enforcement

    # Primary tool must be in the expected list (partial match allowed for tool names with suffixes)
    primary_lower = primary.lower()
    if not any(primary_lower in t.lower() or t.lower() in primary_lower for t in expected_tools):
        raise DomainCheckError(
            f"tool_selection.primary '{primary}' is not appropriate for "
            f"protocol={protocol}, layer={osi_layer}. "
            f"Expected one of: {expected_tools}. "
            f"Update primary to use the correct tool for this fault type."
        )


def _check_decision_flow_starts_l1(output: CanBusAnalystOutput) -> None:
    """
    Decision flow must open at L1 Physical — never jump straight to L2 or higher.
    Checks the first non-empty line of the decision_flow list.
    """
    flow = output.decision_flow
    if not flow:
        raise DomainCheckError(
            "decision_flow is empty. Must start at L1 Physical and branch through each layer."
        )
    first_line = flow[0].lower()
    if not any(word in first_line for word in L1_ANCHOR_WORDS):
        raise DomainCheckError(
            f"decision_flow must start at L1 Physical. "
            f"First line '{flow[0][:80]}' does not reference L1/Physical/Vcc/GND/supply. "
            f"Always begin diagnostic flow at the physical layer before checking higher layers."
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
                    f"Got: '{field_value}'. "
                    f"Must name what is being measured AND include a numeric threshold. "
                    f"BAD: '< 50 mV' — GOOD: 'GND offset < 50 mV' or 'Ripple < 200 mV peak-to-peak'."
                )


def _check_self_evaluation_has_evidence(output: CanBusAnalystOutput) -> None:
    for line in output.self_evaluation:
        if line.result == "PASS" and len(line.evidence.strip()) < 10:
            raise DomainCheckError(
                f"self_evaluation item '{line.item}' claims PASS "
                f"but evidence field is empty or too short: '{line.evidence}'"
            )
