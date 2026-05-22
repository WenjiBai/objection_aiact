"""Streamlit render helpers — pure functions reading from CaseFile.

UI is read-only against CaseFile except for chat_history (Sync v1 §2.2).
"""

from __future__ import annotations

import streamlit as st

from shared.schema import (
    CaseFile, ConfidenceLabel, EvidenceCategory, RiskTier, Severity,
)


# ----------------------------------------------------------- visual maps

_TIER_COLOR = {
    RiskTier.PROHIBITED: "#7f1d1d",
    RiskTier.HIGH_RISK: "#b91c1c",
    RiskTier.POTENTIAL_HIGH_RISK: "#d97706",
    RiskTier.LIMITED_RISK: "#ca8a04",
    RiskTier.MINIMAL_RISK: "#15803d",
    RiskTier.UNKNOWN: "#475569",
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


# ------------------------------------------------------------ sections

def header():
    st.markdown(
        """
        <div style="padding:14px 18px;border-radius:10px;
                    background:linear-gradient(90deg,#0f172a,#1e293b);
                    color:#fef3c7;border-left:6px solid #f59e0b;">
          <div style="font-size:28px;font-weight:900;letter-spacing:1px;">
            ⚖️  OBJECTION! AI ACT
          </div>
          <div style="font-size:13px;color:#fcd34d;margin-top:4px;">
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
    color = _TIER_COLOR[tier]
    label = _TIER_LABEL[tier]
    score = v.confidence_score if v else 0
    conf_label = v.confidence_label.value if v else "—"
    first_doc = case.documents[0].filename if case.documents else case.case_id
    cols = st.columns([3, 2, 2])
    with cols[0]:
        st.markdown(f"### 🗂️ {first_doc}")
        st.caption(f"Case ID: `{case.case_id}` · Status: `{case.status.value}`")
    with cols[1]:
        st.markdown(
            f"""
            <div style="background:{color};color:white;padding:10px 14px;
                        border-radius:8px;text-align:center;font-weight:800;">
              {label}
            </div>
            """,
            unsafe_allow_html=True,
        )
    with cols[2]:
        st.metric("Confidence", f"{score} / 10", help=f"Label: {conf_label}")
        st.progress(score / 10)


def verdict_card(case: CaseFile):
    if not case.verdict:
        st.info("No verdict yet — upload documents and run the courtroom.")
        return
    v = case.verdict
    color = _TIER_COLOR[v.tier]
    st.markdown(
        f"""
        <div style="border-left:6px solid {color};padding:14px 18px;
                    background:#f8fafc;border-radius:6px;margin-bottom:8px;">
          <div style="font-size:18px;font-weight:700;color:{color};">
            Preliminary Verdict — {_TIER_LABEL[v.tier]}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.expander("Reasoning trail", expanded=True):
        st.markdown(v.reasoning_trail)
    for cav in v.caveats:
        st.caption(f"⚖️ {cav}")


def evidence_board(case: CaseFile):
    st.markdown("#### 📋 Evidence Board")
    tab_e, tab_r, tab_a = st.tabs([
        f"Facts (E · {len(case.facts)})",
        f"References (R · {len(case.refs)})",
        f"Assumptions (A · {len(case.assumptions)})",
    ])
    with tab_e:
        if not case.facts:
            st.caption("No facts extracted yet.")
        for e in case.facts:
            sv = f" → `{e.structured_value}`" if e.structured_value else ""
            badge = _SEVERITY_BADGE.get(e.relevance, "")
            st.markdown(
                f"**`{e.code}`** · *{_humanize(e.category.value)}*{sv} · {badge}  \n{e.text}"
            )
            meta = f"source: `{e.source_doc_id}`"
            if e.source_locator:
                meta += f" · {e.source_locator}"
            st.caption(meta)
            st.divider()
    with tab_r:
        if not case.refs:
            st.caption("No references retrieved yet.")
        for r in case.refs:
            score = f" · score={r.relevance_score:.2f}" if r.relevance_score is not None else ""
            st.markdown(f"**`{r.code}`** — {r.title}  *(Art {r.article_no}{score})*")
            if r.snippet:
                st.caption(f"“{r.snippet}”")
            with st.expander("Full text"):
                st.write(r.full_text)
                st.caption(f"{r.source_type.value} · {r.source_label}")
                if r.url:
                    st.caption(r.url)
            st.divider()
    with tab_a:
        if not case.assumptions:
            st.caption("No assumptions recorded.")
        for a in case.assumptions:
            tag = " 🟡 needs confirmation" if a.needs_confirmation else " ✅ confirmed"
            st.markdown(f"**`{a.code}`**{tag}  \n{a.text}")
            st.caption(f"reasoning: {a.reasoning}")
            st.divider()


def symbolic_rules_panel(case: CaseFile):
    st.markdown("#### 🧮 Symbolic Risk Gate — Rule Trace")
    if not case.rule_firings:
        st.caption("No rules evaluated yet.")
        return
    for rf in case.rule_firings:
        icon = "✅" if rf.fired else "⚪"
        with st.expander(
            f"{icon}  **{rf.rule_id}** — {rf.description}",
            expanded=rf.fired,
        ):
            st.write(f"**Fired:** `{rf.fired}`")
            c1, c2 = st.columns(2)
            with c1:
                st.caption("when (rule conditions)")
                st.json(rf.when_conditions)
            with c2:
                st.caption("evaluated against (case facts)")
                st.json(rf.evaluated_against)
            if rf.then_actions:
                st.caption("then (actions)")
                st.json(rf.then_actions)
            if rf.supporting_evidence_codes:
                st.write("**Supporting evidence:** " +
                         ", ".join(f"`{c}`" for c in rf.supporting_evidence_codes))
            if rf.maps_to_refs:
                st.write("**Maps to references:** " +
                         ", ".join(f"`{c}`" for c in rf.maps_to_refs))
            if rf.yaml_source:
                st.caption("YAML source (verbatim from rules.yaml):")
                st.code(rf.yaml_source, language="yaml")


def objections_section(case: CaseFile):
    if not case.objections:
        return
    open_obs = [o for o in case.objections if o.resolution is None]
    closed_obs = [o for o in case.objections if o.resolution is not None]
    st.markdown("#### 🚨 Objections")
    for ob in open_obs:
        st.error(
            f"**OBJECTION!**  `{ob.objection_id}` → {ob.target_type} `{ob.target_id}`  "
            f"· {_SEVERITY_BADGE.get(ob.severity, '')}\n\n{ob.reason}"
        )
        if ob.challenging_evidence_codes:
            st.caption("challenging evidence: " +
                       ", ".join(f"`{c}`" for c in ob.challenging_evidence_codes))
    for ob in closed_obs:
        st.success(
            f"~~OBJECTION `{ob.objection_id}` (resolved)~~ — {ob.reason}\n\n"
            f"**Resolution:** {ob.resolution}"
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
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### ❓ Missing Evidence")
        if not case.missing_evidence:
            st.caption("Nothing outstanding.")
        for m in case.missing_evidence:
            badge = _SEVERITY_BADGE.get(m.severity, "")
            blocks = " 🚧 blocks verdict" if m.blocks_verdict else ""
            st.markdown(f"☐ {badge}{blocks}  \n{m.description}")
            for q in m.suggested_questions:
                st.caption(f"💬 *{q}*")
    with c2:
        st.markdown("#### ✅ Governance Checklist")
        if not case.governance_checklist:
            st.caption("Nothing required at this tier.")
        for g in case.governance_checklist:
            mark = "☐" if g.applies else "—"
            ref = f" *(see {g.ai_act_reference})*" if g.ai_act_reference else ""
            st.markdown(f"{mark} **{g.item}**{ref}")
            if g.note:
                st.caption(g.note)


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
