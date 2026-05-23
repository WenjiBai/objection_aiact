"""Preliminary Verdict PDF export.

Pure-Python via reportlab (no GTK/Pango system deps — works on Windows).
Entry point: ``case_to_pdf_bytes(case: CaseFile) -> bytes``.
"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from .schema import CaseFile, RiskTier, Severity

_LOGO_PATH = Path(__file__).resolve().parent.parent / "assets" / "Objection_AI_ACT.png"


# ----------------------------------------------------------------- styling

_PRIMARY = colors.HexColor("#0F172A")
_SUBTLE = colors.HexColor("#64748B")
_RULE = colors.HexColor("#CBD5E1")
_CARD_BG = colors.HexColor("#F8FAFC")
_CARD_BD = colors.HexColor("#E2E8F0")

_TIER_COLOR = {
    RiskTier.PROHIBITED: colors.HexColor("#EF4444"),
    RiskTier.HIGH_RISK: colors.HexColor("#EF4444"),
    RiskTier.POTENTIAL_HIGH_RISK: colors.HexColor("#F59E0B"),
    RiskTier.LIMITED_RISK: colors.HexColor("#F59E0B"),
    RiskTier.MINIMAL_RISK: colors.HexColor("#10B981"),
    RiskTier.UNKNOWN: colors.HexColor("#6B7280"),
}

_TIER_LABEL = {
    RiskTier.PROHIBITED: "PROHIBITED",
    RiskTier.HIGH_RISK: "HIGH RISK",
    RiskTier.POTENTIAL_HIGH_RISK: "POTENTIAL HIGH RISK",
    RiskTier.LIMITED_RISK: "LIMITED RISK",
    RiskTier.MINIMAL_RISK: "MINIMAL RISK",
    RiskTier.UNKNOWN: "UNKNOWN",
}


def _styles() -> dict:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "act_title", parent=base["Title"], fontName="Helvetica-Bold",
            fontSize=22, leading=26, textColor=_PRIMARY, spaceAfter=2,
        ),
        "subtitle": ParagraphStyle(
            "act_subtitle", parent=base["Normal"], fontName="Helvetica",
            fontSize=10, leading=13, textColor=_SUBTLE, spaceAfter=8,
            alignment=TA_CENTER,
        ),
        "h2": ParagraphStyle(
            "act_h2", parent=base["Heading2"], fontName="Helvetica-Bold",
            fontSize=13, leading=16, textColor=_PRIMARY,
            spaceBefore=10, spaceAfter=4,
        ),
        "h3": ParagraphStyle(
            "act_h3", parent=base["Heading3"], fontName="Helvetica-Bold",
            fontSize=10.5, leading=13, textColor=_PRIMARY,
            spaceBefore=6, spaceAfter=2,
        ),
        "body": ParagraphStyle(
            "act_body", parent=base["Normal"], fontName="Helvetica",
            fontSize=9.5, leading=13, textColor=_PRIMARY,
        ),
        "meta": ParagraphStyle(
            "act_meta", parent=base["Normal"], fontName="Helvetica",
            fontSize=8.5, leading=11, textColor=_SUBTLE,
        ),
        "code": ParagraphStyle(
            "act_code", parent=base["Normal"], fontName="Courier-Bold",
            fontSize=8.5, leading=11, textColor=_PRIMARY,
        ),
        "caveat": ParagraphStyle(
            "act_caveat", parent=base["Normal"], fontName="Helvetica-Oblique",
            fontSize=8.5, leading=11, textColor=colors.HexColor("#92400E"),
        ),
        "tier": ParagraphStyle(
            "act_tier", parent=base["Normal"], fontName="Helvetica-Bold",
            fontSize=11, leading=14, textColor=colors.white, alignment=TA_CENTER,
        ),
        "ring": ParagraphStyle(
            "act_ring", parent=base["Normal"], fontName="Helvetica-Bold",
            fontSize=22, leading=26, textColor=_PRIMARY, alignment=TA_CENTER,
        ),
        "ring_lbl": ParagraphStyle(
            "act_ring_lbl", parent=base["Normal"], fontName="Helvetica",
            fontSize=8.5, leading=11, textColor=_SUBTLE, alignment=TA_CENTER,
        ),
    }


# ----------------------------------------------------------------- helpers

def _esc(value: object) -> str:
    """Escape user-supplied text for ReportLab's mini-XML paragraphs."""
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _hr(width_total: float) -> HRFlowable:
    return HRFlowable(
        width=width_total, thickness=0.6, color=_RULE,
        spaceBefore=6, spaceAfter=6,
    )


