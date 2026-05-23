"""Detective agent — extracts the structured Facts Table from uploaded docs.

Spec: ActScout_Hybrid_Concept_v2.md §4.1 / Frontend_Backend_Sync_v1.md §7.1.

The Detective's `structured_value` discipline is what allows the symbolic
gate to fire downstream — see backend/prompts/detective.txt for the
controlled vocabulary contract.
"""
from __future__ import annotations

from backend.agents.base import BaseAgent
from shared.agent_outputs import DetectiveOutput
from shared.schema import AgentName, CaseFile


class DetectiveAgent(BaseAgent):
    agent_name = AgentName.DETECTIVE
    output_schema = DetectiveOutput
    prompt_filename = "detective.txt"
    action_summary = "Extracting facts from uploaded documents"

    def build_prompt(self, case: CaseFile) -> tuple[str, str]:
        system_prompt = self.load_prompt()

        doc_blocks: list[str] = []
        for d in case.documents:
            doc_blocks.append(
                f"=== doc_id: {d.doc_id} | filename: {d.filename} ===\n{d.content}"
            )
        user_prompt = (
            "Here are the documents for one AI use case. "
            "Extract the Facts Table following the contract above.\n\n"
            + "\n\n".join(doc_blocks)
        )
        return system_prompt, user_prompt

    def merge(self, case: CaseFile, output: DetectiveOutput) -> None:
        case.facts = output.facts

    def summarise(self, output: DetectiveOutput) -> str:
        categories = {f.category.value for f in output.facts}
        return f"{len(output.facts)} facts across {len(categories)} categories"


__all__ = ["DetectiveAgent"]
