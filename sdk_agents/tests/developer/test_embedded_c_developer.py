"""
Unit tests for embedded_c_developer — no API calls required.
Tests: schema structure, validator logic, skill loader, agent instantiation.
All API calls are mocked — runs without a GROQ_API_KEY.
"""

import pytest
from unittest.mock import patch, MagicMock
from sdk_agents.developer.embedded_c_developer.schema import (
    EmbeddedCDeveloperOutput, LayerDiagnosis, CfsrDecode, MisraNote,
    InputAnalysis, DataSufficiency,
)
from sdk_agents.developer.embedded_c_developer import EmbeddedCDeveloperAgent
from sdk_agents.developer.embedded_c_developer import validators
from sdk_agents.core.base_agent import AgentError, DomainCheckError
from sdk_agents.core.skill_loader import load_skills
from sdk_agents.core.shared_schema import SelfEvaluationLine, NarrowingQuestion


# ── Fixtures ──────────────────────────────────────────────────────────────────

def make_valid_output(**overrides) -> EmbeddedCDeveloperOutput:
    """Build a valid EmbeddedCDeveloperOutput for testing.
    Scenario: Stack overflow during CAN ISR on TC387 — RTOS layer fault.
    """
    data = {
        "problem_classification": (
            "Stack overflow during CAN ISR on TC387 — RTOS layer fault"
        ),
        "input_analysis": InputAnalysis(
            input_facts=[
                "MCU: Infineon TC387",
                "Symptom: ECU resets randomly during high CAN bus load",
                "CFSR = 0x02000000 observed in TRACE32 after crash",
                "CAN_Task stack allocated: 512 bytes",
                "RTOS: AUTOSAR OS",
            ],
            assumptions=[
                "Assumed task call depth is 3 levels — exact call chain not provided",
                "Assumed 500 kbps CAN rate — baudrate not stated",
            ],
        ),
        "data_sufficiency": DataSufficiency(
            level="PARTIAL",
            confidence="MEDIUM",
            confidence_reason=(
                "CFSR value and stack allocation are present but call chain depth "
                "and local variable sizes are not provided — stack calculation requires assumptions"
            ),
            missing_critical_data=[
                "[CRITICAL] sizeof each local variable in CAN_Task — needed for exact stack sizing",
                "[CRITICAL] TRACE32 Task window stack HWM — needed to confirm overflow vs other fault",
                "[OPTIONAL] Call chain depth from TRACE32 Call Stack — would remove assumption on depth",
            ],
        ),
        "layer_diagnosis": [
            LayerDiagnosis(
                layer="Physical",
                status="CLEAR",
                evidence="CAN controller TEC/REC at zero — no bus errors; power supply stable at 3.3 V",
                tool="TRACE32 Peripheral register window",
                check="CAN TEC register = 0x00, VCC measurement at ECU pin",
            ),
            LayerDiagnosis(
                layer="RTOS",
                status="SUSPECT",
                evidence="CFSR = 0x02000000 (Bit 25 STKERR) indicates stack push failure on exception entry",
                tool="TRACE32 Task window",
                check="CAN_Task stack HWM — check remaining bytes vs allocated 512",
            ),
            LayerDiagnosis(
                layer="Application",
                status="UNKNOWN",
                evidence="Application logic not yet ruled out — pending RTOS confirmation",
                tool="TRACE32 Watch window",
                check="State machine state variable after reset — check for unexpected state",
            ),
        ],
        "cfsr_decode": CfsrDecode(
            cfsr_value="0x02000000",
            bit_set="Bit 25 STKERR",
            meaning=(
                "Stack push failed during exception entry — "
                "the processor attempted to save context to stack but ran out of stack space"
            ),
            action=(
                "Increase CAN_Task stack from 512 to 768 bytes. "
                "Verify with TRACE32 Task window stack HWM after fix."
            ),
        ),
        "root_cause": (
            "Stack overflow in CAN_Task during ISR preemption — "
            "RTOS layer fault confirmed by CFSR Bit 25 STKERR"
        ),
        "code_pattern": (
            "#define CAN_TASK_STACK_SIZE  768U  /* increased from 512U — STKERR Bit25 */\n"
            "static StackType_t xCanTaskStack[CAN_TASK_STACK_SIZE];\n"
            "/* Rule 8.4: external definition must match — update header too */"
        ),
        "misra_notes": [
            MisraNote(
                rule="Rule 8.4",
                category="Required",
                violation_pattern="uint32_t g_canCount;  /* defined without matching header declaration */",
                compliant_fix="extern uint32_t g_canCount;  /* header: sdk_agents/can_task.h */",
            ),
        ],
        "rtos_calc": [
            "Stack Sizing — worst-case calculation",
            "base_frame: 3 locals × 4 bytes = 12 bytes",
            "call_chain: 3 frames × 80 bytes = 240 bytes (assumed depth — not provided)",
            "ISR_frame: 8 registers × 4 bytes = 32 bytes",
            "subtotal = 12 + 240 + 32 = 284 bytes",
            "safety_margin: 284 × 0.20 = 57 bytes",
            "worst_case = 284 + 57 = 341 bytes",
            "→ Calculated worst-case stack: 341 bytes. This fits within the allocated 512 bytes — SAFE on paper, but CFSR Bit25 fired. Provide exact call depth to confirm.",
        ],
        "cpu_load_calc": ["N/A — symptom does not indicate CPU load as the cause"],
        "narrowing_questions": [
            NarrowingQuestion(
                question="Does the TRACE32 Task window show CAN_Task stack HWM below 32 bytes remaining?",
                yes_consequence="Stack overflow confirmed — increase CAN_Task stack allocation",
                no_consequence="Stack has headroom — investigate ISR preemption depth or other fault source",
            ),
            NarrowingQuestion(
                question="Does the crash reproduce only during high CAN bus load (>60%)?",
                yes_consequence="Load-dependent stack depth — ISR nesting during burst likely culprit",
                no_consequence="Random reset unrelated to load — check WDT configuration or power supply",
            ),
            NarrowingQuestion(
                question="Is the CFSR value 0x02000000 on every reset or only occasionally?",
                yes_consequence="Deterministic STKERR — stack size is consistently insufficient",
                no_consequence="Intermittent — secondary cause; check for memory corruption corrupting stack pointer",
            ),
        ],
        "self_evaluation": [
            SelfEvaluationLine(
                item="input_analysis",
                result="PASS",
                evidence="5 input facts extracted, 2 assumptions stated — call depth and baudrate",
            ),
            SelfEvaluationLine(
                item="data_sufficiency",
                result="PASS",
                evidence="PARTIAL level set — sizeof locals and stack HWM flagged as missing critical",
            ),
            SelfEvaluationLine(
                item="layer_diagnosis",
                result="PASS",
                evidence="All 3 layers covered: Physical=CLEAR, RTOS=SUSPECT, Application=UNKNOWN",
            ),
            SelfEvaluationLine(
                item="cfsr_decode",
                result="PASS",
                evidence="CFSR 0x02000000 decoded to Bit 25 STKERR with meaning and action",
            ),
            SelfEvaluationLine(
                item="code_pattern",
                result="PASS",
                evidence="Actual C code shown with stack size constant and MISRA Rule 8.4 comment",
            ),
        ],
    }
    data.update(overrides)
    return EmbeddedCDeveloperOutput(**data)


