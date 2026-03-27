from sdk_agents.core.base_agent import BaseAgent, DomainCheckError
from .schema import EmbeddedCDeveloperOutput
from .prompt import get_system_prompt
from . import validators


class EmbeddedCDeveloperAgent(BaseAgent):
    AGENT_NAME = "embedded-c-developer"

    def get_schema(self) -> type[EmbeddedCDeveloperOutput]:
        return EmbeddedCDeveloperOutput

    def get_prompt(self) -> str:
        return get_system_prompt()

    def _validate_domain(self, parsed: EmbeddedCDeveloperOutput) -> None:
        validators.validate(parsed)
