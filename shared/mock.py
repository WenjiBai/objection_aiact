"""Mock CaseFiles for Case A (HR screening) and Case B (inventory forecaster).

Targets §7 acceptance criteria in Frontend_Backend_Sync_v1.md.
Backend stub returns these until A wires the real agents.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from .schema import (
    AgentActivity, AgentName, AgentStatus, Allegation, Assumption, CaseFile,
    CaseStatus, ChatTurn, ChecklistItem, ConfidenceLabel, Defense, Document,
    Evidence, EvidenceCategory, MissingEvidenceItem, Objection, OutputType,
    Reference, RiskTier, RuleFiring, Sector, Severity, SourceType, Verdict,
)


# ------------------------------------------------------- yaml-source blobs

_YAML_HIRE = """\
- id: R-HIRE-001
  description: Employment-related ranking or screening
  when:
    sector: employment
    output: [ranking, screening, recommendation, scoring]
    affected_persons: [job_applicants, workers]
  then:
    preliminary_tier: potential_high_risk
    high_risk_candidate: true
    basis: "AI Act Annex III, employment context"
  maps_to_refs: [R-Annex-III-4, R-Art-6]
  severity: high
"""

_YAML_OVERSIGHT = """\
- id: R-OVERSIGHT-001
  description: Missing human oversight evidence
  when:
    human_oversight: unverified
  then:
    require_evidence: true
    objection_target: oversight_claim
  maps_to_refs: [R-Art-14]
  severity: medium
"""

_YAML_GPAI = """\
- id: R-GPAI-001
  description: Use of general-purpose AI model
  when:
    gpai_usage: true
  then:
    trigger: gpai_responsibility_chain_analysis
  maps_to_refs: [R-Art-51]
  severity: medium
"""

_YAML_CHAT = """\
- id: R-CHAT-001
  description: AI system interacting directly with humans
  when:
    deployment_context: [chatbot, direct_user_interaction]
  then:
    transparency_obligation: true
    basis: "AI Act Article 50"
  maps_to_refs: [R-Art-50]
  severity: low
