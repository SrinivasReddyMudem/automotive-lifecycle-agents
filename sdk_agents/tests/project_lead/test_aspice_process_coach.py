"""
Unit tests for aspice_process_coach — no API calls required.
Tests: schema structure, validator logic, skill loader, agent instantiation.
All API calls are mocked — runs without a GROQ_API_KEY.
"""

import pytest
from unittest.mock import patch, MagicMock
from sdk_agents.project_lead.aspice_process_coach.schema import (
    AspiceProcessCoachOutput, WorkProductStatus, BpStatus,
    ProcessAreaGap, Pa22Check, InputAnalysis, DataSufficiency,
)
from sdk_agents.project_lead.aspice_process_coach import AspiceProcessCoachAgent
from sdk_agents.project_lead.aspice_process_coach import validators
from sdk_agents.core.base_agent import AgentError, DomainCheckError
from sdk_agents.core.skill_loader import load_skill
from sdk_agents.core.shared_schema import SelfEvaluationLine


# ── Fixtures ──────────────────────────────────────────────────────────────────

def make_valid_output(**overrides) -> AspiceProcessCoachOutput:
    """Build a valid AspiceProcessCoachOutput for testing.
    Scenario: EPS ECU project, Level 2 target, 6 weeks to assessment.
    SWE.1 BP4 traceability missing, PA 2.2 gap on SRS review approval.
    """
    data = {
        "project_context": "EPS ECU SW project — ASPICE Level 2 assessment scope: SWE.1–SWE.5, SUP.8, SUP.10",
        "input_analysis": InputAnalysis(
            input_facts=[
                "Project: EPS ECU SW",
                "Target capability level: Level 2",
                "Weeks to assessment: 6",
                "SWE.1: SRS exists but traceability table to system requirements missing",
                "SWE.4: unit test specification present but no TC-to-requirement mapping",
                "SUP.8: documents tracked in SharePoint — not a CM tool",
            ],
            assumptions=[
                "Assumed SWE.2–SWE.3 work products exist based on typical Level 2 state — not explicitly stated",
                "Assumed assessment covers SWE.1–SWE.5, SUP.8, SUP.10 — scope not fully confirmed",
            ],
        ),
        "data_sufficiency": DataSufficiency(
            level="PARTIAL",
            confidence="MEDIUM",
            confidence_reason=(
                "Process areas and key gaps are described but full work product status "
                "table and CM tool setup status are not provided"
            ),
            missing_critical_data=[
                "[CRITICAL] Complete work product status per process area — needed to calculate realistic effort estimate",
                "[CRITICAL] CM tool name and setup status — needed to confirm SUP.8 BP1 gap severity",
                "[OPTIONAL] Review records for SWE.1 SRS — would confirm PA 2.2 gap scope",
            ],
        ),
        "target_level": "Level 2",
        "weeks_to_assessment": "6",
        "overall_readiness": "AMBER",
        "process_area_gaps": [
            ProcessAreaGap(
                process_area="SWE.1",
                work_products=[
                    WorkProductStatus(
                        name="Software Requirements Specification",
                        wp_id="17-08",
                        status="Document exists and is approved but traceability table to system requirements is missing",
                        rag="AMBER",
                        bp_at_risk="BP4",
                        finding_type="Major",
                    ),
                ],
                bp_statuses=[
                    BpStatus(
                        bp_id="BP4",
                        status="NOT_SATISFIED",
                        evidence_gap="No bidirectional traceability table linking SRS IDs to system requirement IDs",
                    ),
                ],
                top_risk="BP4 — traceability table missing — assessor will ask to show the link from SRS to system req",
                recommended_action=(
                    "Create bidirectional traceability matrix in DOORS: "
                    "each SRS requirement must reference the system requirement ID it implements. "
                    "Matrix must be reviewed, approved, and placed in CM baseline."
                ),
            ),
        ],
        "pa22_check": Pa22Check(
            review_record_exists="YES",
            review_record_approved="NO",
            document_in_cm_baseline="NO",
            overall_pa22_status="RED",
            gap_description=(
                "Review record exists but is not approved — reviewer signed the document, "
                "not the review record itself. Document is not in CM baseline after approval."
            ),
        ),
        "top_3_risks": (
            "Risk 1 [MAJOR]: SWE.1 BP4 — traceability table missing — assessor will challenge link from SRS to system req. "
            "Risk 2 [MAJOR]: PA 2.2 — review record not approved + no CM baseline — applies to all SWE.1 work products. "
            "Risk 3 [MAJOR]: SUP.8 BP1 — SharePoint is not a CM tool — all CI identification evidence at risk."
        ),
        "immediate_actions": (
            "Day 1: Create traceability matrix template in DOORS with System Req ID and SRS ID columns. "
            "Day 2–3: Populate all SRS IDs against system requirements. "
            "Day 4: Review matrix with system engineer. "
            "Day 5: Approve review record and CM baseline under CM-2025-001."
        ),
        "short_term_actions": (
            "Week 2: Configure CM tool (PVCS or Dimensions) for all SWE.1 work products. "
            "Week 2: Retroactively approve existing review records and baseline all approved documents. "
            "Week 3: Address SWE.4 TC-to-requirement mapping gap."
        ),
        "finding_response_template": (
            "Action taken: Traceability matrix created in DOORS linking all 47 SRS requirements to system requirements. "
            "Evidence produced: Traceability_Matrix_v1.0.pdf approved by SW Architect on 2025-01-15, baselined as CM-2025-001. "
            "Root cause fixed: SRS template updated with System Req ID column; SWE.1 procedure requires traceability before approval."
        ),
        "self_evaluation": [
            SelfEvaluationLine(
                item="gap_analysis",
                result="PASS",
                evidence="SWE.1 BP4 gap identified with specific evidence: traceability table missing",
            ),
            SelfEvaluationLine(
                item="pa22_check",
                result="PASS",
                evidence="All 3 PA 2.2 conditions checked: review record exists=YES, approved=NO, CM baseline=NO",
            ),
            SelfEvaluationLine(
                item="action_plan",
                result="PASS",
                evidence="Day-by-day immediate actions with specific DOORS steps and CM baseline target",
            ),
        ],
    }
    data.update(overrides)
    return AspiceProcessCoachOutput(**data)


