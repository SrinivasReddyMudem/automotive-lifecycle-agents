"""
Output schema for embedded_c_developer.
Covers systematic layer-by-layer diagnosis, RTOS concerns, CFSR decode, MISRA notes.
"""

from pydantic import BaseModel, Field
from typing import Literal
from sdk_agents.core.shared_schema import NarrowingQuestion, SelfEvaluationLine, InputAnalysis, DataSufficiency


class LayerDiagnosis(BaseModel):
    layer: Literal["Physical", "RTOS", "Application"]
    status: Literal["SUSPECT", "CLEAR", "UNKNOWN"]
    evidence: str = Field(description="What evidence points to this layer being the fault source")
    tool: str = Field(description="Tool to verify this layer: oscilloscope / TRACE32 Task window / DLT Viewer")
    check: str = Field(description="Specific check to perform: register name, signal, address, or log filter")


class CfsrDecode(BaseModel):
    cfsr_value: str = Field(description="CFSR register value e.g. 0x02000000 or N/A if not a Cortex fault")
    bit_set: str = Field(description="Which bits are set e.g. Bit 25 STKERR or N/A")
    meaning: str = Field(description="What this bit combination means in the MCU fault context")
    action: str = Field(description="Concrete next action based on CFSR decode")


class MisraNote(BaseModel):
    rule: str = Field(description="MISRA C:2012 rule number e.g. Rule 14.4")
    category: Literal["Mandatory", "Required", "Advisory"]
    violation_pattern: str = Field(description="Synthetic code pattern showing the violation")
    compliant_fix: str = Field(description="The compliant rewrite or approach")


class EmbeddedCDeveloperOutput(BaseModel):
    model_config = {"extra": "ignore"}

    problem_classification: str = Field(
        description=(
            "One sentence: MCU family + fault type + layer. "
            "E.g. 'Stack overflow during CAN ISR on TC387 — OS layer fault'"
        )
    )
    input_analysis: InputAnalysis = Field(
        description=(
            "STEP 0 (before layer diagnosis): separate what the user directly stated "
            "(input_facts) from what you inferred or assumed (assumptions). "
            "Extract only explicitly provided data: MCU family, fault symptoms, "
            "CFSR register value, RTOS task names, stack sizes, error logs. "
            "Never mix assumed values into input_facts."
        )
    )
    data_sufficiency: DataSufficiency = Field(
        description=(
            "Rate data completeness for this specific embedded diagnosis. "
            "SUFFICIENT = MCU fault registers + RTOS task state + code context all present. "
            "PARTIAL = some key data missing but fault layer direction is clear. "
            "INSUFFICIENT = only symptom description, no register values or stack data. "
            "missing_critical_data: ONLY list inputs that caused an N/A in a field, "
            "forced an assumption, or would change the layer diagnosis ranking if provided."
        )
    )
    layer_diagnosis: list[LayerDiagnosis] = Field(
        min_length=3,
        max_length=3,
        description="Exactly 3 layers: Physical, RTOS, Application — each with SUSPECT/CLEAR/UNKNOWN",
    )
    cfsr_decode: CfsrDecode = Field(
        description="CFSR register decode for Cortex-M/R faults, or N/A for non-Cortex MCUs"
    )
    root_cause: str = Field(
        description="Specific root cause conclusion after layer analysis — not a generic statement"
    )
    code_pattern: str = Field(
        description=(
            "The actual code fix, MISRA-compliant pattern, or configuration change. "
            "Show actual C code — not pseudo-code. Use synthetic variable names."
        )
    )
    misra_notes: list[MisraNote] = Field(
        description="MISRA rules applicable to this implementation or fix"
    )
    rtos_calc: list[str] = Field(
        description=(
            "RTOS timing calculations as a list of strings — one string per line. "
            "Cover stack sizing and/or watchdog window with actual numbers. "
            "First element: header e.g. 'Stack Sizing — worst-case calculation'. "
            "Middle elements: one arithmetic step per line with actual numbers. "
            "Last element: plain-English confirmation starting with →. "
            "If no RTOS is involved or numbers are not provided: "
            "['N/A — no RTOS involved in this scenario'] or "
            "['N/A — stack sizes and call depth not stated. Provide sizeof each local, "
            "deepest call chain depth, and whether ISR preemption applies.']"
        )
    )
    cpu_load_calc: list[str] = Field(
        description=(
            "CPU load calculation as a list of strings — one string per line. "
            "ONLY populate when symptom indicates CPU resource pressure: "
            "task deadline missed, random WDT reset, CPU overload reported, or "
            "performance degradation after adding new task/ISR. "
            "Otherwise: ['N/A — symptom does not indicate CPU load as the cause']. "
            "First element: header 'CPU Load — per-task utilisation analysis'. "
            "Middle elements: WCET × frequency per task, one line each. "
            "Last element: plain-English confirmation starting with → stating whether "
            "total load is within safe limits (< 70% sustained, < 90% peak). "
            "If WCET or task rates not provided: "
            "['N/A — task WCET and execution frequency not stated. "
            "Provide TRACE32 Performance window output or measured WCET per task.']"
        )
    )
    narrowing_questions: list[NarrowingQuestion] = Field(
        min_length=3,
        max_length=3,
        description="Exactly 3 yes/no diagnostic questions with yes/no consequences",
    )
    self_evaluation: list[SelfEvaluationLine] = Field(
        description="PASS/FAIL check for layer diagnosis, CFSR decode, and code pattern"
    )
