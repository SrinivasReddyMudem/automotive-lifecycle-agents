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
    _check_layer_suspect_matches_root_cause(output)
    _check_rtos_calc_structure(output)
    _check_cpu_load_calc(output)
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


def _check_layer_suspect_matches_root_cause(output: EmbeddedCDeveloperOutput) -> None:
    """
    The root_cause text must reference the name of the SUSPECT layer.
    This ensures the agent's conclusion is anchored to its own layer diagnosis.
    """
    suspects = [d for d in output.layer_diagnosis if d.status == "SUSPECT"]
    root_lower = output.root_cause.lower()
    for suspect in suspects:
        layer_lower = suspect.layer.lower()
        # Allow layer name OR common synonyms
        synonyms = {
            "physical": [
                "physical", "hardware", "supply", "power", "clock", "crystal",
                "vcc", "voltage", "current", "signal", "gnd", "ground", "rail",
                "oscillator", "peripheral", "register", "pin", "transceiver",
            ],
            "rtos": [
                "rtos", "os", "task", "stack", "scheduler", "watchdog", "wdt",
                "isr", "interrupt", "deadline", "cpu", "overload", "preempt",
                "context", "tick", "period", "execution", "timing", "budget",
                "utilisation", "utilization", "load", "starvation", "priority",
            ],
            "application": [
                "application", "app", "logic", "state", "sw", "software", "code",
                "algorithm", "function", "data", "variable", "flag", "mode",
                "value", "calculation", "buffer", "pointer", "null", "overflow",
            ],
        }
        accepted_words = synonyms.get(layer_lower, [layer_lower])
        if not any(word in root_lower for word in accepted_words):
            raise DomainCheckError(
                f"root_cause does not reference the SUSPECT layer '{suspect.layer}'. "
                f"The root_cause conclusion must name or describe the layer identified as SUSPECT. "
                f"root_cause starts with: '{output.root_cause[:80]}'"
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


def _check_cpu_load_calc(output: EmbeddedCDeveloperOutput) -> None:
    calc = output.cpu_load_calc
    text = "\n".join(calc) if isinstance(calc, list) else str(calc)
    if "N/A" in text:
        return  # symptom did not indicate CPU load — fallback is valid
    digits = sum(c.isdigit() for c in text)
    if digits < 3:
        raise DomainCheckError(
            f"cpu_load_calc contains fewer than 3 numeric characters but N/A was not declared. "
            f"Either show per-task WCET × frequency arithmetic or write 'N/A — [reason]'. "
            f"Got: '{text[:80]}'"
        )


def _check_self_evaluation_has_evidence(output: EmbeddedCDeveloperOutput) -> None:
    for line in output.self_evaluation:
        if line.result == "PASS" and len(line.evidence.strip()) < 10:
            raise DomainCheckError(
                f"self_evaluation item '{line.item}' claims PASS "
                f"but evidence is empty or too short: '{line.evidence}'"
            )
