from sdk_agents.core.base_agent import BaseAgent
from .schema import SwProjectLeadOutput
from .prompt import get_system_prompt
from . import validators


class SwProjectLeadAgent(BaseAgent):
    AGENT_NAME = "sw-project-lead"

    def get_schema(self) -> type[SwProjectLeadOutput]:
        return SwProjectLeadOutput

    def get_prompt(self) -> str:
        return get_system_prompt()

    def _validate_domain(self, parsed: SwProjectLeadOutput) -> None:
        validators.validate(parsed)
