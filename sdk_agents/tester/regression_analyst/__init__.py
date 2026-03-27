from sdk_agents.core.base_agent import BaseAgent, DomainCheckError
from .schema import RegressionAnalystOutput
from .prompt import get_system_prompt
from . import validators


class RegressionAnalystAgent(BaseAgent):
    AGENT_NAME = "regression-analyst"

    def get_schema(self) -> type[RegressionAnalystOutput]:
        return RegressionAnalystOutput

    def get_prompt(self) -> str:
        return get_system_prompt()

    def _validate_domain(self, parsed: RegressionAnalystOutput) -> None:
        validators.validate(parsed)