def _humanize(s: str) -> str:
    return s.replace("_", " ").title()


def _card_table(rows: list[list], col_widths: list[float], styles: dict) -> Table:
    t = Table(rows, colWidths=col_widths, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), _CARD_BG),
        ("BOX", (0, 0), (-1, -1), 0.6, _CARD_BD),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, _CARD_BD),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


# ----------------------------------------------------------------- sections

def _logo_flowable(width: float) -> Image | None:
    if not _LOGO_PATH.exists():
        return None
    # Source asset is 1536x1024 (3:2). Cap display width so it doesn't dominate
    # the page; keep aspect ratio.
    target_w = min(width, 90 * mm)
    target_h = target_w * (1024 / 1536)
    img = Image(str(_LOGO_PATH), width=target_w, height=target_h)
    img.hAlign = "CENTER"
    return img


def _section_header(case: CaseFile, styles: dict, width: float) -> list:
    first_doc = case.documents[0].filename if case.documents else case.case_id
    out: list = []
    logo = _logo_flowable(width)
    if logo is not None:
        out.append(logo)
        out.append(Spacer(1, 4))
    else:
        out.append(Paragraph("OBJECTION! — AI ACT", styles["title"]))
    out += [
        Paragraph("Preliminary Verdict — not legal advice", styles["subtitle"]),
        _hr(width),
        Paragraph(f"<b>Case:</b> {_esc(first_doc)}", styles["body"]),
        Paragraph(
            f"<b>Case ID:</b> {_esc(case.case_id)} &nbsp;·&nbsp; "
            f"<b>Created:</b> {_esc(case.created_at.strftime('%Y-%m-%d %H:%M'))} &nbsp;·&nbsp; "
            f"<b>Documents:</b> {len(case.documents)}",
            styles["meta"],
        ),
    ]
    if case.documents:
        names = ", ".join(_esc(d.filename) for d in case.documents)
        out.append(Paragraph(f"<b>Files:</b> {names}", styles["meta"]))
    return out


def _verdict_block(case: CaseFile, styles: dict, width: float) -> list:
    if not case.verdict:
        return [Paragraph("No verdict has been issued yet.", styles["body"])]

    v = case.verdict
    tier_color = _TIER_COLOR.get(v.tier, _SUBTLE)
    tier_label = _TIER_LABEL.get(v.tier, "UNKNOWN")

    tier_cell = Table(
        [[Paragraph(_esc(tier_label), styles["tier"])]],
        colWidths=[60 * mm], rowHeights=[18 * mm],
    )
    tier_cell.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), tier_color),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("BOX", (0, 0), (-1, -1), 0, tier_color),
    ]))

    ring_cell = Table(
        [
            [Paragraph(f"{v.confidence_score}/10", styles["ring"])],
            [Paragraph(
                f"Confidence — <b>{_esc(v.confidence_label.value)}</b>",
                styles["ring_lbl"],
            )],
        ],
        colWidths=[60 * mm],
    )
    ring_cell.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), _CARD_BG),
        ("BOX", (0, 0), (-1, -1), 0.6, _CARD_BD),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))

    summary_row = Table(
        [[tier_cell, ring_cell]], colWidths=[width / 2, width / 2], hAlign="LEFT",
    )
    summary_row.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))

    out: list = [
        Paragraph("Preliminary Verdict", styles["h2"]),
        summary_row,
        Spacer(1, 6),
        Paragraph("<b>Reasoning trail</b>", styles["h3"]),
        Paragraph(_esc(v.reasoning_trail), styles["body"]),
    ]
    if v.caveats:
        out.append(Spacer(1, 4))
        for c in v.caveats:
            out.append(Paragraph(f"⚠ {_esc(c)}", styles["caveat"]))
    return out


