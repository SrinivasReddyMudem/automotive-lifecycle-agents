"""
Output schema for field_debug_fae.
Covers DTC triage, UDS session analysis, CAN fault correlation, and debug steps.
"""

from pydantic import BaseModel, Field
from typing import Literal
from sdk_agents.core.shared_schema import (
    ProbableCause, NarrowingQuestion, SelfEvaluationLine, DebugStep
)


class SymptomTranslation(BaseModel):
    customer_complaint: str = Field(description="Exact customer complaint in their words")
    function_affected: str = Field(description="Vehicle function or ECU subsystem affected")
    translated_to: str = Field(description="Engineering domain this maps to")
    autosar_layer: str = Field(description="SWC / RTE / COM / DCM / CanIf / MCAL / DEM")
    osi_layer: str = Field(description="L1 / L2 / L3-L4 / L5 / L7")
    primary_tool: str = Field(description="CANoe / DLT Viewer / TRACE32 / Saleae / Wireshark")
    probable_domain: str = Field(description="CAN bus / UDS session / AUTOSAR SWC / HW power")


class FaultDetails(BaseModel):
    dtc_code: str = Field(description="DTC code e.g. U0100 or N/A if not reported")
    dtc_description: str = Field(description="Human-readable description of the DTC")
    status_byte: str = Field(description="Hex status byte e.g. 0x6F or N/A if not available")
    status_byte_decoded: str = Field(
        description="Bit-by-bit interpretation: Bit 0 = testFailed, Bit 3 = confirmedDTC, etc."
    )
    system: str = Field(description="ECU or subsystem affected")
    safety_relevant: Literal["YES", "NO"]
    safety_impact: str = Field(description="Safety impact if YES, or 'Not safety-critical' if NO")


class UdsSessionAnalysis(BaseModel):
    session_type: str = Field(
        description="Session type involved: default / extended / programming / N/A"
    )
    nrc_code: str = Field(description="NRC hex e.g. 0x22 or N/A if no NRC reported")
    nrc_name: str = Field(description="Full NRC name e.g. conditionsNotCorrect or N/A")
    nrc_root_causes: list[str] = Field(
        description="3 most likely root causes for this specific NRC in automotive ECUs"
    )
    session_sequence_issue: str = Field(
        description="Expected session sequence and where it broke, or N/A if no UDS issue"
    )


class FieldDebugFaeOutput(BaseModel):
    model_config = {"extra": "ignore"}

    symptom_translation: SymptomTranslation = Field(
        description="STEP 0: translate customer complaint to engineering layer before any diagnosis"
    )
    fault_details: FaultDetails = Field(
        description="STEP 1 header: DTC code, status byte decoded bit-by-bit, safety relevance"
    )
    analysis: str = Field(
        description=(
            "What the data tells us about fault timing, pattern, and conditions. "
            "Relate status byte bits, freeze frame values, and symptom correlation."
        )
    )
    probable_causes: list[ProbableCause] = Field(
        min_length=3,
        max_length=3,
        description="Exactly 3 ranked causes. Each test must name tool + probe point + action.",
    )
    uds_session_analysis: UdsSessionAnalysis = Field(
        description="UDS NRC analysis and session sequence reconstruction"
    )
    tec_math: str = Field(
        description=(
            "TEC accumulation calculation if CAN is involved. "
            "Show: net_TEC/s = (error_rate*8) - ((1-error_rate)*1), time to bus-off. "
            "Use 'N/A — no CAN trace involved' if not applicable."
        )
    )
    decision_flow: str = Field(
        description=(
            "ASCII branching diagnostic tree starting at symptom classification. "
            "Each branch has Yes/No leading to next layer or conclusion."
        )
    )
    debug_steps: list[DebugStep] = Field(
        min_length=3,
        max_length=3,
        description="Exactly 3 prioritised debug steps with tool, action, expected output",
    )
    lab_vs_field: str = Field(
        description="State whether field data only is enough or lab reproduction is required and why"
    )
    narrowing_questions: list[NarrowingQuestion] = Field(
        min_length=3,
        max_length=3,
        description="Exactly 3 yes/no questions to narrow the fault, each with consequence",
    )
    self_evaluation: list[SelfEvaluationLine] = Field(
        description="PASS/FAIL check for each major section with quoted evidence from this response"
    )
