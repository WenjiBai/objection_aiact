// Mock CaseFiles ported from shared/mock.py.
// Used in place of run_courtroom() / handle_chat() in this static React UI.

const YAML_HIRE = `- id: R-HIRE-001
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
`;

const YAML_OVERSIGHT = `- id: R-OVERSIGHT-001
  description: Missing human oversight evidence
  when:
    human_oversight: unverified
  then:
    require_evidence: true
    objection_target: oversight_claim
  maps_to_refs: [R-Art-14]
  severity: medium
`;

const YAML_GPAI = `- id: R-GPAI-001
  description: Use of general-purpose AI model
  when:
    gpai_usage: true
  then:
    trigger: gpai_responsibility_chain_analysis
  maps_to_refs: [R-Art-51]
  severity: medium
`;

const YAML_CHAT = `- id: R-CHAT-001
  description: AI system interacting directly with humans
  when:
    deployment_context: [chatbot, direct_user_interaction]
  then:
    transparency_obligation: true
    basis: "AI Act Article 50"
  maps_to_refs: [R-Art-50]
  severity: low
`;

function nowOffset(seconds) {
  return new Date(Date.now() + seconds * 1000).toISOString();
}

export function makeCaseA() {
  return {
    case_id: "case_a_demo",
    status: "verdict_ready",
    documents: [
      {
        doc_id: "doc_a1",
        filename: "vendor_whitepaper.md",
        mime_type: "text/markdown",
        content:
          "CV-Sage is an AI-powered candidate screening platform. It ingests CVs, parses interview notes, and ranks job applicants for HR managers...",
      },
      {
        doc_id: "doc_a2",
        filename: "internal_process_notes.md",
        mime_type: "text/markdown",
        content:
          "HR managers receive the ranked list. Override mechanism not documented. No formal appeal process.",
      },
    ],
    facts: [
      { code: "E-01", source_doc_id: "doc_a1", text: "System screens CVs and ranks job applicants for HR managers.", category: "purpose", relevance: "high" },
      { code: "E-02", source_doc_id: "doc_a1", text: "Use case is employment-related (hiring).", structured_value: "employment", category: "sector", relevance: "high" },
      { code: "E-03", source_doc_id: "doc_a1", text: "Output is a ranked list of candidates.", structured_value: "ranking", category: "output", relevance: "high" },
      { code: "E-04", source_doc_id: "doc_a1", text: "Affected persons: job applicants.", category: "affected_persons", relevance: "high" },
      { code: "E-05", source_doc_id: "doc_a2", text: "Vendor claims human oversight, but override mechanism not documented.", category: "human_oversight", relevance: "medium" },
      { code: "E-06", source_doc_id: "doc_a1", text: "No GPAI model mentioned in uploaded docs.", structured_value: "unknown", category: "gpai_usage", relevance: "low" },
      { code: "E-07", source_doc_id: "doc_a2", text: "Ranking influences which applicants advance to interview.", category: "decision_impact", relevance: "high" },
    ],
    refs: [
      { code: "R-Annex-III-4", article_no: "Annex-III-4", title: "Employment, workers management and access to self-employment", snippet: "AI systems intended to be used for the recruitment or selection of natural persons…", source_label: "EU AI Act 2024/1689", source_type: "legislation" },
      { code: "R-Art-6", article_no: "6", title: "Classification rules for high-risk AI systems", snippet: "An AI system shall be considered high-risk where it is listed in Annex III…", source_label: "EU AI Act 2024/1689", source_type: "legislation" },
      { code: "R-Art-14", article_no: "14", title: "Human oversight", snippet: "High-risk AI systems shall be designed and developed so they can be effectively overseen by natural persons…", source_label: "EU AI Act 2024/1689", source_type: "legislation" },
      { code: "R-Art-27", article_no: "27", title: "Fundamental rights impact assessment for high-risk AI systems", snippet: "Deployers shall perform an assessment of the impact on fundamental rights…", source_label: "EU AI Act 2024/1689", source_type: "legislation" },
    ],
    assumptions: [
      { code: "A-01", text: "System acts as a deployer-facing tool used in EU employment context.", reasoning: "Vendor docs describe an HR-facing screening workflow but do not state jurisdiction.", needs_confirmation: true },
      { code: "A-02", text: "No GPAI base model is integrated.", reasoning: "No GPAI provider is named in vendor materials.", needs_confirmation: true },
    ],
    rule_firings: [
      {
        rule_id: "R-HIRE-001", description: "Employment-related ranking or screening", fired: true,
        when_conditions: { sector: "employment", output: ["ranking", "screening", "recommendation", "scoring"], affected_persons: ["job_applicants", "workers"] },
        evaluated_against: { sector: "employment", output: "ranking", affected_persons: "job_applicants" },
        then_actions: { preliminary_tier: "potential_high_risk", high_risk_candidate: true, basis: "AI Act Annex III, employment context" },
        supporting_evidence_codes: ["E-02", "E-03", "E-04"],
        maps_to_refs: ["R-Annex-III-4", "R-Art-6"],
        yaml_source: YAML_HIRE,
      },
      {
        rule_id: "R-OVERSIGHT-001", description: "Missing human oversight evidence", fired: true,
        when_conditions: { human_oversight: "unverified" },
        evaluated_against: { human_oversight: "unverified" },
        then_actions: { require_evidence: true, objection_target: "oversight_claim" },
        supporting_evidence_codes: ["E-05"],
        maps_to_refs: ["R-Art-14"],
        yaml_source: YAML_OVERSIGHT,
      },
      {
        rule_id: "R-GPAI-001", description: "Use of general-purpose AI model", fired: false,
        when_conditions: { gpai_usage: true },
        evaluated_against: { gpai_usage: "unknown" },
        then_actions: {},
        supporting_evidence_codes: ["E-06"],
        maps_to_refs: [],
        yaml_source: YAML_GPAI,
      },
      {
        rule_id: "R-CHAT-001", description: "AI system interacting directly with humans", fired: false,
        when_conditions: { deployment_context: ["chatbot", "direct_user_interaction"] },
        evaluated_against: { deployment_context: "internal_hr_tool" },
        then_actions: {},
        supporting_evidence_codes: [],
        maps_to_refs: [],
        yaml_source: YAML_CHAT,
      },
    ],
    allegations: [
      { allegation_id: "ALL-01", tier: "potential_high_risk", claim: "Employment-related screening of applicants falls under Annex III §4.", basis_evidence_codes: ["E-02", "E-03", "E-04"], basis_ref_codes: ["R-Annex-III-4", "R-Art-6"], strength: "high" },
      { allegation_id: "ALL-02", tier: "potential_high_risk", claim: "Human oversight is mentioned but unverified; Article 14 obligations may not be met.", basis_evidence_codes: ["E-05"], basis_ref_codes: ["R-Art-14"], strength: "medium" },
    ],
    defenses: [
      { defense_id: "DEF-01", targets_allegation_id: "ALL-02", type: "human_oversight", claim: "Vendor states HR managers review top candidates before any hiring decision.", basis_evidence_codes: ["E-05"], basis_ref_codes: ["R-Art-14"], requires_documentation: true },
    ],
    objections: [
      {
        objection_id: "OBJ-01",
        target_type: "defense", target_id: "DEF-01",
        reason: "OBJECTION! The 'human oversight' defense is unsupported — override mechanism is not documented and no appeal process exists for applicants.",
        severity: "high",
        challenging_evidence_codes: ["E-05"],
        resolution: null,
      },
    ],
    verdict: {
      tier: "potential_high_risk",
      confidence_score: 5,
      confidence_label: "medium",
      reasoning_trail:
        "The use case appears to involve employment-related AI that ranks job applicants (Annex III §4). Human oversight is claimed but neither the override mechanism nor an appeal process is documented, leaving Article 14 obligations unverified. Confidence is medium pending evidence of the oversight protocol.",
    },
    missing_evidence: [
      { description: "Documented human-oversight override mechanism for HR managers.", severity: "high", blocks_verdict: false, suggested_questions: ["Can a human reviewer override the AI ranking?", "Is there a written protocol for that override?"] },
      { description: "Appeal process for rejected applicants.", severity: "medium", blocks_verdict: false, suggested_questions: ["Can rejected candidates appeal?"] },
      { description: "Data governance policy (training data sources, bias testing).", severity: "medium", blocks_verdict: false, suggested_questions: ["What data was the model trained on?", "Has the model been tested for bias across protected groups?"] },
    ],
    governance_checklist: [
      { item: "Quality management system", applies: true, ai_act_reference: "Art. 17" },
      { item: "Fundamental rights impact assessment (FRIA)", applies: true, ai_act_reference: "Art. 27" },
      { item: "Transparency measures for affected applicants", applies: true, ai_act_reference: "Art. 13" },
      { item: "Documented human oversight protocol", applies: true, ai_act_reference: "Art. 14", note: "Currently undocumented — see OBJ-01." },
      { item: "Lifecycle logging (10-year retention)", applies: true, ai_act_reference: "Art. 12" },
      { item: "EU database registration", applies: true, ai_act_reference: "Art. 71" },
    ],
    follow_up_questions: [
      "Can HR managers override the AI's ranking? If yes, is the override process documented?",
      "Is there an appeal process for applicants who feel they were unfairly ranked?",
      "What data was the ranking model trained on, and has it been tested for bias?",
    ],
    agent_activity: [
      { agent: "detective", action: "Extracting facts from vendor and internal docs", status: "completed", started_at: nowOffset(0), completed_at: nowOffset(2), output_summary: "7 facts extracted across 7 categories." },
      { agent: "legal_clerk", action: "Retrieving relevant AI Act passages", status: "completed", started_at: nowOffset(2), completed_at: nowOffset(4), output_summary: "Annex III §4, Art 6/14/27 retrieved." },
      { agent: "prosecutor", action: "Raising risk allegations", status: "completed", started_at: nowOffset(4), completed_at: nowOffset(7), output_summary: "2 allegations of POTENTIAL_HIGH_RISK." },
      { agent: "defense", action: "Checking exemptions and mitigations", status: "completed", started_at: nowOffset(7), completed_at: nowOffset(9), output_summary: "1 defense (human oversight, requires documentation)." },
      { agent: "critique", action: "Reviewing claims for weak evidence", status: "completed", started_at: nowOffset(9), completed_at: nowOffset(11), output_summary: "1 OBJECTION raised against DEF-01." },
      { agent: "judge", action: "Issuing preliminary verdict", status: "completed", started_at: nowOffset(11), completed_at: nowOffset(14), output_summary: "POTENTIAL_HIGH_RISK · Confidence 5/10 (Medium)." },
    ],
    chat_history: [],
  };
}

