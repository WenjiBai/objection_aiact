"""
The single contract surface between backend and frontend.

B imports:
    from backend.api import run_courtroom, handle_chat, BackendValidationError

This module is intentionally tiny. All workflow logic lives in
backend/orchestrator.py. All agent logic lives under backend/agents/.
Any internal refactor inside backend/ must not change this file's surface.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from backend.exceptions import BackendValidationError
from backend.orchestrator import Orchestrator

if TYPE_CHECKING:
    from shared.schema import CaseFile

# Module-level singleton. Loads rules.yaml exactly once at import time
# (when real implementation lands). Cheap to keep around.
_orchestrator = Orchestrator()


def run_courtroom(case: "CaseFile") -> "CaseFile":
    """
    Full 6-agent pipeline.

    Pre:
      - case.status == NEW
      - case.documents is non-empty

    Post:
      - case.status in {VERDICT_READY, ERROR}
      - case.agent_activity has >= 6 COMPLETED entries
      - every Objection.resolution is non-None
      - all codes (E-/R-/A-) are globally unique within the CaseFile

    Latency budget: 30 seconds.

    Raises:
        BackendValidationError: an agent's LLM output failed Pydantic
            validation twice in a row. Frontend should roll back to the
            previous snapshot and show an error toast.
    """
    return _orchestrator.run_courtroom(case)


def handle_chat(case: "CaseFile", user_text: str) -> "CaseFile":
    """
    One cross-examination turn.

    Pre:
      - case.status == VERDICT_READY

    Post:
      - case.chat_history appended with user + judge turns
      - May add facts, re-fire rules, update verdict, shrink missing_evidence
      - ChatTurn.triggered_updates is always populated (possibly empty list)

    Forbidden side-effects (handled internally by orchestrator):
      - Never deletes documents
      - Never renames existing codes
      - Never clears agent_activity

    Raises:
        BackendValidationError: agent output failed Pydantic validation twice.
    """
    return _orchestrator.handle_chat(case, user_text)


__all__ = ["run_courtroom", "handle_chat", "BackendValidationError"]
