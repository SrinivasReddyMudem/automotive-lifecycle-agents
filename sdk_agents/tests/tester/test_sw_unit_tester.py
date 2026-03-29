"""
Unit tests for sw_unit_tester — no API calls required.
Tests: schema structure, validator logic, skill loader, agent instantiation.
All API calls are mocked — runs without a GROQ_API_KEY.
"""

import pytest
from unittest.mock import patch, MagicMock
from sdk_agents.tester.sw_unit_tester.schema import (
    SwUnitTesterOutput, UnitTestCase, MCDCPair, StubRequired, CoverageSummary,
)
from sdk_agents.tester.sw_unit_tester import SwUnitTesterAgent
from sdk_agents.tester.sw_unit_tester import validators
from sdk_agents.core.base_agent import AgentError, DomainCheckError
from sdk_agents.core.skill_loader import load_skills
from sdk_agents.core.shared_schema import SelfEvaluationLine, InputAnalysis, DataSufficiency


# ── Fixtures ──────────────────────────────────────────────────────────────────

def make_valid_output(**overrides) -> SwUnitTesterOutput:
    data = {
        "function_signature": "bool BrakeControl_IsEmergencyBrakeRequired(uint8_t pedalPos, bool sensorValid, uint8_t vehicleSpeed)",
        "input_analysis": InputAnalysis(
            input_facts=[
                "function: BrakeControl_IsEmergencyBrakeRequired(uint8_t pedalPos, bool sensorValid, uint8_t vehicleSpeed)",
                "ASIL level: ASIL-D",
                "framework: Unity",
                "input domain: pedalPos 0-255 (uint8_t), sensorValid true/false, vehicleSpeed 0-255 (uint8_t)",
            ],
            assumptions=[
                "assumed pedalPos threshold is 90 based on typical brake pedal calibration",
                "assumed vehicleSpeed minimum threshold is 5 based on function naming convention",
            ],
        ),
        "data_sufficiency": DataSufficiency(
            level="SUFFICIENT",
            confidence="HIGH",
            confidence_reason="Function signature, ASIL level, and input domain bounds are fully specified.",
            missing_critical_data=["None — data is complete"],
        ),
        "asil_level": "ASIL-D",
        "coverage_required": "Statement 100% + Branch 100% + MC/DC 100% per ISO 26262-6 Table 13 (ASIL-D)",
        "framework": "Unity",
        "stubs_required": [
            StubRequired(
                stub_name="Rte_Read_Speed_PP_SpeedValue",
                purpose="Provide controlled vehicleSpeed input without RTE runtime",
                return_value="RTE_E_OK with configured speed value",
            ),
        ],
        "swe4_work_product": "Unit Test Specification SW-UTS-001 (ASPICE 17-50)",
        "design_traceability": "Detailed Design DD-BCM-003 BrakeControl_IsEmergencyBrakeRequired",
        "test_cases": [
            UnitTestCase(
                tc_id="TC-001",
                objective="pedalPos above threshold with valid sensor and speed — emergency brake required",
                precondition="sensorValid=true, vehicleSpeed=10",
                input_values="pedalPos=90 (uint8_t), sensorValid=true, vehicleSpeed=10 (uint8_t)",
                expected_result="return true",
                pass_criteria="return value == true AND no fault DEM reported",
            ),
            UnitTestCase(
                tc_id="TC-002",
                objective="pedalPos below threshold — emergency brake not required",
                precondition="sensorValid=true, vehicleSpeed=10",
                input_values="pedalPos=89 (uint8_t), sensorValid=true, vehicleSpeed=10 (uint8_t)",
                expected_result="return false",
                pass_criteria="return value == false",
            ),
            UnitTestCase(
                tc_id="TC-003",
                objective="sensor invalid — brake ignored regardless of pedal position",
                precondition="sensorValid=false, vehicleSpeed=10",
                input_values="pedalPos=200 (uint8_t), sensorValid=false, vehicleSpeed=10 (uint8_t)",
                expected_result="return false",
                pass_criteria="return value == false when sensorValid=false",
            ),
        ],
        "mcdc_pairs": [
            MCDCPair(
                tc_id="TC-001",
                condition_values="pedalPos>=90=T, sensorValid=T, vehicleSpeed>=5=T",
                decision_result="TRUE",
                independently_tests="Condition pedalPos>=90 (sensorValid and vehicleSpeed held constant)",
            ),
            MCDCPair(
                tc_id="TC-002",
                condition_values="pedalPos>=90=F, sensorValid=T, vehicleSpeed>=5=T",
                decision_result="FALSE",
                independently_tests="Condition pedalPos>=90 pair-FALSE (only pedalPos changed)",
            ),
        ],
        "test_code": [
            "void test_BrakeControl_PedalAboveThreshold_SensorValid_SpeedAbove5(void) {",
            "    TEST_ASSERT_TRUE(BrakeControl_IsEmergencyBrakeRequired(90U, true, 10U));",
            "}",
            "void test_BrakeControl_PedalBelowThreshold(void) {",
            "    TEST_ASSERT_FALSE(BrakeControl_IsEmergencyBrakeRequired(89U, true, 10U));",
            "}",
            "void test_BrakeControl_SensorInvalid_BrakeIgnored(void) {",
            "    TEST_ASSERT_FALSE(BrakeControl_IsEmergencyBrakeRequired(200U, false, 10U));",
            "}",
        ],
        "coverage_summary": [
            CoverageSummary(
                coverage_type="Statement",
                target_pct="100%",
                achieved_pct="100%",
                achieving_tcs="TC-001, TC-002, TC-003",
            ),
            CoverageSummary(
                coverage_type="Branch",
                target_pct="100%",
                achieved_pct="100%",
                achieving_tcs="TC-001 (all true), TC-002 (pedalPos false), TC-003 (sensor false)",
            ),
            CoverageSummary(
                coverage_type="MC/DC",
                target_pct="100%",
                achieved_pct="100%",
                achieving_tcs="TC-001 and TC-002 form independence pair for pedalPos condition",
            ),
        ],
        "self_evaluation": [
            SelfEvaluationLine(
                item="MC/DC pairs",
                result="PASS",
                evidence="2 independence pairs covering pedalPos condition with numeric values",
            ),
            SelfEvaluationLine(
                item="Boundary values",
                result="PASS",
                evidence="TC-002 at pedalPos=89 (max-1), TC-001 at pedalPos=90 (boundary)",
            ),
        ],
    }
    data.update(overrides)
    return SwUnitTesterOutput(**data)


