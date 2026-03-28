from sdk_agents.core.base_agent import BaseAgent
from .schema import AutosarBswDeveloperOutput
from .prompt import get_system_prompt
from . import validators


class AutosarBswDeveloperAgent(BaseAgent):
    AGENT_NAME = "autosar-bsw-developer"

    def get_schema(self) -> type[AutosarBswDeveloperOutput]:
        return AutosarBswDeveloperOutput

    def get_prompt(self) -> str:
        return get_system_prompt()

    def _validate_domain(self, parsed: AutosarBswDeveloperOutput) -> None:
        validators.validate(parsed)
