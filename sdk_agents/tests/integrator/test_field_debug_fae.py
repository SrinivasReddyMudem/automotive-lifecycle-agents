"""
Unit tests for field_debug_fae — no API calls required.
Tests: schema structure, validator logic, skill loader, agent instantiation.
All API calls are mocked — runs without a GROQ_API_KEY.
"""

import pytest
from unittest.mock import patch, MagicMock
from sdk_agents.integrator.field_debug_fae.schema import (
    FieldDebugFaeOutput, SymptomTranslation, FaultDetails,
    UdsSessionAnalysis, ProbableCause, SelfEvaluationLine, DebugStep,
    ProtocolDetection, InputAnalysis, DataSufficiency,
)
from sdk_agents.integrator.field_debug_fae import FieldDebugFaeAgent
from sdk_agents.integrator.field_debug_fae import validators
from sdk_agents.core.base_agent import AgentError, DomainCheckError
from sdk_agents.core.skill_loader import load_skills


# ── Fixtures ──────────────────────────────────────────────────────────────────

def make_valid_output(**overrides) -> FieldDebugFaeOutput:
    """Build a valid FieldDebugFaeOutput for testing.
    Scenario: Customer says door not unlocking after ignition on.
    DTC U0100 stored, status byte 0x09, NRC 0x22 in extended session.
    """
    data = {
        "protocol_detection": ProtocolDetection(
            protocol="CAN",
            detected_from="DTC U0100 (lost communication with ECM) — CAN transport; NRC 0x22 from UDS session log",
            confidence="MEDIUM",
        ),
        "input_analysis": InputAnalysis(
            input_facts=[
                "Customer complaint: door not unlocking after ignition on",
                "DTC U0100 stored (loss of communication with ECM)",
                "DTC status byte: 0x09",
                "NRC 0x22 received during extendedDiagnosticSession request",
            ],
            assumptions=[
                "Assumed BCM is the reporting ECU — not explicitly stated",
                "Assumed standard CAN 500 kbps — baudrate not provided",
            ],
        ),
        "data_sufficiency": DataSufficiency(
            level="PARTIAL",
            confidence="MEDIUM",
            confidence_reason=(
                "DTC code and NRC are present but status byte decode and freeze frame "
                "data are missing — cannot confirm if fault is active or historic"
            ),
            missing_critical_data=[
                "[CRITICAL] Freeze frame data — sensor/actuator state at moment of fault needed "
                "to confirm operating conditions",
                "[CRITICAL] UDS session log — needed to reconstruct session sequence and identify "
                "where the 0x22 NRC was generated",
            ],
        ),
        "symptom_translation": SymptomTranslation(
            customer_complaint="Door not unlocking after ignition on",
            function_affected="Body control — door lock actuator",
            translated_to="CAN communication loss at DCM / CanIf layer — U0100 indicates loss of comms with ECM",
            autosar_layer="DCM / CanIf",
            osi_layer="L2 / L5",
        ),
        "fault_details": FaultDetails(
            dtc_code="U0100",
            dtc_description="Lost communication with ECM / PCM A",
            status_byte="0x09",
            status_byte_decoded=(
                "Bit 0 = 1 (testFailed — fault active now); "
                "Bit 3 = 1 (confirmedDTC — fault confirmed across multiple cycles); "
                "Bits 1,2,4,5,6,7 = 0"
            ),
            system="BCM (Body Control Module)",
            safety_relevant="NO",
            safety_impact="Not safety-critical — door lock function only",
        ),
        "uds_session_analysis": UdsSessionAnalysis(
            nrc_code="0x22",
            nrc_name="conditionsNotCorrect",
            nrc_root_causes=[
                "Security access (0x27 seed/key) not completed before the service requiring it",
                "Vehicle operating condition not met — engine running or speed > 0 may be required",
                "Previous operation not complete or cooldown timer still active from prior attempt",
            ],
            session_sequence_issue=(
                "Expected: 0x10 0x03 (extendedSession) → 0x27 0x01 (requestSeed) → "
                "0x27 0x02 (sendKey) → service. "
                "Observed: 0x10 0x03 → service directly → NRC 0x22. "
                "Security access step was skipped."
            ),
        ),
        "probable_causes": [
            ProbableCause(
                rank="HIGH",
                is_hypothesis=False,
                description="CAN communication loss between BCM and ECM",
                ranking_reason=(
                    "U0100 directly states loss of communication — status byte 0x09 confirms "
                    "fault is active and confirmed, not historic"
                ),
                test=(
                    "CANoe: monitor CAN channel for ECM message IDs while cycling ignition — "
                    "check if ECM messages are present on bus"
                ),
                pass_criteria="ECM CAN messages present at correct ID and DLC within 500 ms of ignition on",
                fail_criteria="ECM messages absent or with error frames — CAN wiring or ECM power fault",
                validation_test=(
                    "CANoe trace during ignition cycle — if ECM ID absent confirmed CAN loss, "
                    "if ECM ID present investigate BCM receive path"
                ),
            ),
            ProbableCause(
                rank="HIGH",
                is_hypothesis=False,
                description="Security access sequence not completed before service call",
                ranking_reason=(
                    "NRC 0x22 in extended session specifically indicates precondition failure, "
                    "not session type error — session sequence issue identified"
                ),
                test=(
                    "CANoe diagnostic console: send 0x10 0x03, then 0x27 0x01 seed request, "
                    "then 0x27 0x02 with calculated key, then retry the failing service"
                ),
                pass_criteria="Service returns positive response after security access completes",
                fail_criteria="NRC 0x22 persists after correct security sequence — investigate vehicle state preconditions",
                validation_test=(
                    "Send full sequence 0x10 0x03 → 0x27 01/02 → service — positive response "
                    "confirms sequence issue, NRC 0x22 still means vehicle state precondition"
                ),
            ),
            ProbableCause(
                rank="MEDIUM",
                is_hypothesis=True,
                description="BCM software state machine stuck after previous failed session",
                ranking_reason=(
                    "Attempt counter or cooldown timer from prior NRC 0x36 could block new "
                    "session — less likely than sequence error but possible if retries were made"
                ),
                test=(
                    "ECU reset via 0x11 0x01 (hardReset), wait 10 s, retry full session sequence — "
                    "check if NRC 0x22 clears after reset"
                ),
                pass_criteria="Service succeeds after ECU reset and fresh session — state machine was stuck",
                fail_criteria="NRC 0x22 persists after reset — root cause is not state machine, investigate preconditions",
                validation_test=(
                    "0x11 0x01 hardReset → 30 s wait → 0x10 0x03 → service — "
                    "success confirms stuck state, failure points to precondition or wiring"
                ),
            ),
        ],
        "tec_math": ["N/A — no CAN trace involved; fault is UDS session and DTC based"],
        "analysis": (
            "Status byte 0x09 (Bits 0+3 set) confirms fault is ACTIVE and CONFIRMED — "
            "this is not a historic entry. U0100 indicates BCM has lost communication with ECM "
            "on the CAN bus. NRC 0x22 in extended session points to a precondition failure, "
            "not a session type error — the session itself was correct. "
            "Field trace is sufficient for session analysis. "
            "Lab reproduction recommended to capture CAN wiring continuity under load. "
            "Decision: Is ECM present on CAN bus? Yes → investigate security sequence. "
            "No → CAN wiring or ECM power issue."
        ),
        "debug_steps": [
            DebugStep(
                step_number=1,
                tool="CANoe",
                action=(
                    "Monitor CAN bus during ignition cycle — filter for ECM message IDs from DBC. "
                    "Confirm ECM is transmitting before investigating UDS session."
                ),
                expected_output="ECM messages present at correct rate — confirms CAN physical layer OK",
            ),
            DebugStep(
                step_number=2,
                tool="CANoe Diagnostic Console",
                action=(
                    "Send 0x10 0x03 (extendedSession), then 0x27 0x01 (requestSeed), "
                    "calculate and send 0x27 0x02 (sendKey), then retry failing service."
                ),
                expected_output="Positive response after security access — confirms sequence was the issue",
            ),
            DebugStep(
                step_number=3,
                tool="CANoe / DLT Viewer",
                action=(
                    "Read DTC freeze frame via 0x19 0x04 U0100 — extract vehicle speed, "
                    "ignition state, and timestamp at moment of fault."
                ),
                expected_output="Freeze frame shows operating conditions — confirms or rules out vehicle state precondition",
            ),
        ],
        "self_evaluation": [
            SelfEvaluationLine(
                item="input_analysis",
                result="PASS",
                evidence="4 input facts extracted, 2 assumptions stated — baudrate and ECU identity",
            ),
            SelfEvaluationLine(
                item="data_sufficiency",
                result="PASS",
                evidence="PARTIAL level set — freeze frame and UDS log flagged as missing critical",
            ),
            SelfEvaluationLine(
                item="status_byte_decoded",
                result="PASS",
                evidence="0x09 decoded: Bit 0 = testFailed, Bit 3 = confirmedDTC",
            ),
            SelfEvaluationLine(
                item="probable_causes",
                result="PASS",
                evidence="3 causes with tool + action + numeric/condition thresholds",
            ),
            SelfEvaluationLine(
                item="analysis",
                result="PASS",
                evidence="Lab vs field assessment included — lab recommended for wiring check",
            ),
        ],
    }
    data.update(overrides)
    return FieldDebugFaeOutput(**data)


