"""Helpers per CaseFile_Schema_Spec.md §"必须实现的 4 个 helper"."""

from __future__ import annotations

from typing import Optional

from .schema import CaseFile, Evidence, Reference


def get_evidence(case: CaseFile, code: str) -> Optional[Evidence]:
    for e in case.facts:
        if e.code == code:
            return e
    return None


def get_ref(case: CaseFile, code: str) -> Optional[Reference]:
    for r in case.refs:
        if r.code == code:
            return r
    return None


def snapshot(case: CaseFile) -> CaseFile:
    """Deep copy for rollback before a chat turn."""
    return case.model_copy(deep=True)


def validate_codes(case: CaseFile) -> list[str]:
    """Return a list of human-readable code-integrity errors. Empty = OK.

    Used by the frontend after handle_chat() to catch hallucinated references
    that pydantic alone wouldn't flag (Sync v1 §6.3).
    """
    errs: list[str] = []

    e_codes = [e.code for e in case.facts]
    r_codes = [r.code for r in case.refs]
    a_codes = [a.code for a in case.assumptions]

    for codes, label in [(e_codes, "Evidence"), (r_codes, "Reference"), (a_codes, "Assumption")]:
        if len(set(codes)) != len(codes):
            dups = sorted({c for c in codes if codes.count(c) > 1})
            errs.append(f"Duplicate {label} codes: {dups}")

    e_set, r_set = set(e_codes), set(r_codes)

    for al in case.allegations:
        missing_e = [c for c in al.basis_evidence_codes if c not in e_set]
        missing_r = [c for c in al.basis_ref_codes if c not in r_set]
        if missing_e:
            errs.append(f"Allegation {al.allegation_id} references unknown evidence: {missing_e}")
        if missing_r:
            errs.append(f"Allegation {al.allegation_id} references unknown refs: {missing_r}")

    for df in case.defenses:
        missing_e = [c for c in df.basis_evidence_codes if c not in e_set]
        missing_r = [c for c in df.basis_ref_codes if c not in r_set]
        if missing_e:
            errs.append(f"Defense {df.defense_id} references unknown evidence: {missing_e}")
        if missing_r:
            errs.append(f"Defense {df.defense_id} references unknown refs: {missing_r}")

    for ob in case.objections:
        missing_e = [c for c in ob.challenging_evidence_codes if c not in e_set]
        if missing_e:
            errs.append(f"Objection {ob.objection_id} references unknown evidence: {missing_e}")

    for rf in case.rule_firings:
        missing_e = [c for c in rf.supporting_evidence_codes if c not in e_set]
        if missing_e:
            errs.append(f"RuleFiring {rf.rule_id} references unknown evidence: {missing_e}")

    return errs
