"""Judge agent — issues the Preliminary Verdict + resolves every Objection.

Spec: Backend_Architecture_v1.md §5 step 7 / Frontend_Backend_Sync_v1.md §3.2.

The Judge MUST set `Objection.resolution` for every objection raised by the
Critique step — that's a hard spec invariant. Since shared/agent_outputs.py's
`JudgeOutput` does not (yet) carry resolutions, this agent uses a locally
extended schema `_JudgeFullOutput` for the LLM call, then unpacks both the
JudgeOutput fields and the resolutions onto the CaseFile in `merge`.
"""
from __future__ import annotations

import json

from pydantic import BaseModel, ConfigDict, Field

from backend.agents.base import BaseAgent
from shared.agent_outputs import JudgeOutput
from shared.schema import AgentName, CaseFile


class _ObjectionResolution(BaseModel):
    model_config = ConfigDict(extra="forbid", use_enum_values=False)
    objection_id: str
    resolution: str


class _JudgeFullOutput(JudgeOutput):
    """Extends `JudgeOutput` with the per-objection resolutions the spec demands."""
    objection_resolutions: list[_ObjectionResolution] = Field(default_factory=list)


class JudgeAgent(BaseAgent):
    agent_name = AgentName.JUDGE
    output_schema = _JudgeFullOutput
    prompt_filename = "judge.txt"
    action_summary = "Issuing preliminary verdict"
    # Judge emits verdict + missing-evidence + governance checklist + assumptions
    # + one resolution per objection — the largest payload in the pipeline.
    max_tokens = 16000

    def build_prompt(self, case: CaseFile) -> tuple[str, str]:
        system_prompt = self.load_prompt()

        facts_view = [
            {"code": f.code, "category": f.category.value,
             "structured_value": f.structured_value, "text": f.text}
            for f in case.facts
        ]
        refs_view = [
            {"code": r.code, "title": r.title, "snippet": r.snippet}
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
        allegations_view = [
            {
                "allegation_id": a.allegation_id, "tier": a.tier.value,
                "claim": a.claim, "strength": a.strength.value,
                "basis_evidence_codes": a.basis_evidence_codes,
                "basis_ref_codes": a.basis_ref_codes,
            }
            for a in case.allegations
        ]
        defenses_view = [
            {
                "defense_id": d.defense_id,
                "targets_allegation_id": d.targets_allegation_id,
                "type": d.type, "claim": d.claim,
                "requires_documentation": d.requires_documentation,
                "basis_evidence_codes": d.basis_evidence_codes,
                "basis_ref_codes": d.basis_ref_codes,
            }
            for d in case.defenses
        ]
        objections_view = [
            {
                "objection_id": o.objection_id,
                "target_type": o.target_type, "target_id": o.target_id,
                "reason": o.reason, "severity": o.severity.value,
                "challenging_evidence_codes": o.challenging_evidence_codes,
            }
            for o in case.objections
        ]

        objection_ids = [o.objection_id for o in case.objections]
        objection_demand = (
            f"\n\nYou MUST emit exactly one entry in `objection_resolutions` per "
            f"objection above. Required objection_ids: {objection_ids}."
            if objection_ids else
            "\n\n(No objections raised; objection_resolutions should be an empty list.)"
        )

        user_prompt = (
            "Facts Table:\n"
            f"{json.dumps(facts_view, indent=2, ensure_ascii=False)}\n\n"
            "Retrieved References:\n"
            f"{json.dumps(refs_view, indent=2, ensure_ascii=False)}\n\n"
            "Symbolic Rule Firings:\n"
            f"{json.dumps(firings_view, indent=2, ensure_ascii=False)}\n\n"
            "Prosecutor allegations:\n"
            f"{json.dumps(allegations_view, indent=2, ensure_ascii=False)}\n\n"
            "Defense arguments:\n"
            f"{json.dumps(defenses_view, indent=2, ensure_ascii=False)}\n\n"
            "Critique objections (resolution is null — you must fill them):\n"
            f"{json.dumps(objections_view, indent=2, ensure_ascii=False)}"
            + objection_demand
        )
        return system_prompt, user_prompt

    def merge(self, case: CaseFile, output: _JudgeFullOutput) -> None:
        case.verdict = output.verdict
        case.missing_evidence = output.missing_evidence
        case.governance_checklist = output.governance_checklist
        case.follow_up_questions = output.follow_up_questions
        case.assumptions = output.assumptions

        # Apply objection resolutions back onto the in-place Objection objects.
        by_id = {r.objection_id: r.resolution for r in output.objection_resolutions}
        for obj in case.objections:
            if obj.objection_id in by_id:
                obj.resolution = by_id[obj.objection_id]

    def summarise(self, output: _JudgeFullOutput) -> str:
        v = output.verdict
        return (
            f"{v.tier.value.upper()} · "
            f"confidence={v.confidence_score}/10 ({v.confidence_label.value}) · "
            f"{len(output.missing_evidence)} missing-evidence items · "
            f"{len(output.objection_resolutions)} objections resolved"
        )


__all__ = ["JudgeAgent"]
