"""
Unit tests for sw_integrator — no API calls required.
Tests: schema structure, validator logic, skill loader, agent instantiation.
All API calls are mocked — runs without a GROQ_API_KEY.
"""

import pytest
from unittest.mock import patch, MagicMock
from sdk_agents.integrator.sw_integrator.schema import (
    SwIntegratorOutput, IntegrationErrorClassification, MemorySection,
    AspiceSwe5WorkProduct,
)
from sdk_agents.integrator.sw_integrator import SwIntegratorAgent
from sdk_agents.integrator.sw_integrator import validators
from sdk_agents.core.base_agent import AgentError, DomainCheckError
from sdk_agents.core.skill_loader import load_skill
from sdk_agents.core.shared_schema import (
    ProbableCause, NarrowingQuestion, SelfEvaluationLine, DebugStep,
    InputAnalysis, DataSufficiency,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

def make_valid_output(**overrides) -> SwIntegratorOutput:
    """Build a valid SwIntegratorOutput for testing.
    Scenario: SWC sender-receiver port not connected after ARXML composition — RTE generation fails.
    """
    data = {
        "error_classification": IntegrationErrorClassification(
            error_type="Port not connected",
            autosar_layer="RTE",
            tool_view="DaVinci System Design port view — unconnected P-Port shown in red",
            root_cause_hypothesis="VehicleSpeed_PP port missing consumer connection in composition ARXML",
        ),
        "input_analysis": InputAnalysis(
            input_facts=[
                "error: RTE generation fails with 'port not connected' for VehicleSpeed_PP",
                "SWC: SpeedProvider_SWC with P-Port VehicleSpeed_PP",
                "tool: DaVinci Developer",
                "AUTOSAR version: R4.4",
            ],
            assumptions=[
                "assumed interface type is sender-receiver — not stated explicitly",
                "assumed composition ARXML is the root cause — connector not verified yet",
            ],
        ),
        "data_sufficiency": DataSufficiency(
            level="PARTIAL",
            confidence="MEDIUM",
            confidence_reason="Error message and SWC name present but ARXML composition file not provided.",
            missing_critical_data=[
                "[CRITICAL] ARXML composition file or DaVinci port view screenshot — required to confirm missing connector",
                "[OPTIONAL] full RTE generation log — would identify all affected ports in one pass",
            ],
        ),
        "analysis": (
            "RTE generation failure at composition level. "
            "VehicleSpeed_PP P-Port has no R-Port consumer connected in the composition ARXML. "
            "Trace path: SWC P-Port → composition connector → consumer R-Port — connector element missing."
        ),
        "probable_causes": [
            ProbableCause(
                rank="HIGH",
                description="Composition ARXML connector between VehicleSpeed_PP and consumer R-Port is missing",
                is_hypothesis=False,
                ranking_reason="Direct match to error message — port not connected is an ARXML structural issue",
                test="Open composition ARXML in DaVinci System Design — check connectors tab for VehicleSpeed_PP",
                pass_criteria="Connector element present linking P-Port to consumer R-Port",
                fail_criteria="No connector element found for VehicleSpeed_PP",
                validation_test="In DaVinci System Design port view: if VehicleSpeed_PP shown in red with no line to consumer — confirmed missing connector",
            ),
            ProbableCause(
                rank="MEDIUM",
                description="Consumer SWC R-Port interface name does not match provider interface SR_VehicleSpeed_I",
                is_hypothesis=True,
                ranking_reason="Interface mismatch would also block RTE generation — less likely than missing connector",
                test="Compare interface name in provider ARXML vs consumer ARXML",
                pass_criteria="Both reference SR_VehicleSpeed_I exactly",
                fail_criteria="Consumer references a different interface name",
                validation_test="grep for SR_VehicleSpeed_I in both SWC ARXML files — mismatch confirms interface error",
            ),
            ProbableCause(
                rank="LOW",
                description="Consumer SWC was removed from composition but provider port not cleaned up",
                is_hypothesis=True,
                ranking_reason="Less likely — would show as missing SWC in composition, not just port error",
                test="Check composition ARXML for all SWC instances",
                pass_criteria="All SWC instances that reference VehicleSpeed_PP are present",
                fail_criteria="Consumer SWC instance missing from composition",
                validation_test="Open composition in DaVinci — if consumer SWC instance not listed, this cause confirmed",
            ),
        ],
        "memory_budget": [
            MemorySection(
                section=".text",
                used_hex="UNKNOWN",
                total_hex="UNKNOWN",
                utilization_pct="UNKNOWN",
                headroom_ok="UNKNOWN",
            ),
        ],
        "resource_budget_calc": ["N/A — symptom does not indicate a resource constraint"],
        "resolution_steps": [
            DebugStep(
                step_number=1,
                tool="DaVinci System Design",
                action="Open composition ARXML in port view, locate VehicleSpeed_PP P-Port, check for red unconnected status",
                expected_output="Port shown in red with no consumer connector line — confirms missing connector",
            ),
            DebugStep(
                step_number=2,
                tool="DaVinci System Design",
                action="Add connector from VehicleSpeed_PP P-Port to consumer SpeedConsumer_SWC R-Port VehicleSpeed_RP",
                expected_output="Connector line appears in port view, port status changes from red to connected",
            ),
            DebugStep(
                step_number=3,
                tool="DaVinci Developer RTE Generator",
                action="Regenerate RTE after adding connector — run full RTE generation and check for errors",
                expected_output="RTE generation completes without port connection errors; RTE C files updated",
            ),
        ],
        "aspice_swe5_evidence": [
            AspiceSwe5WorkProduct(
                work_product="Integration Test Specification",
                wp_id="17-50",
                status="MISSING",
                note="RTE generation error must be resolved before integration test spec can be baselined",
            ),
        ],
        "narrowing_questions": [
            NarrowingQuestion(
                question="Is the consumer SWC instance present in the composition ARXML?",
                yes_consequence="Missing connector between present SWCs — add connector in DaVinci",
                no_consequence="Consumer SWC removed from composition — re-add SWC instance and connector",
            ),
            NarrowingQuestion(
                question="Does the consumer R-Port interface name match SR_VehicleSpeed_I exactly?",
                yes_consequence="Interface names match — connector is the only missing element",
                no_consequence="Interface name mismatch — correct consumer ARXML interface reference",
            ),
            NarrowingQuestion(
                question="Does the RTE generation log show more than one unconnected port error?",
                yes_consequence="Multiple connectors missing — systematic ARXML composition issue",
                no_consequence="Single port error — isolated connection problem",
            ),
        ],
        "self_evaluation": [
            SelfEvaluationLine(
                item="AUTOSAR layer identified",
                result="PASS",
                evidence="error_classification.autosar_layer = 'RTE' — RTE generation failure confirmed",
            ),
            SelfEvaluationLine(
                item="Resolution steps are specific",
                result="PASS",
                evidence="Step 1: DaVinci port view; Step 2: add connector; Step 3: regenerate RTE — all tool-specific",
            ),
        ],
    }
    data.update(overrides)
    return SwIntegratorOutput(**data)


# ── Schema tests ──────────────────────────────────────────────────────────────

class TestSchemaStructure:
    def test_valid_output_instantiates(self):
        output = make_valid_output()
        assert output.error_classification.autosar_layer == "RTE"

    def test_memory_section_headroom_must_be_valid(self):
        with pytest.raises(Exception):
            MemorySection(
                section=".text",
                used_hex="0x1000",
                total_hex="0x2000",
                utilization_pct="50%",
                headroom_ok="MAYBE",  # invalid — must be YES/NO/UNKNOWN
            )

    def test_aspice_work_product_status_must_be_valid(self):
        with pytest.raises(Exception):
            AspiceSwe5WorkProduct(
                work_product="Integration Test Specification",
                wp_id="17-50",
                status="DRAFT",  # invalid — must be PRESENT/MISSING/INCOMPLETE
                note="test",
            )

    def test_schema_has_required_fields(self):
        schema = SwIntegratorOutput.model_json_schema()
        required = schema.get("required", [])
        for field in [
            "error_classification", "analysis", "probable_causes",
            "memory_budget", "resolution_steps", "aspice_swe5_evidence",
            "narrowing_questions", "self_evaluation",
        ]:
            assert field in required, f"'{field}' missing from schema required list"

    def test_schema_extra_is_ignore(self):
        output = SwIntegratorOutput.model_validate(
            {**make_valid_output().model_dump(), "extra_field": "x"}
        )
        assert output.error_classification.autosar_layer == "RTE"

    def test_input_analysis_present(self):
        output = make_valid_output()
        assert output.input_analysis is not None
        assert len(output.input_analysis.input_facts) > 0

    def test_input_analysis_has_error_fact(self):
        output = make_valid_output()
        assert any("port not connected" in f.lower() for f in output.input_analysis.input_facts)

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
                confidence_reason="Error message, SWC name, ARXML file, and AUTOSAR version all present.",
                missing_critical_data=["None — data is complete"],
            )
        )
        assert output.data_sufficiency.level == "SUFFICIENT"
        assert output.data_sufficiency.missing_critical_data == ["None — data is complete"]


