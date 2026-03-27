"""
Output schema for sil_hil_test_planner.
Covers SIL/HIL test planning for ASPICE SWE.5 and SWE.6.
"""

from pydantic import BaseModel, Field
from typing import Literal
from sdk_agents.core.shared_schema import SelfEvaluationLine


class TestEnvironment(BaseModel):
    sil_setup: str = Field(
        description="SIL host platform, simulation tools, virtual IO, stubs. N/A if SIL not applicable."
    )
    hil_setup: str = Field(
        description="HIL platform (dSPACE/NI), ECU hardware, plant model, real bus interfaces"
    )
    bus_configuration: str = Field(
        description="CAN bitrate, Ethernet speed, LIN schedule, or N/A if not applicable"
    )
    measurement_tools: str = Field(
        description="Tools used for measurement: oscilloscope, CANoe logger, dSPACE recorder"
    )


class TestCase(BaseModel):
    tc_id: str = Field(description="Test case ID e.g. TC-SWE5-001")
    requirement: str = Field(description="SRS requirement ID or ASPICE process area this test covers")
    objective: str = Field(description="What this test case verifies")
    environment: Literal["SIL", "HIL", "SIL+HIL"]
    fault_injected: str = Field(description="Specific fault injected or N/A for normal path tests")
    pass_criteria: str = Field(
        description="Exact numerical pass criterion — no subjective language like 'works correctly'"
    )
    asil_note: str = Field(
        description="Safety mechanism verified by this test, or N/A for QM tests"
    )


class FaultInjection(BaseModel):
    fault_type: str = Field(description="Type: voltage drop / CAN bus-off / sensor open / temperature ramp")
    parameters: str = Field(
        description="Exact fault parameters: voltage level, duration, ramp rate, affected signal"
    )
    expected_dtc: str = Field(description="Expected DTC code set by ECU, or N/A")
    timing: str = Field(description="When to inject relative to test start: e.g. at T+5s after CAN communication established")


class AspiceEvidence(BaseModel):
    process_area: Literal["SWE.5", "SWE.6"]
    work_product: str = Field(description="Work product name e.g. Integration Test Specification")
    wp_id: str = Field(description="ASPICE ID e.g. 17-50")
    content: str = Field(description="What this test activity produces as evidence")


class SilHilTestPlannerOutput(BaseModel):
    model_config = {"extra": "ignore"}

    ecu_name: str
    aspice_scope: str = Field(description="SWE.5 / SWE.6 / SWE.5 + SWE.6")
    asil_level: str
    test_environment: TestEnvironment
    test_cases: list[TestCase] = Field(
        description="Test cases with explicit SIL or HIL allocation and pass criteria"
    )
    sil_scope: str = Field(
        description="What CAN be tested in SIL and why SIL is sufficient for those cases"
    )
    hil_only_scope: str = Field(
        description="What CANNOT be tested in SIL and why target hardware is required"
    )
    fault_injections: list[FaultInjection] = Field(
        description="Fault injection test specifications with exact parameters"
    )
    regression_strategy: str = Field(
        description=(
            "Impact-based selection criteria for regression — not 'run everything'. "
            "Which tests run after which code change type."
        )
    )
    aspice_evidence: list[AspiceEvidence] = Field(
        description="ASPICE SWE.5/6 work products produced by this test activity"
    )
    self_evaluation: list[SelfEvaluationLine] = Field(
        description="PASS/FAIL for SIL/HIL separation, pass criteria specificity, fault parameters"
    )
