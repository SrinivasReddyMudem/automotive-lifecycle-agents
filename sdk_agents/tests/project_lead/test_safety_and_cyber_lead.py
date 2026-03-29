"""
Unit tests for safety_and_cyber_lead — no API calls required.
Tests: schema structure, validator logic, skill loader, agent instantiation.
All API calls are mocked — runs without a GROQ_API_KEY.
"""

import pytest
from unittest.mock import patch, MagicMock
from sdk_agents.project_lead.safety_and_cyber_lead.schema import (
    SafetyAndCyberLeadOutput, HazardousEvent, SafetyGoal,
    ThreatScenario, AttackFeasibility, CybersecurityGoal,
    InputAnalysis, DataSufficiency,
)
from sdk_agents.project_lead.safety_and_cyber_lead import SafetyAndCyberLeadAgent
from sdk_agents.project_lead.safety_and_cyber_lead import validators
from sdk_agents.core.base_agent import AgentError, DomainCheckError
from sdk_agents.core.skill_loader import load_skills
from sdk_agents.core.shared_schema import SelfEvaluationLine


# ── Fixtures ──────────────────────────────────────────────────────────────────

def make_valid_output(**overrides) -> SafetyAndCyberLeadOutput:
    data = {
        "item_name": "Electric Power Steering ECU",
        "input_analysis": InputAnalysis(
            input_facts=[
                "Item: Electric Power Steering ECU",
                "Item boundary: controls steering assist torque, inputs torque sensor and vehicle speed",
                "Operational scenario OS-01: high-speed motorway driving",
                "Operational scenario OS-02: urban manoeuvring at low speed",
                "Threat: OTA firmware injection via update channel",
            ],
            assumptions=[
                "Assumed mechanical steering column is in scope boundary exclusion — not explicitly stated",
                "Assumed S3 severity for unintended assist — driver-stated scenario, injury class inferred",
            ],
        ),
        "data_sufficiency": DataSufficiency(
            level="PARTIAL",
            confidence="MEDIUM",
            confidence_reason=(
                "Item boundary and operational scenarios are described but S, E, C "
                "parameters and TARA threat actor details are not fully stated"
            ),
            missing_critical_data=[
                "[CRITICAL] S/E/C parameter values with justification — needed to confirm ASIL assignment from table",
                "[OPTIONAL] Existing safety mechanisms — would reduce ASIL decomposition assumptions",
            ],
        ),
        "analysis_type": "HARA+TARA",
        "item_definition": (
            "EPS ECU controls steering assist torque. "
            "Inputs: torque sensor, vehicle speed, ignition. "
            "Outputs: motor current command. "
            "Boundary: excludes mechanical steering column."
        ),
        "hazardous_events": [
            HazardousEvent(
                he_id="HE-01",
                malfunctioning_behavior="Unintended steering assist in wrong direction",
                operational_situation="OS-01 high-speed motorway driving",
                severity="S3",
                exposure="E4",
                controllability="C2",
                asil="ASIL-C",
            ),
            HazardousEvent(
                he_id="HE-02",
                malfunctioning_behavior="Loss of steering assist at low speed",
                operational_situation="OS-02 urban manoeuvring",
                severity="S1",
                exposure="E3",
                controllability="C1",
                asil="QM",
            ),
        ],
        "sec_justifications": (
            "S3: loss of steering at speed can cause fatality — highest severity class. "
            "E4: motorway driving occurs frequently, daily for most vehicles. "
            "C2: a typical driver can normally correct unexpected steering but margin is limited."
        ),
        "safety_goals": [
            SafetyGoal(
                sg_id="SG-01",
                goal_statement="The vehicle shall not experience unintended lateral deviation due to EPS malfunction",
                asil="ASIL-C",
                safe_state="Deactivate assist, driver falls back to manual steering",
                ftti="100 ms",
            ),
        ],
        "hw_metrics_note": (
            "ASIL-C targets: SPFM ≥ 90%, LFM ≥ 60%, PMHF < 10^-7 h^-1."
        ),
        "threat_scenarios": [
            ThreatScenario(
                ts_id="TS-01",
                actor="remote attacker",
                attack_vector="OTA",
                scenario="Attacker injects malicious firmware via OTA update channel to override torque commands",
                target_asset="Firmware update service",
            ),
        ],
        "attack_feasibility": [
            AttackFeasibility(
                ts_id="TS-01",
                time_factor=2,
                expertise_factor=2,
                knowledge_factor=2,
                opportunity_factor=1,
                equipment_factor=1,
                total=8,
                feasibility="Low",
            ),
        ],
        "cybersecurity_goals": [
            CybersecurityGoal(
                cg_id="CG-01",
                goal_statement="The firmware update process shall ensure authenticity and integrity of software",
                cal="CAL-2",
                control="Code signing with PKI and secure boot verification",
            ),
        ],
        "co_engineering_interface": (
            "OTA update on ASIL-C ECU requires secure boot and code signing — "
            "safety and cybersecurity must co-engineer the update chain."
        ),
        "mandatory_review_note": (
            "This analysis requires review and approval by a qualified engineer "
            "before use in any project."
        ),
        "self_evaluation": [
            SelfEvaluationLine(
                item="HARA completeness",
                result="PASS",
                evidence="2 hazardous events with S/E/C justifications and safety goal derived",
            ),
            SelfEvaluationLine(
                item="TARA feasibility",
                result="PASS",
                evidence="5-factor total=8, mapped to Low feasibility, CAL-2 assigned",
            ),
        ],
    }
    data.update(overrides)
    return SafetyAndCyberLeadOutput(**data)


