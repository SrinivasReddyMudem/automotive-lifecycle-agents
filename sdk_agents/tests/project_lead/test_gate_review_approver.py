"""
Unit tests for gate_review_approver — no API calls required.
Tests: schema structure, validator logic, skill loader, agent instantiation.
All API calls are mocked — runs without a GROQ_API_KEY.
"""

import pytest
from unittest.mock import patch, MagicMock
from sdk_agents.project_lead.gate_review_approver.schema import (
    GateReviewApproverOutput, GateCriterion, OpenFinding,
)
from sdk_agents.project_lead.gate_review_approver import GateReviewApproverAgent
from sdk_agents.project_lead.gate_review_approver import validators
from sdk_agents.core.base_agent import AgentError, DomainCheckError
from sdk_agents.core.skill_loader import load_skill
from sdk_agents.core.shared_schema import SelfEvaluationLine, InputAnalysis, DataSufficiency


# ── Fixtures ──────────────────────────────────────────────────────────────────

def _make_criteria(count: int = 6, status: str = "PASS") -> list[GateCriterion]:
    return [
        GateCriterion(
            criterion=f"Gate criterion {i + 1}",
            status=status,
            evidence=f"Work product {i + 1} approved and baselined",
            finding="None",
        )
        for i in range(count)
    ]


def make_valid_output(**overrides) -> GateReviewApproverOutput:
    """Build a valid GateReviewApproverOutput for testing.
    Scenario: SOP gate review for EPS ECU project — all PASS.
    """
    data = {
        "gate_type": "SOP",
        "input_analysis": InputAnalysis(
            input_facts=[
                "gate type: SOP",
                "project/ECU: EPS_ECU programme, Electric Power Steering",
                "assessment date: 2026-04-10",
                "SW requirements: SRS approved and baselined",
                "integration test: completed and results reviewed",
            ],
            assumptions=[
                "assumed 6 standard SOP gate criteria from programme release procedure",
                "assumed safety sign-off from safety manager — not explicitly stated",
            ],
        ),
        "data_sufficiency": DataSufficiency(
            level="PARTIAL",
            confidence="MEDIUM",
            confidence_reason="Gate type and project stated but individual criterion evidence not fully detailed.",
            missing_critical_data=[
                "[CRITICAL] work product status per criterion — required to assign PASS/AMBER/FAIL to each",
                "[OPTIONAL] safety manager sign-off date — would confirm safety criterion status",
            ],
        ),
        "project_ecu": "EPS_ECU",
        "assessment_date": "2026-04-10",
        "criteria_assessment": _make_criteria(6, "PASS"),
        "overall": "PASS",
        "score": "6/6 criteria met — 6 PASS / 0 AMBER / 0 FAIL",
        "open_findings": [],
        "mandatory_closing_note": (
            "This assessment is a structured checklist output. "
            "Final release decision requires sign-off by SW Project Lead, Quality Manager, "
            "and Functional Safety Manager per project release procedure. "
            "This tool does not constitute a formal release approval."
        ),
        "self_evaluation": [
            SelfEvaluationLine(
                item="Criteria count",
                result="PASS",
                evidence="6 criteria assessed for SOP gate — matches SOP_CRITERIA_COUNT",
            ),
            SelfEvaluationLine(
                item="Closing note present",
                result="PASS",
                evidence="mandatory_closing_note references formal release approval and sign-off",
            ),
        ],
    }
    data.update(overrides)
    return GateReviewApproverOutput(**data)


# ── Schema tests ──────────────────────────────────────────────────────────────

class TestSchemaStructure:
    def test_valid_output_instantiates(self):
        output = make_valid_output()
        assert output.gate_type == "SOP"

    def test_gate_type_must_be_valid(self):
        with pytest.raises(Exception):
            make_valid_output(gate_type="DESIGN_FREEZE")  # invalid — only SOR or SOP

    def test_criterion_status_must_be_valid(self):
        with pytest.raises(Exception):
            GateCriterion(
                criterion="SW requirements freeze",
                status="UNCLEAR",  # invalid — must be PASS/AMBER/FAIL
                evidence="some evidence",
                finding="None",
            )

    def test_overall_must_be_valid(self):
        with pytest.raises(Exception):
            make_valid_output(overall="PARTIAL")  # invalid — must be PASS/AMBER/FAIL

    def test_open_finding_risk_must_be_valid(self):
        with pytest.raises(Exception):
            OpenFinding(
                finding="ASPICE work product missing",
                risk="CRITICAL",  # invalid — must be HIGH/MEDIUM/LOW
                required_action="Create and approve work product",
            )

    def test_schema_has_required_fields(self):
        schema = GateReviewApproverOutput.model_json_schema()
        required = schema.get("required", [])
        for field in [
            "gate_type", "project_ecu", "criteria_assessment", "overall",
            "score", "open_findings", "mandatory_closing_note", "self_evaluation",
        ]:
            assert field in required, f"'{field}' missing from schema required list"

    def test_schema_extra_is_ignore(self):
        output = GateReviewApproverOutput.model_validate(
            {**make_valid_output().model_dump(), "extra_field": "x"}
        )
        assert output.gate_type == "SOP"

    def test_input_analysis_present(self):
        output = make_valid_output()
        assert output.input_analysis is not None
        assert len(output.input_analysis.input_facts) > 0

    def test_input_analysis_has_gate_type_fact(self):
        output = make_valid_output()
        assert any("SOP" in f for f in output.input_analysis.input_facts)

    def test_data_sufficiency_level_is_valid(self):
        output = make_valid_output()
        assert output.data_sufficiency.level in ("SUFFICIENT", "PARTIAL", "INSUFFICIENT")

    def test_data_sufficiency_partial_has_missing_items(self):
        output = make_valid_output()
        assert output.data_sufficiency.level == "PARTIAL"
        assert len(output.data_sufficiency.missing_critical_data) > 0

    def test_data_sufficiency_sufficient_has_empty_missing(self):
        output = make_valid_output(
            data_sufficiency=DataSufficiency(
                level="SUFFICIENT",
                confidence="HIGH",
                confidence_reason="All criteria evidence, gate type, and project name present.",
                missing_critical_data=["None — data is complete"],
            )
        )
        assert output.data_sufficiency.level == "SUFFICIENT"
        assert output.data_sufficiency.missing_critical_data == ["None — data is complete"]


