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
    case_file_summary,
    chat_history,
    evidence_board,
    missing_and_governance,
    objections_section,
    symbolic_rules_panel,
    upload_hero,
    upload_topbar,
    verdict_card,
)
from ui.theme import apply_theme, init_theme_state


st.set_page_config(
    page_title="OBJECTION! AI ACT",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_theme_state()
apply_theme()


# --------------------------------------------------------- session state

def _init_state():
    if "case_file" not in st.session_state:
        st.session_state.case_file = None
    if "error_toast" not in st.session_state:
        st.session_state.error_toast = None


_init_state()


# ----------------------------------------------------------------- helpers

def _build_new_case(uploaded_files, pasted_text: str = "") -> CaseFile:
    docs: list[Document] = []
    for i, up in enumerate(uploaded_files, start=1):
        try:
            raw = up.read().decode("utf-8", errors="replace")
        except Exception:
            raw = f"[Binary document uploaded: {up.name}]"
        mime = up.type or ("text/markdown" if up.name.endswith(".md") else "text/plain")
        docs.append(
            Document(
                doc_id=f"doc_{i:02d}",
                filename=up.name,
                mime_type=mime,
                content=raw,
            )
        )
    if pasted_text.strip():
        docs.append(
            Document(
                doc_id=f"doc_{len(docs) + 1:02d}",
                filename="pasted_use_case.md",
                mime_type="text/markdown",
                content=pasted_text.strip(),
            )
        )
    return CaseFile(
        case_id=f"case_{uuid.uuid4().hex[:8]}",
        status=CaseStatus.NEW,
        documents=docs,
    )


# ---------------------------------------------------------------- sidebar

with st.sidebar:
    st.markdown(
        """
        <div class="act-brand">
          <span class="mark">⚖</span>
          <span class="name">ActScout</span>
          <span class="tag">hybrid</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("＋ New case", use_container_width=True):
        st.session_state.case_file = None
        st.session_state.error_toast = None
        st.rerun()
    st.button("⌕ Search cases", use_container_width=True, disabled=True)

    st.markdown('<div class="act-side-section">Recent cases</div>', unsafe_allow_html=True)
    if st.button("● AI hiring screener", use_container_width=True):
        from shared.mock import make_mock_case_a
        st.session_state.case_file = make_mock_case_a()
        st.rerun()
    if st.button("● Inventory forecaster", use_container_width=True):
        from shared.mock import make_mock_case_b
        st.session_state.case_file = make_mock_case_b()
        st.rerun()
    st.markdown(
        """
        <div class="act-case-link"><span class="act-dot" style="background:#BA7517"></span> Customer chatbot (draft)</div>
        <div class="act-case-link"><span class="act-dot" style="background:#0F6E56"></span> Email spam filter</div>
        <div class="act-side-section">Settings</div>
        <div class="act-side-link">⚙ Preferences</div>
        """,
        unsafe_allow_html=True,
    )


# --------------------------------------------------------------- main pane

if st.session_state.error_toast:
    st.error(st.session_state.error_toast)
    st.session_state.error_toast = None

case: CaseFile | None = st.session_state.case_file

if case is None:
    upload_topbar()
    upload_hero()
    center = st.columns([1, 1.6, 1])[1]
    with center:
        uploaded = st.file_uploader(
            "Documents",
            type=["pdf", "docx", "txt", "md"],
            accept_multiple_files=True,
            key="uploader",
            label_visibility="collapsed",
        )
        st.markdown('<div class="act-or"><span>or</span></div>', unsafe_allow_html=True)
        pasted = st.text_area(
            "Paste use-case description",
            placeholder="Paste a use-case description here...",
            height=92,
            label_visibility="collapsed",
        )
        can_run = bool(uploaded) or bool(pasted.strip())
        if st.button("⚖ Open courtroom hearing", type="primary", use_container_width=True, disabled=not can_run):
            case = _build_new_case(uploaded, pasted)
            with st.spinner("Six agents are deliberating..."):
                try:
                    st.session_state.case_file = run_courtroom(case)
                except BackendValidationError as e:
                    st.session_state.error_toast = f"Backend failed: {e}"
            st.rerun()
else:
    case_file_summary(case)
    verdict_card(case)
    evidence_board(case)
    symbolic_rules_panel(case)
    objections_section(case)
    missing_and_governance(case)
    agent_activity_timeline(case)

    # --- Cross-exam chat -----------------------------------------------
    st.markdown('<div class="act-chat-wrap">', unsafe_allow_html=True)
    st.markdown("#### Cross-examine the verdict")
    if case.follow_up_questions:
        with st.expander("Suggested follow-up questions", expanded=False):
            for q in case.follow_up_questions:
                st.markdown(f"- {q}")

    chat_history(case)
    st.markdown("</div>", unsafe_allow_html=True)

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
