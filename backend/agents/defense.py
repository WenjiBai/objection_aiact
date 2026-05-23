"""Defense agent — builds exemption / mitigation arguments against allegations.

Spec: ActScout_Hybrid_Concept_v2.md §4.1 / Frontend_Backend_Sync_v1.md §7.1.

The Defense is required to be intellectually honest: if a mitigation is
claimed but the underlying procedure is undocumented, `requires_documentation`
must be `True`. That sets up the OBJECTION the Critique agent will raise next.
"""
from __future__ import annotations

import json

from backend.agents.base import BaseAgent
from shared.agent_outputs import DefenseOutput
from shared.schema import AgentName, CaseFile


class DefenseAgent(BaseAgent):
    agent_name = AgentName.DEFENSE
    output_schema = DefenseOutput
    prompt_filename = "defense.txt"
    action_summary = "Checking exemptions and mitigations"

    def build_prompt(self, case: CaseFile) -> tuple[str, str]:
        system_prompt = self.load_prompt()

        facts_view = [
            {
                "code": f.code,
                "category": f.category.value,
                "structured_value": f.structured_value,
                "text": f.text,
            }
            for f in case.facts
        ]
        refs_view = [
            {"code": r.code, "title": r.title, "snippet": r.snippet}
            for r in case.refs
        ]
        allegations_view = [
            {
                "allegation_id": a.allegation_id,
                "tier": a.tier.value,
                "claim": a.claim,
                "basis_evidence_codes": a.basis_evidence_codes,
                "basis_ref_codes": a.basis_ref_codes,
                "strength": a.strength.value,
            }
            for a in case.allegations
        ]

        user_prompt = (
            "Facts Table (E-codes):\n"
            f"{json.dumps(facts_view, indent=2, ensure_ascii=False)}\n\n"
            "Retrieved References (R-codes):\n"
            f"{json.dumps(refs_view, indent=2, ensure_ascii=False)}\n\n"
            "Prosecutor allegations (ALL-codes):\n"
            f"{json.dumps(allegations_view, indent=2, ensure_ascii=False)}\n\n"
            "Build defenses per the contract above. "
            "Mark requires_documentation=true whenever the supporting evidence is claimed-but-not-documented."
        )
        return system_prompt, user_prompt

    def merge(self, case: CaseFile, output: DefenseOutput) -> None:
        case.defenses = output.defenses

    def summarise(self, output: DefenseOutput) -> str:
        if not output.defenses:
            return "no defenses (no allegations or no mitigation available)"
        undocumented = sum(1 for d in output.defenses if d.requires_documentation)
        return f"{len(output.defenses)} defenses · {undocumented} flagged requires_documentation=true"


__all__ = ["DefenseAgent"]
