"""
Output schema for aspice_process_coach.
Covers gap analysis, work product RAG status, PA 2.2 checks, assessment readiness.
"""

from pydantic import BaseModel, Field
from typing import Literal
from sdk_agents.core.shared_schema import SelfEvaluationLine, InputAnalysis, DataSufficiency


class WorkProductStatus(BaseModel):
    name: str = Field(description="Work product name e.g. Software Requirements Specification")
    wp_id: str = Field(description="ASPICE work product ID e.g. 17-08")
    status: str = Field(description="Description of current state: exists, approved, baselined or missing")
    rag: Literal["GREEN", "AMBER", "RED"]
    bp_at_risk: str = Field(description="Base practice number at risk e.g. BP4 or None")
    finding_type: Literal["Major", "Minor", "Observation", "None"]


class BpStatus(BaseModel):
    bp_id: str = Field(description="Base practice ID e.g. BP1")
    status: Literal["SATISFIED", "PARTIAL", "NOT_SATISFIED"]
    evidence_gap: str = Field(description="What evidence is missing or N/A if satisfied")


class ProcessAreaGap(BaseModel):
    process_area: str = Field(description="Process area e.g. SWE.1 / SWE.4 / SWE.5")
    work_products: list[WorkProductStatus]
    bp_statuses: list[BpStatus]
    top_risk: str = Field(description="Highest risk finding for this process area with BP number")
    recommended_action: str = Field(
        description="Specific action required: not 'document it' but what the document must contain"
    )


class Pa22Check(BaseModel):
    review_record_exists: Literal["YES", "NO", "PARTIAL"]
    review_record_approved: Literal["YES", "NO", "PARTIAL"]
    document_in_cm_baseline: Literal["YES", "NO", "PARTIAL"]
    overall_pa22_status: Literal["GREEN", "AMBER", "RED"]
    gap_description: str = Field(description="Which of the 3 PA 2.2 conditions is missing")


class AspiceProcessCoachOutput(BaseModel):
    model_config = {"extra": "ignore"}

    project_context: str = Field(description="ECU / project name and assessment scope")
    input_analysis: InputAnalysis = Field(
        description=(
            "STEP 0 (before gap analysis): separate what the user directly stated "
            "(input_facts) from what you inferred or assumed (assumptions). "
            "Extract only explicitly provided data: project name, capability level target, "
            "assessment date, work products mentioned, process areas named, "
            "existing evidence described. "
            "Never mix assumed values into input_facts."
        )
    )
    data_sufficiency: DataSufficiency = Field(
        description=(
            "Rate data completeness for this specific assessment coaching. "
            "SUFFICIENT = process areas in scope + work product status + timeline all present. "
            "PARTIAL = process areas known but work product status or timeline missing. "
            "INSUFFICIENT = only project name with no assessment scope or work product status. "
            "missing_critical_data: ONLY list inputs that caused N/A in a field or "
            "forced an assumption that would change the RAG rating or finding type if provided."
        )
    )
    target_level: str = Field(description="Capability level target: Level 1 / Level 2 / Level 3")
    weeks_to_assessment: str = Field(description="Weeks remaining to assessment date")
    overall_readiness: Literal["GREEN", "AMBER", "RED"]
    process_area_gaps: list[ProcessAreaGap] = Field(
        description="Gap analysis per process area in scope — use RAG rating system"
    )
    pa22_check: Pa22Check = Field(
        description=(
            "PA 2.2 three-condition check: review exists + review approved + CM baseline. "
            "Missing any one of the three = PA 2.2 finding regardless of document quality."
        )
    )
    top_3_risks: str = Field(
        description="Top 3 Major finding risks with BP numbers and evidence gap description"
    )
    immediate_actions: str = Field(description="Actions needed this week — specific, not generic")
    short_term_actions: str = Field(description="Actions needed within 2 weeks")
    finding_response_template: str = Field(
        description=(
            "Template for formal finding response using 3-part format: "
            "Action taken / Evidence produced / Root cause prevented"
        )
    )
    self_evaluation: list[SelfEvaluationLine] = Field(
        description="PASS/FAIL check for gap analysis, PA 2.2 check, and action plans with evidence"
    )
