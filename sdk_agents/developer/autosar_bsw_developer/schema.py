"""
Output schema for autosar_bsw_developer.
Covers SWC design, BSW configuration, RTE API, and AUTOSAR naming.
"""

from pydantic import BaseModel, Field
from typing import Literal
from sdk_agents.core.shared_schema import SelfEvaluationLine, InputAnalysis, DataSufficiency


class PortDesign(BaseModel):
    port_name: str = Field(description="AUTOSAR port name e.g. VehicleSpeed_PP")
    port_direction: Literal["P-Port", "R-Port"]
    interface_type: Literal["sender-receiver", "client-server", "mode-switch", "nv-data"]
    interface_name: str = Field(description="AUTOSAR interface name e.g. SR_VehicleSpeed_I")
    data_element_or_operation: str = Field(
        description="Data element (SR) or operation name (CS) with type, range, unit"
    )
    rte_api: str = Field(description="Exact RTE API signature e.g. Rte_Write_VehicleSpeed_PP_VehicleSpeed_DE()")
    asil_constraint: str = Field(
        description="ASIL-specific constraint: return value check, invalidation policy, or N/A"
    )


class RunnableDesign(BaseModel):
    name: str = Field(description="Runnable name e.g. VehicleSpeedProvider_RunFunc")
    trigger: str = Field(description="Trigger type and period e.g. TimingEvent 10ms / DataReceivedErrorEvent")
    os_task: str = Field(description="Mapped OS task name and priority e.g. OsTask_10ms priority 10")
    timing_protection: str = Field(description="Timing protection budget or N/A if QM")


class BswParameter(BaseModel):
    module: str = Field(description="BSW module name e.g. Com / PduR / CanIf / NvM / Dcm")
    parameter_path: str = Field(description="Exact parameter path in DaVinci/tresos")
    value: str = Field(description="Valid range and typical value")
    impact: str = Field(description="What changes when you set this parameter")
    common_mistake: str = Field(description="Common misconfiguration to avoid")


class AutosarBswDeveloperOutput(BaseModel):
    model_config = {"extra": "ignore"}

    autosar_version: str = Field(description="AUTOSAR version assumed: R4.4 / R4.3 / R22 / Adaptive R22")
    input_analysis: InputAnalysis = Field(
        description=(
            "Structured extraction of what the user stated vs what was assumed. "
            "input_facts: SWC type stated, ASIL level stated, AUTOSAR version stated, "
            "interface type (sender-receiver/client-server) stated, data element name and type given, "
            "trigger type and period stated, BSW module mentioned. "
            "assumptions: AUTOSAR version assumed from context, ASIL assumed from system context, "
            "interface type assumed, OS task priority assumed."
        )
    )
    data_sufficiency: DataSufficiency = Field(
        description=(
            "Rate completeness for this specific SWC design only. "
            "SUFFICIENT: SWC type + ASIL level + interface type + data element details all present. "
            "PARTIAL: SWC described but ASIL level or interface type or data element details missing. "
            "INSUFFICIENT: only a feature name with no SWC type or data interface description. "
            "missing_critical_data: only flag inputs that caused N/A, forced an assumption, "
            "or would change the RTE API signature or ASIL notes if provided."
        )
    )
    asil_level: str = Field(description="ASIL level: QM / ASIL-A / ASIL-B / ASIL-C / ASIL-D or N/A")
    swc_name: str = Field(description="Primary SWC name in AUTOSAR naming convention")
    swc_type: str = Field(
        description="SWC type: Application / Sensor-Actuator / Service / Parameter / Composition"
    )
    provider_ports: list[PortDesign] = Field(
        description="P-Port designs for this SWC — provide sender or server side"
    )
    consumer_ports: list[PortDesign] = Field(
        description="R-Port designs for this SWC — provide receiver or client side"
    )
    runnables: list[RunnableDesign] = Field(
        description="All runnables with trigger, OS task mapping, and timing protection"
    )
    bsw_parameters: list[BswParameter] = Field(
        description="Relevant BSW configuration parameters with exact paths and values"
    )
    misra_notes: str = Field(
        description="MISRA C:2012 rules relevant to this implementation with specific rule numbers"
    )
    asil_notes: str = Field(
        description=(
            "ASIL implementation notes: freedom from interference, RTE return value checking, "
            "invalid data handling, ASIL decomposition if applicable. N/A if QM."
        )
    )
    self_evaluation: list[SelfEvaluationLine] = Field(
        description="PASS/FAIL check for naming convention, RTE APIs, ASIL notes with evidence"
    )