# ── Validator tests ───────────────────────────────────────────────────────────

class TestValidators:
    def test_valid_output_passes(self):
        validators.validate(make_valid_output())

    def test_unknown_autosar_layer_fails(self):
        ec = IntegrationErrorClassification(
            error_type="Port not connected",
            autosar_layer="UnknownLayer",
            tool_view="some tool",
            root_cause_hypothesis="some hypothesis",
        )
        output = make_valid_output(error_classification=ec)
        with pytest.raises(DomainCheckError, match="does not match any known AUTOSAR layer"):
            validators.validate(output)

    def test_short_analysis_fails(self):
        output = make_valid_output(analysis="too short")
        with pytest.raises(DomainCheckError, match="too short"):
            validators.validate(output)

    def test_vague_resolution_step_fails(self):
        short_step = DebugStep(
            step_number=1,
            tool="DaVinci",
            action="check it",  # too short
            expected_output="something",
        )
        output = make_valid_output(resolution_steps=[
            short_step,
            make_valid_output().resolution_steps[1],
            make_valid_output().resolution_steps[2],
        ])
        with pytest.raises(DomainCheckError, match="too vague"):
            validators.validate(output)

    def test_linker_error_without_calc_fails(self):
        ec = IntegrationErrorClassification(
            error_type="Linker section overflow",
            autosar_layer="Linker",
            tool_view="GCC .map file",
            root_cause_hypothesis=".text section exceeds flash allocation",
        )
        output = make_valid_output(
            error_classification=ec,
            resource_budget_calc=["N/A — symptom does not indicate a resource constraint"],
        )
        with pytest.raises(DomainCheckError, match="Linker error"):
            validators.validate(output)

    def test_self_eval_pass_without_evidence_fails(self):
        output = make_valid_output(self_evaluation=[
            SelfEvaluationLine(item="AUTOSAR layer", result="PASS", evidence="ok")
        ])
        with pytest.raises(DomainCheckError, match="evidence is empty or too short"):
            validators.validate(output)


