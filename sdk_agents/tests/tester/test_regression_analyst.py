"""
Unit tests for regression_analyst — no API calls required.
Tests: schema structure, validator logic, skill loader, agent instantiation.
All API calls are mocked — runs without a GROQ_API_KEY.
"""

import pytest
from unittest.mock import patch, MagicMock
from sdk_agents.tester.regression_analyst.schema import (
    RegressionAnalystOutput, RegressionSummary, FailureCluster,
    CoverageDelta,
)
from sdk_agents.tester.regression_analyst import RegressionAnalystAgent
from sdk_agents.tester.regression_analyst import validators
from sdk_agents.core.base_agent import AgentError, DomainCheckError
from sdk_agents.core.skill_loader import load_skill
from sdk_agents.core.shared_schema import SelfEvaluationLine


# ── Fixtures ──────────────────────────────────────────────────────────────────

def make_valid_output(**overrides) -> RegressionAnalystOutput:
    data = {
        "build_current": "SW-1.4.2-RC3",
        "build_baseline": "SW-1.4.1-release",
        "summary": RegressionSummary(
            previous_pass=1015,
            previous_fail=2,
            previous_coverage_pct="87.3%",
            current_pass=990,
            current_fail=27,
            current_coverage_pct="84.1%",
            new_failures=25,
            asil_d_affected=3,
            asil_b_affected=8,
            qm_affected=14,
        ),
        "failure_clusters": [
            FailureCluster(
                cluster_name="ASIL-D safety monitor failures",
                failure_count=3,
                risk_level="ASIL-D",
                probable_cause="CAN API contract change in CanIf_Transmit broke safety monitor polling",
                confirming_check="diff CanIf.h between baseline and RC3 — look for return type change",
            ),
            FailureCluster(
                cluster_name="CAN driver integration failures",
                failure_count=8,
                risk_level="ASIL-B",
                probable_cause="New CanDrv version 3.2 changed Tx confirmation callback signature",
                confirming_check="check CanDrv_3.2 release notes for API breaking changes",
            ),
            FailureCluster(
                cluster_name="Signal processing QM tests",
                failure_count=14,
                risk_level="QM",
                probable_cause="Refactored signal normalisation function changed floating point rounding",
                confirming_check="run git diff on SignalProc.c between SW-1.4.1 and RC3",
            ),
        ],
        "coverage_deltas": [
            CoverageDelta(
                module="SafetyMonitor",
                previous_pct="92.1%",
                current_pct="88.9%",
                delta_pct="-3.2%",
                lost_function="SafetyMonitor_CheckHeartbeat — branch not covered after API change",
                is_blocker="YES",
            ),
        ],
        "flaky_test_assessment": (
            "No flaky tests identified. All 25 new failures are deterministic — "
            "they fail on every run without variation."
        ),
        "environment_vs_sw": (
            "Real SW defect — failures are consistent across three clean builds. "
            "Test harness unchanged between baseline and RC3."
        ),
        "investigation_sequence": (
            "1. ASIL-D cluster first: diff CanIf.h API, fix safety monitor — HOLD until resolved. "
            "2. ASIL-B cluster: check CanDrv callback signature, update integration stubs. "
            "3. QM cluster: review SignalProc.c rounding change, confirm expected behaviour."
        ),
        "aspice_impact": (
            "SWE.5 integration test baseline cannot be cut — ASIL-D failures block release."
        ),
        "hold_proceed_recommendation": "HOLD",
        "hold_proceed_rationale": (
            "ASIL-D safety monitor failures are present. "
            "Per policy, ASIL-D failures trigger HOLD until root cause confirmed and fixed."
        ),
        "self_evaluation": [
            SelfEvaluationLine(
                item="Failure clustering",
                result="PASS",
                evidence="3 clusters: ASIL-D=3, ASIL-B=8, QM=14, each with specific probable cause",
            ),
            SelfEvaluationLine(
                item="HOLD/PROCEED recommendation",
                result="PASS",
                evidence="HOLD stated, ASIL-D blocking cluster named as justification",
            ),
        ],
    }
    data.update(overrides)
    return RegressionAnalystOutput(**data)


# ── Schema tests ──────────────────────────────────────────────────────────────

