"""
Base agent — Groq-backed implementation.
Uses json_schema response_format to enforce structured JSON output.
No prompt-based format instructions needed — schema enforcement is at API level.

Free tier: Groq — 14,400 requests/day, 6000 tokens/min on llama-3.3-70b.
Get a free API key (no credit card) at: console.groq.com
"""

import os
import json
from groq import Groq
from pydantic import BaseModel, ValidationError
from typing import Literal
from .logger import get_logger

MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
MAX_RETRIES = 2  # retry twice: once for transient validation, once with domain-check feedback


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
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "GROQ_API_KEY not set.\n"
                "Get a free key (no credit card) at console.groq.com\n"
                "Then add it to sdk_agents/.env as: GROQ_API_KEY=your-key"
            )
        self.client = Groq(api_key=api_key)
        self.logger = get_logger(self.AGENT_NAME)

    def run(self, user_message: str) -> BaseModel | AgentError:
        """
        Run the agent. Always returns a Pydantic model or AgentError — never raises.
        On DomainCheckError the agent retries once with the failure reason fed back
        to the model so it can self-correct the specific field.
        """
        raw = None
        domain_feedback: str | None = None

        for attempt in range(MAX_RETRIES + 1):
            try:
                raw = self._call_api(user_message, domain_feedback=domain_feedback)
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
                self.logger.warning(
                    f"Domain check failed (attempt {attempt + 1}): {e}"
                )
                if attempt == MAX_RETRIES:
                    return AgentError(
                        agent=self.AGENT_NAME,
                        error_type="domain_check_failed",
                        message=str(e),
                    )
                # Feed the failure reason back so the model can fix the specific field
                domain_feedback = (
                    f"Your previous response failed a quality check: {e} "
                    f"Please fix this specific issue and return the complete corrected response."
                )

            except Exception as e:
                self.logger.error(f"API error: {e}")
                return AgentError(
                    agent=self.AGENT_NAME,
                    error_type="api_error",
                    message=str(e),
                )

    @staticmethod
    def _inline_schema(schema: dict) -> dict:
        """
        Inline $defs/$ref references so the schema is flat.
        Groq's json_schema enforcement requires no $ref — all types must be inline.
        Also strips minItems/maxItems and title fields not supported by the API.
        """
        defs = schema.get("$defs", {})

        def resolve(obj):
            if isinstance(obj, dict):
                if "$ref" in obj:
                    ref_name = obj["$ref"].split("/")[-1]
                    return resolve(dict(defs[ref_name]))
                result = {}
                for k, v in obj.items():
                    if k in ("$defs", "title", "minItems", "maxItems"):
                        continue
                    result[k] = resolve(v)
                # Groq strict mode requires additionalProperties: false on every object
                if result.get("type") == "object" and "additionalProperties" not in result:
                    result["additionalProperties"] = False
                return result
            if isinstance(obj, list):
                return [resolve(item) for item in obj]
            return obj

        return resolve(schema)

    def _call_api(self, user_message: str, domain_feedback: str | None = None) -> str:
        """
        Call Groq API with json_schema response_format enforcement.
        The model must return JSON matching the schema — cannot return free text.
        If domain_feedback is set (retry after DomainCheckError), it is appended
        as a follow-up user message so the model knows exactly what to fix.
        """
        schema = self._inline_schema(self.get_schema().model_json_schema())
        messages: list[dict] = [
            {"role": "system", "content": self.get_prompt()},
            {"role": "user", "content": user_message},
        ]
        if domain_feedback:
            messages.append({"role": "user", "content": domain_feedback})
        response = self.client.chat.completions.create(
            model=MODEL,
            messages=messages,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": self.AGENT_NAME.replace("-", "_"),
                    "schema": schema,
                    "strict": True,
                },
            },
        )
        raw = response.choices[0].message.content
        self.logger.debug(f"Raw response preview: {raw[:300]}")
        return raw

    def _parse(self, raw: str) -> BaseModel:
        return self.get_schema().model_validate_json(raw)

    def _validate_domain(self, parsed: BaseModel) -> None:
        """Override in subclass for domain-specific semantic checks."""
        pass

    def get_schema(self) -> type[BaseModel]:
        raise NotImplementedError

    def get_prompt(self) -> str:
        raise NotImplementedError
