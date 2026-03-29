"""
Output schema for gate_review_approver.
Covers SOR/SOP gate criteria assessment with pass/fail/amber scoring.
Only activated via explicit /gate-review command.
"""

from pydantic import BaseModel, Field
from typing import Literal
from sdk_agents.core.shared_schema import SelfEvaluationLine, InputAnalysis, DataSufficiency


class GateCriterion(BaseModel):
    criterion: str = Field(description="Gate criterion name e.g. SW requirements freeze")
    status: Literal["PASS", "AMBER", "FAIL"]
    evidence: str = Field(description="Evidence provided or evidence gap")
    finding: str = Field(description="Finding description or 'None' if PASS")


class OpenFinding(BaseModel):
    finding: str = Field(description="Finding description")
    risk: Literal["HIGH", "MEDIUM", "LOW"]
    required_action: str = Field(description="Specific action required before release")


class GateReviewApproverOutput(BaseModel):
    model_config = {"extra": "ignore"}

    gate_type: Literal["SOR", "SOP"]
    input_analysis: InputAnalysis = Field(
        description=(
            "Structured extraction of what the user stated vs what was assumed. "
            "input_facts: gate type stated (SOR/SOP), project/ECU name stated, assessment date given, "
            "specific work products mentioned with status, ASPICE level target stated, "
            "safety/cybersecurity sign-off status stated. "
            "assumptions: gate criteria assumed from gate type, ASPICE scope assumed, "
            "work product status assumed from brief description."
        )
    )
    data_sufficiency: DataSufficiency = Field(
        description=(
            "Rate completeness for this specific gate review only. "
            "SUFFICIENT: gate type + project name + work product status per criterion all present. "
            "PARTIAL: gate type and project present but individual criterion evidence missing. "
            "INSUFFICIENT: only project name with no work product status or gate criteria evidence. "
            "missing_critical_data: only flag inputs that caused N/A, forced an assumption, "
            "or would change a criterion status (PASS/AMBER/FAIL) or the overall gate result if provided."
        )
    )
    project_ecu: str = Field(description="Project and ECU name")
    assessment_date: str = Field(description="Assessment date or 'not provided'")
    criteria_assessment: list[GateCriterion] = Field(
        description="Assessment of each gate criterion with evidence and finding"
    )
    overall: Literal["PASS", "AMBER", "FAIL"]
    score: str = Field(description="Score e.g. 3/6 criteria met — 1 PASS / 4 AMBER / 1 FAIL")
    open_findings: list[OpenFinding] = Field(
        description="All AMBER and FAIL findings with risk and required action"
    )
    mandatory_closing_note: str = Field(
        description=(
            "Mandatory note: this assessment is a structured checklist output. "
            "Final release decision requires sign-off by SW Project Lead, Quality Manager, "
            "and Functional Safety Manager per project release procedure. "
            "This tool does not constitute a formal release approval."
        )
    )
    self_evaluation: list[SelfEvaluationLine] = Field(
        description="PASS/FAIL check for criteria assessment, score, findings, closing note"
    )