# ── Schema tests ──────────────────────────────────────────────────────────────

class TestSchema:
    def test_valid_output_instantiates(self):
        output = make_valid_output()
        assert "BrakeControl_IsEmergencyBrakeRequired" in output.function_signature

    def test_coverage_summary_type_must_be_valid(self):
        with pytest.raises(Exception):
            CoverageSummary(
                coverage_type="MCDC",  # invalid — must be "MC/DC"
                target_pct="100%",
                achieved_pct="100%",
                achieving_tcs="TC-001",
            )

    def test_mcdc_pair_decision_must_be_valid(self):
        with pytest.raises(Exception):
            MCDCPair(
                tc_id="TC-001",
                condition_values="A=T, B=T",
                decision_result="MAYBE",  # invalid — must be TRUE or FALSE
                independently_tests="Condition A",
            )

    def test_test_code_is_list_of_strings(self):
        output = make_valid_output()
        assert isinstance(output.test_code, list)
        assert all(isinstance(line, str) for line in output.test_code)

    def test_schema_has_required_fields(self):
        schema = SwUnitTesterOutput.model_json_schema()
        required = schema.get("required", [])
        for field in [
            "function_signature", "asil_level", "coverage_required", "framework",
            "test_cases", "mcdc_pairs", "test_code", "coverage_summary", "self_evaluation",
        ]:
            assert field in required, f"'{field}' missing from schema required list"

    def test_schema_extra_is_ignore(self):
        output = SwUnitTesterOutput.model_validate(
            {**make_valid_output().model_dump(), "extra_field": "x"}
        )
        assert output.asil_level == "ASIL-D"

    def test_input_analysis_present(self):
        output = make_valid_output()
        assert output.input_analysis is not None
        assert len(output.input_analysis.input_facts) > 0

    def test_input_analysis_has_function_signature_fact(self):
        output = make_valid_output()
        assert any("BrakeControl" in f for f in output.input_analysis.input_facts)

    def test_data_sufficiency_level_is_valid(self):
        output = make_valid_output()
        assert output.data_sufficiency.level in ("SUFFICIENT", "PARTIAL", "INSUFFICIENT")

    def test_data_sufficiency_sufficient_has_empty_missing(self):
        output = make_valid_output()
        assert output.data_sufficiency.level == "SUFFICIENT"
        assert output.data_sufficiency.missing_critical_data == ["None — data is complete"]

    def test_data_sufficiency_partial_has_missing_items(self):
        output = make_valid_output(
            data_sufficiency=DataSufficiency(
                level="PARTIAL",
                confidence="MEDIUM",
                confidence_reason="ASIL level not stated — assumed ASIL-D from module name.",
                missing_critical_data=["[CRITICAL] ASIL level — determines MC/DC coverage requirement"],
            )
        )
        assert output.data_sufficiency.level == "PARTIAL"
        assert len(output.data_sufficiency.missing_critical_data) > 0


# ── Validator tests ───────────────────────────────────────────────────────────

