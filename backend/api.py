"""Backend contract surface — the ONLY module the frontend imports from `backend`.

Spec: Backend_Architecture_v1.md §4 / Frontend_Backend_Sync_v1.md §3.

`run_courtroom` and `handle_chat` are synchronous, max latency 30 s, and may
raise `BackendValidationError`. All workflow logic lives in `Orchestrator`;
this file stays a thin adapter that validates pre-conditions and forwards.
"""
from __future__ import annotations

from pydantic import ValidationError

from backend.exceptions import BackendValidationError  # re-exported for B
from backend.orchestrator import Orchestrator
from shared.schema import CaseFile, CaseStatus

# Module-level singleton — Orchestrator.__init__ parses rules.yaml once.
_orchestrator = Orchestrator()


def run_courtroom(case: CaseFile) -> CaseFile:
    """Full 6-agent pipeline.

    Pre:  case.status == NEW, case.documents non-empty.
    Post: case.status in {VERDICT_READY, ERROR}; agent_activity has 6 entries;
          every Objection.resolution is non-None.

    Raises:
        BackendValidationError: agent output failed schema validation twice.
    """
    result = _orchestrator.run_courtroom(case)
    try:
        return CaseFile.model_validate(result.model_dump())
    except ValidationError as e:
        raise BackendValidationError(agent="run_courtroom", errors=e.errors())


def handle_chat(case: CaseFile, user_text: str) -> CaseFile:
    """One cross-examination turn.

    Pre:  case.status == VERDICT_READY (or RE_EXAMINING).
    Post: case.chat_history appended with user + judge turns; may add facts,
          re-fire rules, update verdict, shrink missing_evidence.
    """
    if case.status not in (CaseStatus.VERDICT_READY, CaseStatus.RE_EXAMINING):
        raise BackendValidationError(
            agent="handle_chat",
            errors=f"case.status must be verdict_ready, got {case.status.value}",
        )
    result = _orchestrator.handle_chat(case, user_text)
    try:
        return CaseFile.model_validate(result.model_dump())
    except ValidationError as e:
        raise BackendValidationError(agent="handle_chat", errors=e.errors())


__all__ = ["run_courtroom", "handle_chat", "BackendValidationError"]
