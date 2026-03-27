from sdk_agents.core.base_agent import BaseAgent, DomainCheckError
from .schema import SilHilTestPlannerOutput
from .prompt import get_system_prompt
from . import validators


class SilHilTestPlannerAgent(BaseAgent):
    AGENT_NAME = "sil-hil-test-planner"

    def get_schema(self) -> type[SilHilTestPlannerOutput]:
        return SilHilTestPlannerOutput

    def get_prompt(self) -> str:
        return get_system_prompt()

    def _validate_domain(self, parsed: SilHilTestPlannerOutput) -> None:
        validators.validate(parsed)
