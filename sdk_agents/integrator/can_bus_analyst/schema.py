"""
Output schema for can_bus_analyst.
Enforced at API level via tool_choice — model cannot deviate from this structure.
"""

from pydantic import BaseModel, Field
from typing import Literal


class ProbableCause(BaseModel):
    rank: Literal["HIGH", "MEDIUM", "LOW"]
    description: str = Field(description="What is causing the fault and why")
    test: str = Field(description="Specific measurement to perform — tool, signal, value")
    pass_criteria: str = Field(description="Exact value/condition that rules this cause out")
    fail_criteria: str = Field(description="Exact value/condition that confirms this cause")


class NarrowingQuestion(BaseModel):
    question: str
    yes_consequence: str = Field(description="What yes means for the diagnosis")
    no_consequence: str = Field(description="What no means for the diagnosis")


class SelfEvaluationLine(BaseModel):
    item: str = Field(description="What was checked")
    result: Literal["PASS", "FAIL"]
    evidence: str = Field(description="Specific numbers or values from this response that prove the result")


class CanBusAnalystOutput(BaseModel):
    model_config = {"extra": "ignore"}

    expert_diagnosis: str = Field(
        description=(
            "1-2 sentence immediate read: which OSI layer the fault is at "
            "and what the symptom pattern rules out"
        )
    )
    osi_layer: str = Field(
        description="Which layer: L1 Physical / L2 Data Link / L3-L4 Network / L7 Application / MCU Execution"
    )
    autosar_layer: str = Field(
        description="AUTOSAR layer: MCAL / CanIf / CanSM / COM / PduR / SWC / RTE / DCM"
    )
    recommended_tool: str = Field(
        description="Primary debug tool for this fault: oscilloscope / CANoe / TRACE32 / DLT Viewer"
    )
    tec_math: str = Field(
        description=(
            "TEC (Transmit Error Counter) accumulation calculation with specific numbers: "
            "msg/s assumption, errors needed for bus-off (256/8=32), "
            "minimum error rate %, net TEC climb rate per second, "
            "calculated time to bus-off in seconds. "
            "Always start with: 'TEC (Transmit Error Counter):' to define the term. "
            "Always end with a plain-English confirmation sentence stating whether "
            "the calculated time matches the reported symptom — e.g. "
            "'Calculated time to bus-off: 181 s — consistent with reported 3-minute onset.' "
            "or 'Calculated time does not match reported symptom — re-examine TX rate assumption.'"
        )
    )
    probable_causes: list[ProbableCause] = Field(
        min_length=3,
        max_length=3,
        description="Exactly 3 ranked causes with specific Test/Pass/Fail measurements",
    )
    decision_flow: list[str] = Field(
        description=(
            "Branching diagnostic tree as a list of lines — one string per line. "
            "Start at L1 Physical. Each branch has Yes/No leading to next layer or conclusion. "
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
