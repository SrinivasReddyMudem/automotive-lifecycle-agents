from sdk_agents.core.base_agent import BaseAgent
from .schema import SwIntegratorOutput
from .prompt import get_system_prompt
from . import validators


class SwIntegratorAgent(BaseAgent):
    AGENT_NAME = "sw-integrator"

    def get_schema(self) -> type[SwIntegratorOutput]:
        return SwIntegratorOutput

    def get_prompt(self) -> str:
        return get_system_prompt()

    def _validate_domain(self, parsed: SwIntegratorOutput) -> None:
        validators.validate(parsed)
