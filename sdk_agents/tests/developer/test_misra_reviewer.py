"""
Unit tests for misra_reviewer — no API calls required.
Tests: schema structure, validator logic, skill loader, agent instantiation.
All API calls are mocked — runs without a GROQ_API_KEY.
"""

import pytest
from unittest.mock import patch, MagicMock
from sdk_agents.developer.misra_reviewer.schema import (
    MisraReviewerOutput, MisraViolation, RootCauseCluster, ActionPlanRow,
)
from sdk_agents.developer.misra_reviewer import MisraReviewerAgent
from sdk_agents.developer.misra_reviewer import validators
from sdk_agents.core.base_agent import AgentError, DomainCheckError
from sdk_agents.core.skill_loader import load_skill
from sdk_agents.core.shared_schema import SelfEvaluationLine, InputAnalysis, DataSufficiency


# ── Fixtures ──────────────────────────────────────────────────────────────────

def make_valid_output(**overrides) -> MisraReviewerOutput:
    """Build a valid MisraReviewerOutput for testing.
    Scenario: ASIL-B CAN driver module, QAC review, 1 mandatory violation (Rule 11.3).
    """
    data = {
        "file_context": "can_driver.c — CAN transmit handler ASIL-B",
        "input_analysis": InputAnalysis(
            input_facts=[
                "file: can_driver.c",
                "ASIL level: ASIL-B",
                "tool: QAC",
                "violations: 1 mandatory (Rule 11.3)",
                "total: 1 violation",
            ],
            assumptions=[
                "assumed C99 standard — not stated in review request",
                "assumed module is safety-relevant based on ASIL-B designation",
            ],
        ),
        "data_sufficiency": DataSufficiency(
            level="SUFFICIENT",
            confidence="HIGH",
            confidence_reason="C code snippet, ASIL level, tool name, and specific rule numbers all stated.",
            missing_critical_data=["None — data is complete"],
        ),
        "asil_level": "ASIL-B",
        "tool": "QAC",
        "total_violations": 1,
        "mandatory_count": 1,
        "required_count": 0,
        "advisory_count": 0,
        "violations": [
            MisraViolation(
                rule="Rule 11.3",
                violation_pattern=[
                    "uint8_t *ptr = (uint8_t *)voidPtr;  /* MISRA Rule 11.3 violation */",
                    "/* Cast from void pointer to object pointer type is prohibited */",
                ],
                explanation=(
                    "Rule 11.3 prohibits casting between a pointer to object type and a pointer to "
                    "a different object type. Void pointer casts are not type-safe and hide errors."
                ),
                compliant_rewrite=[
                    "/* Use a typed pointer from allocation — avoid void* intermediate */",
                    "uint8_t *ptr = typedBufferPtr;  /* compliant: no pointer type cast */",
                ],
            )
        ],
        "root_cause_clusters": [
            RootCauseCluster(
                cluster_name="Type discipline violations",
                rule_numbers="Rule 10.1, Rule 10.4",
                violation_count=2,
                root_cause="Habit of implicit integer promotion — training gap on essential types",
                fix_approach="Add explicit casts at all arithmetic expressions; enable QAC Rule 10.x in CI",
            ),
        ],
        "action_plan": [
            ActionPlanRow(
                priority="P2 Required Safety",
                action="Add explicit cast before mixed-type arithmetic in can_tx_handler()",
                effort_days="1",
                owner="Module owner",
            ),
        ],
        "asil_note": (
            "ASIL-B: Rule 11.3 (mandatory) must be resolved before SW integration baseline. "
            "Required rules (Rule 10.1, 10.4) need deviation or fix before SWE.4 closure."
        ),
        "self_evaluation": [
            SelfEvaluationLine(
                item="Violation counts consistent",
                result="PASS",
                evidence="total_violations=1 = mandatory(1) + required(0) + advisory(0)",
            ),
            SelfEvaluationLine(
                item="Clusters present",
                result="PASS",
                evidence="1 cluster: Type discipline violations covering Rule 10.1 and 10.4",
            ),
        ],
    }
    data.update(overrides)
    return MisraReviewerOutput(**data)


# ── Schema tests ──────────────────────────────────────────────────────────────

class TestSchemaStructure:
    def test_valid_output_instantiates(self):
        output = make_valid_output()
        assert output.file_context == "can_driver.c — CAN transmit handler ASIL-B"

    def test_action_plan_priority_must_be_valid(self):
        with pytest.raises(Exception):
            ActionPlanRow(
                priority="P5 Ignore",  # invalid — not in Literal
                action="Fix something",
                effort_days="1",
                owner="Module owner",
            )

    def test_violation_with_list_fields(self):
        """MisraViolation violation_pattern and compliant_rewrite are list[str]."""
        v = MisraViolation(
            rule="Rule 11.3",
            violation_pattern=["uint8_t *ptr = (uint8_t *)voidPtr;  /* MISRA Rule 11.3 violation */"],
            explanation="Cast from void* to object pointer type is prohibited by Rule 11.3",
            compliant_rewrite=["/* Use typed pointer from the start — avoid void* intermediate */",
                               "uint8_t *ptr = typedPtr;"],
        )
        assert isinstance(v.violation_pattern, list)
        assert isinstance(v.compliant_rewrite, list)

    def test_schema_has_required_fields(self):
        schema = MisraReviewerOutput.model_json_schema()
        required = schema.get("required", [])
        for field in [
            "file_context", "asil_level", "tool", "total_violations",
            "violations", "root_cause_clusters", "action_plan",
            "asil_note", "self_evaluation",
        ]:
            assert field in required, f"'{field}' missing from schema required list"

    def test_schema_extra_is_ignore(self):
        output = MisraReviewerOutput.model_validate(
            {**make_valid_output().model_dump(), "extra_field": "x"}
        )
        assert output.asil_level == "ASIL-B"

    def test_input_analysis_present(self):
        output = make_valid_output()
        assert output.input_analysis is not None
        assert len(output.input_analysis.input_facts) > 0

    def test_input_analysis_has_tool_fact(self):
        output = make_valid_output()
        assert any("QAC" in f for f in output.input_analysis.input_facts)

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
                confidence_reason="ASIL level not stated — assumed ASIL-B from module name.",
                missing_critical_data=["[CRITICAL] ASIL level — determines mandatory vs required violation priority"],
            )
        )
        assert output.data_sufficiency.level == "PARTIAL"
        assert len(output.data_sufficiency.missing_critical_data) > 0


