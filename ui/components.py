"""Streamlit render helpers — pure functions reading from CaseFile.

UI is read-only against CaseFile except for chat_history (Sync v1 §2.2).
"""

from __future__ import annotations

from html import escape

import streamlit as st

from shared.schema import (
    CaseFile, ConfidenceLabel, EvidenceCategory, RiskTier, Severity,
)


# ----------------------------------------------------------- visual maps

_TIER_COLOR = {
    RiskTier.PROHIBITED: "#A32D2D",
    RiskTier.HIGH_RISK: "#A32D2D",
    RiskTier.POTENTIAL_HIGH_RISK: "#BA7517",
    RiskTier.LIMITED_RISK: "#BA7517",
    RiskTier.MINIMAL_RISK: "#0F6E56",
    RiskTier.UNKNOWN: "#605D66",
}

_TIER_DARK = {
    RiskTier.PROHIBITED: "#791F1F",
    RiskTier.HIGH_RISK: "#791F1F",
    RiskTier.POTENTIAL_HIGH_RISK: "#854F0B",
    RiskTier.LIMITED_RISK: "#854F0B",
    RiskTier.MINIMAL_RISK: "#085041",
    RiskTier.UNKNOWN: "#4B4851",
}

_TIER_LABEL = {
    RiskTier.PROHIBITED: "PROHIBITED",
    RiskTier.HIGH_RISK: "HIGH RISK",
    RiskTier.POTENTIAL_HIGH_RISK: "POTENTIAL HIGH RISK",
    RiskTier.LIMITED_RISK: "LIMITED RISK",
    RiskTier.MINIMAL_RISK: "MINIMAL RISK",
    RiskTier.UNKNOWN: "UNKNOWN",
}

_SEVERITY_BADGE = {
    Severity.HIGH: ":red[● HIGH]",
    Severity.MEDIUM: ":orange[● MEDIUM]",
    Severity.LOW: ":green[● LOW]",
}


def _humanize(s: str) -> str:
    return s.replace("_", " ").title()


def _h(value: object) -> str:
    return escape(str(value), quote=True)


def _confidence_bar(score: int) -> str:
    score = max(0, min(10, score))
    segments = "".join(
        f'<span class="act-conf-seg{" on" if i < score else ""}"></span>'
        for i in range(10)
    )
    return segments


def _strength_class(severity: Severity | None) -> str:
    if severity == Severity.HIGH:
        return "act-strong"
    if severity == Severity.MEDIUM:
        return "act-medium"
    return "act-weak"


def _strength_label(severity: Severity | None) -> str:
    if severity == Severity.HIGH:
        return "Strong"
    if severity == Severity.MEDIUM:
        return "Medium"
    return "Needs confirmation"


# ------------------------------------------------------------ sections

