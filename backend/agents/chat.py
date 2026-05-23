"""Chat agent — Judge speaking again during cross-examination.

Spec: Backend_Architecture_v1.md §4 (handle_chat contract) /
      Frontend_Backend_Sync_v1.md §3.3 / §7.1 chat test.

Conceptually this is the Judge re-evaluating with new user input. We treat
chat output as a *structured diff* (`ChatOutput`) which the backend applies
onto the live CaseFile. The signature demo moment is:
    user types "HR managers can override / applicants can appeal"
    → confidence rises by ≥ 2, missing_evidence shrinks by ≥ 2.

Does NOT inherit from BaseAgent because the signature is run(case, user_text)
rather than run(case).
"""
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from backend.exceptions import BackendValidationError
from backend.llm.client import call_agent
from backend.symbolic.gate import evaluate_rules
from backend.symbolic.loader import load_rules
from shared.agent_outputs import ChatOutput
from shared.schema import (
    AgentActivity, AgentName, AgentStatus, CaseFile, CaseStatus, ChatTurn,
    Evidence,
)

PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "chat.txt"


class ChatAgent:
    """Real cross-examination implementation — Phase 5."""

    action_summary = "Cross-examination — re-evaluating with new evidence"

    def __init__(self) -> None:
        self._system_prompt = PROMPT_PATH.read_text(encoding="utf-8")
        self._rules = load_rules()

    def run(self, case: CaseFile, user_text: str) -> CaseFile:
        case.status = CaseStatus.RE_EXAMINING

        # 1. Append the user's turn immediately so prompt sees current chat state.
        case.chat_history.append(
            ChatTurn(role="user", text=user_text)
        )

        started_at = datetime.now()
        user_prompt = self._build_user_prompt(case, user_text)

        try:
            diff: ChatOutput = call_agent(
                self._system_prompt, user_prompt, ChatOutput,
            )
        except BackendValidationError:
            # Push a FAILED activity entry and re-raise — frontend rolls back.
            case.agent_activity.append(
                AgentActivity(
                    agent=AgentName.JUDGE,
                    action=self.action_summary,
                    status=AgentStatus.FAILED,
                    started_at=started_at,
                    completed_at=datetime.now(),
                    output_summary="Chat agent failed validation after retry.",
                )
            )
            raise

        # 2. Apply the diff onto the CaseFile.
        triggered = self._apply_diff(case, diff)

        # 3. Append Judge's turn with the triggered_updates list backend computed.
        judge_turn = diff.judge_turn
        judge_turn.triggered_updates = triggered
        case.chat_history.append(judge_turn)

        # 4. AgentActivity (counts as a Judge speaking again — uses JUDGE).
        case.agent_activity.append(
            AgentActivity(
                agent=AgentName.JUDGE,
                action=self.action_summary,
                status=AgentStatus.COMPLETED,
                started_at=started_at,
                completed_at=datetime.now(),
                output_summary=self._summarise(diff, triggered),
            )
        )

        case.status = CaseStatus.VERDICT_READY
        return case

    # ---------------------------------------------------------- internals

    def _build_user_prompt(self, case: CaseFile, user_text: str) -> str:
        import json

        facts_view = [
            {"code": f.code, "category": f.category.value,
             "structured_value": f.structured_value, "text": f.text}
            for f in case.facts
        ]
        objections_view = [
            {
                "objection_id": o.objection_id,
                "target_type": o.target_type, "target_id": o.target_id,
                "reason": o.reason,
                "current_resolution": o.resolution,
            }
            for o in case.objections
        ]
        missing_view = [
            {"description": m.description, "severity": m.severity.value,
             "blocks_verdict": m.blocks_verdict}
            for m in case.missing_evidence
        ]
        verdict_view = (
            {
                "tier": case.verdict.tier.value,
                "confidence_score": case.verdict.confidence_score,
                "confidence_label": case.verdict.confidence_label.value,
                "reasoning_trail": case.verdict.reasoning_trail,
            }
            if case.verdict else None
        )

        return (
            "Current Facts Table:\n"
            f"{json.dumps(facts_view, indent=2, ensure_ascii=False)}\n\n"
            "Current Verdict:\n"
            f"{json.dumps(verdict_view, indent=2, ensure_ascii=False)}\n\n"
            "Current Objections (with their original resolutions):\n"
            f"{json.dumps(objections_view, indent=2, ensure_ascii=False)}\n\n"
            "Current Missing Evidence:\n"
            f"{json.dumps(missing_view, indent=2, ensure_ascii=False)}\n\n"
            f"USER CHAT TURN:\n{user_text}\n\n"
            "Return a ChatOutput diff per the contract above. Be conservative — "
            "only modify what this turn actually changes."
        )

    def _apply_diff(self, case: CaseFile, diff: ChatOutput) -> list[str]:
        """Mutate `case` per the diff, return list of triggered_updates strings for the UI."""
        triggered: list[str] = []

        # 1. New facts — renumber to avoid collisions with existing E-codes.
        if diff.new_facts:
            next_n = self._next_evidence_number(case)
            for fact in diff.new_facts:
                fact.code = f"E-{next_n:02d}"
                next_n += 1
                case.facts.append(fact)
                triggered.append(fact.code)

        # 2. Re-fire rules if facts changed.
        if diff.new_facts:
            case.rule_firings = evaluate_rules(case, self._rules)
            triggered.append("rule_firings")

        # 3. Resolve objections by id.
        if diff.resolved_objection_ids:
            for obj in case.objections:
                if obj.objection_id in diff.resolved_objection_ids:
                    obj.resolution = (
                        f"Withdrawn — user supplied new evidence during cross-examination. "
                        f"({obj.resolution[:80] + '…' if obj.resolution else ''})"
                        if obj.resolution
                        else "Withdrawn — user supplied new evidence during cross-examination."
                    )
                    triggered.append(obj.objection_id)

        # 4. Resolve missing-evidence items by description match.
        if diff.resolved_missing_evidence_descriptions:
            to_drop = set(diff.resolved_missing_evidence_descriptions)
            kept = []
            for m in case.missing_evidence:
                if m.description in to_drop:
                    triggered.append(m.description)
                else:
                    kept.append(m)
            case.missing_evidence = kept

        # 5. New allegations / objections (rare but allowed).
        if diff.new_allegations:
            for a in diff.new_allegations:
                case.allegations.append(a)
                triggered.append(a.allegation_id)
        if diff.new_objections:
            for o in diff.new_objections:
                if o.resolution is None:
                    o.resolution = "Raised during chat — pending Judge adjudication on next turn."
                case.objections.append(o)
                triggered.append(o.objection_id)

        # 6. Updated verdict.
        if diff.updated_verdict is not None:
            case.verdict = diff.updated_verdict
            triggered.append("verdict")

        return triggered

    @staticmethod
    def _next_evidence_number(case: CaseFile) -> int:
        """Return the next E-code suffix to use (max existing + 1, or 1 if none)."""
        max_n = 0
        for f in case.facts:
            m = re.match(r"E-(\d+)$", f.code)
            if m:
                max_n = max(max_n, int(m.group(1)))
        return max_n + 1

    @staticmethod
    def _summarise(diff: ChatOutput, triggered: list[str]) -> str:
        parts: list[str] = []
        if diff.new_facts:
            parts.append(f"{len(diff.new_facts)} new fact(s)")
        if diff.resolved_objection_ids:
            parts.append(f"{len(diff.resolved_objection_ids)} objection(s) withdrawn")
        if diff.resolved_missing_evidence_descriptions:
            parts.append(f"{len(diff.resolved_missing_evidence_descriptions)} missing-evidence item(s) resolved")
        if diff.updated_verdict is not None:
            parts.append(f"verdict → {diff.updated_verdict.confidence_score}/10")
        return "; ".join(parts) if parts else "no structural changes"


__all__ = ["ChatAgent"]
