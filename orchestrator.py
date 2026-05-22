"""
Workflow control. Stub implementation for Fri 22:00 deliverable.

This file's responsibilities (per Backend_Architecture_v1.md §1):
  - Schedule 6 agents in fixed order
  - Insert Symbolic Gate between Clerk and Prosecutor
  - Maintain AgentActivity timestamps
  - Decide when Judge addresses Objections (no re-loop)

Current state (Fri 21:xx): Dummy. Real implementation lands after B ships
shared/schema.py at Fri 22:00. Until then, run_courtroom() returns a
minimally-valid mock CaseFile so B can integrate the frontend wiring.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shared.schema import CaseFile


class Orchestrator:
    """Single orchestrator instance, held as a module-level singleton by api.py."""

    def __init__(self) -> None:
        # When real implementation lands, this is where we load rules.yaml
        # and instantiate all six agents + the LLM client.
        # For now: nothing. We do not load rules.yaml yet because the file
        # may not exist on B's machine on first checkout.
        self._initialized = True

    def run_courtroom(self, case: "CaseFile") -> "CaseFile":
        """
        STUB: returns the input case with status flipped to VERDICT_READY
        and a single dummy AgentActivity entry per agent.

        Real implementation will:
          1. Detective fills facts
          2. Legal Clerk fills refs (via RAG retrieve())
          3. Symbolic Gate fills rule_firings (internal, no AgentActivity)
          4. Prosecutor fills allegations
          5. Defense fills defenses
          6. Critique fills objections (resolution=None)
          7. Judge fills verdict + missing_evidence + governance_checklist
             + follow_up_questions + assumptions + objection resolutions
        """
        # Import lazily so this module can be imported even before B has
        # shipped shared/schema.py. The real call will fail loudly with a
        # clear message if schema is missing.
        try:
            from shared.schema import CaseFile, AgentActivity, CaseStatus
        except ImportError as e:
            raise RuntimeError(
                "shared/schema.py not found. B (frontend/schema owner) must ship "
                "shared/schema.py before run_courtroom() can execute. "
                "Backend API surface is in place; only the dummy run path is blocked."
            ) from e

        # Walk through the six agents, pushing a COMPLETED AgentActivity each.
        # We mutate the case in place since pydantic models are passed by reference.
        for agent_name in (
            "Detective",
            "Legal Clerk",
            "Prosecutor",
            "Defense",
            "Critique",
            "Judge",
        ):
            case.agent_activity.append(
                AgentActivity(
                    agent=agent_name,
                    status="COMPLETED",
                    note="[STUB] dummy run; real agent not wired yet",
                )
            )

        case.status = CaseStatus.VERDICT_READY
        return case

    def handle_chat(self, case: "CaseFile", user_text: str) -> "CaseFile":
        """
        STUB: appends a single ChatTurn echoing the user's text.

        Real implementation will route through Judge agent with the full
        CaseFile as context, possibly add new facts, re-fire rules, update
        the verdict, and shrink missing_evidence.
        """
        try:
            from shared.schema import ChatTurn
        except ImportError as e:
            raise RuntimeError(
                "shared/schema.py not found. See run_courtroom() for details."
            ) from e

        case.chat_history.append(
            ChatTurn(
                role="user",
                text=user_text,
                triggered_updates=[],
            )
        )
        case.chat_history.append(
            ChatTurn(
                role="judge",
                text="[STUB] cross-examination not yet implemented",
                triggered_updates=[],
            )
        )
        return case
