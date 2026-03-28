"""
Unit tests for sw_project_lead — no API calls required.
Tests: schema structure, validator logic, skill loader, agent instantiation.
All API calls are mocked — runs without a GROQ_API_KEY.
"""

import pytest
from unittest.mock import patch, MagicMock
from sdk_agents.project_lead.sw_project_lead.schema import (
    SwProjectLeadOutput, ImpactItem, ChangeRequestOption, RiskEntry,
)
from sdk_agents.project_lead.sw_project_lead import SwProjectLeadAgent
from sdk_agents.project_lead.sw_project_lead import validators
from sdk_agents.core.base_agent import AgentError, DomainCheckError
from sdk_agents.core.skill_loader import load_skill
from sdk_agents.core.shared_schema import SelfEvaluationLine


# ── Fixtures ──────────────────────────────────────────────────────────────────

def make_valid_output(**overrides) -> SwProjectLeadOutput:
    data = {
        "request_type": "CHANGE_REQUEST",
        "summary": (
            "Customer requests addition of OTA capability at detailed design phase. "
            "3x cost multiplier applies. Recommend deferring to next release."
        ),
        "impact_assessment": [
            ImpactItem(
                dimension="Schedule",
                delta="+15 working days on integration milestone",
                critical_path_affected="YES",
                detail="SWE.5 integration test phase pushed by 3 weeks",
            ),
            ImpactItem(
                dimension="Cost",
                delta="+12 person-days NRE",
                critical_path_affected="NO",
                detail="Additional design + test effort for OTA module",
            ),
            ImpactItem(
                dimension="ASPICE",
                delta="SWE.1 SRS, SWE.2 SAD must be revised",
                critical_path_affected="NO",
                detail="New requirements must be added and reviewed",
            ),
        ],
        "change_request_options": [
            ChangeRequestOption(
                option="Option A — Accept into this release",
                condition="Customer agrees to extend milestone by 15 working days",
                cost_person_days="12 person-days",
                schedule_consequence="+15 working days to SWE.5 milestone",
                risk_of_this_option="Safety re-analysis required — HARA may need reopening for OTA",
            ),
            ChangeRequestOption(
                option="Option B — Defer to next release",
                condition="Customer accepts feature for next program",
                cost_person_days="4 person-days planning only",
                schedule_consequence="Current milestone unaffected",
                risk_of_this_option="Customer dissatisfaction — may escalate to programme management",
            ),
        ],
        "risks": [
            RiskEntry(
                risk_statement="Risk that OTA feature introduces cybersecurity gap requiring TARA reopen",
                category="Safety",
                probability=4,
                impact=4,
                risk_score=16,
                level="HIGH",
                mitigation="Engage safety/cyber lead within 5 days to scope TARA impact",
                residual_risk="MEDIUM after TARA scope confirmed",
            ),
        ],
        "recommendation": (
            "Defer OTA to next release — current milestone has zero buffer and 3x cost applies."
        ),
        "self_evaluation": [
            SelfEvaluationLine(
                item="Cost multiplier applied",
                result="PASS",
                evidence="3x multiplier stated: 4 base days × 3 = 12 days total",
            ),
            SelfEvaluationLine(
                item="Risk scored",
                result="PASS",
                evidence="P=4, I=4, score=16, HIGH band, mitigation named",
            ),
        ],
        "decision_required_by": "2026-04-05",
        "immediate_actions": "Project Lead: raise CR record with CCB by 2026-04-02",
        "short_term_actions": "Safety Lead: scope TARA impact within 5 working days",
        "aspice_reference": "SWE.1 — Software Requirements Specification (17-08); SUP.10 — Change Request (17-51)",
    }
    data.update(overrides)
    return SwProjectLeadOutput(**data)


# ── Schema tests ──────────────────────────────────────────────────────────────

class TestSchema:
    def test_valid_output_instantiates(self):
        output = make_valid_output()
        assert output.request_type == "CHANGE_REQUEST"

    def test_request_type_must_be_valid(self):
        with pytest.raises(Exception):
            make_valid_output(request_type="UNKNOWN_TYPE")

    def test_risk_entry_level_must_be_valid(self):
        with pytest.raises(Exception):
            RiskEntry(
                risk_statement="test risk",
                category="Schedule",
                probability=3,
                impact=3,
                risk_score=9,
                level="EXTREME",  # invalid — not in Literal["LOW", "MEDIUM", "HIGH"]
                mitigation="test",
                residual_risk="LOW",
            )

    def test_impact_item_dimension_must_be_valid(self):
        with pytest.raises(Exception):
            ImpactItem(
                dimension="Unknown",  # invalid
                delta="+5 working days",
                critical_path_affected="YES",
                detail="test detail",
            )

    def test_schema_has_required_fields(self):
        schema = SwProjectLeadOutput.model_json_schema()
        required = schema.get("required", [])
        for field in [
            "request_type", "summary", "impact_assessment",
            "change_request_options", "risks", "recommendation",
            "self_evaluation", "aspice_reference",
        ]:
            assert field in required, f"'{field}' missing from schema required list"

    def test_schema_extra_is_ignore(self):
        output = SwProjectLeadOutput.model_validate(
            {**make_valid_output().model_dump(), "unexpected_field": "x"}
        )
        assert output.request_type == "CHANGE_REQUEST"