# ── Schema structure tests ─────────────────────────────────────────────────────

class TestSchemaStructure:
    def test_valid_output_builds(self):
        output = make_valid_output()
        assert output.fault_details.dtc_code == "U0100"

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
                confidence_reason="All critical inputs provided",
                missing_critical_data=["None — data is complete"],
            )
        )
        assert output.data_sufficiency.level == "SUFFICIENT"

    def test_input_facts_do_not_contain_assumptions(self):
        """input_facts must be stated facts — assumption markers must be in assumptions."""
        output = make_valid_output()
        for fact in output.input_analysis.input_facts:
            assert "assumed" not in fact.lower(), (
                f"input_facts should not contain assumptions: '{fact}'"
            )

    def test_protocol_detection_present(self):
        output = make_valid_output()
        assert output.protocol_detection.protocol == "CAN"
        assert output.protocol_detection.confidence == "MEDIUM"

    def test_probable_causes_exactly_three(self):
        output = make_valid_output()
        assert len(output.probable_causes) == 3

    def test_debug_steps_exactly_three(self):
        output = make_valid_output()
        assert len(output.debug_steps) == 3


# ── Validator tests ────────────────────────────────────────────────────────────

class TestValidators:
    def test_valid_output_passes_all_validators(self):
        output = make_valid_output()
        validators.validate(output)  # must not raise

    def test_safety_relevant_yes_with_safety_impact(self):
        output = make_valid_output(
            fault_details=FaultDetails(
                dtc_code="B1234",
                dtc_description="Airbag deployment fault",
                status_byte="0x6F",
                status_byte_decoded="Bit 0 = testFailed, Bit 3 = confirmedDTC",
                system="Airbag ECU",
                safety_relevant="YES",
                safety_impact="Airbag may not deploy — ASIL-D safety function",
            )
        )
        validators.validate(output)  # YES + real safety_impact = valid

    def test_safety_relevant_contradiction_raises(self):
        output = make_valid_output(
            fault_details=FaultDetails(
                dtc_code="U0100",
                dtc_description="Lost communication",
                status_byte="0x09",
                status_byte_decoded="Bit 0 = testFailed, Bit 3 = confirmedDTC",
                system="BCM",
                safety_relevant="YES",
                safety_impact="Not safety-critical",  # contradiction
            )
        )
        with pytest.raises(DomainCheckError, match="contradiction"):
            validators.validate(output)

    def test_status_byte_decoded_missing_bit_reference_raises(self):
        output = make_valid_output(
            fault_details=FaultDetails(
                dtc_code="U0100",
                dtc_description="Lost communication",
                status_byte="0x09",
                status_byte_decoded="The fault is active and confirmed",  # no Bit reference
                system="BCM",
                safety_relevant="NO",
                safety_impact="Not safety-critical",
            )
        )
        with pytest.raises(DomainCheckError, match="bit-level"):
            validators.validate(output)

    def test_analysis_without_lab_vs_field_raises(self):
        output = make_valid_output(
            analysis="The DTC U0100 indicates a communication loss. Check the CAN bus."
        )
        with pytest.raises(DomainCheckError, match="lab"):
            validators.validate(output)

    def test_probable_cause_test_too_short_raises(self):
        causes = list(make_valid_output().probable_causes)
        causes[0] = ProbableCause(
            rank="HIGH",
            is_hypothesis=False,
            description="CAN loss",
            ranking_reason="Status byte confirms active fault",
            test="Check CAN",  # too short
            pass_criteria="CAN messages present",
            fail_criteria="CAN messages absent",
            validation_test="Monitor CAN bus for ECM messages during ignition cycle",
        )
        output = make_valid_output(probable_causes=causes)
        with pytest.raises(DomainCheckError, match="too vague"):
            validators.validate(output)

    def test_nrc_present_requires_root_causes(self):
        output = make_valid_output(
            uds_session_analysis=UdsSessionAnalysis(
                nrc_code="0x22",
                nrc_name="conditionsNotCorrect",
                nrc_root_causes=["Only one cause"],  # needs at least 2
                session_sequence_issue="N/A",
            )
        )
        with pytest.raises(DomainCheckError, match="root causes"):
            validators.validate(output)

    def test_nrc_na_skips_root_cause_check(self):
        output = make_valid_output(
            uds_session_analysis=UdsSessionAnalysis(
                nrc_code="N/A",
                nrc_name="N/A",
                nrc_root_causes=[],
                session_sequence_issue="N/A",
            )
        )
        validators.validate(output)  # N/A NRC with no causes is valid

    def test_can_protocol_high_confidence_requires_tec_math(self):
        """CAN + HIGH confidence forces tec_math to have actual calculation, not N/A."""
        output = make_valid_output(
            protocol_detection=ProtocolDetection(
                protocol="CAN",
                detected_from="CAN bus-off mentioned in symptom",
                confidence="HIGH",
            ),
            tec_math=["N/A — no CAN trace involved"],
        )
        with pytest.raises(DomainCheckError, match="tec_math"):
            validators.validate(output)

    def test_self_evaluation_pass_needs_evidence(self):
        output = make_valid_output(
            self_evaluation=[
                SelfEvaluationLine(item="status_byte", result="PASS", evidence=""),
            ]
        )
        with pytest.raises(DomainCheckError, match="evidence"):
            validators.validate(output)

    def test_debug_step_action_too_short_raises(self):
        steps = list(make_valid_output().debug_steps)
        steps[0] = DebugStep(
            step_number=1,
            tool="CANoe",
            action="Check it",  # too short
            expected_output="Messages present",
        )
        output = make_valid_output(debug_steps=steps)
        with pytest.raises(DomainCheckError, match="too vague"):
            validators.validate(output)


