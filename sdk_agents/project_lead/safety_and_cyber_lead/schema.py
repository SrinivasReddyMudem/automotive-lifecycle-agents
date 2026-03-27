"""
Output schema for safety_and_cyber_lead.
Covers HARA (ISO 26262), TARA (ISO 21434), ASIL assignment, CAL, co-engineering.
"""

from pydantic import BaseModel, Field
from typing import Literal
from sdk_agents.core.shared_schema import SelfEvaluationLine


class HazardousEvent(BaseModel):
    he_id: str = Field(description="Hazardous event ID e.g. HE-01")
    malfunctioning_behavior: str = Field(description="What the item does wrong")
    operational_situation: str = Field(description="OS-ID and description when this occurs")
    severity: Literal["S0", "S1", "S2", "S3"]
    exposure: Literal["E0", "E1", "E2", "E3", "E4"]
    controllability: Literal["C0", "C1", "C2", "C3"]
    asil: str = Field(description="ASIL result: QM / ASIL-A / ASIL-B / ASIL-C / ASIL-D")


class SafetyGoal(BaseModel):
    sg_id: str = Field(description="Safety goal ID e.g. SG-01")
    goal_statement: str = Field(description="Technology-independent safety goal statement")
    asil: str = Field(description="ASIL assigned to this safety goal")
    safe_state: str = Field(description="Defined safe state when goal is violated")
    ftti: str = Field(description="Fault tolerant time interval or N/A if not yet defined")


class ThreatScenario(BaseModel):
    ts_id: str = Field(description="Threat scenario ID e.g. TS-01")
    actor: str = Field(description="Threat actor: remote attacker / insider / physical access")
    attack_vector: str = Field(description="Attack vector: OTA / CAN injection / physical port")
    scenario: str = Field(description="One-sentence attack scenario description")
    target_asset: str = Field(description="Asset being attacked")


class AttackFeasibility(BaseModel):
    ts_id: str
    time_factor: int = Field(description="Time required factor 0-4 (0=<1 day, 4=>6 months)")
    expertise_factor: int = Field(description="Expertise required 0-4 (0=layman, 4=multiple experts)")
    knowledge_factor: int = Field(description="Knowledge of item 0-4 (0=public, 4=restricted)")
    opportunity_factor: int = Field(description="Window of opportunity 0-4 (0=easy, 4=very limited)")
    equipment_factor: int = Field(description="Equipment required 0-4 (0=standard, 4=bespoke)")
    total: int = Field(description="Sum of all factors")
    feasibility: Literal["Low", "Medium", "High", "Very High"]


class CybersecurityGoal(BaseModel):
    cg_id: str = Field(description="Cybersecurity goal ID e.g. CG-01")
    goal_statement: str = Field(description="Technology-independent cybersecurity goal")
    cal: Literal["CAL-1", "CAL-2", "CAL-3", "CAL-4"]
    control: str = Field(description="Primary security control to achieve this goal")


class SafetyAndCyberLeadOutput(BaseModel):
    model_config = {"extra": "ignore"}

    item_name: str = Field(description="Item name being analysed e.g. Electric Power Steering ECU")
    analysis_type: Literal["HARA", "TARA", "HARA+TARA"]
    item_definition: str = Field(
        description="Item boundary: inputs, functions, outputs, exclusions"
    )
    # HARA outputs
    hazardous_events: list[HazardousEvent] = Field(
        description="Hazardous events table — empty list if TARA only"
    )
    sec_justifications: str = Field(
        description=(
            "Written S/E/C justifications — one sentence per rating explaining why. "
            "N/A if TARA only."
        )
    )
    safety_goals: list[SafetyGoal] = Field(
        description="Safety goals derived from hazardous events — empty list if TARA only"
    )
    hw_metrics_note: str = Field(
        description=(
            "Hardware metric targets for ASIL-C/D: SPFM ≥ 90% ASIL-C / 99% ASIL-D, "
            "LFM ≥ 60% ASIL-C / 90% ASIL-D, PMHF < 10^-7 h^-1 ASIL-C / 10^-8 ASIL-D. "
            "N/A for QM/ASIL-A/ASIL-B."
        )
    )
    # TARA outputs
    threat_scenarios: list[ThreatScenario] = Field(
        description="Threat scenarios — empty list if HARA only"
    )
    attack_feasibility: list[AttackFeasibility] = Field(
        description="5-factor feasibility assessment per threat scenario — empty list if HARA only"
    )
    cybersecurity_goals: list[CybersecurityGoal] = Field(
        description="Cybersecurity goals with CAL — empty list if HARA only"
    )
    co_engineering_interface: str = Field(
        description=(
            "Safety and cybersecurity interaction: shared safe states, OTA update impact on ASIL, "
            "secure boot requirements from safety, or N/A if no interaction."
        )
    )
    mandatory_review_note: str = Field(
        description=(
            "Mandatory note: This analysis requires review and approval by a qualified engineer "
            "before use in any project."
        )
    )
    self_evaluation: list[SelfEvaluationLine] = Field(
        description="PASS/FAIL for HARA completeness, S/E/C justifications, TARA feasibility scores"
    )