# ── Validator tests ───────────────────────────────────────────────────────────

class TestValidators:
    def test_valid_output_passes(self):
        validators.validate(make_valid_output())

    def test_risk_score_mismatch_fails(self):
        risk = RiskEntry(
            risk_statement="Risk that X causes Y",
            category="Schedule",
            probability=3,
            impact=4,
            risk_score=99,  # should be 12
            level="HIGH",
            mitigation="test mitigation action",
            residual_risk="LOW",
        )
        output = make_valid_output(risks=[risk])
        with pytest.raises(DomainCheckError, match="does not match"):
            validators.validate(output)

    def test_low_score_with_high_level_fails(self):
        risk = RiskEntry(
            risk_statement="Risk that X causes Y",
            category="Schedule",
            probability=2,
            impact=2,
            risk_score=4,  # score=4, should be LOW
            level="HIGH",  # wrong band
            mitigation="test mitigation action",
            residual_risk="LOW",
        )
        output = make_valid_output(risks=[risk])
        with pytest.raises(DomainCheckError, match="should be LOW"):
            validators.validate(output)

    def test_high_score_with_low_level_fails(self):
        risk = RiskEntry(
            risk_statement="Risk that X causes Y",
            category="Technical",
            probability=5,
            impact=4,
            risk_score=20,  # score=20, should be HIGH
            level="LOW",   # wrong band
            mitigation="test mitigation action",
            residual_risk="MEDIUM",
        )
        output = make_valid_output(risks=[risk])
        with pytest.raises(DomainCheckError, match="should be HIGH"):
            validators.validate(output)

    def test_schedule_impact_without_days_fails(self):
        item = ImpactItem(
            dimension="Schedule",
            delta="some time on the schedule",  # no "day", "week", or "working" — not quantified
            critical_path_affected="YES",
            detail="milestone affected",
        )
        output = make_valid_output(impact_assessment=[item])
        with pytest.raises(DomainCheckError, match="not quantified"):
            validators.validate(output)

    def test_aspice_reference_missing_when_cr_present_fails(self):
        output = make_valid_output(aspice_reference="N/A")
        with pytest.raises(DomainCheckError, match="aspice_reference is missing"):
            validators.validate(output)

    def test_self_eval_pass_without_evidence_fails(self):
        output = make_valid_output(self_evaluation=[
            SelfEvaluationLine(item="Risk scored", result="PASS", evidence="ok")
        ])
        with pytest.raises(DomainCheckError, match="evidence is empty or too short"):
            validators.validate(output)

    def test_medium_risk_score_passes(self):
        """Score 9-15 is MEDIUM — check band boundary."""
        risk = RiskEntry(
            risk_statement="Risk that supplier delay causes milestone slip",
            category="Supplier",
            probability=3,
            impact=3,
            risk_score=9,
            level="MEDIUM",
            mitigation="Weekly supplier sync with escalation path defined",
            residual_risk="LOW",
        )
        output = make_valid_output(risks=[risk])
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
            agent = SwProjectLeadAgent()
            assert agent.AGENT_NAME == "sw-project-lead"

    def test_get_schema_returns_correct_type(self):
        with patch("sdk_agents.core.base_agent.Groq"), \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            agent = SwProjectLeadAgent()
            assert agent.get_schema() is SwProjectLeadOutput

    def test_get_prompt_returns_string_with_cr_content(self):
        with patch("sdk_agents.core.base_agent.Groq"), \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            agent = SwProjectLeadAgent()
            prompt = agent.get_prompt()
            assert isinstance(prompt, str)
            assert "ASPICE" in prompt
            assert "3x Rule" in prompt or "3×" in prompt or "multiplier" in prompt.lower()

    def test_prompt_contains_anti_pattern_guard(self):
        with patch("sdk_agents.core.base_agent.Groq"), \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            agent = SwProjectLeadAgent()
            prompt = agent.get_prompt()
            assert "Anti-Pattern Guard" in prompt

    def test_api_error_returns_agent_error(self):
        with patch("sdk_agents.core.base_agent.Groq") as mock_groq_cls, \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            mock_client = MagicMock()
            mock_groq_cls.return_value = mock_client
            mock_client.chat.completions.create.side_effect = Exception("API connection failed")
            agent = SwProjectLeadAgent()
            result = agent.run("OTA CR analysis")
            assert isinstance(result, AgentError)
            assert result.error_type == "api_error"

    def test_missing_api_key_raises(self):
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(EnvironmentError, match="GROQ_API_KEY not set"):
                SwProjectLeadAgent()
