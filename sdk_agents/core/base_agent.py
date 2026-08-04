"""
Base agent — multi-provider implementation (Groq or Gemini).
Uses schema-enforced structured JSON output. No prompt-based format
instructions needed — schema enforcement is at the API level for both providers.

Provider is selected via LLM_PROVIDER env var: "groq" (default) or "gemini".

Groq free tier: only openai/gpt-oss-20b and openai/gpt-oss-120b support strict
json_schema, both capped at 8,000 tokens/minute — too small for several of this
project's larger agent prompts (sw-integrator, gate-review-approver, etc.).
Get a free key (no credit card) at: console.groq.com

Gemini free tier: no credit card required, much larger token-per-minute budget,
native response_schema support. Get a free key at: aistudio.google.com/apikey
"""

import os
from groq import Groq, BadRequestError, APIStatusError as GroqAPIStatusError
from google.genai.errors import APIError as GeminiAPIError
from pydantic import BaseModel, ValidationError
from typing import Literal
from .logger import get_logger

MAX_RETRIES = 2  # retry up to 2 times after first failure


class AgentError(BaseModel):
    """Returned instead of crashing when API or validation fails."""
    agent: str
    error_type: Literal[
        "api_error", "validation_error", "domain_check_failed", "rate_limited"
    ]
    message: str
    raw_response: str | None = None


class DomainCheckError(Exception):
    """Raised by agent validators.py when semantic checks fail."""
    pass


class BaseAgent:
    AGENT_NAME = "base"

    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "groq").lower()
        self.groq_model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
        self.logger = get_logger(self.AGENT_NAME)

        if self.provider == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise EnvironmentError(
                    "GEMINI_API_KEY not set.\n"
                    "Get a free key (no credit card) at aistudio.google.com/apikey\n"
                    "Then add it to sdk_agents/.env as: GEMINI_API_KEY=your-key"
                )
            from google import genai
            self.client = genai.Client(api_key=api_key)
        elif self.provider == "groq":
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise EnvironmentError(
                    "GROQ_API_KEY not set.\n"
                    "Get a free key (no credit card) at console.groq.com\n"
                    "Then add it to sdk_agents/.env as: GROQ_API_KEY=your-key"
                )
            self.client = Groq(api_key=api_key)
        else:
            raise EnvironmentError(
                f"Unknown LLM_PROVIDER '{self.provider}'. Use 'groq' or 'gemini'."
            )

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
                # Tell the model exactly what was wrong so it can fix the specific field
                domain_feedback = (
                    f"Your previous response failed JSON schema validation: {e} "
                    f"Return the complete corrected response matching the schema exactly."
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

            except BadRequestError as e:
                # Groq 400 — generated JSON does not match schema (model non-determinism).
                # Retry: the model's probabilistic output often succeeds on the next attempt.
                self.logger.warning(
                    f"API schema rejection (attempt {attempt + 1}): {e}"
                )
                if attempt == MAX_RETRIES:
                    return AgentError(
                        agent=self.AGENT_NAME,
                        error_type="api_error",
                        message=str(e),
                    )
                domain_feedback = (
                    f"Your previous response was rejected by schema validation: {e}. "
                    "Return valid JSON matching the schema exactly. "
                    "Check that every required field name is spelled correctly and present."
                )

            except Exception as e:
                # 429 = too many requests; Groq also returns 413 for "request
                # too large for tokens-per-minute budget" — both mean retrying
                # immediately will not help and only wastes the budget further.
                is_rate_limit = (
                    isinstance(e, GroqAPIStatusError) and e.status_code in (429, 413)
                ) or (isinstance(e, GeminiAPIError) and e.code == 429)
                if is_rate_limit:
                    # Retrying immediately only makes rate limiting worse — the
                    # provider just asked us to back off. Fail fast instead of
                    # burning the remaining attempts in a rapid-fire burst.
                    self.logger.warning(f"Rate limited (attempt {attempt + 1}): {e}")
                    return AgentError(
                        agent=self.AGENT_NAME,
                        error_type="rate_limited",
                        message=str(e),
                    )
                self.logger.error(f"Unexpected error (attempt {attempt + 1}): {e}")
                if attempt == MAX_RETRIES:
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
                # Groq strict mode requires ALL properties listed in required.
                # Pydantic omits fields with defaults from required — add them back.
                if result.get("type") == "object" and "properties" in result:
                    all_props = list(result["properties"].keys())
                    existing = result.get("required", [])
                    result["required"] = list(dict.fromkeys(existing + all_props))
                return result
            if isinstance(obj, list):
                return [resolve(item) for item in obj]
            return obj

        return resolve(schema)

    def _call_api(self, user_message: str, domain_feedback: str | None = None) -> str:
        """
        Call the configured provider with schema-enforced structured output.
        The model must return JSON matching the schema — cannot return free text.
        If domain_feedback is set (retry after DomainCheckError), it is appended
        as a follow-up user message so the model knows exactly what to fix.
        """
        if self.provider == "gemini":
            return self._call_gemini(user_message, domain_feedback)
        return self._call_groq(user_message, domain_feedback)

    def _call_groq(self, user_message: str, domain_feedback: str | None = None) -> str:
        schema = self._inline_schema(self.get_schema().model_json_schema())
        messages: list[dict] = [
            {"role": "system", "content": self.get_prompt()},
            {"role": "user", "content": user_message},
        ]
        if domain_feedback:
            messages.append({"role": "user", "content": domain_feedback})
        response = self.client.chat.completions.create(
            model=self.groq_model,
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

    def _call_gemini(self, user_message: str, domain_feedback: str | None = None) -> str:
        # Gemini's SDK accepts a Pydantic model class directly as response_schema
        # and handles the OpenAPI-schema conversion internally — no manual
        # $ref-inlining needed here (unlike Groq's strict json_schema mode).
        contents = user_message
        if domain_feedback:
            contents = f"{user_message}\n\n{domain_feedback}"
        response = self.client.models.generate_content(
            model=self.gemini_model,
            contents=contents,
            config={
                "system_instruction": self.get_prompt(),
                "response_mime_type": "application/json",
                "response_schema": self.get_schema(),
            },
        )
        raw = response.text
        self.logger.debug(f"Raw response preview: {raw[:300]}")
        return raw

    def _parse(self, raw: str) -> BaseModel:
        import json
        # Groq occasionally wraps the output in a JSON array [{}] instead of {}.
        # Unwrap single-element arrays before Pydantic validation.
        try:
            decoded = json.loads(raw)
            if isinstance(decoded, list) and len(decoded) == 1:
                self.logger.warning("Model returned array instead of object — unwrapping.")
                raw = json.dumps(decoded[0])
        except Exception:
            pass  # let model_validate_json handle malformed JSON and report clearly
        return self.get_schema().model_validate_json(raw)

    def _validate_domain(self, parsed: BaseModel) -> None:
        """Override in subclass for domain-specific semantic checks."""
        pass

    def get_schema(self) -> type[BaseModel]:
        raise NotImplementedError

    def get_prompt(self) -> str:
        raise NotImplementedError
