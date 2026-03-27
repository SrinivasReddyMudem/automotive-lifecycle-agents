from sdk_agents.core.base_agent import BaseAgent, DomainCheckError
from .schema import AspiceProcessCoachOutput
from .prompt import get_system_prompt
from . import validators


class AspiceProcessCoachAgent(BaseAgent):
    AGENT_NAME = "aspice-process-coach"

    def get_schema(self) -> type[AspiceProcessCoachOutput]:
        return AspiceProcessCoachOutput

    def get_prompt(self) -> str:
        return get_system_prompt()

    def _validate_domain(self, parsed: AspiceProcessCoachOutput) -> None:
        validators.validate(parsed)
