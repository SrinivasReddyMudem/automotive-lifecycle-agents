"""
Output schema for sw_project_lead.
Covers change request analysis, risk register entries, project status.
"""

from pydantic import BaseModel, Field
from typing import Literal
from sdk_agents.core.shared_schema import SelfEvaluationLine


class ImpactItem(BaseModel):
    dimension: Literal["Schedule", "Safety", "ASPICE", "Cost", "Test", "Risk", "Cybersecurity"]
    delta: str = Field(description="Quantified delta e.g. +8 working days / +3 person-days NRE")
    critical_path_affected: Literal["YES", "NO", "N/A"]
    detail: str = Field(description="Specific milestone or work product affected")


class ChangeRequestOption(BaseModel):
    option: str = Field(description="Option label e.g. Option A — Accept into this release")
    condition: str = Field(description="Precondition for this option to be viable")
    cost_person_days: str = Field(description="Effort cost in person-days")
    schedule_consequence: str = Field(description="Milestone delta or impact on schedule")
    risk_of_this_option: str = Field(description="Risk introduced by choosing this option")


class RiskEntry(BaseModel):
    risk_statement: str = Field(description="One sentence: 'Risk that X causes Y'")
    category: Literal["Schedule", "Safety", "Technical", "Supplier", "Process", "Cybersecurity"]
    probability: int = Field(description="Probability score 1–5")
    impact: int = Field(description="Impact score 1–5")
    risk_score: int = Field(description="Probability x Impact")
    level: Literal["LOW", "MEDIUM", "HIGH"]
    mitigation: str = Field(description="Specific mitigation action with owner")
    residual_risk: str = Field(description="Risk level after mitigation")


class SwProjectLeadOutput(BaseModel):
    model_config = {"extra": "ignore"}

    request_type: Literal["CHANGE_REQUEST", "RISK_REGISTER", "STATUS_REPORT", "CUSTOMER_RESPONSE", "GENERAL"]
    summary: str = Field(
        description="One-paragraph executive summary of the situation and recommendation"
    )
    impact_assessment: list[ImpactItem] = Field(
        description="Quantified impact per dimension — Schedule in working days, Cost in person-days"
    )
    change_request_options: list[ChangeRequestOption] = Field(
        description="Options for CR: Accept / Defer / Reject — each with condition, cost, and risk"
    )
    risks: list[RiskEntry] = Field(
        description="Risk register entries with P x I score and mitigation"
    )
    recommendation: str = Field(
        description="Specific recommendation with one-sentence justification"
    )
    decision_required_by: str = Field(
        description="Date by which decision is needed to protect schedule, or N/A"
    )
    immediate_actions: str = Field(description="Actions this week — named owner per action")
    short_term_actions: str = Field(description="Actions this sprint/2 weeks")
    long_term_actions: str = Field(description="Actions this milestone")
    aspice_reference: str = Field(
        description="ASPICE process area and work product affected e.g. SWE.1 — SRS (17-08)"
    )
    self_evaluation: list[SelfEvaluationLine] = Field(
        description="PASS/FAIL for quantified impacts, risk scores, recommendation with evidence"
    )
