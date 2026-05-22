"""OBJECTION! AI ACT — Streamlit entry.

Run:  streamlit run app.py
"""

from __future__ import annotations

import uuid

import streamlit as st

from backend.api import BackendValidationError, handle_chat, run_courtroom
from shared.schema import CaseFile, CaseStatus, Document
from shared.validators import snapshot, validate_codes
from ui.components import (
    agent_activity_timeline,
    allegations_and_defenses,
    case_file_summary,
    chat_history,
    evidence_board,
    header,
    missing_and_governance,
    objections_section,
    symbolic_rules_panel,
    verdict_card,
)


st.set_page_config(
    page_title="OBJECTION! AI ACT",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------------- session state

def _init_state():
    if "case_file" not in st.session_state:
        st.session_state.case_file = None
    if "error_toast" not in st.session_state:
        st.session_state.error_toast = None


_init_state()


# ----------------------------------------------------------------- helpers

def _build_new_case(uploaded_files) -> CaseFile:
    docs: list[Document] = []
    for i, up in enumerate(uploaded_files, start=1):
        try:
            raw = up.read().decode("utf-8", errors="replace")
        except Exception:
            raw = ""
        mime = up.type or ("text/markdown" if up.name.endswith(".md") else "text/plain")
        docs.append(
            Document(
                doc_id=f"doc_{i:02d}",
                filename=up.name,
                mime_type=mime,
                content=raw,
            )
        )
    return CaseFile(
        case_id=f"case_{uuid.uuid4().hex[:8]}",
        status=CaseStatus.NEW,
        documents=docs,
    )


# ---------------------------------------------------------------- sidebar

with st.sidebar:
    st.markdown("### Case Intake")
    st.caption("Upload one or more docs describing the AI use case.")

    uploaded = st.file_uploader(
        "Documents (txt / md)",
        type=["txt", "md"],
        accept_multiple_files=True,
        key="uploader",
    )

    if st.button("⚖️ Run Courtroom", type="primary", use_container_width=True, disabled=not uploaded):
        case = _build_new_case(uploaded)
        with st.spinner("Six agents are deliberating…"):
            try:
                st.session_state.case_file = run_courtroom(case)
            except BackendValidationError as e:
                st.session_state.error_toast = f"Backend failed: {e}"

    st.divider()
    st.markdown("### Demo Cases")
    c1, c2 = st.columns(2)
    if c1.button("Case A · HR", use_container_width=True):
        from shared.mock import make_mock_case_a
        st.session_state.case_file = make_mock_case_a()
    if c2.button("Case B · Stock", use_container_width=True):
        from shared.mock import make_mock_case_b
        st.session_state.case_file = make_mock_case_b()

    if st.session_state.case_file is not None:
        if st.button("🗑️ Reset session", use_container_width=True):
            st.session_state.case_file = None
            st.session_state.error_toast = None
            st.rerun()

    st.divider()
    st.caption(
        "**Track 3** — Norrin Hackathon · 2026-05-24  \n"
        "Internal codename: *ActScout Hybrid*."
    )


# --------------------------------------------------------------- main pane

header()

if st.session_state.error_toast:
    st.error(st.session_state.error_toast)
    st.session_state.error_toast = None

case: CaseFile | None = st.session_state.case_file

if case is None:
    st.info(
        "👈  Upload AI use-case documents in the sidebar and click **Run Courtroom**, "
        "or load **Case A** (HR screening — flags potential high-risk) or "
        "**Case B** (inventory forecaster — minimal risk)."
    )
    st.markdown(
        """
        #### How it works
        1. **Detective** extracts facts from your documents (E-codes).
        2. **Legal Clerk** retrieves matching EU AI Act passages (R-codes).
        3. **Symbolic Risk Gate** fires transparent YAML rules — visible in the UI.
        4. **Prosecutor** raises risk allegations · **Defense** argues exemptions.
        5. **Critique** raises *OBJECTIONS!* on weak or unsupported claims.
        6. **Judge** issues a Preliminary Verdict with confidence + missing evidence.
        7. **Cross-examine** the verdict in chat — confidence updates live.
        """
    )
else:
    case_file_summary(case)
    st.divider()
    verdict_card(case)

    objections_section(case)

    col_l, col_r = st.columns([3, 2])
    with col_l:
        evidence_board(case)
    with col_r:
        symbolic_rules_panel(case)

    st.divider()
    allegations_and_defenses(case)
    st.divider()
    missing_and_governance(case)
    st.divider()
    agent_activity_timeline(case)

    # --- Cross-exam chat -----------------------------------------------
    st.markdown("### 💬 Cross-examination")
    if case.follow_up_questions:
        with st.expander("Suggested follow-up questions", expanded=False):
            for q in case.follow_up_questions:
                st.markdown(f"- {q}")

    chat_history(case)

    user_text = st.chat_input("Answer a follow-up, add a fact, or challenge the verdict…")
    if user_text:
        # Sync v1 §6.3 — snapshot before mutation; restore on failure.
        snap = snapshot(case)
        try:
            with st.spinner("⚖️ Judge re-evaluating…"):
                updated = handle_chat(case, user_text)
            integrity_errs = validate_codes(updated)
            if integrity_errs:
                raise BackendValidationError(agent="validate_codes", errors=integrity_errs)
            st.session_state.case_file = updated
        except BackendValidationError as e:
            st.session_state.case_file = snap
            st.error(f"Could not process that turn — state restored. ({type(e).__name__}: {e})")
        st.rerun()
