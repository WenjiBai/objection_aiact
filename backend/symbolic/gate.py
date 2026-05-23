"""Symbolic risk gate — evaluate YAML rules against the extracted Facts Table.

Spec: Backend_Architecture_v1.md §2.4 / Frontend_Backend_Sync_v1.md §4.

Match semantics
---------------
- scalar value in `when` → equality against the matching fact's
  `structured_value` (case-insensitive), with a case-insensitive substring
  fallback against the fact's free `text`.
- list value in `when`   → "any-of" match.
- bool value             → `gpai_present: true` matches Evidence with
  `structured_value == "true"`; analogously for `false`.
- missing fact category  → that condition is unmet and the rule does NOT fire.

The gate emits one `RuleFiring` per rule (fired or not) so the UI's
Symbolic Rules Panel can show the full deterministic trace, including
rules that did not fire and why.
"""
from __future__ import annotations

from typing import Any

from shared.schema import CaseFile, Evidence, EvidenceCategory, RuleFiring

from .loader import RuleSpec

# Bridge rules.yaml `when` keys → EvidenceCategory. The rule corpus uses
# shorthand that pre-dates the schema's enum names; this is the seam.
# Unknown keys (system_type, purpose_signal, preliminary_tier, deployer_type,
# output_subject, high_risk_candidate, user_interaction, …) are treated as
# "no matching fact found" and prevent the rule from firing.
KEY_TO_CATEGORY: dict[str, EvidenceCategory] = {
    "sector": EvidenceCategory.SECTOR,
    "output_type": EvidenceCategory.OUTPUT,
    "affected": EvidenceCategory.AFFECTED_PERSONS,
    "human_oversight": EvidenceCategory.HUMAN_OVERSIGHT,
    "gpai_present": EvidenceCategory.GPAI_USAGE,
    "automation_level": EvidenceCategory.AUTOMATION_LEVEL,
    "ai_generated_content": EvidenceCategory.AI_GENERATED_CONTENT,
    "deployment_context": EvidenceCategory.DEPLOYMENT_CONTEXT,
    "decision_impact": EvidenceCategory.DECISION_IMPACT,
    "purpose": EvidenceCategory.PURPOSE,
    "users": EvidenceCategory.USERS,
    "input_data": EvidenceCategory.INPUT_DATA,
}


def evaluate_rules(case: CaseFile, rules: list[RuleSpec]) -> list[RuleFiring]:
    """Return one `RuleFiring` per rule, fired or not, in input order."""
    by_category: dict[str, list[Evidence]] = {}
    for fact in case.facts:
        key = fact.category.value if hasattr(fact.category, "value") else str(fact.category)
        by_category.setdefault(key, []).append(fact)
    return [_evaluate_one(rule, by_category) for rule in rules]


def _evaluate_one(
    rule: RuleSpec, by_category: dict[str, list[Evidence]]
) -> RuleFiring:
    fired = True
    evaluated: dict[str, Any] = {}
    supporting: list[str] = []

    for key, expected in rule.when.items():
        category = KEY_TO_CATEGORY.get(key)
        candidates = by_category.get(category.value, []) if category else []

        if not candidates:
            evaluated[key] = "(no fact)" if category else "(unmapped key)"
            fired = False
            continue

        matched = [f for f in candidates if _matches(f, expected)]
        if matched:
            sample = matched[0]
            evaluated[key] = sample.structured_value or sample.text[:80]
            supporting.extend(f.code for f in matched)
        else:
            sample = candidates[0]
            evaluated[key] = sample.structured_value or sample.text[:80]
            fired = False

    return RuleFiring(
        rule_id=rule.id,
        description=rule.description,
        fired=fired,
        when_conditions=rule.when,
        evaluated_against=evaluated,
        then_actions=rule.then if fired else {},
        supporting_evidence_codes=_dedupe_preserve(supporting) if fired else [],
        maps_to_refs=rule.maps_to_refs if fired else [],
        yaml_source=rule.yaml_source,
    )


def _matches(fact: Evidence, expected: Any) -> bool:
    """True iff `fact` satisfies the rule condition `expected`."""
    sv = fact.structured_value

    if isinstance(expected, bool):
        if sv is None:
            return False
        return sv.strip().lower() == str(expected).lower()

    expected_list = expected if isinstance(expected, list) else [expected]
    expected_norm = {str(e).strip().lower() for e in expected_list}

    if sv is not None and sv.strip().lower() in expected_norm:
        return True

    # Free-text fallback per spec §2.4. Rule corpus uses snake_case tokens
    # (e.g. `job_applicants`) while extracted text uses natural language
    # (`job applicants`), so we accept both spellings.
    text_lower = fact.text.lower()
    for e in expected_list:
        if not isinstance(e, str):
            continue
        e_l = e.lower()
        if e_l in text_lower or e_l.replace("_", " ") in text_lower:
            return True
    return False


def _dedupe_preserve(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


__all__ = ["evaluate_rules", "KEY_TO_CATEGORY"]
