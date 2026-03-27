"""
Base agent — Gemini-backed implementation.
Uses response_schema in GenerationConfig to enforce structured JSON output.
No prompt-based format instructions needed — schema enforcement is at API level.

Free tier: Gemini 1.5 Flash — 15 RPM, 1500 RPD, 1M TPM.
Get a free API key at: aistudio.google.com
"""

import os
import google.generativeai as genai
from pydantic import BaseModel, ValidationError
from typing import Literal
from .logger import get_logger

MODEL = "gemini-1.5-flash"
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
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "GOOGLE_API_KEY not set.\n"
                "Get a free key at aistudio.google.com\n"
                "Then add it to sdk_agents/.env as: GOOGLE_API_KEY=your-key"
            )
        genai.configure(api_key=api_key)
        self.logger = get_logger(self.AGENT_NAME)

    def run(self, user_message: str) -> BaseModel | AgentError:
        """
        Run the agent. Always returns a Pydantic model or AgentError — never raises.
        """
        raw = None
        for attempt in range(MAX_RETRIES + 1):
            try:
                raw = self._call_api(user_message)
                parsed = self._parse(raw)
                self._validate_domain(parsed)
                return parsed

            except ValidationError as e:
                self.logger.error(
                    f"Schema validation failed (attempt {attempt + 1}): {e}"
                )
                if attempt == MAX_RETRIES:
                    return AgentError(
                        agent=self.AGENT_NAME,
                        error_type="validation_error",
                        message=str(e),
                        raw_response=raw,
                    )

            except DomainCheckError as e:
                self.logger.error(f"Domain check failed: {e}")
                return AgentError(
                    agent=self.AGENT_NAME,
                    error_type="domain_check_failed",
                    message=str(e),
                )

            except Exception as e:
                self.logger.error(f"API error: {e}")
                return AgentError(
                    agent=self.AGENT_NAME,
                    error_type="api_error",
                    message=str(e),
                )

    def _call_api(self, user_message: str) -> str:
        """
        Call Gemini API with response_schema enforcement.
        The model must return JSON matching the schema — cannot return free text.
        """
        model = genai.GenerativeModel(
            model_name=MODEL,
            system_instruction=self.get_prompt(),
        )
        response = model.generate_content(
            user_message,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=self.get_schema(),
            ),
        )
        self.logger.debug(f"Raw response preview: {response.text[:300]}")
        return response.text

    def _parse(self, raw: str) -> BaseModel:
        return self.get_schema().model_validate_json(raw)

    def _validate_domain(self, parsed: BaseModel) -> None:
        """Override in subclass for domain-specific semantic checks."""
        pass

    def get_schema(self) -> type[BaseModel]:
        raise NotImplementedError

    def get_prompt(self) -> str:
        raise NotImplementedError