# ── Schema structure tests ─────────────────────────────────────────────────────

class TestSchemaStructure:
    def test_valid_output_builds(self):
        output = make_valid_output()
        assert "TC387" in output.problem_classification

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
                confidence_reason="CFSR, stack HWM, and call depth all provided",
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

    def test_layer_diagnosis_has_three_layers(self):
        output = make_valid_output()
        layers = {d.layer for d in output.layer_diagnosis}
        assert layers == {"Physical", "RTOS", "Application"}

    def test_narrowing_questions_exactly_three(self):
        output = make_valid_output()
        assert len(output.narrowing_questions) == 3

    def test_schema_extra_is_ignore(self):
        output = EmbeddedCDeveloperOutput.model_validate(
            {**make_valid_output().model_dump(), "extra_field": "x"}
        )
        assert "TC387" in output.problem_classification


# ── Validator tests ────────────────────────────────────────────────────────────

class TestValidators:
    def test_valid_output_passes(self):
        validators.validate(make_valid_output())

    def test_all_layers_clear_fails(self):
        layers = [
            LayerDiagnosis(layer="Physical", status="CLEAR", evidence="no issue found", tool="scope", check="VCC"),
            LayerDiagnosis(layer="RTOS", status="CLEAR", evidence="stack ok", tool="TRACE32", check="HWM"),
            LayerDiagnosis(layer="Application", status="CLEAR", evidence="logic ok", tool="DLT", check="state"),
        ]
        output = make_valid_output(layer_diagnosis=layers)
        with pytest.raises(DomainCheckError, match="No layer is marked SUSPECT"):
            validators.validate(output)

    def test_missing_layer_fails(self):
        """Duplicate layer means one required layer name is absent — validator catches it."""
        layers = [
            LayerDiagnosis(layer="Physical", status="SUSPECT", evidence="voltage sag at 2.8 V", tool="scope", check="VCC"),
            LayerDiagnosis(layer="RTOS", status="CLEAR", evidence="stack headroom 200 bytes", tool="TRACE32", check="HWM"),
            LayerDiagnosis(layer="Physical", status="CLEAR", evidence="secondary check clean", tool="scope", check="GND"),
        ]
        output = make_valid_output(layer_diagnosis=layers)
        with pytest.raises(DomainCheckError, match="missing layers"):
            validators.validate(output)

    def test_cfsr_meaning_too_short_fails(self):
        cfsr = CfsrDecode(
            cfsr_value="0x02000000",
            bit_set="Bit 25",
            meaning="stack",  # too short
            action="increase stack",
        )
        output = make_valid_output(cfsr_decode=cfsr)
        with pytest.raises(DomainCheckError, match="cfsr_decode.meaning is too short"):
            validators.validate(output)

    def test_code_pattern_too_short_fails(self):
        output = make_valid_output(code_pattern="fix it")  # too short
        with pytest.raises(DomainCheckError, match="code_pattern is too short"):
            validators.validate(output)

    def test_root_cause_must_reference_suspect_layer(self):
        output = make_valid_output(
            root_cause="The ECU resets due to a configuration error"  # no RTOS reference
        )
        with pytest.raises(DomainCheckError, match="root_cause does not reference"):
            validators.validate(output)

    def test_rtos_calc_na_is_valid(self):
        output = make_valid_output(rtos_calc=["N/A — no RTOS involved in this scenario"])
        validators.validate(output)

    def test_cpu_load_calc_na_is_valid(self):
        output = make_valid_output(cpu_load_calc=["N/A — symptom does not indicate CPU load"])
        validators.validate(output)

    def test_self_eval_pass_without_evidence_fails(self):
        output = make_valid_output(self_evaluation=[
            SelfEvaluationLine(item="layer_diagnosis", result="PASS", evidence="ok"),
        ])
        with pytest.raises(DomainCheckError, match="evidence is empty or too short"):
            validators.validate(output)


