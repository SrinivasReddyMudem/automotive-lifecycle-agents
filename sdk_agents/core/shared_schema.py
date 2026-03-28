"""
Shared Pydantic sub-models reused across multiple agents.
Import from here to keep schemas consistent and avoid duplication.
"""

from pydantic import BaseModel, Field
from typing import Literal


class ProbableCause(BaseModel):
    rank: Literal["HIGH", "MEDIUM", "LOW"]
    description: str = Field(description="What is causing the fault and why")
    is_hypothesis: bool = Field(
        default=False,
        description=(
            "True if this cause is inferred or theoretical with no direct observed evidence. "
            "HIGH rank must always be False — it must be anchored to an observed fact."
        ),
    )
    ranking_reason: str = Field(
        default="",
        description=(
            "Why this cause has this rank vs the others — what evidence or symptom pattern "
            "justifies HIGH over MEDIUM, or MEDIUM over LOW"
        ),
    )
    test: str = Field(description="Specific measurement to perform — tool, signal, value")
    pass_criteria: str = Field(description="Exact value/condition that rules this cause out")
    fail_criteria: str = Field(description="Exact value/condition that confirms this cause")
    validation_test: str = Field(
        default="",
        description=(
            "Single most definitive test to confirm or deny this cause — "
            "one action, one result, one decision. "
            "E.g. 'Measure GND offset DMM at ECU connector pin 4 with engine running at 2000 RPM — "
            "if > 200 mV confirmed, if < 50 mV ruled out.'"
        ),
    )


class ToolSelection(BaseModel):
    """Structured tool recommendation — replaces the single recommended_tool string."""
    primary: str = Field(
        description="Best tool for this specific fault and layer — name it exactly"
    )
    secondary: str = Field(
        description="Second tool to cross-verify or gather data the primary cannot"
    )
    reason: str = Field(
        description="Why the primary tool is optimal for this protocol and OSI layer"
    )
    fallback: str = Field(
        description="Alternative tool if primary is not available in the workshop"
    )


class ProtocolDetection(BaseModel):
    """What protocol/bus the fault is on — detected from the user's input."""
    protocol: Literal["CAN", "CAN-FD", "LIN", "Ethernet", "FlexRay", "RTOS", "UDS", "Unknown"]
    detected_from: str = Field(
        description=(
            "Which words or signals in the user's input reveal the protocol — "
            "e.g. 'user mentioned TEC, bus-off, 500 kbps → CAN'"
        )
    )
    confidence: Literal["HIGH", "MEDIUM", "LOW"]


class DataSufficiency(BaseModel):
    """Rates how complete the input data is for a reliable diagnosis."""
    level: Literal["SUFFICIENT", "PARTIAL", "INSUFFICIENT"]
    confidence: Literal["HIGH", "MEDIUM", "LOW"] = Field(
        description=(
            "How confident is the diagnosis given the available data. "
            "HIGH = strong evidence, MEDIUM = probable but unconfirmed, LOW = speculative."
        )
    )
    confidence_reason: str = Field(
        description=(
            "One sentence explaining why this confidence level was assigned — "
            "e.g. 'Missing oscilloscope trace and exact baudrate reduce confidence.'"
        )
    )
    missing_critical_data: list[str] = Field(
        description=(
            "List of specific measurements or values that are missing and would change the diagnosis. "
            "Write ['None — data is complete'] if level is SUFFICIENT."
        )
    )


class InputAnalysis(BaseModel):
    """Structured extraction of what the user stated vs what was assumed."""
    input_facts: list[str] = Field(
        description=(
            "Facts the user directly stated — no inference. "
            "E.g. 'bus-off after 3 minutes', 'only when engine running', 'other nodes unaffected'."
        )
    )
    assumptions: list[str] = Field(
        description=(
            "Things inferred or assumed because they were not stated — flag uncertainty. "
            "E.g. 'assumed standard CAN frame — DLC not given', 'assumed 500 kbps — baudrate not stated'."
        )
    )


class DiagnosisBasisLine(BaseModel):
    """Links one observed fact to its diagnostic implication — the reasoning chain."""
    fact: str = Field(description="The specific fact or observation from input_analysis")
    implication: str = Field(
        description="What that fact implies about the fault — the diagnostic link"
    )


class NarrowingQuestion(BaseModel):
    question: str
    yes_consequence: str = Field(description="What yes means for the diagnosis")
    no_consequence: str = Field(description="What no means for the diagnosis")


class SelfEvaluationLine(BaseModel):
    item: str = Field(description="What was checked")
    result: Literal["PASS", "FAIL"]
    evidence: str = Field(description="Specific text from this response that proves the result")


class DebugStep(BaseModel):
    step_number: int
    tool: str
    action: str = Field(description="Exactly what to do with the tool")
    expected_output: str = Field(description="What you see in the tool if this is the cause")
