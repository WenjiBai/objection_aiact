"""Streamlit render helpers — pure functions reading from CaseFile.

UI is read-only against CaseFile except for chat_history (Sync v1 §2.2).
"""

from __future__ import annotations

from html import escape

import streamlit as st

from shared.schema import (
    AgentName, AgentStatus, CaseFile, ConfidenceLabel,
    EvidenceCategory, RiskTier, Severity,
)


# ------------------------------------------------------------ SVG icons
# Inline Lucide-style icons. Always render correctly across OS/fonts,
# inherit color via currentColor.

def _svg(path: str, size: int = 14, stroke: float = 2) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        f'stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round" '
        f'aria-hidden="true">{path}</svg>'
    )


ICON_WORKFLOW = _svg(
    '<rect x="3" y="3" width="6" height="6" rx="1"/>'
    '<rect x="15" y="3" width="6" height="6" rx="1"/>'
    '<rect x="9" y="15" width="6" height="6" rx="1"/>'
    '<path d="M6 9v3a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V9"/>'
    '<path d="M12 14v1"/>'
)
ICON_CLIPBOARD = _svg(
    '<rect x="8" y="2" width="8" height="4" rx="1"/>'
    '<path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/>'
    '<path d="M9 12h6"/><path d="M9 16h6"/>'
)
ICON_CPU = _svg(
    '<rect x="4" y="4" width="16" height="16" rx="2"/>'
    '<rect x="9" y="9" width="6" height="6"/>'
    '<path d="M9 2v2"/><path d="M15 2v2"/>'
    '<path d="M9 20v2"/><path d="M15 20v2"/>'
    '<path d="M2 9h2"/><path d="M2 15h2"/>'
    '<path d="M20 9h2"/><path d="M20 15h2"/>'
)
ICON_ALERT = _svg(
    '<path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0Z"/>'
    '<line x1="12" y1="9" x2="12" y2="13"/>'
    '<line x1="12" y1="17" x2="12.01" y2="17"/>'
)
ICON_CHECK_SQUARE = _svg(
    '<path d="M9 11l3 3L22 4"/>'
    '<path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>'
)
ICON_SEARCH = _svg(
    '<circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>'
)
ICON_DOWNLOAD = _svg(
    '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>'
    '<polyline points="7 10 12 15 17 10"/>'
    '<line x1="12" y1="15" x2="12" y2="3"/>'
)
ICON_PLUS = _svg(
    '<line x1="12" y1="5" x2="12" y2="19"/>'
    '<line x1="5" y1="12" x2="19" y2="12"/>',
    stroke=2.4,
)
ICON_SCALE = _svg(
    '<path d="m16 16 3-8 3 8c-2 1-4 1-6 0z"/>'
    '<path d="m2 16 3-8 3 8c-2 1-4 1-6 0z"/>'
    '<path d="M7 21h10"/><path d="M12 3v18"/><path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/>'
)
ICON_GAVEL = _svg(
    '<path d="m14.5 12.5-8 8a2.119 2.119 0 1 1-3-3l8-8"/>'
    '<path d="m16 16 6-6"/><path d="m8 8 6-6"/>'
    '<path d="m9 7 8 8"/><path d="m21 11-8-8"/>'
)


# ----------------------------------------------------------- visual maps