# ── Skill loader test ──────────────────────────────────────────────────────────

class TestSkillLoader:
    def test_skills_load_without_error(self):
        content = load_skills("uds-diagnostics", "can-bus-analysis")
        assert len(content) > 100

    def test_prompt_loads_without_error(self):
        from sdk_agents.integrator.field_debug_fae.prompt import get_system_prompt
        prompt = get_system_prompt()
        assert len(prompt) > 100


# ── Agent instantiation test ───────────────────────────────────────────────────

class TestAgentInstantiation:
    @patch.dict("os.environ", {"GROQ_API_KEY": "test-key"})
    def test_agent_instantiates(self):
        agent = FieldDebugFaeAgent()
        assert agent.AGENT_NAME == "field-debug-fae"

    @patch.dict("os.environ", {"GROQ_API_KEY": "test-key"})
    def test_agent_returns_correct_schema(self):
        agent = FieldDebugFaeAgent()
        assert agent.get_schema() == FieldDebugFaeOutput

    @patch.dict("os.environ", {"GROQ_API_KEY": "test-key"})
    def test_agent_run_returns_agent_error_on_api_failure(self):
        with patch("sdk_agents.core.base_agent.Groq") as mock_groq:
            mock_client = MagicMock()
            mock_groq.return_value = mock_client
            mock_client.chat.completions.create.side_effect = Exception("API unavailable")
            agent = FieldDebugFaeAgent()
            result = agent.run("door not unlocking, DTC U0100")
            assert isinstance(result, AgentError)
            assert result.agent == "field-debug-fae"