export function makeCaseB() {
  return {
    case_id: "case_b_demo",
    status: "verdict_ready",
    documents: [
      { doc_id: "doc_b1", filename: "forecaster_spec.md", mime_type: "text/markdown", content: "StockGlance is an internal inventory-forecasting tool..." },
      { doc_id: "doc_b2", filename: "data_inventory.md", mime_type: "text/markdown", content: "Inputs: SKU-level weekly sales, supplier lead-times, seasonality. No PII." },
    ],
    facts: [
      { code: "E-01", source_doc_id: "doc_b1", text: "Forecasts weekly inventory needs for a logistics team.", category: "purpose", relevance: "high" },
      { code: "E-02", source_doc_id: "doc_b1", text: "Internal logistics use case.", structured_value: "logistics", category: "sector", relevance: "high" },
      { code: "E-03", source_doc_id: "doc_b1", text: "Output is a weekly stock-need forecast.", structured_value: "forecast", category: "output", relevance: "high" },
      { code: "E-04", source_doc_id: "doc_b2", text: "No personal data, no individuals are affected by the forecast.", category: "affected_persons", relevance: "low" },
      { code: "E-05", source_doc_id: "doc_b2", text: "Forecast is advisory; humans place all purchase orders.", category: "decision_impact", relevance: "high" },
      { code: "E-06", source_doc_id: "doc_b1", text: "No general-purpose AI model is used; classical time-series methods.", structured_value: "false", category: "gpai_usage", relevance: "low" },
    ],
    refs: [
      { code: "R-Art-6", article_no: "6", title: "Classification rules for high-risk AI systems", snippet: "An AI system shall be considered high-risk only where it is listed in Annex III…", source_label: "EU AI Act 2024/1689", source_type: "legislation" },
      { code: "R-Recital-53", article_no: "Recital-53", title: "Minimal-risk systems", snippet: "The vast majority of AI systems currently used in the Union pose minimal or no risk…", source_label: "EU AI Act 2024/1689", source_type: "legislation" },
    ],
    assumptions: [],
    rule_firings: [
      { rule_id: "R-HIRE-001", description: "Employment-related ranking or screening", fired: false, when_conditions: { sector: "employment" }, evaluated_against: { sector: "logistics" }, then_actions: {}, supporting_evidence_codes: ["E-02"], maps_to_refs: [], yaml_source: YAML_HIRE },
      { rule_id: "R-OVERSIGHT-001", description: "Missing human oversight evidence", fired: false, when_conditions: { human_oversight: "unverified" }, evaluated_against: { human_oversight: "not_required" }, then_actions: {}, supporting_evidence_codes: ["E-05"], maps_to_refs: [], yaml_source: YAML_OVERSIGHT },
      { rule_id: "R-GPAI-001", description: "Use of general-purpose AI model", fired: false, when_conditions: { gpai_usage: true }, evaluated_against: { gpai_usage: "false" }, then_actions: {}, supporting_evidence_codes: ["E-06"], maps_to_refs: [], yaml_source: YAML_GPAI },
      { rule_id: "R-CHAT-001", description: "AI system interacting directly with humans", fired: false, when_conditions: { deployment_context: ["chatbot", "direct_user_interaction"] }, evaluated_against: { deployment_context: "internal_forecaster" }, then_actions: {}, supporting_evidence_codes: [], maps_to_refs: [], yaml_source: YAML_CHAT },
    ],
    allegations: [],
    defenses: [],
    objections: [],
    verdict: {
      tier: "minimal_risk",
      confidence_score: 8,
      confidence_label: "high",
      reasoning_trail:
        "The system performs advisory inventory forecasting for an internal logistics team using non-personal data. It does not fall under Annex III, does not interact with affected persons, and does not make decisions about individuals. No high-risk rules fired. GDPR and other sectoral laws may still apply if scope changes.",
    },
    missing_evidence: [
      { description: "Reassessment trigger if the system is later used for staffing or decisions about people.", severity: "low", blocks_verdict: false, suggested_questions: ["Will the system ever be applied to workforce planning?"] },
    ],
    governance_checklist: [
      { item: "Document scope; reassess if expanded to people-affecting decisions", applies: true, ai_act_reference: "Art. 6" },
    ],
    follow_up_questions: [],
    agent_activity: [
      { agent: "detective", action: "Extracting facts from spec and data inventory", status: "completed", started_at: nowOffset(0), completed_at: nowOffset(2), output_summary: "6 facts; no affected persons, no PII." },
      { agent: "legal_clerk", action: "Retrieving AI Act references", status: "completed", started_at: nowOffset(2), completed_at: nowOffset(4), output_summary: "Art 6 and Recital 53 retrieved." },
      { agent: "prosecutor", action: "Checking for risk allegations", status: "completed", started_at: nowOffset(4), completed_at: nowOffset(5), output_summary: "No high-risk allegations." },
      { agent: "defense", action: "Looking for applicable exemptions", status: "skipped", started_at: nowOffset(5), completed_at: nowOffset(5.2), output_summary: "No defense needed at minimal-risk tier." },
      { agent: "critique", action: "Reviewing for weak claims", status: "completed", started_at: nowOffset(6), completed_at: nowOffset(7), output_summary: "No objections raised." },
      { agent: "judge", action: "Issuing preliminary verdict", status: "completed", started_at: nowOffset(7), completed_at: nowOffset(9), output_summary: "MINIMAL_RISK · Confidence 8/10 (High)." },
    ],
    chat_history: [],
  };
}

