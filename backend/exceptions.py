"""Backend-specific exceptions.

Spec: Backend_Architecture_v1.md §7.

Raised inside `backend.api` when an agent output fails Pydantic validation
after retry. Frontend (B) catches this and rolls back to a pre-call snapshot
(Sync v1 §6.3).
"""
from __future__ import annotations

from typing import Any


class BackendValidationError(Exception):
    """Raised when an agent's output cannot be coerced into its Pydantic schema.

    Carries:
        agent: name of the failing agent (or call site) for UI display.
        errors: usually `pydantic.ValidationError.errors()` (list[dict]); may be
            a plain string for non-LLM contract violations (e.g. wrong status).
        raw_output: first 500 chars of the offending LLM output, for debugging.
    """

    def __init__(self, agent: str, errors: Any, raw_output: str = ""):
        self.agent = agent
        self.errors = errors
        self.raw_output = raw_output[:500] if raw_output else ""
        super().__init__(f"[{agent}] backend validation failed: {errors}")


__all__ = ["BackendValidationError"]
