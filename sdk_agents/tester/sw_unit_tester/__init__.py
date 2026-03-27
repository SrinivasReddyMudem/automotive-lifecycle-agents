from sdk_agents.core.base_agent import BaseAgent, DomainCheckError
from .schema import SwUnitTesterOutput
from .prompt import get_system_prompt
from . import validators


class SwUnitTesterAgent(BaseAgent):
    AGENT_NAME = "sw-unit-tester"

    def get_schema(self) -> type[SwUnitTesterOutput]:
        return SwUnitTesterOutput

    def get_prompt(self) -> str:
        return get_system_prompt()

    def _validate_domain(self, parsed: SwUnitTesterOutput) -> None:
        validators.validate(parsed)