"""


# =========================================================== Case A

def make_mock_case_a() -> CaseFile:
    """§7.1 — POTENTIAL_HIGH_RISK, MEDIUM confidence, OBJECTION on oversight."""
    t0 = datetime.now()

    documents = [
        Document(
            doc_id="doc_a1", filename="vendor_whitepaper.md",
            mime_type="text/markdown",
            content=(
                "CV-Sage is an AI-powered candidate screening platform. It ingests "
                "CVs, parses interview notes, and ranks job applicants for HR "
                "managers. The top-5 ranked candidates are surfaced for human "
                "review. Our system includes human oversight."
            ),
        ),
        Document(
            doc_id="doc_a2", filename="internal_process_notes.md",
            mime_type="text/markdown",
            content=(
                "HR managers receive the ranked list and decide whom to invite to "
                "interview. The override mechanism is not documented. No formal "
                "appeal process for rejected applicants."
            ),
        ),
    ]

    facts = [
        Evidence(code="E-01", source_doc_id="doc_a1",
                 text="System screens CVs and ranks job applicants for HR managers.",
                 category=EvidenceCategory.PURPOSE, relevance=Severity.HIGH),
        Evidence(code="E-02", source_doc_id="doc_a1",
                 text="Use case is employment-related (hiring).",
                 structured_value=Sector.EMPLOYMENT.value,
                 category=EvidenceCategory.SECTOR, relevance=Severity.HIGH),
        Evidence(code="E-03", source_doc_id="doc_a1",
                 text="Output is a ranked list of candidates.",
                 structured_value=OutputType.RANKING.value,
                 category=EvidenceCategory.OUTPUT, relevance=Severity.HIGH),
        Evidence(code="E-04", source_doc_id="doc_a1",
                 text="Affected persons: job applicants.",
                 category=EvidenceCategory.AFFECTED_PERSONS, relevance=Severity.HIGH),
        Evidence(code="E-05", source_doc_id="doc_a2",
                 text="Vendor claims human oversight, but override mechanism not documented.",
                 category=EvidenceCategory.HUMAN_OVERSIGHT, relevance=Severity.MEDIUM),
        Evidence(code="E-06", source_doc_id="doc_a1",
                 text="No GPAI model mentioned in uploaded docs.",
                 structured_value="unknown",
                 category=EvidenceCategory.GPAI_USAGE, relevance=Severity.LOW),
        Evidence(code="E-07", source_doc_id="doc_a2",
                 text="Ranking influences which applicants advance to interview.",
                 category=EvidenceCategory.DECISION_IMPACT, relevance=Severity.HIGH),
    ]

    refs = [
        Reference(
            code="R-Annex-III-4", article_no="Annex-III-4",
            title="Employment, workers management and access to self-employment",
            snippet="AI systems intended to be used for the recruitment or selection of natural persons…",
            full_text=("AI systems intended to be used for the recruitment or selection of natural "
                       "persons, in particular to place targeted job advertisements, to analyse and "
                       "filter job applications, and to evaluate candidates."),
            source_type=SourceType.LEGISLATION, source_label="EU AI Act 2024/1689",
        ),
        Reference(
            code="R-Art-6", article_no="6",
            title="Classification rules for high-risk AI systems",
            snippet="An AI system shall be considered high-risk where it is listed in Annex III…",
            full_text=("An AI system shall be considered high-risk only where it is listed in Annex III "
                       "or used as a safety component of a product covered by Annex I."),
            source_type=SourceType.LEGISLATION, source_label="EU AI Act 2024/1689",
        ),
        Reference(
            code="R-Art-14", article_no="14",
            title="Human oversight",
            snippet="High-risk AI systems shall be designed and developed in such a way that they can be effectively overseen by natural persons…",
            full_text=("High-risk AI systems shall be designed and developed in such a way, including with "
                       "appropriate human-machine interface tools, that they can be effectively overseen by "
                       "natural persons during the period in which they are in use."),
            source_type=SourceType.LEGISLATION, source_label="EU AI Act 2024/1689",
        ),
        Reference(
            code="R-Art-27", article_no="27",
            title="Fundamental rights impact assessment for high-risk AI systems",
            snippet="Deployers shall perform an assessment of the impact on fundamental rights…",
            full_text=("Prior to deploying a high-risk AI system referred to in Article 6(2), deployers "
                       "shall perform an assessment of the impact on fundamental rights that the use of "
                       "such system may produce."),
            source_type=SourceType.LEGISLATION, source_label="EU AI Act 2024/1689",
        ),
    ]

    assumptions = [
        Assumption(code="A-01",
                   text="System acts as a deployer-facing tool used in EU employment context.",
                   reasoning="Vendor docs describe an HR-facing screening workflow but do not state jurisdiction.",
                   needs_confirmation=True),
        Assumption(code="A-02",
                   text="No GPAI base model is integrated.",
                   reasoning="No GPAI provider is named in vendor materials.",
                   needs_confirmation=True),
    ]

    rule_firings = [
        RuleFiring(
            rule_id="R-HIRE-001", description="Employment-related ranking or screening",
            fired=True,
            when_conditions={
                "sector": "employment",
                "output": ["ranking", "screening", "recommendation", "scoring"],
                "affected_persons": ["job_applicants", "workers"],
            },
            evaluated_against={
                "sector": "employment",
                "output": "ranking",
                "affected_persons": "job_applicants",
            },
            then_actions={
                "preliminary_tier": "potential_high_risk",
                "high_risk_candidate": True,
                "basis": "AI Act Annex III, employment context",
            },
            supporting_evidence_codes=["E-02", "E-03", "E-04"],
            maps_to_refs=["R-Annex-III-4", "R-Art-6"],
            yaml_source=_YAML_HIRE,
        ),
        RuleFiring(
            rule_id="R-OVERSIGHT-001", description="Missing human oversight evidence",
            fired=True,
            when_conditions={"human_oversight": "unverified"},
            evaluated_against={"human_oversight": "unverified"},
            then_actions={"require_evidence": True, "objection_target": "oversight_claim"},
            supporting_evidence_codes=["E-05"],
            maps_to_refs=["R-Art-14"],
            yaml_source=_YAML_OVERSIGHT,
        ),
        RuleFiring(
            rule_id="R-GPAI-001", description="Use of general-purpose AI model",
            fired=False,
            when_conditions={"gpai_usage": True},
            evaluated_against={"gpai_usage": "unknown"},
            then_actions={},
            supporting_evidence_codes=["E-06"],
            maps_to_refs=[],
            yaml_source=_YAML_GPAI,
        ),
        RuleFiring(
            rule_id="R-CHAT-001", description="AI system interacting directly with humans",
            fired=False,
            when_conditions={"deployment_context": ["chatbot", "direct_user_interaction"]},
            evaluated_against={"deployment_context": "internal_hr_tool"},
            then_actions={},
            supporting_evidence_codes=[],
            maps_to_refs=[],
            yaml_source=_YAML_CHAT,
        ),
    ]

    allegations = [
        Allegation(allegation_id="ALL-01", tier=RiskTier.POTENTIAL_HIGH_RISK,
                   claim="Employment-related screening of applicants falls under Annex III §4.",
                   basis_evidence_codes=["E-02", "E-03", "E-04"],
                   basis_ref_codes=["R-Annex-III-4", "R-Art-6"],
                   strength=Severity.HIGH),
        Allegation(allegation_id="ALL-02", tier=RiskTier.POTENTIAL_HIGH_RISK,
                   claim="Human oversight is mentioned but unverified; Article 14 obligations may not be met.",
                   basis_evidence_codes=["E-05"],
                   basis_ref_codes=["R-Art-14"],
                   strength=Severity.MEDIUM),
    ]

    defenses = [
        Defense(defense_id="DEF-01",
                targets_allegation_id="ALL-02",
                type="human_oversight",
                claim="Vendor states HR managers review top candidates before any hiring decision.",
                basis_evidence_codes=["E-05"],
                basis_ref_codes=["R-Art-14"],
                requires_documentation=True),
    ]

    objections = [
        Objection(objection_id="OBJ-01",
                  target_type="defense", target_id="DEF-01",
                  reason=("OBJECTION! The 'human oversight' defense is unsupported — "
                          "override mechanism is not documented and no appeal process exists for applicants."),
                  severity=Severity.HIGH,
                  challenging_evidence_codes=["E-05"]),
    ]

    verdict = Verdict(
        tier=RiskTier.POTENTIAL_HIGH_RISK,
        confidence_score=5,
        confidence_label=ConfidenceLabel.MEDIUM,
        reasoning_trail=(
            "The use case appears to involve employment-related AI that ranks "
            "job applicants (Annex III §4). Human oversight is claimed but "
            "neither the override mechanism nor an appeal process is documented, "
            "leaving Article 14 obligations unverified. Confidence is medium "
            "pending evidence of the oversight protocol."
        ),
    )

    missing_evidence = [
        MissingEvidenceItem(
            description="Documented human-oversight override mechanism for HR managers.",
            severity=Severity.HIGH, blocks_verdict=False,
            suggested_questions=[
                "Can a human reviewer override the AI ranking?",
                "Is there a written protocol for that override?",
            ]),
        MissingEvidenceItem(
            description="Appeal process for rejected applicants.",
            severity=Severity.MEDIUM, blocks_verdict=False,
            suggested_questions=["Can rejected candidates appeal?"]),
        MissingEvidenceItem(
            description="Data governance policy (training data sources, bias testing).",
            severity=Severity.MEDIUM, blocks_verdict=False,
            suggested_questions=["What data was the model trained on?",
                                 "Has the model been tested for bias across protected groups?"]),
    ]

    governance_checklist = [
        ChecklistItem(item="Quality management system", applies=True,
                      ai_act_reference="Art. 17", evidence_codes=[]),
        ChecklistItem(item="Fundamental rights impact assessment (FRIA)", applies=True,
                      ai_act_reference="Art. 27", evidence_codes=[]),
        ChecklistItem(item="Transparency measures for affected applicants", applies=True,
                      ai_act_reference="Art. 13"),
        ChecklistItem(item="Documented human oversight protocol", applies=True,
                      ai_act_reference="Art. 14",
                      note="Currently undocumented — see OBJ-01."),
        ChecklistItem(item="Lifecycle logging (10-year retention)", applies=True,
                      ai_act_reference="Art. 12"),
        ChecklistItem(item="EU database registration", applies=True,
                      ai_act_reference="Art. 71"),
    ]

    follow_up_questions = [
        "Can HR managers override the AI's ranking? If yes, is the override process documented?",
        "Is there an appeal process for applicants who feel they were unfairly ranked?",
        "What data was the ranking model trained on, and has it been tested for bias?",
    ]

    agent_activity = [
        AgentActivity(agent=AgentName.DETECTIVE, action="Extracting facts from vendor and internal docs",
                      status=AgentStatus.COMPLETED,
                      started_at=t0, completed_at=t0 + timedelta(seconds=2),
                      output_summary="7 facts extracted across 7 categories."),
        AgentActivity(agent=AgentName.LEGAL_CLERK, action="Retrieving relevant AI Act passages",
                      status=AgentStatus.COMPLETED,
                      started_at=t0 + timedelta(seconds=2), completed_at=t0 + timedelta(seconds=4),
                      output_summary="Annex III §4, Art 6/14/27 retrieved."),
        AgentActivity(agent=AgentName.PROSECUTOR, action="Raising risk allegations",
                      status=AgentStatus.COMPLETED,
                      started_at=t0 + timedelta(seconds=4), completed_at=t0 + timedelta(seconds=7),
                      output_summary="2 allegations of POTENTIAL_HIGH_RISK."),
        AgentActivity(agent=AgentName.DEFENSE, action="Checking exemptions and mitigations",
                      status=AgentStatus.COMPLETED,
                      started_at=t0 + timedelta(seconds=7), completed_at=t0 + timedelta(seconds=9),
                      output_summary="1 defense (human oversight, requires documentation)."),
        AgentActivity(agent=AgentName.CRITIQUE, action="Reviewing claims for weak evidence",
                      status=AgentStatus.COMPLETED,
                      started_at=t0 + timedelta(seconds=9), completed_at=t0 + timedelta(seconds=11),
                      output_summary="1 OBJECTION raised against DEF-01."),
        AgentActivity(agent=AgentName.JUDGE, action="Issuing preliminary verdict",
                      status=AgentStatus.COMPLETED,
                      started_at=t0 + timedelta(seconds=11), completed_at=t0 + timedelta(seconds=14),
                      output_summary="POTENTIAL_HIGH_RISK · Confidence 5/10 (Medium)."),
    ]

    return CaseFile(
        case_id="case_a_demo",
        status=CaseStatus.VERDICT_READY,
        documents=documents,
        facts=facts,
        refs=refs,
        assumptions=assumptions,
        rule_firings=rule_firings,
        allegations=allegations,
        defenses=defenses,
        objections=objections,
        verdict=verdict,
        missing_evidence=missing_evidence,
        governance_checklist=governance_checklist,
        follow_up_questions=follow_up_questions,
        agent_activity=agent_activity,
        chat_history=[],
    )


# =========================================================== Case B

def make_mock_case_b() -> CaseFile:
    """§7.2 — MINIMAL_RISK, HIGH confidence, no high-risk rules fired."""
    t0 = datetime.now()

    documents = [
        Document(doc_id="doc_b1", filename="forecaster_spec.md", mime_type="text/markdown",
                 content=("StockGlance is an internal inventory-forecasting tool for the "
                          "logistics team. It predicts weekly stock needs from 3 years of "
                          "historical sales data. No personal data is used. The system "
                          "produces forecasts only; humans place all purchase orders.")),
        Document(doc_id="doc_b2", filename="data_inventory.md", mime_type="text/markdown",
                 content=("Inputs: SKU-level weekly sales, supplier lead-times, seasonality. "
                          "No PII, no customer data, no employee data. The forecast is advisory; "
                          "it does not make decisions about people.")),
    ]

    facts = [
        Evidence(code="E-01", source_doc_id="doc_b1",
                 text="Forecasts weekly inventory needs for a logistics team.",
                 category=EvidenceCategory.PURPOSE, relevance=Severity.HIGH),
        Evidence(code="E-02", source_doc_id="doc_b1",
                 text="Internal logistics use case.",
                 structured_value=Sector.LOGISTICS.value,
                 category=EvidenceCategory.SECTOR, relevance=Severity.HIGH),
        Evidence(code="E-03", source_doc_id="doc_b1",
                 text="Output is a weekly stock-need forecast.",
                 structured_value=OutputType.FORECAST.value,
                 category=EvidenceCategory.OUTPUT, relevance=Severity.HIGH),
        Evidence(code="E-04", source_doc_id="doc_b2",
                 text="No personal data, no individuals are affected by the forecast.",
                 category=EvidenceCategory.AFFECTED_PERSONS, relevance=Severity.LOW),
        Evidence(code="E-05", source_doc_id="doc_b2",
                 text="Forecast is advisory; humans place all purchase orders.",
                 category=EvidenceCategory.DECISION_IMPACT, relevance=Severity.HIGH),
        Evidence(code="E-06", source_doc_id="doc_b1",
                 text="No general-purpose AI model is used; classical time-series methods.",
                 structured_value="false",
                 category=EvidenceCategory.GPAI_USAGE, relevance=Severity.LOW),
    ]

    refs = [
        Reference(code="R-Art-6", article_no="6",
                  title="Classification rules for high-risk AI systems",
                  snippet="An AI system shall be considered high-risk only where it is listed in Annex III…",
                  full_text=("An AI system shall be considered high-risk only where it is listed in Annex III "
                             "or used as a safety component of a product covered by Annex I."),
                  source_type=SourceType.LEGISLATION, source_label="EU AI Act 2024/1689"),
        Reference(code="R-Recital-53", article_no="Recital-53",
                  title="Minimal-risk systems",
                  snippet="The vast majority of AI systems currently used in the Union pose minimal or no risk…",
                  full_text=("The vast majority of AI systems currently used in the Union pose minimal or no risk "
                             "and may contribute to important societal and economic benefits."),
                  source_type=SourceType.LEGISLATION, source_label="EU AI Act 2024/1689"),
    ]

    rule_firings = [
        RuleFiring(rule_id="R-HIRE-001", description="Employment-related ranking or screening",
                   fired=False,
                   when_conditions={"sector": "employment"},
                   evaluated_against={"sector": "logistics"},
                   then_actions={},
                   supporting_evidence_codes=["E-02"], maps_to_refs=[],
                   yaml_source=_YAML_HIRE),
        RuleFiring(rule_id="R-OVERSIGHT-001", description="Missing human oversight evidence",
                   fired=False,
                   when_conditions={"human_oversight": "unverified"},
                   evaluated_against={"human_oversight": "not_required"},
                   then_actions={},
                   supporting_evidence_codes=["E-05"], maps_to_refs=[],
                   yaml_source=_YAML_OVERSIGHT),
        RuleFiring(rule_id="R-GPAI-001", description="Use of general-purpose AI model",
                   fired=False,
                   when_conditions={"gpai_usage": True},
                   evaluated_against={"gpai_usage": "false"},
                   then_actions={},
                   supporting_evidence_codes=["E-06"], maps_to_refs=[],
                   yaml_source=_YAML_GPAI),
        RuleFiring(rule_id="R-CHAT-001", description="AI system interacting directly with humans",
                   fired=False,
                   when_conditions={"deployment_context": ["chatbot", "direct_user_interaction"]},
                   evaluated_against={"deployment_context": "internal_forecaster"},
                   then_actions={},
                   supporting_evidence_codes=[], maps_to_refs=[],
                   yaml_source=_YAML_CHAT),
    ]

    verdict = Verdict(
        tier=RiskTier.MINIMAL_RISK,
        confidence_score=8,
        confidence_label=ConfidenceLabel.HIGH,
        reasoning_trail=(
            "The system performs advisory inventory forecasting for an internal "
            "logistics team using non-personal data. It does not fall under "
            "Annex III, does not interact with affected persons, and does not "
            "make decisions about individuals. No high-risk rules fired. "
            "GDPR and other sectoral laws may still apply if scope changes."
        ),
    )

    missing_evidence = [
        MissingEvidenceItem(
            description="Reassessment trigger if the system is later used for staffing or decisions about people.",
            severity=Severity.LOW, blocks_verdict=False,
            suggested_questions=["Will the system ever be applied to workforce planning?"]),
    ]

    governance_checklist = [
        ChecklistItem(item="Document scope; reassess if expanded to people-affecting decisions",
                      applies=True, ai_act_reference="Art. 6"),
    ]

    agent_activity = [
        AgentActivity(agent=AgentName.DETECTIVE, action="Extracting facts from spec and data inventory",
                      status=AgentStatus.COMPLETED,
                      started_at=t0, completed_at=t0 + timedelta(seconds=2),
                      output_summary="6 facts; no affected persons, no PII."),
        AgentActivity(agent=AgentName.LEGAL_CLERK, action="Retrieving AI Act references",
                      status=AgentStatus.COMPLETED,
                      started_at=t0 + timedelta(seconds=2), completed_at=t0 + timedelta(seconds=4),
                      output_summary="Art 6 and Recital 53 retrieved."),
        AgentActivity(agent=AgentName.PROSECUTOR, action="Checking for risk allegations",
                      status=AgentStatus.COMPLETED,
                      started_at=t0 + timedelta(seconds=4), completed_at=t0 + timedelta(seconds=5),
                      output_summary="No high-risk allegations."),
        AgentActivity(agent=AgentName.DEFENSE, action="Looking for applicable exemptions",
                      status=AgentStatus.SKIPPED,
                      started_at=t0 + timedelta(seconds=5), completed_at=t0 + timedelta(seconds=5, milliseconds=200),
                      output_summary="No defense needed at minimal-risk tier."),
        AgentActivity(agent=AgentName.CRITIQUE, action="Reviewing for weak claims",
                      status=AgentStatus.COMPLETED,
                      started_at=t0 + timedelta(seconds=6), completed_at=t0 + timedelta(seconds=7),
                      output_summary="No objections raised."),
        AgentActivity(agent=AgentName.JUDGE, action="Issuing preliminary verdict",
                      status=AgentStatus.COMPLETED,
                      started_at=t0 + timedelta(seconds=7), completed_at=t0 + timedelta(seconds=9),
                      output_summary="MINIMAL_RISK · Confidence 8/10 (High)."),
    ]

    return CaseFile(
        case_id="case_b_demo",
        status=CaseStatus.VERDICT_READY,
        documents=documents,
        facts=facts,
        refs=refs,
        rule_firings=rule_firings,
        verdict=verdict,
        missing_evidence=missing_evidence,
        governance_checklist=governance_checklist,
        agent_activity=agent_activity,
    )


# =========================================================== chat sim

def simulate_chat_response(case: CaseFile, user_text: str) -> CaseFile:
    """Stub for handle_chat — bumps confidence when override/appeal is mentioned.

    Backend (Person A) will replace this with the real Judge re-evaluation loop.
    """
    user_turn = ChatTurn(role="user", text=user_text)

    lowered = user_text.lower()
    triggered: list[str] = []
    response_text = (
        "Thank you. I've noted that and re-evaluated the case. "
        "Nothing changed materially — please provide more specifics if available."
    )

    # Detect "Case A-like" by tier + presence of the canonical objection.
    is_case_a_like = (
        case.verdict is not None
        and case.verdict.tier == RiskTier.POTENTIAL_HIGH_RISK
        and any(o.objection_id == "OBJ-01" for o in case.objections)
    )

    if is_case_a_like and case.verdict and ("override" in lowered or "appeal" in lowered):
        new_score = min(10, case.verdict.confidence_score + 3)
        if new_score <= 3:
            new_label = ConfidenceLabel.LOW
        elif new_score <= 6:
            new_label = ConfidenceLabel.MEDIUM
        else:
            new_label = ConfidenceLabel.HIGH
        case.verdict = Verdict(
            tier=case.verdict.tier,
            confidence_score=new_score,
            confidence_label=new_label,
            reasoning_trail=case.verdict.reasoning_trail + (
                " Update: user confirmed HR managers can override the ranking "
                "and applicants can appeal; oversight evidence strengthened."
            ),
            caveats=case.verdict.caveats,
        )
        # Resolve the matching objection.
        for ob in case.objections:
            if ob.objection_id == "OBJ-01":
                ob.resolution = "Withdrawn — user confirmed documented override and appeal path."
                triggered.append(ob.objection_id)
        # Drop the two resolved missing-evidence items by description match.
        keep: list = []
        for m in case.missing_evidence:
            if any(k in m.description.lower() for k in ("override", "appeal")):
                triggered.append(m.description)
                continue
            keep.append(m)
        case.missing_evidence = keep
        triggered.append("verdict.confidence_score")
        response_text = (
            f"Noted — override mechanism and appeal process confirmed. "
            f"Confidence raised to {new_label.value} ({new_score}/10). "
            f"Two missing-evidence items resolved. Objection OBJ-01 withdrawn."
        )
    elif "gpai" in lowered:
        response_text = (
            "Acknowledged — no GPAI usage. The R-GPAI-001 rule already shows "
            "fired=False, so no change to the verdict."
        )

    judge_turn = ChatTurn(role="judge", text=response_text, triggered_updates=triggered)

    case.chat_history.append(user_turn)
    case.chat_history.append(judge_turn)
    case.status = CaseStatus.VERDICT_READY
    return case
