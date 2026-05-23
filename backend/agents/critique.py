"""Critique agent — raises OBJECTIONS on weak claims and contradictions.

Spec: ActScout_Hybrid_Concept_v2.md §4.1 / §6.4 / Frontend_Backend_Sync_v1.md §7.1.

Critique populates `case.objections` with `resolution=None` for every entry.
The Judge (step 7) must resolve every objection before the case reaches
VERDICT_READY — see orchestrator.run_courtroom.
"""
from __future__ import annotations

import json

from backend.agents.base import BaseAgent
from shared.agent_outputs import CritiqueOutput
from shared.schema import AgentName, CaseFile


class CritiqueAgent(BaseAgent):
    agent_name = AgentName.CRITIQUE
    output_schema = CritiqueOutput
    prompt_filename = "critique.txt"
    action_summary = "Reviewing claims for weak evidence"

    def build_prompt(self, case: CaseFile) -> tuple[str, str]:
        system_prompt = self.load_prompt()

        facts_view = [
            {"code": f.code, "category": f.category.value,
             "structured_value": f.structured_value, "text": f.text}
            for f in case.facts
        ]
        refs_view = [{"code": r.code, "title": r.title} for r in case.refs]
        allegations_view = [
            {
                "allegation_id": a.allegation_id,
                "tier": a.tier.value,
                "strength": a.strength.value,
                "claim": a.claim,
                "basis_evidence_codes": a.basis_evidence_codes,
                "basis_ref_codes": a.basis_ref_codes,
            }
            for a in case.allegations
        ]
        defenses_view = [
            {
                "defense_id": d.defense_id,
                "targets_allegation_id": d.targets_allegation_id,
                "type": d.type,
                "requires_documentation": d.requires_documentation,
                "claim": d.claim,
                "basis_evidence_codes": d.basis_evidence_codes,
                "basis_ref_codes": d.basis_ref_codes,
            }
            for d in case.defenses
        ]

        user_prompt = (
            "Facts Table:\n"
            f"{json.dumps(facts_view, indent=2, ensure_ascii=False)}\n\n"
            "Retrieved References:\n"
            f"{json.dumps(refs_view, indent=2, ensure_ascii=False)}\n\n"
            "Prosecutor allegations:\n"
            f"{json.dumps(allegations_view, indent=2, ensure_ascii=False)}\n\n"
            "Defense arguments:\n"
            f"{json.dumps(defenses_view, indent=2, ensure_ascii=False)}\n\n"
            "Review the courtroom record. Raise OBJECTIONS only where claims are "
            "weak, contradicted, or undocumented. Leave `resolution` as null — "
            "the Judge will fill it in the next step."
        )
        return system_prompt, user_prompt

    def merge(self, case: CaseFile, output: CritiqueOutput) -> None:
        # Force resolution=None on entry — Judge fills it.
        for obj in output.objections:
            obj.resolution = None
        case.objections = output.objections

    def summarise(self, output: CritiqueOutput) -> str:
        if not output.objections:
            return "no objections (clean record)"
        sev = {o.severity.value for o in output.objections}
        return f"{len(output.objections)} objection(s) · severities: {sorted(sev)}"


__all__ = ["CritiqueAgent"]
