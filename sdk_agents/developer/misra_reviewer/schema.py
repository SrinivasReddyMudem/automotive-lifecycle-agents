"""
Output schema for misra_reviewer.
Covers MISRA C:2012 violation analysis, deviation justification, root cause clusters.
"""

from pydantic import BaseModel, Field
from typing import Literal
from sdk_agents.core.shared_schema import SelfEvaluationLine, InputAnalysis, DataSufficiency


class MisraViolation(BaseModel):
    rule: str = Field(description="MISRA C:2012 rule number e.g. Rule 11.3")
    violation_pattern: list[str] = Field(
        description="Synthetic C code showing the violation — one string per line, with a comment line marking the problem"
    )
    explanation: str = Field(
        description="Precise technical explanation of why this violates the rule"
    )
    compliant_rewrite: list[str] = Field(
        description="The compliant C code rewrite — one string per line, with a comment line per change"
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
    input_analysis: InputAnalysis = Field(
        description=(
            "Structured extraction of what the user stated vs what was assumed. "
            "input_facts: file or module name stated, ASIL level stated, static analysis tool named, "
            "specific rule numbers mentioned, total violation count given, C code snippet provided. "
            "assumptions: ASIL level assumed from module context, tool assumed from project type, "
            "rule category assumed (mandatory/required/advisory) when only rule number given."
        )
    )
    data_sufficiency: DataSufficiency = Field(
        description=(
            "Rate completeness for this specific MISRA review only. "
            "SUFFICIENT: C code or violation list + ASIL level + tool name all present. "
            "PARTIAL: violation descriptions present but C code, ASIL level, or tool name missing. "
            "INSUFFICIENT: only a description of a rule with no code context or violation report. "
            "missing_critical_data: only flag inputs that caused N/A, forced an assumption, "
            "or would change the violation count, root cause cluster, or action plan if provided."
        )
    )
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
