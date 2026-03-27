from sdk_agents.core.base_agent import BaseAgent, DomainCheckError
from .schema import GateReviewApproverOutput
from .prompt import get_system_prompt
from . import validators


class GateReviewApproverAgent(BaseAgent):
    AGENT_NAME = "gate-review-approver"

    def get_schema(self) -> type[GateReviewApproverOutput]:
        return GateReviewApproverOutput

    def get_prompt(self) -> str:
        return get_system_prompt()

    def _validate_domain(self, parsed: GateReviewApproverOutput) -> None:
        validators.validate(parsed)
