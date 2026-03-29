"""
Unit tests for sil_hil_test_planner — no API calls required.
Tests: schema structure, validator logic, skill loader, agent instantiation.
All API calls are mocked — runs without a GROQ_API_KEY.
"""

import pytest
from unittest.mock import patch, MagicMock
from sdk_agents.tester.sil_hil_test_planner.schema import (
    SilHilTestPlannerOutput, TestEnvironment, TestCase,
    FaultInjection, AspiceEvidence,
)
from sdk_agents.tester.sil_hil_test_planner import SilHilTestPlannerAgent
from sdk_agents.tester.sil_hil_test_planner import validators
from sdk_agents.core.base_agent import AgentError, DomainCheckError
from sdk_agents.core.skill_loader import load_skill
from sdk_agents.core.shared_schema import SelfEvaluationLine, InputAnalysis, DataSufficiency


# ── Fixtures ──────────────────────────────────────────────────────────────────

def make_valid_output(**overrides) -> SilHilTestPlannerOutput:
    data = {
        "ecu_name": "Brake Control ECU",
        "input_analysis": InputAnalysis(
            input_facts=[
                "ECU: Brake Control ECU",
                "ASIL level: ASIL-B",
                "ASPICE scope: SWE.5 + SWE.6",
                "HIL platform: dSPACE SCALEXIO",
                "SRS requirement: SRS-BCM-012 — DTC P0601 within 500 ms of brake sensor failure",
                "fault: open circuit on brake pressure sensor",
            ],
            assumptions=[
                "assumed CAN 500 kbps as standard automotive bus — bitrate not stated",
                "assumed standard brake pedal sensor range from typical ECU specification",
            ],
        ),
        "data_sufficiency": DataSufficiency(
            level="PARTIAL",
            confidence="MEDIUM",
            confidence_reason="ECU and ASIL present but full SRS requirement list and bus configuration not stated.",
            missing_critical_data=[
                "[CRITICAL] complete SRS requirement list — required to allocate all test cases to SIL or HIL",
                "[OPTIONAL] CAN bitrate — would confirm bus configuration for HIL setup",
            ],
        ),
        "aspice_scope": "SWE.5 + SWE.6",
        "asil_level": "ASIL-B",
        "test_environment": TestEnvironment(
            sil_setup="Linux host, GCC 9.4, QEMU virtual CAN, CANoe simulation",
            hil_setup="dSPACE SCALEXIO, real ECU hardware, plant model for brake pressure",
            bus_configuration="CAN 500 kbps, standard frames, 11-bit IDs",
            measurement_tools="dSPACE ControlDesk 1 kHz logging, CANoe for bus capture",
        ),
        "test_cases": [
            TestCase(
                tc_id="TC-SWE5-001",
                requirement="SRS-BCM-012 — ECU shall set DTC P0601 within 500 ms of brake sensor failure",
                objective="Verify DTC P0601 set within 500 ms of sensor open-circuit fault injection",
                environment="HIL",
                fault_injected="Open circuit on brake pressure sensor signal wire at T+5s",
                pass_criteria="DTC P0601 status byte = 0x09 (confirmed, active) within 500 ms ±20 ms of fault injection; measured via CANoe UDS read",
                asil_note="Safety mechanism: plausibility check for brake sensor validates ASIL-B requirement SRS-BCM-012",
            ),
            TestCase(
                tc_id="TC-SWE5-002",
                requirement="SRS-BCM-015 — Normal brake apply response within 20 ms of pedal input",
                objective="Verify brake assist torque response time under normal conditions",
                environment="SIL",
                fault_injected="N/A — normal path test",
                pass_criteria="Brake torque command issued within 20 ms ±2 ms of pedal input; verified via SIL trace at 1 kHz",
                asil_note="N/A — response time is QM metric; safety mechanism not under test",
            ),
        ],
        "sil_scope": (
            "Logic correctness, state machine transitions, signal plausibility algorithms, "
            "and timing in simulation can all be verified in SIL."
        ),
        "hil_only_scope": (
            "Watchdog timeout behavior, real interrupt latency, hardware fault injection "
            "(voltage drop, open circuit), and CAN bus-off induction require real ECU on HIL."
        ),
        "fault_injections": [
            FaultInjection(
                fault_type="Sensor open circuit",
                parameters="Open circuit on brake pressure sensor pin; maintained for 2 s; injected via relay box at T+5s after CAN confirmed active",
                expected_dtc="P0601",
                timing="T+5s after CAN bus confirmed active on CANoe trace",
            ),
            FaultInjection(
                fault_type="Voltage supply drop",
                parameters="14V to 6V ramp over 500 ms; hold at 6V for 1 s; measure ECU reset via TRACE32",
                expected_dtc="N/A — watchdog reset expected",
                timing="T+10s after normal operation confirmed for 10 s",
            ),
        ],
        "regression_strategy": (
            "Impact-based: CAN driver changes → run TC-SWE5-001 to TC-SWE5-010. "
            "Safety mechanism changes → run full ASIL-B test suite. "
            "QM logic changes → run affected module tests only."
        ),
        "aspice_evidence": [
            AspiceEvidence(
                process_area="SWE.5",
                work_product="Integration Test Specification",
                wp_id="17-50",
                content="Test cases TC-SWE5-001 to TC-SWE5-050 with pass criteria and environment",
            ),
            AspiceEvidence(
                process_area="SWE.6",
                work_product="SW Qualification Test Specification",
                wp_id="17-50",
                content="SRS-traced qualification test cases with review and approval signatures",
            ),
        ],
        "self_evaluation": [
            SelfEvaluationLine(
                item="SIL/HIL separation",
                result="PASS",
                evidence="Watchdog verification assigned to HIL, logic tests to SIL — explicitly stated",
            ),
            SelfEvaluationLine(
                item="Pass criteria specificity",
                result="PASS",
                evidence="TC-SWE5-001: 500 ms ±20 ms threshold with measurement method named",
            ),
        ],
    }
    data.update(overrides)
    return SilHilTestPlannerOutput(**data)