# ── Validator tests ───────────────────────────────────────────────────────────

class TestValidators:
    def test_valid_output_passes(self):
        validators.validate(make_valid_output())

    def test_violation_count_mismatch_fails(self):
        output = make_valid_output(
            total_violations=5,  # claims 5 but 1+0+0=1
            mandatory_count=1,
            required_count=0,
            advisory_count=0,
        )
        with pytest.raises(DomainCheckError, match="does not match"):
            validators.validate(output)

    def test_empty_clusters_fails(self):
        output = make_valid_output(root_cause_clusters=[])
        with pytest.raises(DomainCheckError, match="empty"):
            validators.validate(output)

    def test_action_plan_missing_effort_fails(self):
        row = ActionPlanRow(
            priority="P1 Mandatory",
            action="Fix the Rule 11.3 violation in can_driver.c",
            effort_days="",  # empty effort
            owner="Module owner",
        )
        output = make_valid_output(action_plan=[row])
        with pytest.raises(DomainCheckError, match="effort_days is empty"):
            validators.validate(output)

    def test_short_asil_note_fails(self):
        output = make_valid_output(asil_note="ASIL-B applies")  # too short
        with pytest.raises(DomainCheckError, match="too short"):
            validators.validate(output)

    def test_self_eval_pass_without_evidence_fails(self):
        output = make_valid_output(self_evaluation=[
            SelfEvaluationLine(item="Counts", result="PASS", evidence="ok")
        ])
        with pytest.raises(DomainCheckError, match="evidence is empty or too short"):
            validators.validate(output)

    def test_violation_with_short_pattern_fails(self):
        """Validator must reject violations whose pattern is too short (tests list[str] join fix)."""
        short_violation = MisraViolation(
            rule="Rule 11.3",
            violation_pattern=["x = y;"],  # too short — only 6 chars
            explanation="Cast violation",
            compliant_rewrite=["uint8_t *ptr = typedPtr;  /* compliant rewrite */"],
        )
        output = make_valid_output(violations=[short_violation])
        with pytest.raises(DomainCheckError, match="violation_pattern is too short"):
            validators.validate(output)

    def test_violation_with_short_rewrite_fails(self):
        """Validator must reject violations whose rewrite is too short (tests list[str] join fix)."""
        short_rewrite_violation = MisraViolation(
            rule="Rule 11.3",
            violation_pattern=[
                "uint8_t *ptr = (uint8_t *)voidPtr;  /* MISRA Rule 11.3 violation */",
            ],
            explanation="Cast from void pointer to object pointer type is prohibited",
            compliant_rewrite=["ptr = buf;"],  # too short — only 9 chars
        )
        output = make_valid_output(violations=[short_rewrite_violation])
        with pytest.raises(DomainCheckError, match="compliant_rewrite is too short"):
            validators.validate(output)


# ── Skill loader tests ────────────────────────────────────────────────────────

class TestSkillLoader:
    def test_misra_skill_loads(self):
        content = load_skill("misra-c-2012")
        assert len(content) > 100

    def test_misra_skill_contains_rule_content(self):
        content = load_skill("misra-c-2012")
        assert "Rule" in content or "MISRA" in content

    def test_unknown_skill_raises(self):
        with pytest.raises(FileNotFoundError, match="not found"):
            load_skill("nonexistent-skill")


# ── Agent instantiation tests (no API calls) ─────────────────────────────────

class TestAgentInstantiation:
    def test_agent_instantiates(self):
        with patch("sdk_agents.core.base_agent.Groq"), \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            agent = MisraReviewerAgent()
            assert agent.AGENT_NAME == "misra-reviewer"

    def test_get_schema_returns_correct_type(self):
        with patch("sdk_agents.core.base_agent.Groq"), \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            agent = MisraReviewerAgent()
            assert agent.get_schema() is MisraReviewerOutput

    def test_get_prompt_returns_string_with_misra_content(self):
        with patch("sdk_agents.core.base_agent.Groq"), \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            agent = MisraReviewerAgent()
            prompt = agent.get_prompt()
            assert isinstance(prompt, str)
            assert "MISRA" in prompt
            assert "Rule" in prompt

    def test_prompt_contains_asil_guidance(self):
        with patch("sdk_agents.core.base_agent.Groq"), \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            agent = MisraReviewerAgent()
            prompt = agent.get_prompt()
            assert "ASIL" in prompt or "deviation" in prompt.lower()

    def test_api_error_returns_agent_error(self):
        with patch("sdk_agents.core.base_agent.Groq") as mock_groq_cls, \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            mock_client = MagicMock()
            mock_groq_cls.return_value = mock_client
            mock_client.chat.completions.create.side_effect = Exception("API connection failed")
            agent = MisraReviewerAgent()
            result = agent.run("MISRA review for CAN driver ASIL-B module")
            assert isinstance(result, AgentError)
            assert result.error_type == "api_error"

    def test_missing_api_key_raises(self):
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(EnvironmentError, match="GROQ_API_KEY not set"):
                MisraReviewerAgent()