def header():
    st.markdown(
        """
        <div class="aa-hero">
          <div class="aa-hero-title">
            ⚖️  OBJECTION! AI ACT
          </div>
          <div class="aa-hero-subtitle">
            A neuro-symbolic multi-agent courtroom for EU AI Act first-pass assessment.
            <i>Preliminary — not legal advice.</i>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def case_file_summary(case: CaseFile):
    v = case.verdict
    tier = v.tier if v else RiskTier.UNKNOWN
    first_doc = case.documents[0].filename if case.documents else case.case_id
    status = "Preliminary hearing" if v else "Intake"
    doc_count = len(case.documents)
    st.markdown(
        f"""
        <div class="act-case-banner">
          <div class="act-case-title">
            <span>▣</span>
            <span>{_h(first_doc)}</span>
            <span class="act-status-pill">{_h(status)}</span>
          </div>
          <div class="act-case-actions">
            <span class="act-mini-button">{doc_count} docs</span>
            <span class="act-mini-button">Export PDF</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def upload_topbar():
    st.markdown(
        """
        <div class="act-topbar">
          <div class="act-top-title">
            <span style="color:var(--aa-primary)">□</span>
            <span>New case session</span>
          </div>
          <div class="act-top-actions">
            <span class="act-mini-button">AI Act corpus</span>
            <span class="act-mini-button">Guide</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def upload_hero():
    st.markdown(
        """
        <div class="act-upload-wrap">
          <div class="act-upload-zone">
            <div class="act-upload-icon">⇧</div>
            <div class="act-upload-title">Upload case documents</div>
            <div class="act-upload-sub">
              Drop vendor white papers, technical specs, policy docs, model cards,
              or internal process notes describing your AI use case.
            </div>
            <div class="act-upload-formats">PDF, DOCX, TXT, MD (up to 10 files)</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def verdict_card(case: CaseFile):
    if not case.verdict:
        st.info("No verdict yet — upload documents and run the courtroom.")
        return
    v = case.verdict
    color = _TIER_COLOR[v.tier]
    dark = _TIER_DARK[v.tier]
    missing = case.missing_evidence[:3]
    missing_rows = ""
    for m in missing:
        missing_rows += (
            '<div class="act-missing-item">'
            f'<span>☐</span><span>{_h(m.description)}</span></div>'
        )
    if not missing_rows:
        missing_rows = '<div class="act-missing-item"><span>☑</span><span>No missing evidence recorded</span></div>'
    st.markdown(
        f"""
        <div class="act-verdict-card" style="--tier-color:{color};--tier-dark:{dark};">
          <div class="act-verdict-top">
            <div>
              <div class="act-label">Preliminary verdict</div>
              <div class="act-tier">{_h(_humanize(v.tier.value))}</div>
            </div>
            <div class="act-confidence">
              <div class="act-label">Confidence</div>
              <div class="act-conf-bar">
                {_confidence_bar(v.confidence_score)}
                <span class="act-conf-text">{_h(v.confidence_label.value.title())} ({v.confidence_score}/10)</span>
              </div>
            </div>
          </div>
          <div class="act-reason">{_h(v.reasoning_trail)}</div>
          <div class="act-missing">
            <div class="act-missing-title">Missing evidence ({len(case.missing_evidence)})</div>
            {missing_rows}
          </div>
          <div class="act-guard">
            Preliminary assessment only. Not legal advice. Human legal review is recommended before deployment.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def evidence_board(case: CaseFile):
    rows: list[str] = []
    for e in case.facts[:7]:
        rows.append(
            "<tr>"
            f'<td><span class="act-code e">{_h(e.code)}</span></td>'
            f"<td>{_h(e.source_doc_id)}</td>"
            f"<td>{_h(e.text)}</td>"
            f"<td>{_h(_humanize(e.category.value))}</td>"
            f'<td><span class="act-strength {_strength_class(e.relevance)}">{_h(_strength_label(e.relevance))}</span></td>'
            "</tr>"
        )
    for r in case.refs[:4]:
        ref_text = r.snippet or r.title
        rows.append(
            "<tr>"
            f'<td><span class="act-code r">{_h(r.code)}</span></td>'
            f"<td>{_h(r.source_label)}</td>"
            f"<td>{_h(ref_text)}</td>"
            f"<td>Legal basis</td>"
            '<td><span class="act-strength act-strong">Strong</span></td>'
            "</tr>"
        )
    for a in case.assumptions[:3]:
        strength = "act-weak" if a.needs_confirmation else "act-medium"
        label = "Needs confirmation" if a.needs_confirmation else "Medium"
        rows.append(
            "<tr>"
            f'<td><span class="act-code a">{_h(a.code)}</span></td>'
            "<td>Assumption</td>"
            f"<td>{_h(a.text)}</td>"
            "<td>Risk reasoning</td>"
            f'<td><span class="act-strength {strength}">{label}</span></td>'
            "</tr>"
        )

    body = "".join(rows) or '<tr><td colspan="5">No evidence extracted yet.</td></tr>'
    st.markdown(
        f"""
        <div class="act-section-title"><span class="icon">▦</span>Evidence board</div>
        <table class="act-table">
          <thead>
            <tr><th>Code</th><th>Source</th><th>Fact / reference</th><th>Used for</th><th>Strength</th></tr>
          </thead>
          <tbody>{body}</tbody>
        </table>
        """,
        unsafe_allow_html=True,
    )


def symbolic_rules_panel(case: CaseFile):
    fired = sum(1 for rf in case.rule_firings if rf.fired)
    inactive = len(case.rule_firings) - fired
    rows = ""
    for rf in case.rule_firings[:6]:
        icon = "✓" if rf.fired else "×"
        icon_color = "#0F6E56" if rf.fired else "#8a8790"
        badge_class = "act-strong" if rf.fired else "act-weak"
        badge_text = "Fired" if rf.fired else "Inactive"
        if rf.then_actions:
            action = ", ".join(f"{k}={v}" for k, v in rf.then_actions.items())
        else:
            action = ", ".join(f"{k}={v}" for k, v in rf.evaluated_against.items()) or rf.description
        rows += (
            '<div class="act-rule-row">'
            f'<span style="color:{icon_color}">{icon}</span>'
            f'<span class="act-rule-id">{_h(rf.rule_id)}</span>'
            f'<span class="act-rule-desc">{_h(action)}</span>'
            f'<span class="act-rule-result {badge_class}">{badge_text}</span>'
            '</div>'
        )
    if not rows:
        rows = '<div class="act-rule-row"><span class="act-rule-desc">No rules evaluated yet.</span></div>'
    st.markdown(
        f"""
        <div class="act-section-title"><span class="icon">⌬</span>Symbolic risk gate</div>
        <div class="act-rules-panel">
          <div class="act-rules-head">
            <span>Rule trace ({fired} fired, {inactive} inactive)</span>
            <span style="color:#8a8790">⌄</span>
          </div>
          <div class="act-rule-body">{rows}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def objections_section(case: CaseFile):
    if not case.objections:
        return
    open_obs = [o for o in case.objections if o.resolution is None]
    closed_obs = [o for o in case.objections if o.resolution is not None]
    st.markdown('<div class="act-section-title"><span class="icon">△</span>Objection</div>', unsafe_allow_html=True)
    for ob in open_obs:
        evidence = ", ".join(ob.challenging_evidence_codes) or "weak evidence"
        st.markdown(
            f"""
            <div class="act-obj-card">
              <div class="act-obj-header">Objection: {_h(ob.target_type)} {_h(ob.target_id)}</div>
              <div class="act-obj-body">{_h(ob.reason)}</div>
              <div class="act-obj-action">→ Reclassification review triggered by {_h(evidence)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    for ob in closed_obs:
        st.markdown(
            f"""
            <div class="act-obj-card" style="background:#E1F5EE;border-color:#0F6E56;">
              <div class="act-obj-header" style="color:#085041;">Resolved objection: {_h(ob.objection_id)}</div>
              <div class="act-obj-body" style="color:#085041;">{_h(ob.resolution or ob.reason)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def allegations_and_defenses(case: CaseFile):
    if not (case.allegations or case.defenses):
        return
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 🔴 Prosecutor — Allegations")
        if not case.allegations:
            st.caption("No allegations.")
        for al in case.allegations:
            st.markdown(
                f"**`{al.allegation_id}`** → {_TIER_LABEL[al.tier]}  · "
                f"{_SEVERITY_BADGE.get(al.strength, '')}\n\n{al.claim}"
            )
            meta = []
            if al.basis_evidence_codes:
                meta.append("E: " + ", ".join(f"`{c}`" for c in al.basis_evidence_codes))
            if al.basis_ref_codes:
                meta.append("R: " + ", ".join(f"`{c}`" for c in al.basis_ref_codes))
            if meta:
                st.caption(" · ".join(meta))
            st.divider()
    with c2:
        st.markdown("#### 🛡️ Defense — Exemptions & Mitigations")
        if not case.defenses:
            st.caption("No defenses raised.")
        for df in case.defenses:
            doc_tag = " ⚠️ requires documentation" if df.requires_documentation else ""
            targets = f" · targets `{df.targets_allegation_id}`" if df.targets_allegation_id else ""
            st.markdown(
                f"**`{df.defense_id}`** · *{_humanize(df.type)}*{doc_tag}{targets}\n\n{df.claim}"
            )
            meta = []
            if df.basis_evidence_codes:
                meta.append("E: " + ", ".join(f"`{c}`" for c in df.basis_evidence_codes))
            if df.basis_ref_codes:
                meta.append("R: " + ", ".join(f"`{c}`" for c in df.basis_ref_codes))
            if meta:
                st.caption(" · ".join(meta))
            st.divider()


def missing_and_governance(case: CaseFile):
    rows = ""
    for g in case.governance_checklist:
        mark = "☐" if g.applies else "—"
        ref = f" ({g.ai_act_reference})" if g.ai_act_reference else ""
        rows += f'<div class="act-gov-item"><span>{mark}</span><span>{_h(g.item + ref)}</span></div>'
    if not rows:
        rows = '<div class="act-gov-item"><span>—</span><span>Nothing required at this tier.</span></div>'
    st.markdown(
        f"""
        <div class="act-section-title"><span class="icon">☑</span>Governance checklist</div>
        <div class="act-gov-grid">{rows}</div>
        """,
        unsafe_allow_html=True,
    )


def agent_activity_timeline(case: CaseFile):
    if not case.agent_activity:
        return
    with st.expander("🕒 Agent Activity Timeline", expanded=False):
        for a in case.agent_activity:
            dur = ""
            if a.started_at and a.completed_at:
                ms = (a.completed_at - a.started_at).total_seconds() * 1000
                dur = f" · {ms:.0f} ms"
            icon = {
                "completed": "✅", "running": "⏳", "failed": "❌",
                "pending": "⚪", "skipped": "⏭️",
            }.get(a.status.value, "·")
            st.markdown(f"{icon} **{_humanize(a.agent.value)}** — {a.action}{dur}")
            if a.output_summary:
                st.caption(a.output_summary)


def chat_history(case: CaseFile):
    if not case.chat_history:
        st.caption("No cross-examination turns yet.")
        return
    for turn in case.chat_history:
        if turn.role == "user":
            with st.chat_message("user"):
                st.write(turn.text)
        elif turn.role == "judge":
            with st.chat_message("assistant", avatar="⚖️"):
                st.write(turn.text)
                if turn.triggered_updates:
                    st.caption("Updated: " + ", ".join(f"`{u}`" for u in turn.triggered_updates))
        else:
            with st.chat_message("assistant", avatar="ℹ️"):
                st.warning(turn.text)