# ── Schema tests ──────────────────────────────────────────────────────────────

class TestSchema:
    def test_valid_output_instantiates(self):
        output = make_valid_output()
        assert output.ecu_name == "Brake Control ECU"

    def test_test_case_environment_must_be_valid(self):
        with pytest.raises(Exception):
            TestCase(
                tc_id="TC-001",
                requirement="SRS-001",
                objective="test objective description",
                environment="REAL_CAR",  # invalid
                fault_injected="N/A",
                pass_criteria="ECU responds within 500 ms of fault injection",
                asil_note="N/A",
            )

    def test_aspice_evidence_process_area_must_be_valid(self):
        with pytest.raises(Exception):
            AspiceEvidence(
                process_area="SWE.4",  # invalid — only SWE.5 and SWE.6
                work_product="Unit Test Specification",
                wp_id="17-50",
                content="unit test content",
            )

    def test_schema_has_required_fields(self):
        schema = SilHilTestPlannerOutput.model_json_schema()
        required = schema.get("required", [])
        for field in [
            "ecu_name", "aspice_scope", "asil_level", "test_environment",
            "test_cases", "sil_scope", "hil_only_scope",
            "fault_injections", "aspice_evidence", "self_evaluation",
        ]:
            assert field in required, f"'{field}' missing from schema required list"

    def test_schema_extra_is_ignore(self):
        output = SilHilTestPlannerOutput.model_validate(
            {**make_valid_output().model_dump(), "extra_field": "x"}
        )
        assert output.ecu_name == "Brake Control ECU"

    def test_input_analysis_present(self):
        output = make_valid_output()
        assert output.input_analysis is not None
        assert len(output.input_analysis.input_facts) > 0

    def test_input_analysis_has_ecu_fact(self):
        output = make_valid_output()
        assert any("Brake Control ECU" in f for f in output.input_analysis.input_facts)

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
                confidence_reason="ECU, ASIL, ASPICE scope, and SRS requirement list all present.",
                missing_critical_data=["None — data is complete"],
            )
        )
        assert output.data_sufficiency.level == "SUFFICIENT"
        assert output.data_sufficiency.missing_critical_data == ["None — data is complete"]


# ── Validator tests ───────────────────────────────────────────────────────────