# Risk tier visuals — core hue plus a "soft" glow halo.
_TIER_COLOR = {
    RiskTier.PROHIBITED: "#EF4444",
    RiskTier.HIGH_RISK: "#EF4444",
    RiskTier.POTENTIAL_HIGH_RISK: "#F59E0B",
    RiskTier.LIMITED_RISK: "#F59E0B",
    RiskTier.MINIMAL_RISK: "#10B981",
    RiskTier.UNKNOWN: "#6B7280",
}
_TIER_SOFT = {
    RiskTier.PROHIBITED: "rgba(239,68,68,0.18)",
    RiskTier.HIGH_RISK: "rgba(239,68,68,0.18)",
    RiskTier.POTENTIAL_HIGH_RISK: "rgba(245,158,11,0.20)",
    RiskTier.LIMITED_RISK: "rgba(245,158,11,0.18)",
    RiskTier.MINIMAL_RISK: "rgba(16,185,129,0.18)",
    RiskTier.UNKNOWN: "rgba(107,114,128,0.18)",
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

_AGENT_ORDER = [
    AgentName.DETECTIVE,
    AgentName.LEGAL_CLERK,
    AgentName.PROSECUTOR,
    AgentName.DEFENSE,
    AgentName.CRITIQUE,
    AgentName.JUDGE,
]

_AGENT_INITIAL = {
    AgentName.DETECTIVE: "D",
    AgentName.LEGAL_CLERK: "L",
    AgentName.PROSECUTOR: "P",
    AgentName.DEFENSE: "D",
    AgentName.CRITIQUE: "C",
    AgentName.JUDGE: "J",
}

_AGENT_LABEL = {
    AgentName.DETECTIVE: "Detective",
    AgentName.LEGAL_CLERK: "Legal Clerk",
    AgentName.PROSECUTOR: "Prosecutor",
    AgentName.DEFENSE: "Defense",
    AgentName.CRITIQUE: "Critique",
    AgentName.JUDGE: "Judge",
}


def _humanize(s: str) -> str:
    return s.replace("_", " ").title()


def _h(value: object) -> str:
    return escape(str(value), quote=True)


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
    return "Confirm"


# ============================================================== sections

def header():
    """Legacy hero used by tests/older mocks. Replaced by landing_hero."""
    st.html(
        """
        <div class="act-hero-wrap">
          <div class="act-hero-badge">⚖ OBJECTION! · AI ACT</div>
          <div class="act-hero-title">Put your AI use case on trial.</div>
          <div class="act-hero-sub">
            Neuro-symbolic, multi-agent EU AI Act first-pass assessment.
            Preliminary — not legal advice.
          </div>
        </div>
        """
    )


def landing_hero():
    st.html(
        """
        <div class="act-hero-wrap">
          <div class="act-hero-badge">⚖ OBJECTION! · AI ACT</div>
          <div class="act-hero-title">Put your AI use case on trial.</div>
          <div class="act-hero-sub">
            Six AI agents, thirteen symbolic rules, and a grounded EU AI Act corpus
            deliver a first-pass risk verdict with citations, uncertainty,
            and a governance checklist.
          </div>
          <div class="act-trust-row">
            <span class="act-trust-chip"><b>6</b> agents</span>
            <span class="act-trust-chip"><b>13</b> symbolic rules</span>
            <span class="act-trust-chip"><b>29</b> AI Act references</span>
            <span class="act-trust-chip"><b>~12s</b> avg verdict</span>
          </div>
        </div>
        """
    )


def upload_topbar():
    st.html(
        """
        <div class="act-topbar">
          <div class="act-top-title">
            <span style="color:var(--aa-primary-strong)">●</span>
            <span>New case session</span>
          </div>
          <div class="act-top-actions">
            <span class="act-mini-button">📚 AI Act corpus</span>
            <span class="act-mini-button">❓ Guide</span>
          </div>
        </div>
        """
    )


def case_file_summary(case: CaseFile):
    v = case.verdict
    tier = v.tier if v else RiskTier.UNKNOWN
    first_doc = case.documents[0].filename if case.documents else case.case_id
    status = "Preliminary verdict ready" if v else "Intake"
    doc_count = len(case.documents)
    tier_label = _TIER_LABEL.get(tier, "UNKNOWN")
    tier_color = _TIER_COLOR.get(tier, "#6B7280")
    tier_soft = _TIER_SOFT.get(tier, "rgba(107,114,128,0.18)")

    st.html(
        f"""
        <div class="act-case-banner">
          <div class="act-case-title">
            <div class="act-case-icon">⚖</div>
            <div style="display:flex;flex-direction:column;gap:2px;min-width:0;">
              <span class="filename">{_h(first_doc)}</span>
              <span style="font-size:11px;color:var(--aa-subtle);font-weight:500;">
                {_h(case.case_id)} · {doc_count} doc{"s" if doc_count != 1 else ""}
              </span>
            </div>
            <span class="act-status-pill">● {_h(status)}</span>
          </div>
          <div class="act-case-actions">
            <span class="act-tier-pill"
                  style="--tier-color:{tier_color};--tier-soft:{tier_soft};
                         color:{tier_color};border-color:{tier_color};
                         background:{tier_soft};">
              <span class="dot" style="background:{tier_color};box-shadow:0 0 12px {tier_color};"></span>
              {_h(tier_label)}
            </span>
            <span class="act-mini-button">{ICON_DOWNLOAD} Export PDF</span>
          </div>
        </div>
        """
    )


def agent_stepper(case: CaseFile):
    """Always-visible horizontal stepper for the 6 agents."""

    by_agent = {a.agent: a for a in case.agent_activity}

    cards = []
    for agent in _AGENT_ORDER:
        act = by_agent.get(agent)
        status = act.status if act else AgentStatus.PENDING
        status_cls = status.value  # "pending"|"running"|"completed"|"failed"|"skipped"
        initial = _AGENT_INITIAL[agent]
        name = _AGENT_LABEL[agent]
        action = (act.action if act and act.action else "Awaiting trigger")
        duration = ""
        if act and act.started_at and act.completed_at:
            ms = (act.completed_at - act.started_at).total_seconds() * 1000
            duration = f"{ms:.0f} ms"
        elif act and act.started_at and status == AgentStatus.RUNNING:
            duration = "running…"

        cards.append(
            f'''
            <div class="act-step {status_cls}">
              <div class="step-row">
                <div class="step-dot">{_h(initial)}</div>
                <div class="step-name">{_h(name)}</div>
              </div>
              <div class="step-action">{_h(action)}</div>
              <div class="step-duration">{_h(duration)}</div>
            </div>
            '''
        )

    st.html(
        f'<div class="act-section-title"><span class="icon">{ICON_WORKFLOW}</span>Courtroom workflow</div>'
    )
    st.html(f'<div class="act-stepper">{"".join(cards)}</div>')


def _confidence_ring(score: int, color: str, soft: str) -> str:
    score = max(0, min(10, score))
    pct = score / 10.0
    radius = 36
    circumference = 2 * 3.1415926 * radius
    dash = circumference * pct
    return f'''
    <div class="act-ring-block">
      <svg class="act-ring" viewBox="0 0 86 86">
        <circle class="track" cx="43" cy="43" r="{radius}"></circle>
        <circle class="fill"  cx="43" cy="43" r="{radius}"
                style="stroke:{color};filter:drop-shadow(0 0 6px {soft});"
                stroke-dasharray="{dash:.2f} {circumference:.2f}"></circle>
      </svg>
      <div class="act-ring-center">
        <span class="score">{score}</span>
        <span class="out-of">/ 10</span>
      </div>
    </div>
    '''


def verdict_card(case: CaseFile):
    if not case.verdict:
        st.info("No verdict yet — upload documents and run the courtroom.")
        return
    v = case.verdict
    color = _TIER_COLOR[v.tier]
    soft = _TIER_SOFT[v.tier]
    tier_label = _TIER_LABEL[v.tier]

    missing = case.missing_evidence[:3]
    if missing:
        rows = "".join(
            f'<div class="act-missing-item"><span class="checkbox"></span>'
            f'<span>{_h(m.description)}</span></div>'
            for m in missing
        )
    else:
        rows = (
            '<div class="act-missing-item ok"><span class="checkbox"></span>'
            '<span>No missing evidence recorded</span></div>'
        )

    ring = _confidence_ring(v.confidence_score, color, soft)

    st.html(
        f"""
        <div class="act-verdict-card" style="--tier-color:{color};--tier-soft:{soft};">
          <div class="act-verdict-top">
            <div class="act-verdict-tier">
              <div class="act-label">Preliminary verdict</div>
              <span class="act-tier-pill">
                <span class="dot"></span>
                {_h(tier_label)}
              </span>
            </div>
            <div class="act-ring-wrap">
              {ring}
              <div class="act-ring-info">
                <span class="lbl">Confidence</span>
                <span class="val">{_h(v.confidence_label.value)}</span>
                <span class="lbl" style="margin-top:2px;">{_h(v.confidence_score)} / 10</span>
              </div>
            </div>
          </div>
          <div class="act-reason">{_h(v.reasoning_trail)}</div>
          <div class="act-missing">
            <div class="act-missing-title">
              Missing evidence
              <span class="badge">{len(case.missing_evidence)}</span>
            </div>
            {rows}
          </div>
          <div class="act-guard">
            ⚠ Preliminary assessment only — not legal advice.
            Human legal review is recommended before deployment.
          </div>
        </div>
        """
    )


def _evidence_cards(case: CaseFile, tab: str) -> str:
    cards = []
    if tab == "facts":
        for e in case.facts:
            cards.append(
                f'''
                <div class="act-ev-card">
                  <div class="act-ev-head">
                    <span class="act-code e">{_h(e.code)}</span>
                    <span class="act-strength {_strength_class(e.relevance)}">
                      {_h(_strength_label(e.relevance))}
                    </span>
                  </div>
                  <div class="act-ev-body">{_h(e.text)}</div>
                  <div class="act-ev-meta">
                    <span>📄 {_h(e.source_doc_id)}</span>
                    <span class="sep">·</span>
                    <span>{_h(_humanize(e.category.value))}</span>
                  </div>
                </div>
                '''
            )
    elif tab == "refs":
        for r in case.refs:
            text = r.snippet or r.title
            cards.append(
                f'''
                <div class="act-ev-card">
                  <div class="act-ev-head">
                    <span class="act-code r">{_h(r.code)}</span>
                    <span class="act-strength act-strong">Legal</span>
                  </div>
                  <div class="act-ev-body">{_h(text)}</div>
                  <div class="act-ev-meta">
                    <span>⚖ {_h(r.source_label)}</span>
                    <span class="sep">·</span>
                    <span>{_h(r.article_no)}</span>
                  </div>
                </div>
                '''
            )
    else:  # assumptions
        for a in case.assumptions:
            strength_cls = "act-weak" if a.needs_confirmation else "act-medium"
            label = "Confirm" if a.needs_confirmation else "Medium"
            cards.append(
                f'''
                <div class="act-ev-card">
                  <div class="act-ev-head">
                    <span class="act-code a">{_h(a.code)}</span>
                    <span class="act-strength {strength_cls}">{label}</span>
                  </div>
                  <div class="act-ev-body">{_h(a.text)}</div>
                  <div class="act-ev-meta">
                    <span>🧠 {_h(a.reasoning[:80])}{"…" if len(a.reasoning) > 80 else ""}</span>
                  </div>
                </div>
                '''
            )

    if not cards:
        return '<div class="act-empty">No items in this view.</div>'
    return f'<div class="act-evidence-grid">{"".join(cards)}</div>'


def evidence_board(case: CaseFile):
    n_e, n_r, n_a = len(case.facts), len(case.refs), len(case.assumptions)
    st.html(
        f"""
        <div class="act-section-title">
          <span class="icon">{ICON_CLIPBOARD}</span>Evidence board
          <span class="count">· {n_e + n_r + n_a} items</span>
        </div>
        """
    )

    tabs = st.tabs([f"Facts · {n_e}", f"References · {n_r}", f"Assumptions · {n_a}"])
    with tabs[0]:
        st.html(_evidence_cards(case, "facts"))
    with tabs[1]:
        st.html(_evidence_cards(case, "refs"))
    with tabs[2]:
        st.html(_evidence_cards(case, "assumptions"))


def symbolic_rules_panel(case: CaseFile):
    fired = sum(1 for rf in case.rule_firings if rf.fired)
    inactive = len(case.rule_firings) - fired

    rows = []
    for rf in case.rule_firings:
        icon_cls = "fired" if rf.fired else "inactive"
        icon = "✓" if rf.fired else "·"
        if rf.then_actions:
            action = ", ".join(f"{k}={v}" for k, v in rf.then_actions.items())
        else:
            action = (
                ", ".join(f"{k}={v}" for k, v in rf.evaluated_against.items())
                or rf.description
            )
        badge_cls = "act-strong" if rf.fired else "act-weak"
        badge_text = "Fired" if rf.fired else "Inactive"
        rows.append(
            f'''
            <div class="act-rule-row {icon_cls}">
              <div class="act-rule-icon {icon_cls}">{icon}</div>
              <span class="act-rule-id">{_h(rf.rule_id)}</span>
              <span class="act-rule-desc">{_h(action)}</span>
              <span class="act-strength {badge_cls}">{badge_text}</span>
            </div>
            '''
        )
    body = (
        "".join(rows)
        if rows
        else '<div class="act-empty">No rules evaluated yet.</div>'
    )

    st.html(
        f"""
        <div class="act-section-title">
          <span class="icon">{ICON_CPU}</span>Symbolic risk gate
          <span class="count">· deterministic & inspectable</span>
        </div>
        <div class="act-rules-panel">
          <div class="act-rules-head">
            <span>Rule trace</span>
            <span class="summary">
              <span><b>{fired}</b> fired</span>
              <span>·</span>
              <span><b>{inactive}</b> inactive</span>
            </span>
          </div>
          <div class="act-rule-body">{body}</div>
        </div>
        """
    )


def objections_section(case: CaseFile):
    if not case.objections:
        return
    open_obs = [o for o in case.objections if o.resolution is None]
    closed_obs = [o for o in case.objections if o.resolution is not None]

    st.html(
        f"""
        <div class="act-section-title">
          <span class="icon">{ICON_ALERT}</span>Critique objections
          <span class="count">· {len(open_obs)} open · {len(closed_obs)} resolved</span>
        </div>
        """
    )

    for ob in open_obs:
        evidence = ", ".join(ob.challenging_evidence_codes) or "weak evidence"
        st.html(
            f"""
            <div class="act-obj-card">
              <div class="act-obj-header">
                <span class="act-obj-gavel">⚖</span>
                Objection — {_h(ob.target_type)} {_h(ob.target_id)}
              </div>
              <div class="act-obj-body">{_h(ob.reason)}</div>
              <div class="act-obj-action">→ Reclassification review triggered by {_h(evidence)}</div>
            </div>
            """
        )

    for ob in closed_obs:
        st.html(
            f"""
            <div class="act-obj-card resolved">
              <div class="act-obj-header">
                <span class="act-obj-gavel">✓</span>
                Resolved — {_h(ob.objection_id)}
              </div>
              <div class="act-obj-body">{_h(ob.resolution or ob.reason)}</div>
            </div>
            """
        )


def allegations_and_defenses(case: CaseFile):
    """Legacy two-column allegation/defense view."""
    if not (case.allegations or case.defenses):
        return
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 🔴 Prosecutor — Allegations")
        if not case.allegations:
            st.caption("No allegations.")
        for al in case.allegations:
            st.html(
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
    rows = []
    for g in case.governance_checklist:
        cls = "required" if g.applies else ""
        ref = f'<span class="act-gov-ref">{_h(g.ai_act_reference)}</span>' if g.ai_act_reference else ""
        rows.append(
            f'''
            <div class="act-gov-item {cls}">
              <span class="gov-check"></span>
              <span class="act-gov-text">
                <span>{_h(g.item)}</span>
                {ref}
              </span>
            </div>
            '''
        )
    body = (
        "".join(rows)
        if rows
        else '<div class="act-empty">Nothing required at this tier.</div>'
    )

    applies = sum(1 for g in case.governance_checklist if g.applies)
    st.html(
        f"""
        <div class="act-section-title">
          <span class="icon">{ICON_CHECK_SQUARE}</span>Governance checklist
          <span class="count">· {applies} required item{"s" if applies != 1 else ""}</span>
        </div>
        <div class="act-gov-grid">{body}</div>
        """
    )


def agent_activity_timeline(case: CaseFile):
    """Detail view — collapsed; the always-visible stepper is the main signal."""
    if not case.agent_activity:
        return
    with st.expander("🕒 Agent activity (detailed log)", expanded=False):
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
        st.caption("No cross-examination turns yet. Drop a fact below or pick a follow-up.")
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
