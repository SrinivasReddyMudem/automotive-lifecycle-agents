from sdk_agents.core.base_agent import BaseAgent
from .schema import FieldDebugFaeOutput
from .prompt import get_system_prompt
from . import validators


class FieldDebugFaeAgent(BaseAgent):
    AGENT_NAME = "field-debug-fae"

    def get_schema(self) -> type[FieldDebugFaeOutput]:
        return FieldDebugFaeOutput

    def get_prompt(self) -> str:
        return get_system_prompt()

    def _validate_domain(self, parsed: FieldDebugFaeOutput) -> None:
        validators.validate(parsed)
