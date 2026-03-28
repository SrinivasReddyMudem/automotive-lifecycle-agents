"""
Output schema for sw_integrator.
Covers AUTOSAR integration errors, memory map analysis, ASPICE SWE.5 evidence.
"""

from pydantic import BaseModel, Field
from typing import Literal
from sdk_agents.core.shared_schema import (
    ProbableCause, NarrowingQuestion, SelfEvaluationLine, DebugStep
)


class IntegrationErrorClassification(BaseModel):
    error_type: str = Field(
        description="Error category: Port not connected / Interface mismatch / Linker overflow / Stack overflow / Undefined symbol / BSW config inconsistency"
    )
    autosar_layer: str = Field(
        description="Affected AUTOSAR layer: RTE / BSW / Linker / OS / MCAL / ComStack"
    )
    tool_view: str = Field(
        description="Tool and view to diagnose: DaVinci System Design port view / GCC .map file / TRACE32 Task window"
    )
    root_cause_hypothesis: str = Field(
        description="Most likely root cause in one sentence before further investigation"
    )


class MemorySection(BaseModel):
    section: str = Field(description=".text / .rodata / .data / .bss")
    used_hex: str = Field(description="Used size in hex e.g. 0x1A200 or UNKNOWN")
    total_hex: str = Field(description="Total allocated size in hex or UNKNOWN")
    utilization_pct: str = Field(description="Utilization percent or UNKNOWN")
    headroom_ok: Literal["YES", "NO", "UNKNOWN"]


class AspiceSwe5WorkProduct(BaseModel):
    work_product: str = Field(description="Work product name e.g. Integration Test Specification")
    wp_id: str = Field(description="ASPICE work product ID e.g. 17-50")
    status: Literal["PRESENT", "MISSING", "INCOMPLETE"]
    note: str = Field(description="Specific gap or confirmation")


class SwIntegratorOutput(BaseModel):
    model_config = {"extra": "ignore"}

    error_classification: IntegrationErrorClassification = Field(
        description="Classify the integration error by AUTOSAR layer before diagnosing"
    )
    analysis: str = Field(
        description=(
            "What the error means at the AUTOSAR layer level. "
            "Trace the full path: SWC port -> RTE -> COM -> PduR -> CanIf -> CAN driver if relevant. "
            "Never suggest 'regenerate RTE' without diagnosing root cause in ARXML first."
        )
    )
    probable_causes: list[ProbableCause] = Field(
        min_length=3,
        max_length=3,
        description="Exactly 3 ranked causes. Test must name specific tool view + element + action.",
    )
    memory_budget: list[MemorySection] = Field(
        description=(
            "ROM/RAM budget per section. Fill with UNKNOWN if no .map file provided. "
            "Headroom < 10% = warning; < 5% = blocker."
        )
    )
    resource_budget_calc: list[str] = Field(
        description=(
            "Resource budget calculations as a list of strings — one string per line. "
            "ONLY populate when the symptom explicitly indicates a resource constraint: "
            "random resets, task deadline missed, NvM write failure, after adding new SWC/feature, "
            "CPU overload reported, or flash/RAM overflow. "
            "Otherwise: ['N/A — symptom does not indicate a resource constraint']. "
            "Cover whichever metrics are relevant: "
            "(1) CPU load: 'load% = WCET_ms × frequency_hz / 1000 × 100' per task, "
            "(2) NvM endurance: 'remaining = rated_endurance − current_write_count', "
            "(3) EEPROM write rate vs lifetime. "
            "First element: header naming the metric being calculated. "
            "Middle elements: one arithmetic step per line with actual numbers. "
            "Last element: plain-English confirmation starting with →."
        )
    )
    resolution_steps: list[DebugStep] = Field(
        min_length=3,
        max_length=3,
        description="Exactly 3 ordered resolution steps with tool, action, expected result",
    )
    aspice_swe5_evidence: list[AspiceSwe5WorkProduct] = Field(
        description="ASPICE SWE.5 work product status relevant to this integration activity"
    )
    narrowing_questions: list[NarrowingQuestion] = Field(
        min_length=3,
        max_length=3,
        description="Exactly 3 yes/no questions to narrow the integration fault",
    )
    self_evaluation: list[SelfEvaluationLine] = Field(
        description="PASS/FAIL check for each major section with quoted evidence from this response"
    )
