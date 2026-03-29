"""
Unit tests for autosar_bsw_developer — no API calls required.
Tests: schema structure, validator logic, skill loader, agent instantiation.
All API calls are mocked — runs without a GROQ_API_KEY.
"""

import pytest
from unittest.mock import patch, MagicMock
from sdk_agents.developer.autosar_bsw_developer.schema import (
    AutosarBswDeveloperOutput, PortDesign, RunnableDesign, BswParameter,
)
from sdk_agents.developer.autosar_bsw_developer import AutosarBswDeveloperAgent
from sdk_agents.developer.autosar_bsw_developer import validators
from sdk_agents.core.base_agent import AgentError, DomainCheckError
from sdk_agents.core.skill_loader import load_skills
from sdk_agents.core.shared_schema import SelfEvaluationLine, InputAnalysis, DataSufficiency


# ── Fixtures ──────────────────────────────────────────────────────────────────

def make_valid_output(**overrides) -> AutosarBswDeveloperOutput:
    """Build a valid AutosarBswDeveloperOutput for testing.
    Scenario: ASIL-B sender-receiver SWC for vehicle speed on AUTOSAR R4.4.
    """
    data = {
        "autosar_version": "R4.4",
        "input_analysis": InputAnalysis(
            input_facts=[
                "SWC type: Application SWC",
                "ASIL level: ASIL-B",
                "interface: sender-receiver for vehicle speed signal",
                "data element: VehicleSpeed_DE, uint16, range 0-32767, unit km/h × 100",
                "trigger: TimingEvent 10ms",
                "AUTOSAR version: R4.4",
            ],
            assumptions=[
                "assumed P-Port naming convention _PP suffix from AUTOSAR standard",
                "assumed OS task OsTask_10ms at priority 8 — task name not stated",
            ],
        ),
        "data_sufficiency": DataSufficiency(
            level="SUFFICIENT",
            confidence="HIGH",
            confidence_reason="SWC type, ASIL level, interface type, and data element details all stated.",
            missing_critical_data=["None — data is complete"],
        ),
        "asil_level": "ASIL-B",
        "swc_name": "VehicleSpeedProvider_SWC",
        "swc_type": "Application",
        "provider_ports": [
            PortDesign(
                port_name="VehicleSpeed_PP",
                port_direction="P-Port",
                interface_type="sender-receiver",
                interface_name="SR_VehicleSpeed_I",
                data_element_or_operation="VehicleSpeed_DE: uint16, range 0–32767 (km/h × 100), init value 0",
                rte_api="Rte_Write_VehicleSpeed_PP_VehicleSpeed_DE(uint16 data)",
                asil_constraint="Check return value == RTE_E_OK; invalidate on sensor error",
            ),
        ],
        "consumer_ports": [],
        "runnables": [
            RunnableDesign(
                name="VehicleSpeedProvider_RunFunc",
                trigger="TimingEvent 10ms",
                os_task="OsTask_10ms priority 8",
                timing_protection="WCET 0.5ms; budget 1ms per OS task period",
            ),
        ],
        "bsw_parameters": [
            BswParameter(
                module="Com",
                parameter_path="ComConfig/ComSignal/VehicleSpeed_DE/ComSignalLength",
                value="16 bits",
                impact="Signal width in CAN frame — must match DBC definition",
                common_mistake="Setting 8 bits instead of 16 — causes truncation of speed values above 255",
            ),
        ],
        "misra_notes": "Rule 10.4: mixed arithmetic — cast uint16 before division. Rule 11.3: no pointer cast from uint16* to void*.",
        "asil_notes": (
            "ASIL-B: check Rte_Write return value and set DEM event if RTE_E_LOST_DATA. "
            "Freedom from interference: no shared memory with QM runnables. "
            "Runnable must not call non-reentrant BSW functions."
        ),
        "self_evaluation": [
            SelfEvaluationLine(
                item="RTE API present",
                result="PASS",
                evidence="Rte_Write_VehicleSpeed_PP_VehicleSpeed_DE(uint16 data) — full signature shown",
            ),
            SelfEvaluationLine(
                item="ASIL-B return value check",
                result="PASS",
                evidence="asil_notes: Rte_Write return value checked, DEM event set on RTE_E_LOST_DATA",
            ),
        ],
    }
    data.update(overrides)
    return AutosarBswDeveloperOutput(**data)


# ── Schema tests ──────────────────────────────────────────────────────────────

class TestSchemaStructure:
    def test_valid_output_instantiates(self):
        output = make_valid_output()
        assert output.swc_name == "VehicleSpeedProvider_SWC"

    def test_port_direction_must_be_valid(self):
        with pytest.raises(Exception):
            PortDesign(
                port_name="Speed_XP",
                port_direction="X-Port",  # invalid — must be P-Port or R-Port
                interface_type="sender-receiver",
                interface_name="SR_Speed_I",
                data_element_or_operation="SpeedDE: uint16",
                rte_api="Rte_Write_Speed_XP_SpeedDE(uint16 data)",
                asil_constraint="N/A",
            )

    def test_interface_type_must_be_valid(self):
        with pytest.raises(Exception):
            PortDesign(
                port_name="Speed_PP",
                port_direction="P-Port",
                interface_type="publish-subscribe",  # invalid
                interface_name="SR_Speed_I",
                data_element_or_operation="SpeedDE: uint16",
                rte_api="Rte_Write_Speed_PP_SpeedDE(uint16 data)",
                asil_constraint="N/A",
            )

    def test_schema_has_required_fields(self):
        schema = AutosarBswDeveloperOutput.model_json_schema()
        required = schema.get("required", [])
        for field in [
            "autosar_version", "asil_level", "swc_name", "swc_type",
            "provider_ports", "consumer_ports", "runnables",
            "misra_notes", "self_evaluation",
        ]:
            assert field in required, f"'{field}' missing from schema required list"

    def test_schema_extra_is_ignore(self):
        output = AutosarBswDeveloperOutput.model_validate(
            {**make_valid_output().model_dump(), "extra_field": "x"}
        )
        assert output.swc_name == "VehicleSpeedProvider_SWC"

    def test_input_analysis_present(self):
        output = make_valid_output()
        assert output.input_analysis is not None
        assert len(output.input_analysis.input_facts) > 0

    def test_input_analysis_has_asil_fact(self):
        output = make_valid_output()
        assert any("ASIL" in f for f in output.input_analysis.input_facts)

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
                confidence_reason="ASIL level not stated — assumed ASIL-B from module context.",
                missing_critical_data=["[CRITICAL] ASIL level — determines RTE return value check requirement"],
            )
        )
        assert output.data_sufficiency.level == "PARTIAL"
        assert len(output.data_sufficiency.missing_critical_data) > 0


