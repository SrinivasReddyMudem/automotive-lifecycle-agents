from sdk_agents.core.base_agent import BaseAgent
from .schema import CanBusAnalystOutput
from .prompt import get_system_prompt
from . import validators


class CanBusAnalystAgent(BaseAgent):
    AGENT_NAME = "can-bus-analyst"

    def get_schema(self) -> type[CanBusAnalystOutput]:
        return CanBusAnalystOutput

    def get_prompt(self) -> str:
        return get_system_prompt()

    def _validate_domain(self, parsed: CanBusAnalystOutput) -> None:
        validators.validate(parsed)
