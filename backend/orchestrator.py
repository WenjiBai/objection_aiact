"""6-agent + symbolic-gate courtroom orchestrator.

Spec: Backend_Architecture_v1.md §2.3 / §2.5 / §5.

Workflow (run_courtroom):
    Detective → Legal Clerk → [Symbolic Gate] → Prosecutor → Defense
    → Critique → Judge  →  status=VERDICT_READY

The symbolic gate is an internal step — it pushes NO AgentActivity entry.
Each of the 6 agents pushes exactly one COMPLETED (or FAILED) entry, so the
final CaseFile has exactly 6 agent_activity rows in the timeline.

`handle_chat` runs the ChatAgent (real Judge re-evaluation, Phase 5).
"""
from __future__ import annotations

from backend.agents.chat import ChatAgent
from backend.agents.critique import CritiqueAgent
from backend.agents.defense import DefenseAgent
from backend.agents.detective import DetectiveAgent
from backend.agents.judge import JudgeAgent
from backend.agents.legal_clerk import LegalClerkAgent
from backend.agents.prosecutor import ProsecutorAgent
from backend.symbolic.gate import evaluate_rules
from backend.symbolic.loader import load_rules
from shared.schema import CaseFile, CaseStatus


class Orchestrator:
    """Sequential state machine wiring the 6 agents + symbolic gate.

    Built once at module import and reused for every request. The rule file
    is read at construction so we don't re-parse it per call.
    """

    def __init__(self) -> None:
        self.rules = load_rules()
        self.detective = DetectiveAgent()
        self.legal_clerk = LegalClerkAgent()
        self.prosecutor = ProsecutorAgent()
        self.defense = DefenseAgent()
        self.critique = CritiqueAgent()
        self.judge = JudgeAgent()
        self.chat = ChatAgent()

    # ---------------------------------------------------- public entry points

    def run_courtroom(self, case: CaseFile) -> CaseFile:
        """Full pipeline. Pre: status=NEW + non-empty documents. Post: VERDICT_READY."""
        case.status = CaseStatus.INGESTING
        self.detective.run(case)

        case.status = CaseStatus.RETRIEVING
        self.legal_clerk.run(case)

        # Symbolic Gate is an internal step — no AgentActivity entry per spec §3.2.
        case.rule_firings = evaluate_rules(case, self.rules)

        case.status = CaseStatus.DELIBERATING
        self.prosecutor.run(case)
        self.defense.run(case)
        self.critique.run(case)
        self.judge.run(case)

        # Defensive fallback — Judge prompt requires one resolution per objection,
        # but if the model still slips one through, attach a placeholder rather
        # than violating the spec invariant.
        for objection in case.objections:
            if objection.resolution is None:
                objection.resolution = (
                    "Acknowledged — Judge did not emit an explicit resolution."
                )

        case.status = CaseStatus.VERDICT_READY
        return case

    def handle_chat(self, case: CaseFile, user_text: str) -> CaseFile:
        """One cross-examination turn — real LLM Judge re-evaluation (Phase 5)."""
        return self.chat.run(case, user_text)


__all__ = ["Orchestrator"]