# ── Validator tests ───────────────────────────────────────────────────────────

class TestValidators:
    def test_valid_output_passes(self):
        validators.validate(make_valid_output())

    def test_too_few_criteria_fails(self):
        output = make_valid_output(criteria_assessment=_make_criteria(4, "PASS"))
        with pytest.raises(DomainCheckError, match="requires 6 criteria"):
            validators.validate(output)

    def test_closing_note_missing_keywords_fails(self):
        output = make_valid_output(mandatory_closing_note="This is a review summary.")
        with pytest.raises(DomainCheckError, match="mandatory_closing_note is missing required content"):
            validators.validate(output)

    def test_fail_criterion_with_pass_overall_fails(self):
        criteria = _make_criteria(5, "PASS") + [
            GateCriterion(
                criterion="Safety sign-off",
                status="FAIL",
                evidence="Safety manager review not completed",
                finding="Safety Manager review record missing",
            )
        ]
        output = make_valid_output(
            criteria_assessment=criteria,
            overall="PASS",  # wrong — should be FAIL
            open_findings=[
                OpenFinding(
                    finding="Safety Manager review record missing",
                    risk="HIGH",
                    required_action="Complete safety review before SOP",
                )
            ],
        )
        with pytest.raises(DomainCheckError, match="must be FAIL when any criterion is FAIL"):
            validators.validate(output)

    def test_amber_criterion_with_pass_overall_fails(self):
        criteria = _make_criteria(5, "PASS") + [
            GateCriterion(
                criterion="ASPICE work products",
                status="AMBER",
                evidence="SRS present but not baselined",
                finding="SRS not in CM baseline",
            )
        ]
        output = make_valid_output(
            criteria_assessment=criteria,
            overall="PASS",  # wrong — should be AMBER
            open_findings=[
                OpenFinding(
                    finding="SRS not in CM baseline",
                    risk="MEDIUM",
                    required_action="Baseline SRS in CM tool before SOP",
                )
            ],
        )
        with pytest.raises(DomainCheckError, match="must be AMBER"):
            validators.validate(output)

    def test_amber_criterion_without_open_finding_fails(self):
        criteria = _make_criteria(5, "PASS") + [
            GateCriterion(
                criterion="ASPICE work products",
                status="AMBER",
                evidence="SRS present but not baselined",
                finding="SRS not in CM baseline",
            )
        ]
        output = make_valid_output(
            criteria_assessment=criteria,
            overall="AMBER",
            open_findings=[],  # should have at least one finding
        )
        with pytest.raises(DomainCheckError, match="open_findings is empty"):
            validators.validate(output)

    def test_self_eval_pass_without_evidence_fails(self):
        output = make_valid_output(self_evaluation=[
            SelfEvaluationLine(item="Criteria count", result="PASS", evidence="ok")
        ])
        with pytest.raises(DomainCheckError, match="evidence is empty or too short"):
            validators.validate(output)

    def test_sor_gate_type_accepted(self):
        output = make_valid_output(gate_type="SOR")
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
            agent = GateReviewApproverAgent()
            assert agent.AGENT_NAME == "gate-review-approver"

    def test_get_schema_returns_correct_type(self):
        with patch("sdk_agents.core.base_agent.Groq"), \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            agent = GateReviewApproverAgent()
            assert agent.get_schema() is GateReviewApproverOutput

    def test_get_prompt_returns_string_with_gate_content(self):
        with patch("sdk_agents.core.base_agent.Groq"), \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            agent = GateReviewApproverAgent()
            prompt = agent.get_prompt()
            assert isinstance(prompt, str)
            assert "SOR" in prompt or "SOP" in prompt

    def test_api_error_returns_agent_error(self):
        with patch("sdk_agents.core.base_agent.Groq") as mock_groq_cls, \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            mock_client = MagicMock()
            mock_groq_cls.return_value = mock_client
            mock_client.chat.completions.create.side_effect = Exception("API connection failed")
            agent = GateReviewApproverAgent()
            result = agent.run("SOP gate review for EPS ECU")
            assert isinstance(result, AgentError)
            assert result.error_type == "api_error"

    def test_missing_api_key_raises(self):
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(EnvironmentError, match="GROQ_API_KEY not set"):
                GateReviewApproverAgent()
