"""
Output schema for can_bus_analyst.
Enforced at API level via tool_choice — model cannot deviate from this structure.

ProbableCause, NarrowingQuestion, SelfEvaluationLine are re-exported from shared_schema
so existing imports from this module continue to work unchanged.
"""

from pydantic import BaseModel, Field
from sdk_agents.core.shared_schema import (
    ProbableCause,       # re-exported for backward compatibility
    NarrowingQuestion,   # re-exported for backward compatibility
    SelfEvaluationLine,  # re-exported for backward compatibility
    ToolSelection,
    ProtocolDetection,
    DataSufficiency,
    InputAnalysis,
    DiagnosisBasisLine,
)

# Re-export so "from can_bus_analyst.schema import ProbableCause" still works
__all__ = [
    "CanBusAnalystOutput",
    "ProbableCause",
    "NarrowingQuestion",
    "SelfEvaluationLine",
    "ToolSelection",
    "ProtocolDetection",
    "DataSufficiency",
    "InputAnalysis",
    "DiagnosisBasisLine",
]


class CanBusAnalystOutput(BaseModel):
    model_config = {"extra": "ignore"}

    protocol_detection: ProtocolDetection = Field(
        description=(
            "STEP 0: identify the bus protocol from the user's input before any diagnosis. "
            "State the protocol (CAN / CAN-FD / LIN / Ethernet / RTOS / UDS / Unknown), "
            "what words in the input revealed it, and your confidence level."
        )
    )
    input_analysis: InputAnalysis = Field(
        description=(
            "STEP 1: separate what the user directly stated (input_facts) from what you inferred "
            "or assumed (assumptions). This is the traceability anchor for the whole diagnosis. "
            "Never mix assumed values into input_facts."
        )
    )
    data_sufficiency: DataSufficiency = Field(
        description=(
            "STEP 2: rate data completeness. SUFFICIENT = enough to diagnose with confidence. "
            "PARTIAL = diagnosis possible but one or more key measurements are missing. "
            "INSUFFICIENT = too little data — list exactly what is needed."
        )
    )
    expert_diagnosis: str = Field(
        description=(
            "1-2 sentence immediate read: which OSI layer the fault is at "
            "and what the symptom pattern rules out"
        )
    )
    diagnosis_basis: list[DiagnosisBasisLine] = Field(
        description=(
            "Explicit fact → implication chain that justifies expert_diagnosis. "
            "Each line links one observed fact to one diagnostic conclusion. "
            "Minimum 2 lines. This prevents unsupported leaps in reasoning."
        )
    )
    osi_layer: str = Field(
        description="Which layer: L1 Physical / L2 Data Link / L3-L4 Network / L7 Application / MCU Execution"
    )
    autosar_layer: str = Field(
        description="AUTOSAR layer: MCAL / CanIf / CanSM / COM / PduR / SWC / RTE / DCM"
    )
    tool_selection: ToolSelection = Field(
        description=(
            "Structured tool recommendation for this specific fault. "
            "primary: best tool for this protocol + OSI layer. "
            "secondary: cross-verification tool. "
            "reason: why primary is optimal. "
            "fallback: alternative if primary unavailable."
        )
    )
    tec_math: list[str] = Field(
        description=(
            "TEC (Transmit Error Counter) accumulation calculation as a list of strings — "
            "one string per line. First element: header. Second: formula. "
            "Middle elements: step-by-step arithmetic with actual numbers. "
            "Last element: plain-English confirmation whether calculated time matches reported symptom. "
            "If no symptom timing is provided, use a single-element list: "
            "['N/A — no symptom timing provided. State how long before bus-off occurs.']"
        )
    )
    bus_load_calc: list[str] = Field(
        description=(
            "CAN bus load calculation as a list of strings — one string per line. "
            "First element: header 'CAN Bus Load — utilisation analysis'. "
            "Second element: formula 'Formula: load% = (n_msgs × frame_bits × msg_rate) / baudrate × 100'. "
            "Middle elements: one arithmetic step per line with actual numbers. "
            "Last element: plain-English confirmation starting with → stating whether "
            "load is within safe limits (< 30% normal, < 60% maximum). "
            "If baudrate or message count not provided: "
            "['N/A — baudrate and message schedule not provided. "
            "State baudrate (bps), number of CAN messages, and TX rate per message.']"
        )
    )
    probable_causes: list[ProbableCause] = Field(
        min_length=3,
        max_length=3,
        description=(
            "Exactly 3 ranked causes with specific Test/Pass/Fail measurements. "
            "ranking_reason must justify why this cause has this rank vs the others. "
            "validation_test must be one single definitive action + expected result."
        ),
    )
    contradictions: list[str] = Field(
        description=(
            "Observations in the input that contradict each other or contradict an eliminated cause. "
            "Each string is one contradiction: 'Observation X contradicts Y because Z'. "
            "Write ['None identified'] if all observations are consistent."
        )
    )
    decision_flow: list[str] = Field(
        description=(
            "Branching diagnostic tree as a list of lines — one string per line. "
            "MUST start at L1 Physical layer — never start at a higher layer. "
            "Each branch has Yes/No leading to next layer or conclusion. "
            "Example lines: "
            "'L1 Physical: Vcc ripple and GND offset OK?', "
            "'+-- No  --> Fix supply / GND, retest', "
            "'+-- Yes --> L2 Data Link: Error frames in CANoe?', "
            "'    +-- No  --> Check thermal drift with heat gun', "
            "'    +-- Yes --> Bit error = L1; ACK error = check L7'"
        )
    )
    narrowing_questions: list[NarrowingQuestion] = Field(
        min_length=3,
        max_length=3,
        description="Exactly 3 questions to narrow the fault, each with Yes and No consequence",
    )
    self_evaluation: list[SelfEvaluationLine] = Field(
        description="PASS/FAIL check for each major section with quoted evidence"
    )
