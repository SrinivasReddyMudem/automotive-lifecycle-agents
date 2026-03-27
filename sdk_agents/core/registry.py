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

    return {
        # can-bus-analyst
        "can-bus-analyst":   CanBusAnalystAgent,
        "can_bus_analyst":   CanBusAnalystAgent,
        "can-bus":           CanBusAnalystAgent,
        # Add more agents here as they are built
    }


# Human-readable display names for UI
AGENT_DISPLAY_NAMES = {
    "can-bus-analyst": "CAN Bus Analyst",
    # Add more as built
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
            f"Aliases also accepted (e.g. 'can-bus', 'can_bus_analyst')"
        )
    return cls()
