"""
Output schema for regression_analyst.
Covers test delta analysis, failure clustering, coverage drops, HOLD/PROCEED decision.
"""

from pydantic import BaseModel, Field
from typing import Literal
from sdk_agents.core.shared_schema import SelfEvaluationLine


class RegressionSummary(BaseModel):
    previous_pass: int
    previous_fail: int
    previous_coverage_pct: str = Field(description="Coverage percentage e.g. 87.3% or UNKNOWN")
    current_pass: int
    current_fail: int
    current_coverage_pct: str
    new_failures: int = Field(description="Net new failures (not previously failing)")
    asil_d_affected: int = Field(description="New failures in ASIL-D tests")
    asil_b_affected: int = Field(description="New failures in ASIL-B tests")
    qm_affected: int = Field(description="New failures in QM tests")


class FailureCluster(BaseModel):
    cluster_name: str = Field(description="Descriptive name e.g. CAN driver API failures")
    failure_count: int
    risk_level: Literal["ASIL-D", "ASIL-B", "QM", "ENVIRONMENT"]
    probable_cause: str = Field(
        description="Most likely code change or area that caused this cluster — specific, not generic"
    )
    confirming_check: str = Field(
        description="First concrete thing to look at to confirm this probable cause"
    )


class CoverageDelta(BaseModel):
    module: str = Field(description="Module name that lost coverage")
    previous_pct: str
    current_pct: str
    delta_pct: str = Field(description="Coverage change e.g. -3.2%")
    lost_function: str = Field(description="Specific function or branch that lost coverage")
    is_blocker: Literal["YES", "NO"] = Field(
        description="YES if ASIL-D/C module and delta > 0; NO for QM modules"
    )


class RegressionAnalystOutput(BaseModel):
    model_config = {"extra": "ignore"}

    build_current: str = Field(description="Current build identifier")
    build_baseline: str = Field(description="Baseline build being compared against")
    summary: RegressionSummary
    failure_clusters: list[FailureCluster] = Field(
        description="Failures grouped by probable common cause — ranked ASIL-D first"
    )
    coverage_deltas: list[CoverageDelta] = Field(
        description="Coverage drops per module — blocker = YES for ASIL-D/C modules"
    )
    flaky_test_assessment: str = Field(
        description=(
            "Assessment of which failures may be flaky vs real regressions. "
            "State what makes them flaky: timing dependency, shared state, test order. "
            "N/A if no flaky tests identified."
        )
    )
    environment_vs_sw: str = Field(
        description=(
            "Distinguish: is this a real SW defect or a test bench/harness problem? "
            "State evidence for the conclusion."
        )
    )
    investigation_sequence: str = Field(
        description=(
            "Prioritised investigation order — ASIL-D first. "
            "Name the specific cluster, the module, and the first check for each step."
        )
    )
    aspice_impact: str = Field(
        description=(
            "ASPICE SWE.4/5 impact: do failures block a planned baseline? "
            "State which baseline and why."
        )
    )
    hold_proceed_recommendation: Literal["HOLD", "PROCEED_WITH_EXCEPTIONS", "PROCEED"]
    hold_proceed_rationale: str = Field(
        description=(
            "Specific justification for the recommendation. "
            "For HOLD: name the blocking cluster. "
            "For PROCEED_WITH_EXCEPTIONS: list exceptions and named owners. "
            "For PROCEED: state why all failures are confirmed non-blocking."
        )
    )
    self_evaluation: list[SelfEvaluationLine] = Field(
        description="PASS/FAIL for clustering, ASIL prioritisation, HOLD/PROCEED justification"
    )
