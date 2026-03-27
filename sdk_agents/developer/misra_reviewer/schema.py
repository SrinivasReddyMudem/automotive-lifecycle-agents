"""
Output schema for misra_reviewer.
Covers MISRA C:2012 violation analysis, deviation justification, root cause clusters.
"""

from pydantic import BaseModel, Field
from typing import Literal
from sdk_agents.core.shared_schema import SelfEvaluationLine


class MisraViolation(BaseModel):
    rule: str = Field(description="MISRA C:2012 rule number e.g. Rule 11.3")
    title: str = Field(description="Rule title from MISRA C:2012 document")
    category: Literal["Mandatory", "Required", "Advisory"]
    asil_relevance: Literal["High", "Medium", "Low"]
    violation_pattern: str = Field(
        description="Synthetic C code showing the violation with comment marking the problem line"
    )
    explanation: str = Field(
        description="Precise technical explanation of why this violates the rule"
    )
    compliant_rewrite: str = Field(
        description="The compliant C code rewrite with comment per change"
    )
    deviation_possible: Literal["YES", "NO"]
    deviation_justification: str = Field(
        description="Deviation justification text if possible, or 'N/A — Mandatory rule, no deviation permitted'"
    )


class RootCauseCluster(BaseModel):
    cluster_name: str = Field(description="Descriptive name e.g. Type discipline violations")
    rule_numbers: str = Field(description="Comma-separated rule numbers in this cluster e.g. Rule 10.1, Rule 10.3")
    violation_count: int
    root_cause: str = Field(description="Single underlying cause: habit, training gap, toolchain issue")
    fix_approach: str = Field(description="How to fix the root cause — not just the symptom")


class ActionPlanRow(BaseModel):
    priority: Literal["P1 Mandatory", "P2 Required Safety", "P3 Required", "P4 Advisory"]
    action: str
    effort_days: str = Field(description="Estimated effort in person-days e.g. 2–3 days")
    owner: str = Field(description="Role responsible e.g. Module owner / SW lead")


class MisraReviewerOutput(BaseModel):
    model_config = {"extra": "ignore"}

    file_context: str = Field(description="File or module being reviewed, or 'synthetic pattern analysis'")
    asil_level: str = Field(description="ASIL level of the module: QM / ASIL-A / ASIL-B / ASIL-C / ASIL-D")
    tool: str = Field(description="Static analysis tool: Polyspace / QAC / PC-lint / Coverity / N/A")
    total_violations: int
    mandatory_count: int
    required_count: int
    advisory_count: int
    violations: list[MisraViolation] = Field(
        description="All violations analysed — each with violation pattern, explanation, and compliant rewrite"
    )
    root_cause_clusters: list[RootCauseCluster] = Field(
        description="Group violations by common root cause — never analyse violations in isolation"
    )
    action_plan: list[ActionPlanRow] = Field(
        description="Prioritised action plan: one row per cluster, with effort and owner"
    )
    asil_note: str = Field(
        description="What this ASIL level requires for this violation set — specific, not generic"
    )
    self_evaluation: list[SelfEvaluationLine] = Field(
        description="PASS/FAIL check for report header, rewrites, clusters, action plan with evidence"
    )
