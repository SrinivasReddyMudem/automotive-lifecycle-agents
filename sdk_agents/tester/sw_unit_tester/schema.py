"""
Output schema for sw_unit_tester.
Covers ASPICE SWE.4 unit test design: equivalence partitioning, boundary values, MC/DC.
"""

from pydantic import BaseModel, Field
from typing import Literal
from sdk_agents.core.shared_schema import SelfEvaluationLine


class UnitTestCase(BaseModel):
    tc_id: str = Field(description="Test case ID e.g. TC-001")
    objective: str = Field(description="What this test case verifies — one sentence")
    precondition: str = Field(description="Initial state or setup required before test")
    input_values: str = Field(description="Exact input values with variable names and types")
    expected_result: str = Field(description="Exact expected output or return value")
    pass_criteria: str = Field(description="Explicit condition: return value == X AND output == Y")
    coverage_target: str = Field(
        description="Coverage element: statement / branch-true / branch-false / MC/DC pair A"
    )


class MCDCPair(BaseModel):
    tc_id: str = Field(description="Test case that demonstrates this independence pair")
    condition_values: str = Field(description="All condition values e.g. A=T, B=F, C=T")
    decision_result: Literal["TRUE", "FALSE"]
    independently_tests: str = Field(
        description="Which condition is independently tested e.g. Condition A (B and C held constant)"
    )


class StubRequired(BaseModel):
    stub_name: str = Field(description="Function name to stub e.g. Rte_Read_Speed_PP_SpeedValue")
    purpose: str = Field(description="Why this stub is needed")
    return_value: str = Field(description="What the stub returns in test context")


class CoverageSummary(BaseModel):
    coverage_type: Literal["Statement", "Branch", "MC/DC"]
    target_pct: str = Field(description="Required coverage % per ISO 26262-6 e.g. 100%")
    achieved_pct: str = Field(description="Coverage achieved by this test set")
    achieving_tcs: str = Field(description="Test case IDs that achieve this coverage")


class SwUnitTesterOutput(BaseModel):
    model_config = {"extra": "ignore"}

    function_signature: str = Field(
        description="Full C function signature e.g. bool BrakeControl_IsEmergencyBrakeRequired(uint8_t pedalPos, bool sensorValid)"
    )
    asil_level: str = Field(description="ASIL level: QM / ASIL-A / ASIL-B / ASIL-C / ASIL-D")
    coverage_required: str = Field(
        description="Coverage requirements per ISO 26262-6 Table 13 e.g. Statement 100% + Branch 100% + MC/DC 100% (ASIL-D)"
    )
    framework: str = Field(description="Test framework: GoogleTest / Unity / CppUTest / VectorCAST / LDRA")
    stubs_required: list[StubRequired] = Field(
        description="List of stubs needed for this function under test"
    )
    swe4_work_product: str = Field(
        description="ASPICE SWE.4 work product: Unit Test Specification [ID]"
    )
    design_traceability: str = Field(
        description="Reference to detailed design document this test traces to"
    )
    test_cases: list[UnitTestCase] = Field(
        description="Test cases covering equivalence classes, boundaries, and MC/DC pairs"
    )
    mcdc_pairs: list[MCDCPair] = Field(
        description="MC/DC independence pairs — empty list for ASIL-A/B functions"
    )
    test_code: str = Field(
        description=(
            "Actual test code in framework syntax for key test cases. "
            "Use synthetic variable names. Show SETUP, test body, assertions."
        )
    )
    coverage_summary: list[CoverageSummary] = Field(
        description="Statement, Branch, and MC/DC coverage summary with achieving TC IDs"
    )
    self_evaluation: list[SelfEvaluationLine] = Field(
        description="PASS/FAIL for coverage targets, MC/DC pairs, test code, boundary values"
    )
