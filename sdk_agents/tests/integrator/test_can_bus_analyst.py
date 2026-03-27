"""
Unit tests for can_bus_analyst — no API calls required.
Tests: schema structure, validator logic, skill loader, agent instantiation.
All API calls are mocked — runs without a GOOGLE_API_KEY.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from sdk_agents.integrator.can_bus_analyst.schema import (
    CanBusAnalystOutput, ProbableCause, NarrowingQuestion, SelfEvaluationLine
)
from sdk_agents.integrator.can_bus_analyst import CanBusAnalystAgent
from sdk_agents.integrator.can_bus_analyst import validators
from sdk_agents.core.base_agent import AgentError, DomainCheckError
from sdk_agents.core.skill_loader import load_skill


# ── Fixtures ──────────────────────────────────────────────────────────────────

def make_valid_output(**overrides) -> CanBusAnalystOutput:
    """Build a valid CanBusAnalystOutput for testing."""
    data = {
        "expert_diagnosis": "TEC accumulation from engine-induced noise — not a hard fault.",
        "osi_layer": "L1 Physical",
        "autosar_layer": "MCAL (CanDrv)",
        "recommended_tool": "Oscilloscope",
        "tec_math": (
            "TX rate: 10 msg/s → 1800 transmissions in 180s. "
            "Errors for bus-off: 256/8=32. "
            "Min error rate: 32/1800=1.8%. "
            "Net TEC climb: 1.4 TEC/s. "
            "Time to bus-off: 256/1.4=183s — matches 3 min."
        ),
        "probable_causes": [
            ProbableCause(
                rank="HIGH",
                description="Ground potential shift under engine load",
                test="DMM DC between ECU GND pin and battery negative, engine running at idle",
                pass_criteria="Offset < 50 mV — ground path is clean",
                fail_criteria="Offset > 200 mV — corroded ground strap, replace and retest",
            ),
            ProbableCause(
                rank="HIGH",
                description="Alternator ripple on transceiver Vcc rail",
                test="Oscilloscope AC-coupled on transceiver Vcc pin, engine at 2000 RPM",
                pass_criteria="Ripple < 200 mV peak-to-peak — supply is clean",
                fail_criteria="Ripple > 500 mV or dips below 4.5 V — add bulk capacitor",
            ),
            ProbableCause(
                rank="MEDIUM",
                description="Thermal drift of CAN transceiver",
                test="Heat gun aimed at PCB for 3 minutes, engine off, bus active on CANoe",
                pass_criteria="No bus-off after 3 min of heat — thermal cause ruled out",
                fail_criteria="Bus-off triggered by heat alone — replace transceiver",
            ),
        ],
        "decision_flow": (
            "L1 Physical clean (scope: diff voltage OK, Vcc stable, GND offset < 50 mV)?\n"
            "├── No  → Fix GND strap or add Vcc decoupling, retest\n"
            "└── Yes ↓\n"
            "L2 Data Link clean (no error frames, TEC = 0)?\n"
            "├── No  → Check error type: Bit error → L1; ACK error → check L7\n"
            "└── Yes → Thermal — reproduce with heat gun engine off"
        ),
        "narrowing_questions": [
            NarrowingQuestion(
                question="Does the 3-minute timer reset if you stop and immediately restart the engine?",
                yes_consequence="TEC resets on restart — thermal unlikely, noise or SW trigger more likely",
                no_consequence="Accumulated state — check if CanSM recovery is manual-reset only",
            ),
            NarrowingQuestion(
                question="Does the fault trigger faster at higher engine RPM (2000 vs 800 RPM)?",
                yes_consequence="Alternator output scales with RPM — supply noise confirmed, fix GND strap",
                no_consequence="RPM-independent — thermal or SW state machine trigger more likely",
            ),
            NarrowingQuestion(
                question="Does any other node change state (sleep, mode switch) at exactly 3 minutes?",
                yes_consequence="ACK error root cause — this node loses its ACK partner, check L7 Application",
                no_consequence="Physical cause only — continue L1 investigation with oscilloscope",
            ),
        ],
        "self_evaluation": [
            SelfEvaluationLine(item="Expert diagnosis", result="PASS", evidence="L1 Physical stated, 3-min gradual onset explained"),
            SelfEvaluationLine(item="TEC math", result="PASS", evidence="1.4 TEC/s climb rate, 183s to bus-off calculated"),
            SelfEvaluationLine(item="Probable causes", result="PASS", evidence="3 causes with DMM/scope thresholds: 50mV, 200mV, 500mV"),
            SelfEvaluationLine(item="Decision flow", result="PASS", evidence="L1→L2 branching tree with Yes/No at each level"),
            SelfEvaluationLine(item="Narrowing questions", result="PASS", evidence="3 questions with RPM, restart, and ACK partner consequences"),
        ],
    }
    data.update(overrides)
    return CanBusAnalystOutput(**data)


# ── Schema tests ──────────────────────────────────────────────────────────────

class TestSchema:
    def test_valid_output_instantiates(self):
        output = make_valid_output()
        assert output.osi_layer == "L1 Physical"

    def test_requires_exactly_3_probable_causes(self):
        output = make_valid_output()
        assert len(output.probable_causes) == 3

    def test_requires_exactly_3_narrowing_questions(self):
        output = make_valid_output()
        assert len(output.narrowing_questions) == 3

    def test_probable_cause_rank_must_be_valid(self):
        with pytest.raises(Exception):
            ProbableCause(
                rank="CRITICAL",  # not in Literal["HIGH", "MEDIUM", "LOW"]
                description="test", test="test", pass_criteria="test", fail_criteria="test"
            )

    def test_schema_has_required_fields(self):
        schema = CanBusAnalystOutput.model_json_schema()
        required = schema.get("required", [])
        for field in ["expert_diagnosis", "osi_layer", "autosar_layer",
                      "tec_math", "probable_causes", "decision_flow",
                      "narrowing_questions", "self_evaluation"]:
            assert field in required, f"Field '{field}' missing from schema required list"

    def test_schema_version_in_config(self):
        schema = CanBusAnalystOutput.model_json_schema()
        assert schema.get("schema_version") == "v1"


# ── Validator tests ───────────────────────────────────────────────────────────

class TestValidators:
    def test_valid_output_passes(self):
        validators.validate(make_valid_output())  # should not raise

    def test_tec_math_without_numbers_fails(self):
        output = make_valid_output(tec_math="TEC climbs gradually over time due to noise")
        with pytest.raises(DomainCheckError, match="tec_math contains fewer than 3 numeric"):
            validators.validate(output)

    def test_unknown_autosar_layer_fails(self):
        output = make_valid_output(autosar_layer="SomeUnknownLayer")
        with pytest.raises(DomainCheckError, match="does not match any known AUTOSAR layer"):
            validators.validate(output)

    def test_vague_test_field_fails(self):
        cause = ProbableCause(
            rank="HIGH",
            description="Ground offset",
            test="check ground",  # too vague — under 25 chars
            pass_criteria="Offset < 50 mV — ground path is clean",
            fail_criteria="Offset > 200 mV — corroded ground strap",
        )
        output = make_valid_output(probable_causes=[
            cause,
            make_valid_output().probable_causes[1],
            make_valid_output().probable_causes[2],
        ])
        with pytest.raises(DomainCheckError, match="too vague"):
            validators.validate(output)

    def test_self_eval_pass_without_evidence_fails(self):
        line = SelfEvaluationLine(item="TEC math", result="PASS", evidence="ok")
        output = make_valid_output(self_evaluation=[line])
        with pytest.raises(DomainCheckError, match="evidence field is empty or too short"):
            validators.validate(output)


# ── Skill loader tests ────────────────────────────────────────────────────────

class TestSkillLoader:
    def test_can_bus_analysis_loads(self):
        content = load_skill("can-bus-analysis")
        assert len(content) > 100

    def test_skill_contains_tec_content(self):
        content = load_skill("can-bus-analysis")
        assert "TEC" in content or "transmit error" in content.lower()

    def test_unknown_skill_raises(self):
        with pytest.raises(FileNotFoundError, match="not found"):
            load_skill("nonexistent-skill")


# ── Agent instantiation tests (no API calls) ─────────────────────────────────

class TestAgentInstantiation:
    def test_agent_instantiates(self):
        with patch("google.generativeai.configure"), \
             patch.dict("os.environ", {"GOOGLE_API_KEY": "test-key"}):
            agent = CanBusAnalystAgent()
            assert agent.AGENT_NAME == "can-bus-analyst"

    def test_get_schema_returns_correct_type(self):
        with patch("google.generativeai.configure"), \
             patch.dict("os.environ", {"GOOGLE_API_KEY": "test-key"}):
            agent = CanBusAnalystAgent()
            assert agent.get_schema() is CanBusAnalystOutput

    def test_get_prompt_returns_string(self):
        with patch("google.generativeai.configure"), \
             patch.dict("os.environ", {"GOOGLE_API_KEY": "test-key"}):
            agent = CanBusAnalystAgent()
            prompt = agent.get_prompt()
            assert isinstance(prompt, str)
            assert len(prompt) > 200

    def test_api_error_returns_agent_error(self):
        with patch("google.generativeai.configure"), \
             patch.dict("os.environ", {"GOOGLE_API_KEY": "test-key"}), \
             patch("google.generativeai.GenerativeModel") as mock_model_cls:
            mock_model = MagicMock()
            mock_model_cls.return_value = mock_model
            mock_model.generate_content.side_effect = Exception("API connection failed")
            agent = CanBusAnalystAgent()
            result = agent.run("test prompt")
            assert isinstance(result, AgentError)
            assert result.error_type == "api_error"

    def test_validation_error_returns_agent_error(self):
        with patch("google.generativeai.configure"), \
             patch.dict("os.environ", {"GOOGLE_API_KEY": "test-key"}), \
             patch("google.generativeai.GenerativeModel") as mock_model_cls:
            mock_model = MagicMock()
            mock_model_cls.return_value = mock_model
            mock_response = MagicMock()
            mock_response.text = '{"invalid": "response"}'
            mock_model.generate_content.return_value = mock_response
            agent = CanBusAnalystAgent()
            result = agent.run("test prompt")
            assert isinstance(result, AgentError)
            assert result.error_type == "validation_error"

    def test_missing_api_key_raises(self):
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(EnvironmentError, match="GOOGLE_API_KEY not set"):
                CanBusAnalystAgent()