# ── Schema structure tests ─────────────────────────────────────────────────────

class TestSchemaStructure:
    def test_valid_output_builds(self):
        output = make_valid_output()
        assert output.target_level == "Level 2"

    def test_input_analysis_fields_present(self):
        output = make_valid_output()
        assert len(output.input_analysis.input_facts) >= 1
        assert len(output.input_analysis.assumptions) >= 1

    def test_data_sufficiency_fields_present(self):
        output = make_valid_output()
        assert output.data_sufficiency.level in ("SUFFICIENT", "PARTIAL", "INSUFFICIENT")
        assert output.data_sufficiency.confidence in ("HIGH", "MEDIUM", "LOW")
        assert isinstance(output.data_sufficiency.missing_critical_data, list)

    def test_data_sufficiency_partial_has_missing_items(self):
        output = make_valid_output()
        assert output.data_sufficiency.level == "PARTIAL"
        assert len(output.data_sufficiency.missing_critical_data) > 0

    def test_data_sufficiency_sufficient_has_no_missing(self):
        output = make_valid_output(
            data_sufficiency=DataSufficiency(
                level="SUFFICIENT",
                confidence="HIGH",
                confidence_reason="All process areas, work product status, and timeline provided",
                missing_critical_data=["None — data is complete"],
            )
        )
        assert output.data_sufficiency.level == "SUFFICIENT"

    def test_input_facts_do_not_contain_assumptions(self):
        output = make_valid_output()
        for fact in output.input_analysis.input_facts:
            assert "assumed" not in fact.lower(), (
                f"input_facts should not contain assumptions: '{fact}'"
            )

    def test_overall_readiness_must_be_valid(self):
        with pytest.raises(Exception):
            make_valid_output(overall_readiness="YELLOW")

    def test_pa22_status_must_be_valid(self):
        with pytest.raises(Exception):
            Pa22Check(
                review_record_exists="YES",
                review_record_approved="NO",
                document_in_cm_baseline="NO",
                overall_pa22_status="ORANGE",  # invalid
                gap_description="Review record not approved",
            )

    def test_schema_extra_is_ignore(self):
        output = AspiceProcessCoachOutput.model_validate(
            {**make_valid_output().model_dump(), "extra_field": "x"}
        )
        assert output.target_level == "Level 2"


# ── Validator tests ────────────────────────────────────────────────────────────