# ── Validator tests ───────────────────────────────────────────────────────────

class TestValidators:
    def test_valid_output_passes(self):
        validators.validate(make_valid_output())

    def test_unknown_autosar_version_fails(self):
        output = make_valid_output(autosar_version="R5.0")
        with pytest.raises(DomainCheckError, match="does not match known versions"):
            validators.validate(output)

    def test_generic_swc_name_fails(self):
        output = make_valid_output(swc_name="swc")
        with pytest.raises(DomainCheckError, match="too generic or too short"):
            validators.validate(output)

    def test_short_rte_api_fails(self):
        port = PortDesign(
            port_name="Speed_PP",
            port_direction="P-Port",
            interface_type="sender-receiver",
            interface_name="SR_Speed_I",
            data_element_or_operation="SpeedDE: uint16",
            rte_api="Rte_Write()",  # too short — under 20 chars
            asil_constraint="N/A",
        )
        output = make_valid_output(provider_ports=[port])
        with pytest.raises(DomainCheckError, match="too short or missing"):
            validators.validate(output)

    def test_non_rte_api_fails(self):
        port = PortDesign(
            port_name="Speed_PP",
            port_direction="P-Port",
            interface_type="sender-receiver",
            interface_name="SR_Speed_I",
            data_element_or_operation="SpeedDE: uint16",
            rte_api="Write_VehicleSpeed_PP_VehicleSpeed_DE(uint16 data)",  # missing Rte_ prefix
            asil_constraint="N/A",
        )
        output = make_valid_output(provider_ports=[port])
        with pytest.raises(DomainCheckError, match="does not start with 'Rte_'"):
            validators.validate(output)

    def test_short_misra_notes_fails(self):
        output = make_valid_output(misra_notes="Rule 10")  # too short
        with pytest.raises(DomainCheckError, match="too short"):
            validators.validate(output)

    def test_self_eval_pass_without_evidence_fails(self):
        output = make_valid_output(self_evaluation=[
            SelfEvaluationLine(item="RTE API", result="PASS", evidence="ok")
        ])
        with pytest.raises(DomainCheckError, match="evidence is empty or too short"):
            validators.validate(output)


# ── Skill loader tests ────────────────────────────────────────────────────────

class TestSkillLoader:
    def test_autosar_skill_loads(self):
        content = load_skills("autosar-classic")
        assert len(content) > 100

    def test_autosar_skill_contains_rte_content(self):
        content = load_skills("autosar-classic")
        assert "RTE" in content or "SWC" in content

    def test_unknown_skill_raises(self):
        from sdk_agents.core.skill_loader import load_skill
        with pytest.raises(FileNotFoundError, match="not found"):
            load_skill("nonexistent-skill")


# ── Agent instantiation tests (no API calls) ─────────────────────────────────

class TestAgentInstantiation:
    def test_agent_instantiates(self):
        with patch("sdk_agents.core.base_agent.Groq"), \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            agent = AutosarBswDeveloperAgent()
            assert agent.AGENT_NAME == "autosar-bsw-developer"

    def test_get_schema_returns_correct_type(self):
        with patch("sdk_agents.core.base_agent.Groq"), \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            agent = AutosarBswDeveloperAgent()
            assert agent.get_schema() is AutosarBswDeveloperOutput

    def test_get_prompt_returns_string_with_autosar_content(self):
        with patch("sdk_agents.core.base_agent.Groq"), \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            agent = AutosarBswDeveloperAgent()
            prompt = agent.get_prompt()
            assert isinstance(prompt, str)
            assert "AUTOSAR" in prompt
            assert "RTE" in prompt

    def test_prompt_contains_naming_guidance(self):
        with patch("sdk_agents.core.base_agent.Groq"), \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            agent = AutosarBswDeveloperAgent()
            prompt = agent.get_prompt()
            assert "Rte_Write" in prompt or "AUTOSAR" in prompt

    def test_api_error_returns_agent_error(self):
        with patch("sdk_agents.core.base_agent.Groq") as mock_groq_cls, \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            mock_client = MagicMock()
            mock_groq_cls.return_value = mock_client
            mock_client.chat.completions.create.side_effect = Exception("API connection failed")
            agent = AutosarBswDeveloperAgent()
            result = agent.run("ASIL-B sender-receiver SWC for vehicle speed")
            assert isinstance(result, AgentError)
            assert result.error_type == "api_error"

    def test_missing_api_key_raises(self):
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(EnvironmentError, match="GROQ_API_KEY not set"):
                AutosarBswDeveloperAgent()