def _evidence_block(case: CaseFile, styles: dict, width: float) -> list:
    if not (case.facts or case.refs or case.assumptions):
        return []

    out: list = [Paragraph("Evidence Board", styles["h2"])]

    if case.facts:
        out.append(Paragraph(f"Facts &middot; {len(case.facts)}", styles["h3"]))
        rows = [[
            Paragraph("<b>Code</b>", styles["meta"]),
            Paragraph("<b>Category</b>", styles["meta"]),
            Paragraph("<b>Text</b>", styles["meta"]),
            Paragraph("<b>Source</b>", styles["meta"]),
        ]]
        for e in case.facts:
            rows.append([
                Paragraph(_esc(e.code), styles["code"]),
                Paragraph(_esc(_humanize(e.category.value)), styles["meta"]),
                Paragraph(_esc(e.text), styles["body"]),
                Paragraph(_esc(e.source_doc_id), styles["meta"]),
            ])
        out.append(_card_table(
            rows, [22 * mm, 28 * mm, width - 22 * mm - 28 * mm - 24 * mm, 24 * mm], styles,
        ))

    if case.refs:
        out.append(Paragraph(f"References &middot; {len(case.refs)}", styles["h3"]))
        rows = [[
            Paragraph("<b>Code</b>", styles["meta"]),
            Paragraph("<b>Article</b>", styles["meta"]),
            Paragraph("<b>Snippet</b>", styles["meta"]),
            Paragraph("<b>Source</b>", styles["meta"]),
        ]]
        for r in case.refs:
            rows.append([
                Paragraph(_esc(r.code), styles["code"]),
                Paragraph(_esc(r.article_no), styles["meta"]),
                Paragraph(_esc(r.snippet or r.title), styles["body"]),
                Paragraph(_esc(r.source_label), styles["meta"]),
            ])
        out.append(_card_table(
            rows, [30 * mm, 22 * mm, width - 30 * mm - 22 * mm - 26 * mm, 26 * mm], styles,
        ))

    if case.assumptions:
        out.append(Paragraph(f"Assumptions &middot; {len(case.assumptions)}", styles["h3"]))
        rows = [[
            Paragraph("<b>Code</b>", styles["meta"]),
            Paragraph("<b>Assumption</b>", styles["meta"]),
            Paragraph("<b>Confirm?</b>", styles["meta"]),
        ]]
        for a in case.assumptions:
            rows.append([
                Paragraph(_esc(a.code), styles["code"]),
                Paragraph(_esc(a.text), styles["body"]),
                Paragraph("Yes" if a.needs_confirmation else "No", styles["meta"]),
            ])
        out.append(_card_table(
            rows, [22 * mm, width - 22 * mm - 22 * mm, 22 * mm], styles,
        ))

    return out


def _rules_block(case: CaseFile, styles: dict, width: float) -> list:
    if not case.rule_firings:
        return []
    fired = sum(1 for r in case.rule_firings if r.fired)
    out: list = [
        Paragraph(
            f"Symbolic Risk Gate &middot; {fired} fired / "
            f"{len(case.rule_firings) - fired} inactive",
            styles["h2"],
        ),
    ]
    rows = [[
        Paragraph("<b>Rule</b>", styles["meta"]),
        Paragraph("<b>Fired</b>", styles["meta"]),
        Paragraph("<b>Description / actions</b>", styles["meta"]),
        Paragraph("<b>Refs</b>", styles["meta"]),
    ]]
    for rf in case.rule_firings:
        if rf.then_actions:
            action = ", ".join(f"{k}={v}" for k, v in rf.then_actions.items())
        else:
            action = rf.description
        rows.append([
            Paragraph(_esc(rf.rule_id), styles["code"]),
            Paragraph("✓" if rf.fired else "·", styles["body"]),
            Paragraph(_esc(action), styles["body"]),
            Paragraph(", ".join(_esc(c) for c in rf.maps_to_refs), styles["meta"]),
        ])
    out.append(_card_table(
        rows, [30 * mm, 14 * mm, width - 30 * mm - 14 * mm - 36 * mm, 36 * mm], styles,
    ))
    return out


