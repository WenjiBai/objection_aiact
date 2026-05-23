"""Legal Clerk agent — retrieves relevant AI Act references via RAG.

Spec: Backend_Architecture_v1.md §3 / Frontend_Backend_Sync_v1.md §3.2 step 2.

The Legal Clerk's autonomous decision is **which queries to issue** to the
RAG retrieval layer based on Detective's facts. The retrieval itself is
handled by `rag.retrieve` (B-owned interface).

No LLM call: the rule corpus is small (~25 chunks) and the retrieval scoring
is what matters here. Skipping the LLM keeps total pipeline latency under
spec's 30 s budget. The "agent autonomy" is the query-derivation logic.
"""
from __future__ import annotations

from datetime import datetime

from backend.agents.base import BaseAgent
from rag.retrieve import retrieve
from shared.agent_outputs import LegalClerkOutput
from shared.schema import (
    AgentActivity, AgentName, AgentStatus, CaseFile, Evidence,
    EvidenceCategory, Reference,
)

_TOP_K_PER_QUERY = 4
_MAX_TOTAL_REFS = 12


class LegalClerkAgent(BaseAgent):
    agent_name = AgentName.LEGAL_CLERK
    output_schema = LegalClerkOutput
    prompt_filename = "legal_clerk.txt"  # unused — run() is overridden
    action_summary = "Retrieving relevant AI Act passages"

    def run(self, case: CaseFile) -> CaseFile:  # type: ignore[override]
        """Override BaseAgent.run — no LLM call, just deterministic RAG dispatch."""
        started_at = datetime.now()
        queries = self._derive_queries(case.facts)

        seen: dict[str, Reference] = {}
        for q in queries:
            for ref in retrieve(q, top_k=_TOP_K_PER_QUERY):
                if ref.code not in seen:
                    seen[ref.code] = ref

        ordered = sorted(
            seen.values(),
            key=lambda r: r.relevance_score if r.relevance_score is not None else 0.0,
            reverse=True,
        )[:_MAX_TOTAL_REFS]

        case.refs = ordered
        case.agent_activity.append(
            AgentActivity(
                agent=self.agent_name,
                action=self.action_summary,
                status=AgentStatus.COMPLETED,
                started_at=started_at,
                completed_at=datetime.now(),
                output_summary=(
                    f"{len(ordered)} refs across {len(queries)} queries: "
                    + ", ".join(r.code for r in ordered[:5])
                    + ("…" if len(ordered) > 5 else "")
                ),
            )
        )
        return case

    def _derive_queries(self, facts: list[Evidence]) -> list[str]:
        """Pick search queries grounded in extracted facts.

        Empty fact lists still get the general query so retrieval never returns nothing.
        """
        queries: list[str] = [
            "EU AI Act risk classification high-risk obligations",
        ]

        sectors = [
            f.structured_value for f in facts
            if f.category == EvidenceCategory.SECTOR and f.structured_value
        ]
        for s in sectors:
            queries.append(f"AI system {s} Annex III high risk")

        outputs = [
            (f.structured_value or "").lower() for f in facts
            if f.category == EvidenceCategory.OUTPUT
        ]
        if "generation" in outputs:
            queries.append("AI generated content labelling Article 50 transparency")

        gpai_present = any(
            f.category == EvidenceCategory.GPAI_USAGE and (f.structured_value or "").lower() == "true"
            for f in facts
        )
        if gpai_present:
            queries.append("GPAI general-purpose AI obligations Chapter V Article 51 53 55")

        if any(f.category == EvidenceCategory.HUMAN_OVERSIGHT for f in facts):
            queries.append("human oversight Article 14 override mechanism")

        if any(f.category == EvidenceCategory.DECISION_IMPACT for f in facts):
            queries.append("fundamental rights impact assessment FRIA Article 27")

        ai_gen_true = any(
            f.category == EvidenceCategory.AI_GENERATED_CONTENT and (f.structured_value or "").lower() == "true"
            for f in facts
        )
        if ai_gen_true:
            queries.append("synthetic content deep fake disclosure Article 50 Recital 134")

        return queries

    # BaseAgent requires these abstract methods even though run() is overridden.
    def build_prompt(self, case: CaseFile) -> tuple[str, str]:
        return "", ""

    def merge(self, case: CaseFile, output) -> None:
        pass


__all__ = ["LegalClerkAgent"]