// Lightweight stub of shared/mock.py::simulate_chat_response.
export function simulateChat(caseFile, userText) {
  const next = structuredClone(caseFile);
  const triggered = [];
  const lowered = userText.toLowerCase();

  next.chat_history.push({ role: "user", text: userText });

  let responseText =
    "Thank you. I've noted that and re-evaluated the case. Nothing changed materially — please provide more specifics if available.";

  const isCaseALike =
    next.verdict?.tier === "potential_high_risk" &&
    next.objections.some((o) => o.objection_id === "OBJ-01");

  if (isCaseALike && (lowered.includes("override") || lowered.includes("appeal"))) {
    const newScore = Math.min(10, next.verdict.confidence_score + 3);
    const newLabel = newScore <= 3 ? "low" : newScore <= 6 ? "medium" : "high";
    next.verdict = {
      ...next.verdict,
      confidence_score: newScore,
      confidence_label: newLabel,
      reasoning_trail:
        next.verdict.reasoning_trail +
        " Update: user confirmed HR managers can override the ranking and applicants can appeal; oversight evidence strengthened.",
    };
    next.objections = next.objections.map((o) =>
      o.objection_id === "OBJ-01"
        ? { ...o, resolution: "Withdrawn — user confirmed documented override and appeal path." }
        : o
    );
    triggered.push("OBJ-01");
    next.missing_evidence = next.missing_evidence.filter((m) => {
      const d = m.description.toLowerCase();
      if (d.includes("override") || d.includes("appeal")) {
        triggered.push(m.description);
        return false;
      }
      return true;
    });
    triggered.push("verdict.confidence_score");
    responseText = `Noted — override mechanism and appeal process confirmed. Confidence raised to ${newLabel} (${newScore}/10). Two missing-evidence items resolved. Objection OBJ-01 withdrawn.`;
  } else if (lowered.includes("gpai")) {
    responseText = "Acknowledged — no GPAI usage. The R-GPAI-001 rule already shows fired=False, so no change to the verdict.";
  }

  next.chat_history.push({
    role: "judge",
    text: responseText,
    triggered_updates: triggered,
  });
  return next;
}