def _allegations_defenses_block(case: CaseFile, styles: dict, width: float) -> list:
    if not (case.allegations or case.defenses):
        return []
    out: list = [Paragraph("Allegations & Defenses", styles["h2"])]

    if case.allegations:
        out.append(Paragraph(f"Prosecutor &middot; {len(case.allegations)} allegation(s)", styles["h3"]))
        for al in case.allegations:
            meta_bits = []
            if al.basis_evidence_codes:
                meta_bits.append("E: " + ", ".join(al.basis_evidence_codes))
            if al.basis_ref_codes:
                meta_bits.append("R: " + ", ".join(al.basis_ref_codes))
            meta = " &middot; ".join(_esc(b) for b in meta_bits)
            out.append(Paragraph(
                f"<b>{_esc(al.allegation_id)}</b> &middot; tier=<i>{_esc(_TIER_LABEL.get(al.tier, al.tier.value))}</i> "
                f"&middot; strength=<i>{_esc(al.strength.value)}</i>",
                styles["body"],
            ))
            out.append(Paragraph(_esc(al.claim), styles["body"]))
            if meta:
                out.append(Paragraph(meta, styles["meta"]))
            out.append(Spacer(1, 3))

    if case.defenses:
        out.append(Paragraph(f"Defense &middot; {len(case.defenses)} argument(s)", styles["h3"]))
        for df in case.defenses:
            targets = f" → targets {df.targets_allegation_id}" if df.targets_allegation_id else ""
            doc_req = " (requires documentation)" if df.requires_documentation else ""
            meta_bits = []
            if df.basis_evidence_codes:
                meta_bits.append("E: " + ", ".join(df.basis_evidence_codes))
            if df.basis_ref_codes:
                meta_bits.append("R: " + ", ".join(df.basis_ref_codes))
            meta = " &middot; ".join(_esc(b) for b in meta_bits)
            out.append(Paragraph(
                f"<b>{_esc(df.defense_id)}</b> &middot; <i>{_esc(_humanize(df.type))}</i>"
                f"{_esc(targets)}{_esc(doc_req)}",
                styles["body"],
            ))
            out.append(Paragraph(_esc(df.claim), styles["body"]))
            if meta:
                out.append(Paragraph(meta, styles["meta"]))
            out.append(Spacer(1, 3))
    return out


def _objections_block(case: CaseFile, styles: dict, width: float) -> list:
    if not case.objections:
        return []
    open_n = sum(1 for o in case.objections if o.resolution is None)
    out: list = [
        Paragraph(
            f"Critique Objections &middot; {open_n} open / "
            f"{len(case.objections) - open_n} resolved",
            styles["h2"],
        ),
    ]
    for ob in case.objections:
        status = "Resolved" if ob.resolution else "Open"
        out.append(Paragraph(
            f"<b>OBJECTION!</b> &middot; {_esc(status)} &middot; "
            f"target={_esc(ob.target_type)} {_esc(ob.target_id)} "
            f"&middot; severity={_esc(ob.severity.value)}",
            styles["body"],
        ))
        out.append(Paragraph(_esc(ob.reason), styles["body"]))
        if ob.challenging_evidence_codes:
            out.append(Paragraph(
                "Challenging evidence: " + ", ".join(_esc(c) for c in ob.challenging_evidence_codes),
                styles["meta"],
            ))
        if ob.resolution:
            out.append(Paragraph(f"Resolution: {_esc(ob.resolution)}", styles["meta"]))
        out.append(Spacer(1, 3))
    return out


