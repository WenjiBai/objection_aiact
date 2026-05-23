"""Prosecutor agent — raises grounded risk allegations under the EU AI Act.

Spec: ActScout_Hybrid_Concept_v2.md §4.1 / Frontend_Backend_Sync_v1.md §7.1.

Every allegation references real E-codes (from Detective) and R-codes (from
Legal Clerk), so the schema's "codes must exist" invariant (Sync v1 §2.1.3)
is structurally satisfied if the prompt is followed. Validation falls back
to the LLM client's retry-on-validation-error loop.
"""
from __future__ import annotations

import json

from backend.agents.base import BaseAgent
from shared.agent_outputs import ProsecutorOutput
from shared.schema import AgentName, CaseFile


class ProsecutorAgent(BaseAgent):
    agent_name = AgentName.PROSECUTOR
    output_schema = ProsecutorOutput
    prompt_filename = "prosecutor.txt"
    action_summary = "Raising risk allegations"

    def build_prompt(self, case: CaseFile) -> tuple[str, str]:
        system_prompt = self.load_prompt()

        # Compact facts view — full text is dropped to keep tokens manageable
        # if Detective produced a long list.
        facts_view = [
            {
                "code": f.code,
                "category": f.category.value,
                "structured_value": f.structured_value,
                "text": f.text,
                "relevance": f.relevance.value,
            }
            for f in case.facts
        ]
        refs_view = [
            {
                "code": r.code,
                "title": r.title,
                "snippet": r.snippet,
                "source_type": r.source_type.value,
            }
            for r in case.refs
        ]
        firings_view = [
            {
                "rule_id": rf.rule_id,
                "description": rf.description,
                "fired": rf.fired,
                "supporting_evidence_codes": rf.supporting_evidence_codes,
                "maps_to_refs": rf.maps_to_refs,
            }
            for rf in case.rule_firings
        ]

        user_prompt = (
            "Facts Table (E-codes):\n"
            f"{json.dumps(facts_view, indent=2, ensure_ascii=False)}\n\n"
            "Retrieved References (R-codes):\n"
            f"{json.dumps(refs_view, indent=2, ensure_ascii=False)}\n\n"
            "Symbolic Rule Firings:\n"
            f"{json.dumps(firings_view, indent=2, ensure_ascii=False)}\n\n"
            "Raise grounded allegations per the contract above. "
            "Every basis_evidence_codes / basis_ref_codes must reference codes that exist above."
        )
        return system_prompt, user_prompt

    def merge(self, case: CaseFile, output: ProsecutorOutput) -> None:
        case.allegations = output.allegations

    def summarise(self, output: ProsecutorOutput) -> str:
        if not output.allegations:
            return "no allegations (minimal-risk path)"
        tiers = {a.tier.value for a in output.allegations}
        return f"{len(output.allegations)} allegations · tiers: {sorted(tiers)}"


__all__ = ["ProsecutorAgent"]
