"""OBJECTION! AI ACT — Streamlit entry.

Run:  streamlit run app.py
"""

from __future__ import annotations

import uuid
from pathlib import Path

import streamlit as st

from backend.api import BackendValidationError, handle_chat, run_courtroom
from shared.document_parser import extract_text
from shared.pdf_export import case_pdf_filename, case_to_pdf_bytes
from shared.schema import CaseFile, CaseStatus, Document
from shared.validators import snapshot, validate_codes
from ui.components import (
    agent_activity_timeline,
    agent_stepper,
    case_file_summary,
    chat_history,
    evidence_board,
    landing_hero,
    missing_and_governance,
    objections_section,
    symbolic_rules_panel,
    upload_topbar,
    verdict_card,
)
from ui.theme import apply_theme, get_mode, init_theme_state, set_mode


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

def _build_new_case(uploaded_files, pasted_text: str = "") -> tuple[CaseFile, list[str]]:
    """Build a CaseFile from uploads + pasted text.

    Returns (case_file, warnings). Warnings cover truncated or unparsable docs;
    the caller surfaces them via st.warning so the demo never silently feeds
    garbage to the LLM (the original UTF-8-decode bug that blew the rate limit).
    """
    docs: list[Document] = []
    warnings: list[str] = []
    for i, up in enumerate(uploaded_files, start=1):
        parsed = extract_text(up)
        if parsed.parser == "fallback":
            warnings.append(f"Could not parse {up.name} — sent placeholder text to the courtroom.")
        elif parsed.truncated:
            warnings.append(
                f"{up.name} was {parsed.original_chars:,} chars — truncated to 30,000 to stay under the LLM rate limit."
            )
        mime = up.type or ("text/markdown" if up.name.endswith(".md") else "text/plain")
        docs.append(
            Document(
                doc_id=f"doc_{i:02d}",
                filename=up.name,
                mime_type=mime,
                content=parsed.text,
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
    case = CaseFile(
        case_id=f"case_{uuid.uuid4().hex[:8]}",
        status=CaseStatus.NEW,
        documents=docs,
    )
    return case, warnings


# ---------------------------------------------------------------- sidebar

_LOGO_PATH = Path(__file__).resolve().parent / "assets" / "Objection_AI_ACT.png"

with st.sidebar:
    st.image(str(_LOGO_PATH), use_container_width=True)
    st.html(
        '<div class="act-brand-sub">Puts your AI use case on trial.</div>'
    )

    # Theme mode toggle
    mode = get_mode()
    tcol1, tcol2 = st.columns(2)
    with tcol1:
        if st.button(
            "🌙 Dark",
            use_container_width=True,
            type="primary" if mode == "dark" else "secondary",
            key="mode_dark",
        ):
            set_mode("dark")
            st.rerun()
    with tcol2:
        if st.button(
            "☀ Light",
            use_container_width=True,
            type="primary" if mode == "light" else "secondary",
            key="mode_light",
        ):
            set_mode("light")
            st.rerun()

    st.html("<div style='height:6px'></div>")

    if st.button("+ New case", use_container_width=True, type="primary"):
        st.session_state.case_file = None
        st.session_state.error_toast = None
        st.rerun()
    st.button("Search cases", use_container_width=True, disabled=True)

    st.html('<div class="act-side-section">Demo cases</div>')
    if st.button("● AI hiring screener", use_container_width=True):
        from shared.mock import make_mock_case_a
        st.session_state.case_file = make_mock_case_a()
        st.rerun()
    if st.button("● Inventory forecaster", use_container_width=True):
        from shared.mock import make_mock_case_b
        st.session_state.case_file = make_mock_case_b()
        st.rerun()




# --------------------------------------------------------------- main pane

if st.session_state.error_toast:
    st.error(st.session_state.error_toast)
    st.session_state.error_toast = None

case: CaseFile | None = st.session_state.case_file

# ============================================================== landing
if case is None:
    upload_topbar()
    landing_hero()

    center = st.columns([1, 1.6, 1])[1]
    with center:
        uploaded = st.file_uploader(
            "Documents",
            type=["pdf", "docx", "pptx", "txt", "md"],
            accept_multiple_files=True,
            key="uploader",
            label_visibility="collapsed",
            help="Vendor white papers, model cards, policy docs, internal process notes",
        )
        st.html('<div class="act-or"><span>or paste use-case description</span></div>')
        pasted = st.text_area(
            "Paste use-case description",
            placeholder="e.g. We're building an AI tool that ranks job applicants...",
            height=110,
            label_visibility="collapsed",
        )
        can_run = bool(uploaded) or bool(pasted.strip())
        if st.button(
            "⚖ Open courtroom hearing",
            type="primary",
            use_container_width=True,
            disabled=not can_run,
        ):
            new_case, parse_warnings = _build_new_case(uploaded, pasted)
            for w in parse_warnings:
                st.warning(w)
            with st.spinner("Six agents are deliberating…"):
                try:
                    st.session_state.case_file = run_courtroom(new_case)
                except BackendValidationError as e:
                    st.session_state.error_toast = f"Backend failed: {e}"
                except Exception as e:
                    # anthropic.RateLimitError surfaces as a 429; catch by name so
                    # we don't hard-depend on the anthropic package at import time.
                    if type(e).__name__ == "RateLimitError" or "rate_limit" in str(e).lower() or "429" in str(e):
                        st.session_state.error_toast = (
                            "Rate limit hit — wait ~1 minute and try again, "
                            "or upload fewer / smaller documents."
                        )
                    else:
                        raise
            st.rerun()

        st.html(
            """
            <div class="act-quickstart">
              <span class="act-quickstart-chip">💡 Try a demo case →</span>
            </div>
            """
        )
        qc1, qc2 = st.columns(2)
        with qc1:
            if st.button("👤 AI hiring screener", use_container_width=True):
                from shared.mock import make_mock_case_a
                st.session_state.case_file = make_mock_case_a()
                st.rerun()
        with qc2:
            if st.button("📦 Inventory forecaster", use_container_width=True):
                from shared.mock import make_mock_case_b
                st.session_state.case_file = make_mock_case_b()
                st.rerun()

# ============================================================== workspace
else:
    case_file_summary(case)

    # Export Preliminary Verdict as PDF (button sits just under the case banner).
    pdf_col = st.columns([1, 1, 1])[2]
    with pdf_col:
        try:
            pdf_bytes = case_to_pdf_bytes(case)
            st.download_button(
                label="⬇ Export Preliminary Verdict (PDF)",
                data=pdf_bytes,
                file_name=case_pdf_filename(case),
                mime="application/pdf",
                use_container_width=True,
                key=f"pdf_dl_{case.case_id}",
                help="Download the full case file: verdict, evidence, rule trace, objections, and checklist.",
            )
        except Exception as e:
            st.error(f"PDF export failed: {type(e).__name__}: {e}")

    agent_stepper(case)

    verdict_card(case)
    evidence_board(case)
    symbolic_rules_panel(case)
    objections_section(case)
    missing_and_governance(case)
    agent_activity_timeline(case)

    user_text = None

    st.html(
        """
        <div class="act-chat-head">
          <div class="act-chat-title">⚖ Cross-examine the verdict</div>
          <span class="act-chat-hint">Add a fact · challenge a claim · answer a follow-up</span>
        </div>
        """
    )
    if case.follow_up_questions:
        chips = "".join(
            f'<span class="act-followup-chip">❓ {q[:80]}{"…" if len(q) > 80 else ""}</span>'
            for q in case.follow_up_questions[:4]
        )
        st.html(
            f'<div style="margin-bottom:10px;">{chips}</div>'
        )
    chat_history(case)
    with st.form("cross_exam_form", clear_on_submit=True, border=False):
        typed = st.text_area(
            "Cross-examination input",
            placeholder="Answer a follow-up, add a fact, or challenge the verdict...",
            height=92,
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button(
            "Submit to judge",
            type="primary",
            use_container_width=True,
        )
        if submitted and typed.strip():
            st.session_state.cross_exam_pending = typed.strip()

    user_text = st.chat_input("Answer a follow-up, add a fact, or challenge the verdict…")
    if not user_text:
        user_text = st.session_state.pop("cross_exam_pending", None)
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