# ── Schema tests ──────────────────────────────────────────────────────────────

class TestSchema:
    def test_valid_output_instantiates(self):
        output = make_valid_output()
        assert output.item_name == "Electric Power Steering ECU"

    def test_analysis_type_must_be_valid(self):
        with pytest.raises(Exception):
            make_valid_output(analysis_type="UNKNOWN")

    def test_hazardous_event_severity_must_be_valid(self):
        with pytest.raises(Exception):
            HazardousEvent(
                he_id="HE-01",
                malfunctioning_behavior="test",
                operational_situation="OS-01",
                severity="S9",  # invalid
                exposure="E4",
                controllability="C2",
                asil="ASIL-C",
            )

    def test_attack_feasibility_sum_is_tracked(self):
        af = AttackFeasibility(
            ts_id="TS-01",
            time_factor=2,
            expertise_factor=2,
            knowledge_factor=2,
            opportunity_factor=1,
            equipment_factor=1,
            total=8,
            feasibility="Low",
        )
        computed = af.time_factor + af.expertise_factor + af.knowledge_factor + af.opportunity_factor + af.equipment_factor
        assert computed == af.total

    def test_cybersecurity_goal_cal_must_be_valid(self):
        with pytest.raises(Exception):
            CybersecurityGoal(
                cg_id="CG-01",
                goal_statement="test goal",
                cal="CAL-5",  # invalid — max is CAL-4
                control="test control",
            )

    def test_schema_has_required_fields(self):
        schema = SafetyAndCyberLeadOutput.model_json_schema()
        required = schema.get("required", [])
        for field in [
            "item_name", "analysis_type", "item_definition",
            "hazardous_events", "sec_justifications", "safety_goals",
            "threat_scenarios", "attack_feasibility", "cybersecurity_goals",
            "co_engineering_interface", "mandatory_review_note", "self_evaluation",
        ]:
            assert field in required, f"'{field}' missing from schema required list"

    def test_schema_extra_is_ignore(self):
        output = SafetyAndCyberLeadOutput.model_validate(
            {**make_valid_output().model_dump(), "unknown_extra_field": "x"}
        )
        assert output.item_name == "Electric Power Steering ECU"

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
                confidence_reason="Item boundary, S/E/C parameters, and threat details all provided",
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


# ── Validator tests ───────────────────────────────────────────────────────────