# ── Skill loader tests ────────────────────────────────────────────────────────

class TestSkillLoader:
    def test_aspice_process_skill_loads(self):
        content = load_skill("aspice-process")
        assert len(content) > 100

    def test_aspice_skill_contains_swe5_content(self):
        content = load_skill("aspice-process")
        assert "SWE.5" in content

    def test_unknown_skill_raises(self):
        with pytest.raises(FileNotFoundError, match="not found"):
            load_skill("nonexistent-skill")


# ── Agent instantiation tests (no API calls) ─────────────────────────────────

class TestAgentInstantiation:
    def test_agent_instantiates(self):
        with patch("sdk_agents.core.base_agent.Groq"), \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            agent = SwIntegratorAgent()
            assert agent.AGENT_NAME == "sw-integrator"

    def test_get_schema_returns_correct_type(self):
        with patch("sdk_agents.core.base_agent.Groq"), \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            agent = SwIntegratorAgent()
            assert agent.get_schema() is SwIntegratorOutput

    def test_get_prompt_returns_string_with_autosar_content(self):
        with patch("sdk_agents.core.base_agent.Groq"), \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            agent = SwIntegratorAgent()
            prompt = agent.get_prompt()
            assert isinstance(prompt, str)
            assert "AUTOSAR" in prompt
            assert "RTE" in prompt

    def test_prompt_contains_anti_pattern_guard(self):
        with patch("sdk_agents.core.base_agent.Groq"), \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            agent = SwIntegratorAgent()
            prompt = agent.get_prompt()
            assert "Anti-Pattern Guard" in prompt

    def test_api_error_returns_agent_error(self):
        with patch("sdk_agents.core.base_agent.Groq") as mock_groq_cls, \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            mock_client = MagicMock()
            mock_groq_cls.return_value = mock_client
            mock_client.chat.completions.create.side_effect = Exception("API connection failed")
            agent = SwIntegratorAgent()
            result = agent.run("RTE generation fails with port not connected error")
            assert isinstance(result, AgentError)
            assert result.error_type == "api_error"

    def test_missing_api_key_raises(self):
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(EnvironmentError, match="GROQ_API_KEY not set"):
                SwIntegratorAgent()