class TestSchema:
    def test_valid_output_instantiates(self):
        output = make_valid_output()
        assert output.build_current == "SW-1.4.2-RC3"

    def test_hold_proceed_must_be_valid(self):
        with pytest.raises(Exception):
            make_valid_output(hold_proceed_recommendation="MAYBE")

    def test_failure_cluster_risk_level_must_be_valid(self):
        with pytest.raises(Exception):
            FailureCluster(
                cluster_name="test",
                failure_count=1,
                risk_level="CRITICAL",  # invalid
                probable_cause="some specific cause identified",
                confirming_check="check the module",
            )

    def test_coverage_delta_is_blocker_must_be_valid(self):
        with pytest.raises(Exception):
            CoverageDelta(
                module="TestModule",
                previous_pct="90%",
                current_pct="85%",
                delta_pct="-5%",
                lost_function="some function",
                is_blocker="MAYBE",  # invalid
            )

    def test_schema_has_required_fields(self):
        schema = RegressionAnalystOutput.model_json_schema()
        required = schema.get("required", [])
        for field in [
            "build_current", "build_baseline", "summary", "failure_clusters",
            "coverage_deltas", "hold_proceed_recommendation", "hold_proceed_rationale",
            "self_evaluation",
        ]:
            assert field in required, f"'{field}' missing from schema required list"

    def test_schema_extra_is_ignore(self):
        output = RegressionAnalystOutput.model_validate(
            {**make_valid_output().model_dump(), "extra_field": "x"}
        )
        assert output.build_current == "SW-1.4.2-RC3"


# ── Validator tests ───────────────────────────────────────────────────────────

class TestValidators:
    def test_valid_output_passes(self):
        validators.validate(make_valid_output())

    def test_new_failures_exceeding_current_fail_fails(self):
        summary = RegressionSummary(
            previous_pass=1000,
            previous_fail=2,
            previous_coverage_pct="90%",
            current_pass=990,
            current_fail=10,
            current_coverage_pct="89%",
            new_failures=20,  # > current_fail=10
            asil_d_affected=0,
            asil_b_affected=5,
            qm_affected=5,
        )
        output = make_valid_output(summary=summary)
        with pytest.raises(DomainCheckError, match="new_failures.*current_fail"):
            validators.validate(output)

    def test_asil_d_failures_with_proceed_fails(self):
        summary = RegressionSummary(
            previous_pass=1000, previous_fail=0, previous_coverage_pct="90%",
            current_pass=995, current_fail=5, current_coverage_pct="89%",
            new_failures=5, asil_d_affected=2, asil_b_affected=3, qm_affected=0,
        )
        output = make_valid_output(
            summary=summary,
            hold_proceed_recommendation="PROCEED",
        )
        with pytest.raises(DomainCheckError, match="ASIL-D failures must be HOLD"):
            validators.validate(output)

    def test_asil_d_failures_without_asil_d_cluster_fails(self):
        summary = RegressionSummary(
            previous_pass=1000, previous_fail=0, previous_coverage_pct="90%",
            current_pass=995, current_fail=3, current_coverage_pct="89%",
            new_failures=3, asil_d_affected=3, asil_b_affected=0, qm_affected=0,
        )
        clusters = [
            FailureCluster(
                cluster_name="QM signal failures",
                failure_count=3,
                risk_level="QM",  # wrong — should be ASIL-D
                probable_cause="Signal normalisation change broke QM tests",
                confirming_check="diff SignalProc.c between builds",
            )
        ]
        output = make_valid_output(
            summary=summary,
            failure_clusters=clusters,
            hold_proceed_recommendation="HOLD",
        )
        with pytest.raises(DomainCheckError, match="no cluster has risk_level='ASIL-D'"):
            validators.validate(output)

    def test_vague_cluster_cause_fails(self):
        # Use zero ASIL-D failures so the ASIL-D cluster check does not fire first
        summary_no_asil_d = RegressionSummary(
            previous_pass=1000, previous_fail=2, previous_coverage_pct="90%",
            current_pass=995, current_fail=7, current_coverage_pct="89%",
            new_failures=5, asil_d_affected=0, asil_b_affected=5, qm_affected=0,
        )
        cluster = FailureCluster(
            cluster_name="CAN failures",
            failure_count=5,
            risk_level="ASIL-B",
            probable_cause="code change",  # too vague — under 15 chars
            confirming_check="check the module diff",
        )
        output = make_valid_output(
            summary=summary_no_asil_d,
            failure_clusters=[cluster],
            hold_proceed_recommendation="PROCEED_WITH_EXCEPTIONS",
        )
        with pytest.raises(DomainCheckError, match="probable_cause is too vague"):
            validators.validate(output)

    def test_hold_proceed_rationale_too_short_fails(self):
        output = make_valid_output(hold_proceed_rationale="HOLD")
        with pytest.raises(DomainCheckError, match="hold_proceed_rationale is too short"):
            validators.validate(output)

    def test_blocker_coverage_without_lost_function_fails(self):
        delta = CoverageDelta(
            module="SafetyMonitor",
            previous_pct="92%",
            current_pct="88%",
            delta_pct="-4%",
            lost_function="",  # empty — required when blocker=YES
            is_blocker="YES",
        )
        output = make_valid_output(coverage_deltas=[delta])
        with pytest.raises(DomainCheckError, match="lost_function is empty"):
            validators.validate(output)

    def test_self_eval_pass_without_evidence_fails(self):
        output = make_valid_output(self_evaluation=[
            SelfEvaluationLine(item="Clustering", result="PASS", evidence="ok")
        ])
        with pytest.raises(DomainCheckError, match="evidence is empty or too short"):
            validators.validate(output)

    def test_no_asil_d_allows_proceed(self):
        """No ASIL-D failures — PROCEED is acceptable."""
        summary = RegressionSummary(
            previous_pass=1000, previous_fail=2, previous_coverage_pct="90%",
            current_pass=997, current_fail=5, current_coverage_pct="89%",
            new_failures=3, asil_d_affected=0, asil_b_affected=3, qm_affected=0,
        )
        output = make_valid_output(
            summary=summary,
            hold_proceed_recommendation="PROCEED_WITH_EXCEPTIONS",
        )
        validators.validate(output)  # should not raise


