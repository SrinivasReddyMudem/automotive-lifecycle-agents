from sdk_agents.core.base_agent import BaseAgent
from .schema import SafetyAndCyberLeadOutput
from .prompt import get_system_prompt
from . import validators


class SafetyAndCyberLeadAgent(BaseAgent):
    AGENT_NAME = "safety-and-cyber-lead"

    def get_schema(self) -> type[SafetyAndCyberLeadOutput]:
        return SafetyAndCyberLeadOutput

    def get_prompt(self) -> str:
        return get_system_prompt()

    def _validate_domain(self, parsed: SafetyAndCyberLeadOutput) -> None:
        validators.validate(parsed)
