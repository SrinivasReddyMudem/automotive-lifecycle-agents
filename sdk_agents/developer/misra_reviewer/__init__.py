from sdk_agents.core.base_agent import BaseAgent
from .schema import MisraReviewerOutput
from .prompt import get_system_prompt
from . import validators


class MisraReviewerAgent(BaseAgent):
    AGENT_NAME = "misra-reviewer"

    def get_schema(self) -> type[MisraReviewerOutput]:
        return MisraReviewerOutput

    def get_prompt(self) -> str:
        return get_system_prompt()

    def _validate_domain(self, parsed: MisraReviewerOutput) -> None:
        validators.validate(parsed)
