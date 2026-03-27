"""
Base agent — handles API call, tool_choice enforcement, schema parsing,
retry logic, and structured error return. Never raises to the caller.
"""

import anthropic
from pydantic import BaseModel, ValidationError
from typing import Literal
from .logger import get_logger

MODEL = "claude-sonnet-4-6"
MAX_RETRIES = 1  # retry once on validation failure — no infinite loop


class AgentError(BaseModel):
    """Returned instead of crashing when API or validation fails."""
    agent: str
    error_type: Literal["api_error", "validation_error", "domain_check_failed"]
    message: str
    raw_response: str | None = None


class DomainCheckError(Exception):
    """Raised by agent validators.py when semantic checks fail."""
    pass


class BaseAgent:
    AGENT_NAME = "base"

    def __init__(self):
        self.client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env
        self.logger = get_logger(self.AGENT_NAME)

    def run(self, user_message: str) -> BaseModel | AgentError:
        """
        Run the agent. Always returns a Pydantic model or AgentError — never raises.
        """
        for attempt in range(MAX_RETRIES + 1):
            try:
                raw = self._call_api(user_message)
                parsed = self._parse(raw)
                self._validate_domain(parsed)
                return parsed

            except ValidationError as e:
                self.logger.error(
                    f"Schema validation failed (attempt {attempt + 1})",
                    extra={"error": str(e), "raw": str(raw) if "raw" in dir() else None},
                )
                if attempt == MAX_RETRIES:
                    return AgentError(
                        agent=self.AGENT_NAME,
                        error_type="validation_error",
                        message=str(e),
                        raw_response=str(raw) if "raw" in dir() else None,
                    )

            except DomainCheckError as e:
                self.logger.error(f"Domain check failed: {e}")
                return AgentError(
                    agent=self.AGENT_NAME,
                    error_type="domain_check_failed",
                    message=str(e),
                )

            except anthropic.APIError as e:
                self.logger.error(f"API error: {e}")
                return AgentError(
                    agent=self.AGENT_NAME,
                    error_type="api_error",
                    message=str(e),
                )

    def _call_api(self, user_message: str) -> dict:
        schema = self.get_schema()
        tool_def = {
            "name": "structured_response",
            "description": "Return your complete analysis using this exact structure.",
            "input_schema": schema.model_json_schema(),
        }

        response = self.client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=self.get_prompt(),
            tools=[tool_def],
            tool_choice={"type": "tool", "name": "structured_response"},
            messages=[{"role": "user", "content": user_message}],
        )

        self.logger.debug(f"API response stop_reason: {response.stop_reason}")
        tool_input = response.content[0].input
        self.logger.debug(f"Tool input keys: {list(tool_input.keys())}")
        return tool_input

    def _parse(self, tool_input: dict) -> BaseModel:
        return self.get_schema().model_validate(tool_input)

    def _validate_domain(self, parsed: BaseModel) -> None:
        """Override in subclass for domain-specific semantic checks."""
        pass

    def get_schema(self) -> type[BaseModel]:
        raise NotImplementedError

    def get_prompt(self) -> str:
        raise NotImplementedError
