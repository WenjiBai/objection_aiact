"""Agent output wrappers — one per agent in the 6-agent courtroom.

These are the JSON shapes Person A's prompts ask Claude to emit. Each wrapper
is a thin Pydantic model whose schema is dumped to `schemas/<Name>.json` by
`scripts/dump_schemas.py` and embedded verbatim into the agent prompt.

A then validates the LLM response with `<Name>.model_validate_json(raw)` and
merges the fields back into the shared CaseFile. Wrapping (rather than dumping
raw `list[Evidence]` etc.) lets us add per-agent metadata later (e.g. confidence
in extraction, retrieval stats) without breaking prompts.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .schema import (
    Allegation, Assumption, ChatTurn, ChecklistItem, Defense, Evidence,
    MissingEvidenceItem, Objection, Reference, Verdict,
)


class _AgentOut(BaseModel):
    """Base — same strict config as the rest of the schema."""
    model_config = ConfigDict(extra="forbid", use_enum_values=False)


class DetectiveOutput(_AgentOut):
    """Detective extracts facts from uploaded documents."""
    facts: list[Evidence]
    notes: str = Field(default="", description="Free-text reasoning summary (optional).")


class LegalClerkOutput(_AgentOut):
    """Legal Clerk retrieves relevant AI Act passages via RAG."""
    refs: list[Reference]
    notes: str = Field(default="", description="Retrieval rationale (optional).")


class ProsecutorOutput(_AgentOut):
    """Prosecutor raises risk allegations grounded in facts + references."""
    allegations: list[Allegation]
    notes: str = ""


class DefenseOutput(_AgentOut):
    """Defense argues exemptions / mitigations against specific allegations."""
    defenses: list[Defense]
    notes: str = ""


class CritiqueOutput(_AgentOut):
    """Critique raises OBJECTIONS on weak/contradictory claims."""
    objections: list[Objection]
    notes: str = ""


class JudgeOutput(_AgentOut):
    """Judge fuses prior agents into the Preliminary Verdict bundle.

    Fills the post-deliberation block of CaseFile (Sync v1 §3.2 step 7).
    """
    verdict: Verdict
    missing_evidence: list[MissingEvidenceItem] = Field(default_factory=list)
    governance_checklist: list[ChecklistItem] = Field(default_factory=list)
    follow_up_questions: list[str] = Field(default_factory=list)
    assumptions: list[Assumption] = Field(default_factory=list)


class ChatOutput(_AgentOut):
    """One cross-examination turn — the diff the Judge wants applied.

    Frontend reads `judge_turn` to render. Backend applies the rest as a diff
    onto the CaseFile (add new evidence, resolve objections, update verdict).
    """
    judge_turn: ChatTurn
    new_facts: list[Evidence] = Field(default_factory=list)
    new_allegations: list[Allegation] = Field(default_factory=list)
    new_objections: list[Objection] = Field(default_factory=list)
    resolved_objection_ids: list[str] = Field(default_factory=list)
    resolved_missing_evidence_descriptions: list[str] = Field(
        default_factory=list,
        description="Match-by-description since MissingEvidenceItem has no id.",
    )
    updated_verdict: Optional[Verdict] = None


__all__ = [
    "DetectiveOutput", "LegalClerkOutput", "ProsecutorOutput",
    "DefenseOutput", "CritiqueOutput", "JudgeOutput", "ChatOutput",
]
