"""
Agent registry — maps agent name strings (and aliases) to agent classes.
Mirrors the md_agents role/name structure using snake_case for Python.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base_agent import BaseAgent


def _get_registry() -> dict:
    # Lazy imports to avoid circular dependencies at module load time
    from sdk_agents.integrator.can_bus_analyst import CanBusAnalystAgent
    from sdk_agents.integrator.field_debug_fae import FieldDebugFaeAgent
    from sdk_agents.integrator.sw_integrator import SwIntegratorAgent
    from sdk_agents.developer.autosar_bsw_developer import AutosarBswDeveloperAgent
    from sdk_agents.developer.embedded_c_developer import EmbeddedCDeveloperAgent
    from sdk_agents.developer.misra_reviewer import MisraReviewerAgent
    from sdk_agents.project_lead.aspice_process_coach import AspiceProcessCoachAgent
    from sdk_agents.project_lead.gate_review_approver import GateReviewApproverAgent
    from sdk_agents.project_lead.safety_and_cyber_lead import SafetyAndCyberLeadAgent
    from sdk_agents.project_lead.sw_project_lead import SwProjectLeadAgent
    from sdk_agents.tester.regression_analyst import RegressionAnalystAgent
    from sdk_agents.tester.sil_hil_test_planner import SilHilTestPlannerAgent
    from sdk_agents.tester.sw_unit_tester import SwUnitTesterAgent

    return {
        # ── Integrator ──────────────────────────────────────────────────
        "can-bus-analyst":       CanBusAnalystAgent,
        "can_bus_analyst":       CanBusAnalystAgent,
        "can-bus":               CanBusAnalystAgent,
        "field-debug-fae":       FieldDebugFaeAgent,
        "field_debug_fae":       FieldDebugFaeAgent,
        "fae":                   FieldDebugFaeAgent,
        "sw-integrator":         SwIntegratorAgent,
        "sw_integrator":         SwIntegratorAgent,
        "integrator":            SwIntegratorAgent,
        # ── Developer ───────────────────────────────────────────────────
        "autosar-bsw-developer": AutosarBswDeveloperAgent,
        "autosar_bsw_developer": AutosarBswDeveloperAgent,
        "autosar":               AutosarBswDeveloperAgent,
        "embedded-c-developer":  EmbeddedCDeveloperAgent,
        "embedded_c_developer":  EmbeddedCDeveloperAgent,
        "embedded":              EmbeddedCDeveloperAgent,
        "misra-reviewer":        MisraReviewerAgent,
        "misra_reviewer":        MisraReviewerAgent,
        "misra":                 MisraReviewerAgent,
        # ── Project Lead ────────────────────────────────────────────────
        "aspice-process-coach":  AspiceProcessCoachAgent,
        "aspice_process_coach":  AspiceProcessCoachAgent,
        "aspice":                AspiceProcessCoachAgent,
        "gate-review-approver":  GateReviewApproverAgent,
        "gate_review_approver":  GateReviewApproverAgent,
        "gate-review":           GateReviewApproverAgent,
        "safety-and-cyber-lead": SafetyAndCyberLeadAgent,
        "safety_and_cyber_lead": SafetyAndCyberLeadAgent,
        "safety":                SafetyAndCyberLeadAgent,
        "sw-project-lead":       SwProjectLeadAgent,
        "sw_project_lead":       SwProjectLeadAgent,
        "project-lead":          SwProjectLeadAgent,
        # ── Tester ──────────────────────────────────────────────────────
        "regression-analyst":    RegressionAnalystAgent,
        "regression_analyst":    RegressionAnalystAgent,
        "regression":            RegressionAnalystAgent,
        "sil-hil-test-planner":  SilHilTestPlannerAgent,
        "sil_hil_test_planner":  SilHilTestPlannerAgent,
        "sil-hil":               SilHilTestPlannerAgent,
        "sw-unit-tester":        SwUnitTesterAgent,
        "sw_unit_tester":        SwUnitTesterAgent,
        "unit-tester":           SwUnitTesterAgent,
    }


# Human-readable display names for UI
AGENT_DISPLAY_NAMES = {
    # Integrator
    "can-bus-analyst":       "Integrator — CAN Bus Analyst",
    "field-debug-fae":       "Integrator — Field Debug FAE",
    "sw-integrator":         "Integrator — SW Integrator",
    # Developer
    "autosar-bsw-developer": "Developer — AUTOSAR BSW Developer",
    "embedded-c-developer":  "Developer — Embedded C Developer",
    "misra-reviewer":        "Developer — MISRA Reviewer",
    # Project Lead
    "aspice-process-coach":  "Project Lead — ASPICE Process Coach",
    "gate-review-approver":  "Project Lead — Gate Review Approver",
    "safety-and-cyber-lead": "Project Lead — Safety & Cyber Lead",
    "sw-project-lead":       "Project Lead — SW Project Lead",
    # Tester
    "regression-analyst":    "Tester — Regression Analyst",
    "sil-hil-test-planner":  "Tester — SIL/HIL Test Planner",
    "sw-unit-tester":        "Tester — SW Unit Tester",
}

# Canonical names list for UI dropdowns (one entry per agent)
AGENT_NAMES = list(AGENT_DISPLAY_NAMES.keys())


def get_agent(name: str) -> "BaseAgent":
    registry = _get_registry()
    cls = registry.get(name.lower().strip())
    if not cls:
        valid = sorted(AGENT_DISPLAY_NAMES.keys())
        raise KeyError(
            f"Unknown agent '{name}'.\n"
            f"Available agents: {valid}\n"
            f"Aliases also accepted (e.g. 'can-bus', 'fae', 'misra')"
        )
    return cls()