class TestValidators:
    def test_valid_output_passes(self):
        validators.validate(make_valid_output())

    def test_s0_severity_with_non_qm_asil_fails(self):
        he = HazardousEvent(
            he_id="HE-03",
            malfunctioning_behavior="Minor cosmetic display glitch",
            operational_situation="OS-03 parked",
            severity="S0",
            exposure="E1",
            controllability="C0",
            asil="ASIL-A",  # wrong — S0 must give QM
        )
        output = make_valid_output(hazardous_events=[he])
        with pytest.raises(DomainCheckError, match="S0 must always result in ASIL=QM"):
            validators.validate(output)

    def test_s0_severity_with_qm_passes(self):
        he = HazardousEvent(
            he_id="HE-03",
            malfunctioning_behavior="Minor cosmetic display glitch",
            operational_situation="OS-03 parked",
            severity="S0",
            exposure="E4",
            controllability="C3",
            asil="QM",
        )
        output = make_valid_output(hazardous_events=[he])
        validators.validate(output)

    def test_safety_goal_with_invalid_asil_fails(self):
        sg = SafetyGoal(
            sg_id="SG-01",
            goal_statement="test goal",
            asil="ASIL-Z",  # invalid
            safe_state="Deactivate output",
            ftti="100 ms",
        )
        output = make_valid_output(safety_goals=[sg])
        with pytest.raises(DomainCheckError, match="not a valid ASIL level"):
            validators.validate(output)

    def test_safety_goal_with_empty_safe_state_fails(self):
        sg = SafetyGoal(
            sg_id="SG-01",
            goal_statement="test goal",
            asil="ASIL-C",
            safe_state="",  # empty
            ftti="100 ms",
        )
        output = make_valid_output(safety_goals=[sg])
        with pytest.raises(DomainCheckError, match="safe_state is empty"):
            validators.validate(output)

    def test_sec_justifications_too_short_when_hazards_present_fails(self):
        output = make_valid_output(sec_justifications="S3, E4, C2")  # too short
        with pytest.raises(DomainCheckError, match="sec_justifications is too short"):
            validators.validate(output)

    def test_feasibility_total_mismatch_fails(self):
        af = AttackFeasibility(
            ts_id="TS-01",
            time_factor=2,
            expertise_factor=2,
            knowledge_factor=2,
            opportunity_factor=1,
            equipment_factor=1,
            total=99,  # wrong total
            feasibility="Low",
        )
        output = make_valid_output(attack_feasibility=[af])
        with pytest.raises(DomainCheckError, match="does not match sum of factors"):
            validators.validate(output)

    def test_mandatory_review_note_missing_fails(self):
        output = make_valid_output(mandatory_review_note="Analysis complete.")
        with pytest.raises(DomainCheckError, match="mandatory_review_note is missing"):
            validators.validate(output)

    def test_self_eval_pass_without_evidence_fails(self):
        output = make_valid_output(self_evaluation=[
            SelfEvaluationLine(item="HARA", result="PASS", evidence="ok")
        ])
        with pytest.raises(DomainCheckError, match="evidence is empty or too short"):
            validators.validate(output)

    def test_no_hazards_no_sec_check(self):
        """TARA-only mode: empty hazardous_events skips S/E/C justification check."""
        output = make_valid_output(
            analysis_type="TARA",
            hazardous_events=[],
            sec_justifications="N/A — TARA only",
            safety_goals=[],
        )
        validators.validate(output)  # should not raise


# ── Skill loader tests ────────────────────────────────────────────────────────

class TestSkillLoader:
    def test_iso26262_hara_skill_loads(self):
        content = load_skills("iso26262-hara")
        assert len(content) > 100

    def test_iso21434_tara_skill_loads(self):
        content = load_skills("iso21434-tara")
        assert len(content) > 100

    def test_combined_skills_load(self):
        content = load_skills("iso26262-hara", "iso21434-tara")
        assert "ASIL" in content or "asil" in content.lower()
        assert "TARA" in content or "tara" in content.lower()

    def test_unknown_skill_raises(self):
        from sdk_agents.core.skill_loader import load_skill
        with pytest.raises(FileNotFoundError, match="not found"):
            load_skill("nonexistent-skill")


# ── Agent instantiation tests (no API calls) ─────────────────────────────────

class TestAgentInstantiation:
    def test_agent_instantiates(self):
        with patch("sdk_agents.core.base_agent.Groq"), \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            agent = SafetyAndCyberLeadAgent()
            assert agent.AGENT_NAME == "safety-and-cyber-lead"

    def test_get_schema_returns_correct_type(self):
        with patch("sdk_agents.core.base_agent.Groq"), \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            agent = SafetyAndCyberLeadAgent()
            assert agent.get_schema() is SafetyAndCyberLeadOutput

    def test_get_prompt_returns_string_with_hara_content(self):
        with patch("sdk_agents.core.base_agent.Groq"), \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            agent = SafetyAndCyberLeadAgent()
            prompt = agent.get_prompt()
            assert isinstance(prompt, str)
            assert "ASIL" in prompt
            assert "TARA" in prompt

    def test_prompt_contains_anti_pattern_guard(self):
        with patch("sdk_agents.core.base_agent.Groq"), \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            agent = SafetyAndCyberLeadAgent()
            prompt = agent.get_prompt()
            assert "Anti-Pattern Guard" in prompt

    def test_api_error_returns_agent_error(self):
        with patch("sdk_agents.core.base_agent.Groq") as mock_groq_cls, \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            mock_client = MagicMock()
            mock_groq_cls.return_value = mock_client
            mock_client.chat.completions.create.side_effect = Exception("API connection failed")
            agent = SafetyAndCyberLeadAgent()
            result = agent.run("HARA for EPS ECU")
            assert isinstance(result, AgentError)
            assert result.error_type == "api_error"

    def test_missing_api_key_raises(self):
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(EnvironmentError, match="GROQ_API_KEY not set"):
                SafetyAndCyberLeadAgent()
