"""Anthropic Messages API wrapper used by every agent in backend/agents/.

Spec: Backend_Architecture_v1.md §6.

`call_agent` injects the response schema's JSON Schema into the system prompt,
calls Claude, strips any ```json``` code-fence wrapping, and validates the
output against the schema. On the first `ValidationError` it appends the
failure detail to the user prompt and retries once. A second failure raises
`BackendValidationError`, which the orchestrator surfaces to the frontend.

The client is built lazily so importing this module does not require an
API key — tests that mock `call_agent` keep working in CI.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import TypeVar

from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError

from backend.exceptions import BackendValidationError

# Load .env from the project root so every entry point (CLI script, pytest,
# Streamlit) sees the same environment without manual setup.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(_PROJECT_ROOT / ".env", override=False)

DEFAULT_MODEL = os.getenv("LLM_MODEL", "claude-sonnet-4-5")
DEFAULT_MAX_TOKENS = 8000

T = TypeVar("T", bound=BaseModel)

_client = None


def _get_client():
    """Lazy singleton — avoids requiring ANTHROPIC_API_KEY at import time."""
    global _client
    if _client is None:
        import anthropic
        _client = anthropic.Anthropic()  # picks up ANTHROPIC_API_KEY from env
    return _client


def _strip_code_fence(text: str) -> str:
    """Remove ```json … ``` or ``` … ``` wrapping that some models still emit."""
    s = text.strip()
    if s.startswith("```"):
        nl = s.find("\n")
        if nl != -1:
            s = s[nl + 1:]
    if s.endswith("```"):
        s = s[:-3].rstrip()
    return s.strip()


def call_agent(
    system_prompt: str,
    user_prompt: str,
    response_schema: type[T],
    *,
    model: str | None = None,
    max_tokens: int = DEFAULT_MAX_TOKENS,
) -> T:
    """Send (system_prompt, user_prompt) to Claude and return a validated `response_schema` instance.

    Behaviour matches Backend_Architecture_v1.md §6:
      * The response schema's JSON Schema is injected verbatim into the system prompt.
      * On the first `ValidationError`, the user prompt is augmented with the error
        message and the call is retried once.
      * A second failure raises `BackendValidationError` carrying the offending
        raw output (truncated to 500 chars).
    """
    schema_json = json.dumps(response_schema.model_json_schema(), indent=2)
    full_system = (
        f"{system_prompt}\n\n"
        "Respond with valid JSON matching this schema:\n"
        f"{schema_json}\n\n"
        "Do not include any text outside the JSON object. "
        "Do not wrap the JSON in code fences."
    )

    client = _get_client()
    current_user_prompt = user_prompt
    last_raw = ""

    for attempt in range(2):
        response = client.messages.create(
            model=model or DEFAULT_MODEL,
            max_tokens=max_tokens,
            system=full_system,
            messages=[{"role": "user", "content": current_user_prompt}],
        )
        last_raw = response.content[0].text
        cleaned = _strip_code_fence(last_raw)
        # Detect truncation up front — a max_tokens stop cuts JSON mid-token and
        # surfaces as a misleading "Invalid JSON: EOF" downstream.
        truncated = getattr(response, "stop_reason", None) == "max_tokens"
        try:
            if truncated:
                raise ValidationError.from_exception_data(
                    response_schema.__name__,
                    [{"type": "value_error", "loc": (), "input": cleaned,
                      "ctx": {"error": f"response truncated at max_tokens={max_tokens}"}}],
                )
            return response_schema.model_validate_json(cleaned)
        except ValidationError as e:
            if attempt == 0:
                hint = (
                    "Your previous response was truncated by the max_tokens limit. "
                    "Keep field values terse — short reasoning, shorter caveats — "
                    "and emit a complete JSON object."
                    if truncated else
                    f"Your previous response failed JSON schema validation with these errors:\n{e.errors()}"
                )
                current_user_prompt = (
                    f"{user_prompt}\n\n{hint}\n\n"
                    "Retry with strictly valid JSON that matches the schema exactly. "
                    "Do not wrap the JSON in code fences."
                )
                continue
            raise BackendValidationError(
                agent=response_schema.__name__,
                errors=e.errors() if not truncated else
                       f"response truncated at max_tokens={max_tokens}",
                raw_output=cleaned,
            )

    raise BackendValidationError(
        agent=response_schema.__name__,
        errors="unreachable retry loop exhausted",
        raw_output=last_raw,
    )


__all__ = ["call_agent", "DEFAULT_MODEL", "DEFAULT_MAX_TOKENS"]
