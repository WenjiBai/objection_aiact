"""Backend entry points — STUB until Person A wires the real agents.

Contract (Frontend_Backend_Sync_v1.md §3 / CaseFile_Schema_Spec.md §"Backend 入口约定"):
- Both functions are synchronous.
- run_courtroom: NEW → VERDICT_READY (or ERROR).
- handle_chat: appends user turn + judge turn; may update verdict, facts, rules.
- On second schema-validation failure, raise BackendValidationError; frontend rolls back.
"""

from __future__ import annotations

from pydantic import ValidationError

from shared.mock import make_mock_case_a, make_mock_case_b, simulate_chat_response
from shared.schema import CaseFile, CaseStatus


class BackendValidationError(Exception):
    """Raised when an agent's output cannot be coerced into CaseFile after retries."""

    def __init__(self, agent: str, errors):
        self.agent = agent
        self.errors = errors
        super().__init__(f"[{agent}] backend validation failed: {errors}")


# --------------------------------------------------------------- entries

def run_courtroom(case: CaseFile) -> CaseFile:
    """Full pipeline. STUB — routes to a mock CaseFile based on doc content.

    Person A's real implementation will run the 6-agent graph.
    """
    blob = " ".join(d.content for d in case.documents).lower()
    hr_signal = any(k in blob for k in ("cv", "applicant", "hiring", "screen", "rank", "hr "))
    forecast_signal = any(k in blob for k in ("forecast", "inventory", "stock", "logistics"))

    if forecast_signal and not hr_signal:
        result = make_mock_case_b()
    else:
        result = make_mock_case_a()  # default to the killer demo

    # Preserve the user-supplied identity and uploaded docs.
    if case.case_id:
        result.case_id = case.case_id
    if case.documents:
        result.documents = case.documents
    result.status = CaseStatus.VERDICT_READY

    try:
        return CaseFile.model_validate(result.model_dump())
    except ValidationError as e:
        raise BackendValidationError(agent="run_courtroom", errors=e.errors())


def handle_chat(case: CaseFile, user_text: str) -> CaseFile:
    """One cross-exam turn. STUB — delegates to simulate_chat_response()."""
    if case.status not in (CaseStatus.VERDICT_READY, CaseStatus.RE_EXAMINING):
        raise BackendValidationError(
            agent="handle_chat",
            errors=f"case.status must be verdict_ready, got {case.status.value}",
        )
    updated = simulate_chat_response(case, user_text)
    try:
        return CaseFile.model_validate(updated.model_dump())
    except ValidationError as e:
        raise BackendValidationError(agent="handle_chat", errors=e.errors())