# ── Skill loader tests ────────────────────────────────────────────────────────

class TestSkillLoader:
    def test_misra_skill_loads(self):
        content = load_skills("misra-c-2012")
        assert len(content) > 100

    def test_embedded_patterns_skill_loads(self):
        content = load_skills("embedded-patterns")
        assert len(content) > 100

    def test_prompt_loads_without_error(self):
        from sdk_agents.developer.embedded_c_developer.prompt import get_system_prompt
        prompt = get_system_prompt()
        assert len(prompt) > 100


# ── Agent instantiation tests (no API calls) ─────────────────────────────────

class TestAgentInstantiation:
    def test_agent_instantiates(self):
        with patch("sdk_agents.core.base_agent.Groq"), \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            agent = EmbeddedCDeveloperAgent()
            assert agent.AGENT_NAME == "embedded-c-developer"

    def test_get_schema_returns_correct_type(self):
        with patch("sdk_agents.core.base_agent.Groq"), \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            agent = EmbeddedCDeveloperAgent()
            assert agent.get_schema() is EmbeddedCDeveloperOutput

    def test_get_prompt_returns_string_with_embedded_content(self):
        with patch("sdk_agents.core.base_agent.Groq"), \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            agent = EmbeddedCDeveloperAgent()
            prompt = agent.get_prompt()
            assert isinstance(prompt, str)
            assert "CFSR" in prompt or "stack" in prompt.lower()

    def test_prompt_contains_anti_pattern_guard(self):
        with patch("sdk_agents.core.base_agent.Groq"), \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            agent = EmbeddedCDeveloperAgent()
            prompt = agent.get_prompt()
            assert "Anti-Pattern Guard" in prompt

    def test_api_error_returns_agent_error(self):
        with patch("sdk_agents.core.base_agent.Groq") as mock_groq_cls, \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            mock_client = MagicMock()
            mock_groq_cls.return_value = mock_client
            mock_client.chat.completions.create.side_effect = Exception("API connection failed")
            agent = EmbeddedCDeveloperAgent()
            result = agent.run("ECU resets during CAN ISR on TC387")
            assert isinstance(result, AgentError)
            assert result.error_type == "api_error"

    def test_missing_api_key_raises(self):
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(EnvironmentError, match="GROQ_API_KEY not set"):
                EmbeddedCDeveloperAgent()