class TestValidators:
    def test_valid_output_passes(self):
        validators.validate(make_valid_output())

    def test_empty_test_code_fails(self):
        output = make_valid_output(test_code=[])
        with pytest.raises(DomainCheckError, match="test_code is too short"):
            validators.validate(output)

    def test_short_test_code_fails(self):
        output = make_valid_output(test_code=["// test"])
        with pytest.raises(DomainCheckError, match="test_code is too short"):
            validators.validate(output)

    def test_asil_d_without_mcdc_fails(self):
        output = make_valid_output(mcdc_pairs=[])
        with pytest.raises(DomainCheckError, match="requires MC/DC coverage"):
            validators.validate(output)

    def test_asil_b_without_mcdc_passes(self):
        """ASIL-B does not require MC/DC — empty mcdc_pairs is acceptable."""
        output = make_valid_output(asil_level="ASIL-B", mcdc_pairs=[])
        validators.validate(output)  # should not raise

    def test_qm_without_mcdc_passes(self):
        """QM has no mandatory structural coverage — empty mcdc_pairs is fine."""
        output = make_valid_output(asil_level="QM", mcdc_pairs=[])
        validators.validate(output)  # should not raise

    def test_short_pass_criteria_fails(self):
        tc = UnitTestCase(
            tc_id="TC-001",
            objective="Verify brake required",
            precondition="sensorValid=true",
            input_values="pedalPos=90, sensorValid=true, vehicleSpeed=10",
            expected_result="return true",
            pass_criteria="ok",  # too short
        )
        output = make_valid_output(test_cases=[tc])
        with pytest.raises(DomainCheckError, match="pass_criteria is too short"):
            validators.validate(output)

    def test_empty_coverage_summary_fails(self):
        output = make_valid_output(coverage_summary=[])
        with pytest.raises(DomainCheckError, match="coverage_summary is empty"):
            validators.validate(output)

    def test_coverage_summary_with_empty_achieving_tcs_fails(self):
        cs = CoverageSummary(
            coverage_type="Statement",
            target_pct="100%",
            achieved_pct="100%",
            achieving_tcs="",  # empty
        )
        output = make_valid_output(coverage_summary=[cs])
        with pytest.raises(DomainCheckError, match="achieving_tcs is empty"):
            validators.validate(output)

    def test_self_eval_pass_without_evidence_fails(self):
        output = make_valid_output(self_evaluation=[
            SelfEvaluationLine(item="MC/DC", result="PASS", evidence="ok")
        ])
        with pytest.raises(DomainCheckError, match="evidence is empty or too short"):
            validators.validate(output)


# ── Skill loader tests ────────────────────────────────────────────────────────

class TestSkillLoader:
    def test_aspice_process_skill_loads(self):
        content = load_skills("aspice-process")
        assert len(content) > 100

    def test_misra_c_2012_skill_loads(self):
        content = load_skills("misra-c-2012")
        assert len(content) > 100

    def test_combined_skills_load(self):
        content = load_skills("aspice-process", "misra-c-2012")
        assert "SWE" in content
        assert "MISRA" in content or "misra" in content.lower()

    def test_unknown_skill_raises(self):
        from sdk_agents.core.skill_loader import load_skill
        with pytest.raises(FileNotFoundError, match="not found"):
            load_skill("nonexistent-skill")


# ── Agent instantiation tests (no API calls) ─────────────────────────────────

class TestAgentInstantiation:
    def test_agent_instantiates(self):
        with patch("sdk_agents.core.base_agent.Groq"), \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            agent = SwUnitTesterAgent()
            assert agent.AGENT_NAME == "sw-unit-tester"

    def test_get_schema_returns_correct_type(self):
        with patch("sdk_agents.core.base_agent.Groq"), \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            agent = SwUnitTesterAgent()
            assert agent.get_schema() is SwUnitTesterOutput

    def test_get_prompt_returns_string_with_mcdc_content(self):
        with patch("sdk_agents.core.base_agent.Groq"), \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            agent = SwUnitTesterAgent()
            prompt = agent.get_prompt()
            assert isinstance(prompt, str)
            assert "MC/DC" in prompt
            assert "ISO 26262" in prompt

    def test_prompt_contains_anti_pattern_guard(self):
        with patch("sdk_agents.core.base_agent.Groq"), \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            agent = SwUnitTesterAgent()
            prompt = agent.get_prompt()
            assert "Anti-Pattern Guard" in prompt

    def test_api_error_returns_agent_error(self):
        with patch("sdk_agents.core.base_agent.Groq") as mock_groq_cls, \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            mock_client = MagicMock()
            mock_groq_cls.return_value = mock_client
            mock_client.chat.completions.create.side_effect = Exception("API connection failed")
            agent = SwUnitTesterAgent()
            result = agent.run("Unit tests for saturating uint16 adder ASIL-D")
            assert isinstance(result, AgentError)
            assert result.error_type == "api_error"

    def test_missing_api_key_raises(self):
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(EnvironmentError, match="GROQ_API_KEY not set"):
                SwUnitTesterAgent()