class TestValidators:
    def test_valid_output_passes(self):
        validators.validate(make_valid_output())

    def test_subjective_pass_criteria_fails(self):
        tc = TestCase(
            tc_id="TC-001",
            requirement="SRS-001",
            objective="Verify ECU handles fault correctly",
            environment="HIL",
            fault_injected="Open circuit on sensor",
            pass_criteria="ECU responds correctly to fault",  # "correctly" is subjective
            asil_note="N/A",
        )
        output = make_valid_output(test_cases=[tc, make_valid_output().test_cases[1]])
        with pytest.raises(DomainCheckError, match="subjective word 'correctly'"):
            validators.validate(output)

    def test_short_pass_criteria_fails(self):
        tc = TestCase(
            tc_id="TC-001",
            requirement="SRS-001",
            objective="Verify DTC set",
            environment="HIL",
            fault_injected="sensor open",
            pass_criteria="DTC set",  # too short
            asil_note="N/A",
        )
        output = make_valid_output(test_cases=[tc, make_valid_output().test_cases[1]])
        with pytest.raises(DomainCheckError, match="pass_criteria is too short"):
            validators.validate(output)

    def test_empty_sil_scope_fails(self):
        output = make_valid_output(sil_scope="N/A")
        with pytest.raises(DomainCheckError, match="sil_scope is empty or too short"):
            validators.validate(output)

    def test_empty_hil_only_scope_fails(self):
        output = make_valid_output(hil_only_scope="")
        with pytest.raises(DomainCheckError, match="hil_only_scope is empty or too short"):
            validators.validate(output)

    def test_vague_fault_injection_parameters_fails(self):
        fi = FaultInjection(
            fault_type="voltage drop",
            parameters="low",  # too short — under 10 chars
            expected_dtc="N/A",
            timing="T+5s",
        )
        output = make_valid_output(fault_injections=[fi])
        with pytest.raises(DomainCheckError, match="parameters is too vague"):
            validators.validate(output)

    def test_empty_aspice_evidence_fails(self):
        output = make_valid_output(aspice_evidence=[])
        with pytest.raises(DomainCheckError, match="aspice_evidence is empty"):
            validators.validate(output)

    def test_self_eval_pass_without_evidence_fails(self):
        output = make_valid_output(self_evaluation=[
            SelfEvaluationLine(item="SIL/HIL separation", result="PASS", evidence="ok")
        ])
        with pytest.raises(DomainCheckError, match="evidence is empty or too short"):
            validators.validate(output)

    def test_works_keyword_in_pass_criteria_fails(self):
        tc = TestCase(
            tc_id="TC-001",
            requirement="SRS-001",
            objective="Verify steering works after reset",
            environment="SIL",
            fault_injected="N/A",
            pass_criteria="Steering assist works after ECU power cycle",
            asil_note="N/A",
        )
        output = make_valid_output(test_cases=[tc, make_valid_output().test_cases[1]])
        with pytest.raises(DomainCheckError, match="subjective word 'works'"):
            validators.validate(output)


# ── Skill loader tests ────────────────────────────────────────────────────────

class TestSkillLoader:
    def test_aspice_process_skill_loads(self):
        content = load_skill("aspice-process")
        assert len(content) > 100

    def test_aspice_skill_contains_swe5_content(self):
        content = load_skill("aspice-process")
        assert "SWE.5" in content or "SWE.6" in content

    def test_unknown_skill_raises(self):
        with pytest.raises(FileNotFoundError, match="not found"):
            load_skill("nonexistent-skill")


# ── Agent instantiation tests (no API calls) ─────────────────────────────────

class TestAgentInstantiation:
    def test_agent_instantiates(self):
        with patch("sdk_agents.core.base_agent.Groq"), \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            agent = SilHilTestPlannerAgent()
            assert agent.AGENT_NAME == "sil-hil-test-planner"

    def test_get_schema_returns_correct_type(self):
        with patch("sdk_agents.core.base_agent.Groq"), \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            agent = SilHilTestPlannerAgent()
            assert agent.get_schema() is SilHilTestPlannerOutput

    def test_get_prompt_returns_string_with_sil_hil_content(self):
        with patch("sdk_agents.core.base_agent.Groq"), \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            agent = SilHilTestPlannerAgent()
            prompt = agent.get_prompt()
            assert isinstance(prompt, str)
            assert "SIL" in prompt
            assert "HIL" in prompt

    def test_prompt_contains_anti_pattern_guard(self):
        with patch("sdk_agents.core.base_agent.Groq"), \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            agent = SilHilTestPlannerAgent()
            prompt = agent.get_prompt()
            assert "Anti-Pattern Guard" in prompt

    def test_api_error_returns_agent_error(self):
        with patch("sdk_agents.core.base_agent.Groq") as mock_groq_cls, \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            mock_client = MagicMock()
            mock_groq_cls.return_value = mock_client
            mock_client.chat.completions.create.side_effect = Exception("API connection failed")
            agent = SilHilTestPlannerAgent()
            result = agent.run("HIL test plan for Brake ECU")
            assert isinstance(result, AgentError)
            assert result.error_type == "api_error"

    def test_missing_api_key_raises(self):
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(EnvironmentError, match="GROQ_API_KEY not set"):
                SilHilTestPlannerAgent()