# ── Skill loader tests ────────────────────────────────────────────────────────

class TestSkillLoader:
    def test_aspice_process_skill_loads(self):
        content = load_skill("aspice-process")
        assert len(content) > 100

    def test_aspice_skill_contains_swe4_content(self):
        content = load_skill("aspice-process")
        assert "SWE.4" in content or "SWE.5" in content

    def test_unknown_skill_raises(self):
        with pytest.raises(FileNotFoundError, match="not found"):
            load_skill("nonexistent-skill")


# ── Agent instantiation tests (no API calls) ─────────────────────────────────

class TestAgentInstantiation:
    def test_agent_instantiates(self):
        with patch("sdk_agents.core.base_agent.Groq"), \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            agent = RegressionAnalystAgent()
            assert agent.AGENT_NAME == "regression-analyst"

    def test_get_schema_returns_correct_type(self):
        with patch("sdk_agents.core.base_agent.Groq"), \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            agent = RegressionAnalystAgent()
            assert agent.get_schema() is RegressionAnalystOutput

    def test_get_prompt_returns_string_with_regression_content(self):
        with patch("sdk_agents.core.base_agent.Groq"), \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            agent = RegressionAnalystAgent()
            prompt = agent.get_prompt()
            assert isinstance(prompt, str)
            assert "HOLD" in prompt or "PROCEED" in prompt
            assert "ASIL" in prompt

    def test_prompt_contains_anti_pattern_guard(self):
        with patch("sdk_agents.core.base_agent.Groq"), \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            agent = RegressionAnalystAgent()
            prompt = agent.get_prompt()
            assert "Anti-Pattern Guard" in prompt

    def test_api_error_returns_agent_error(self):
        with patch("sdk_agents.core.base_agent.Groq") as mock_groq_cls, \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            mock_client = MagicMock()
            mock_groq_cls.return_value = mock_client
            mock_client.chat.completions.create.side_effect = Exception("API connection failed")
            agent = RegressionAnalystAgent()
            result = agent.run("Regression delta analysis SW-1.4.2")
            assert isinstance(result, AgentError)
            assert result.error_type == "api_error"

    def test_missing_api_key_raises(self):
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(EnvironmentError, match="GROQ_API_KEY not set"):
                RegressionAnalystAgent()