class TestValidators:
    def test_valid_output_passes(self):
        validators.validate(make_valid_output())

    def test_amber_wp_without_bp_fails(self):
        gap = ProcessAreaGap(
            process_area="SWE.1",
            work_products=[
                WorkProductStatus(
                    name="SRS",
                    wp_id="17-08",
                    status="exists but incomplete",
                    rag="AMBER",
                    bp_at_risk="",  # empty — must reference BP
                    finding_type="Minor",
                ),
            ],
            bp_statuses=[],
            top_risk="SWE.1 risk",
            recommended_action="Complete the SRS content",
        )
        output = make_valid_output(process_area_gaps=[gap])
        with pytest.raises(DomainCheckError, match="bp_at_risk is empty"):
            validators.validate(output)

    def test_pa22_gap_description_too_short_fails(self):
        pa22 = Pa22Check(
            review_record_exists="NO",
            review_record_approved="NO",
            document_in_cm_baseline="NO",
            overall_pa22_status="RED",
            gap_description="missing",  # too short
        )
        output = make_valid_output(pa22_check=pa22)
        with pytest.raises(DomainCheckError, match="gap_description is too short"):
            validators.validate(output)

    def test_top_3_risks_must_reference_bp(self):
        output = make_valid_output(
            top_3_risks="Review records missing and CM not configured and traceability incomplete"
        )
        with pytest.raises(DomainCheckError, match="does not reference any BP numbers"):
            validators.validate(output)

    def test_top_3_risks_too_short_fails(self):
        output = make_valid_output(top_3_risks="SWE.1 BP4 gap")  # too short
        with pytest.raises(DomainCheckError, match="top_3_risks is too short"):
            validators.validate(output)

    def test_immediate_actions_too_short_fails(self):
        output = make_valid_output(immediate_actions="Create traceability")  # too short
        with pytest.raises(DomainCheckError, match="immediate_actions is too short"):
            validators.validate(output)

    def test_self_eval_pass_without_evidence_fails(self):
        output = make_valid_output(self_evaluation=[
            SelfEvaluationLine(item="gap_analysis", result="PASS", evidence="ok"),
        ])
        with pytest.raises(DomainCheckError, match="evidence is empty or too short"):
            validators.validate(output)

    def test_green_wp_skips_bp_check(self):
        """GREEN work products do not need a bp_at_risk reference."""
        gap = ProcessAreaGap(
            process_area="SWE.2",
            work_products=[
                WorkProductStatus(
                    name="Software Architecture Document",
                    wp_id="17-01",
                    status="present, approved, baselined",
                    rag="GREEN",
                    bp_at_risk="None",
                    finding_type="None",
                ),
            ],
            bp_statuses=[],
            top_risk="No risk — all work products GREEN",
            recommended_action="Maintain current state — no action required before assessment",
        )
        output = make_valid_output(process_area_gaps=[gap])
        validators.validate(output)  # should not raise


# ── Skill loader tests ────────────────────────────────────────────────────────

class TestSkillLoader:
    def test_aspice_process_skill_loads(self):
        content = load_skill("aspice-process")
        assert len(content) > 100

    def test_aspice_skill_contains_swe_content(self):
        content = load_skill("aspice-process")
        assert "SWE" in content

    def test_unknown_skill_raises(self):
        with pytest.raises(FileNotFoundError, match="not found"):
            load_skill("nonexistent-skill")


# ── Agent instantiation tests (no API calls) ─────────────────────────────────

class TestAgentInstantiation:
    def test_agent_instantiates(self):
        with patch("sdk_agents.core.base_agent.Groq"), \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            agent = AspiceProcessCoachAgent()
            assert agent.AGENT_NAME == "aspice-process-coach"

    def test_get_schema_returns_correct_type(self):
        with patch("sdk_agents.core.base_agent.Groq"), \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            agent = AspiceProcessCoachAgent()
            assert agent.get_schema() is AspiceProcessCoachOutput

    def test_get_prompt_returns_string_with_aspice_content(self):
        with patch("sdk_agents.core.base_agent.Groq"), \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            agent = AspiceProcessCoachAgent()
            prompt = agent.get_prompt()
            assert isinstance(prompt, str)
            assert "SWE" in prompt
            assert "PA 2.2" in prompt

    def test_prompt_contains_pa22_guidance(self):
        with patch("sdk_agents.core.base_agent.Groq"), \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            agent = AspiceProcessCoachAgent()
            prompt = agent.get_prompt()
            assert "PA 2.2" in prompt

    def test_api_error_returns_agent_error(self):
        with patch("sdk_agents.core.base_agent.Groq") as mock_groq_cls, \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            mock_client = MagicMock()
            mock_groq_cls.return_value = mock_client
            mock_client.chat.completions.create.side_effect = Exception("API connection failed")
            agent = AspiceProcessCoachAgent()
            result = agent.run("EPS ECU, Level 2 target, 6 weeks to assessment")
            assert isinstance(result, AgentError)
            assert result.error_type == "api_error"

    def test_missing_api_key_raises(self):
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(EnvironmentError, match="GROQ_API_KEY not set"):
                AspiceProcessCoachAgent()