def _missing_block(case: CaseFile, styles: dict, width: float) -> list:
    if not case.missing_evidence and not case.follow_up_questions:
        return []
    out: list = [Paragraph("Missing Evidence & Follow-up", styles["h2"])]
    if case.missing_evidence:
        for m in case.missing_evidence:
            blocks = " (blocks verdict)" if m.blocks_verdict else ""
            out.append(Paragraph(
                f"☐ <b>{_esc(m.description)}</b> &middot; severity={_esc(m.severity.value)}{_esc(blocks)}",
                styles["body"],
            ))
            for q in m.suggested_questions:
                out.append(Paragraph(f"&nbsp;&nbsp;&nbsp;• {_esc(q)}", styles["meta"]))
    if case.follow_up_questions:
        out.append(Paragraph("Follow-up questions", styles["h3"]))
        for q in case.follow_up_questions:
            out.append(Paragraph(f"❓ {_esc(q)}", styles["body"]))
    return out


def _governance_block(case: CaseFile, styles: dict, width: float) -> list:
    if not case.governance_checklist:
        return []
    applies = sum(1 for g in case.governance_checklist if g.applies)
    out: list = [
        Paragraph(
            f"Governance Checklist &middot; {applies} required item(s)",
            styles["h2"],
        ),
    ]
    rows = [[
        Paragraph("<b>Required</b>", styles["meta"]),
        Paragraph("<b>Item</b>", styles["meta"]),
        Paragraph("<b>AI Act ref</b>", styles["meta"]),
    ]]
    for g in case.governance_checklist:
        rows.append([
            Paragraph("✔" if g.applies else "—", styles["body"]),
            Paragraph(_esc(g.item), styles["body"]),
            Paragraph(_esc(g.ai_act_reference or ""), styles["meta"]),
        ])
    out.append(_card_table(
        rows, [20 * mm, width - 20 * mm - 38 * mm, 38 * mm], styles,
    ))
    return out


def _chat_block(case: CaseFile, styles: dict, width: float) -> list:
    if not case.chat_history:
        return []
    out: list = [Paragraph("Cross-examination Transcript", styles["h2"])]
    for turn in case.chat_history:
        speaker = {"user": "You", "judge": "Judge", "system": "System"}.get(turn.role, turn.role.title())
        out.append(Paragraph(
            f"<b>{_esc(speaker)}</b> &middot; "
            f"<font color='#64748B'>{_esc(turn.timestamp.strftime('%H:%M:%S'))}</font>",
            styles["meta"],
        ))
        out.append(Paragraph(_esc(turn.text), styles["body"]))
        if turn.triggered_updates:
            out.append(Paragraph(
                "Updated: " + ", ".join(_esc(u) for u in turn.triggered_updates),
                styles["meta"],
            ))
        out.append(Spacer(1, 3))
    return out


# ----------------------------------------------------------------- footer

def _on_page(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(_SUBTLE)
    canvas.drawString(
        15 * mm, 10 * mm,
        "OBJECTION! AI ACT — Preliminary Verdict. Not legal advice.",
    )
    canvas.drawRightString(
        A4[0] - 15 * mm, 10 * mm, f"Page {canvas.getPageNumber()}",
    )
    canvas.restoreState()


# ----------------------------------------------------------------- entry

def case_to_pdf_bytes(case: CaseFile) -> bytes:
    buf = BytesIO()
    margin = 15 * mm
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=margin, rightMargin=margin,
        topMargin=margin, bottomMargin=18 * mm,
        title=f"OBJECTION! AI ACT — {case.case_id}",
        author="OBJECTION! AI ACT",
    )
    width = A4[0] - 2 * margin
    styles = _styles()

    story: list = []
    story += _section_header(case, styles, width)
    story.append(_hr(width))
    story += _verdict_block(case, styles, width)
    story += _evidence_block(case, styles, width)
    story += _rules_block(case, styles, width)
    story += _allegations_defenses_block(case, styles, width)
    story += _objections_block(case, styles, width)
    story += _missing_block(case, styles, width)
    story += _governance_block(case, styles, width)
    story += _chat_block(case, styles, width)

    doc.build(story, onFirstPage=_on_page, onLaterPages=_on_page)
    return buf.getvalue()


def case_pdf_filename(case: CaseFile) -> str:
    first = case.documents[0].filename if case.documents else case.case_id
    stem = first.rsplit(".", 1)[0]
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in stem)[:60] or case.case_id
    return f"objection_verdict_{safe}.pdf"


__all__ = ["case_to_pdf_bytes", "case_pdf_filename"]
