import React from "react";

// ---------------------------------------------------- tier / status maps
const TIER_COLOR = {
  prohibited: "#EF4444",
  high_risk: "#EF4444",
  potential_high_risk: "#F59E0B",
  limited_risk: "#F59E0B",
  minimal_risk: "#10B981",
  unknown: "#6B7280",
};
const TIER_SOFT = {
  prohibited: "rgba(239,68,68,0.18)",
  high_risk: "rgba(239,68,68,0.18)",
  potential_high_risk: "rgba(245,158,11,0.20)",
  limited_risk: "rgba(245,158,11,0.18)",
  minimal_risk: "rgba(16,185,129,0.18)",
  unknown: "rgba(107,114,128,0.18)",
};
const TIER_LABEL = {
  prohibited: "PROHIBITED",
  high_risk: "HIGH RISK",
  potential_high_risk: "POTENTIAL HIGH RISK",
  limited_risk: "LIMITED RISK",
  minimal_risk: "MINIMAL RISK",
  unknown: "UNKNOWN",
};

const AGENT_ORDER = ["detective", "legal_clerk", "prosecutor", "defense", "critique", "judge"];
const AGENT_INITIAL = { detective: "D", legal_clerk: "L", prosecutor: "P", defense: "D", critique: "C", judge: "J" };
const AGENT_LABEL = { detective: "Detective", legal_clerk: "Legal Clerk", prosecutor: "Prosecutor", defense: "Defense", critique: "Critique", judge: "Judge" };

const humanize = (s) => (s || "").replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());

const strengthClass = (s) => (s === "high" ? "act-strong" : s === "medium" ? "act-medium" : "act-weak");
const strengthLabel = (s) => (s === "high" ? "Strong" : s === "medium" ? "Medium" : "Confirm");

// ---------------------------------------------------- icons
const SvgIcon = ({ paths, size = 14, stroke = 2 }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth={stroke}
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden="true"
    dangerouslySetInnerHTML={{ __html: paths }}
  />
);

const ICON_WORKFLOW = <SvgIcon paths='<rect x="3" y="3" width="6" height="6" rx="1"/><rect x="15" y="3" width="6" height="6" rx="1"/><rect x="9" y="15" width="6" height="6" rx="1"/><path d="M6 9v3a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V9"/><path d="M12 14v1"/>' />;
const ICON_CLIPBOARD = <SvgIcon paths='<rect x="8" y="2" width="8" height="4" rx="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="M9 12h6"/><path d="M9 16h6"/>' />;
const ICON_CPU = <SvgIcon paths='<rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M9 2v2"/><path d="M15 2v2"/><path d="M9 20v2"/><path d="M15 20v2"/><path d="M2 9h2"/><path d="M2 15h2"/><path d="M20 9h2"/><path d="M20 15h2"/>' />;
const ICON_ALERT = <SvgIcon paths='<path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>' />;
const ICON_CHECK = <SvgIcon paths='<path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>' />;

// ============================================================ Sidebar
export function Sidebar({ mode, setMode, onNewCase, onSearch, onLoadA, onLoadB }) {
  return (
    <aside className="act-sidebar">
      <img className="logo" src="/Objection_AI_ACT.png" alt="OBJECTION! AI ACT" />
      <div className="act-brand-sub">Puts your AI use case on trial.</div>

      <div className="act-btn-row">
        <button
          className={`act-btn ${mode === "dark" ? "primary" : ""}`}
          onClick={() => setMode("dark")}
        >
          🌙 Dark
        </button>
        <button
          className={`act-btn ${mode === "light" ? "primary" : ""}`}
          onClick={() => setMode("light")}
        >
          ☀ Light
        </button>
      </div>

      <div style={{ height: 6 }} />
      <button className="act-btn primary" onClick={onNewCase}>+ New case</button>
      <button className="act-btn" onClick={onSearch}>Search cases</button>

      <div className="act-side-section">Demo cases</div>
      <button className="act-btn" onClick={onLoadA}>● AI hiring screener</button>
      <button className="act-btn" onClick={onLoadB}>● Inventory forecaster</button>
    </aside>
  );
}

// ============================================================ Landing
export function LandingHero() {
  return (
    <div className="act-hero-wrap">
      <div className="act-hero-badge">⚖ OBJECTION! · AI ACT</div>
      <div className="act-hero-title">Put your AI use case on trial.</div>
      <div className="act-hero-sub">
        Six AI agents, thirteen symbolic rules, and a grounded EU AI Act corpus deliver a first-pass risk verdict with citations, uncertainty, and a governance checklist.
      </div>
      <div className="act-trust-row">
        <span className="act-trust-chip"><b>6</b> agents</span>
        <span className="act-trust-chip"><b>13</b> symbolic rules</span>
        <span className="act-trust-chip"><b>68</b> AI Act references</span>
        <span className="act-trust-chip"><b>~12s</b> avg verdict</span>
      </div>
    </div>
  );
}

export function UploadTopbar({ onOpenCorpus, onOpenGuide }) {
  return (
    <div className="act-topbar">
      <div className="act-topbar-title">
        <span className="dot">●</span>
        <span>New case session</span>
      </div>
      <button className="act-btn" onClick={onOpenCorpus}>📚 AI Act corpus</button>
      <button className="act-btn" onClick={onOpenGuide}>❓ Guide</button>
    </div>
  );
}

export function UploadPane({ onRun, isRunning = false, onLoadA, onLoadB }) {
  const [files, setFiles] = React.useState([]);
  const [pasted, setPasted] = React.useState("");
  const [drag, setDrag] = React.useState(false);
  const inputRef = React.useRef(null);

  const canRun = files.length > 0 || pasted.trim().length > 0;

  const handleFiles = (incoming) => {
    setFiles((prev) => [...prev, ...Array.from(incoming)]);
  };

  return (
    <div className="act-center-col">
      <div
        className={`act-dropzone ${drag ? "drag" : ""}`}
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
        onDragLeave={() => setDrag(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDrag(false);
          if (e.dataTransfer.files.length) handleFiles(e.dataTransfer.files);
        }}
      >
        <div className="act-dropzone-title">Drag &amp; drop files here</div>
        <div className="act-dropzone-hint">
          or click to browse · PDF, DOCX, PPTX, TXT, MD
        </div>
        <input
          ref={inputRef}
          type="file"
          multiple
          accept=".pdf,.docx,.pptx,.txt,.md"
          style={{ display: "none" }}
          onChange={(e) => e.target.files && handleFiles(e.target.files)}
        />
        {files.length > 0 && (
          <div className="act-file-list" onClick={(e) => e.stopPropagation()}>
            {files.map((f, i) => (
              <div className="item" key={i}>📄 {f.name}</div>
            ))}
          </div>
        )}
      </div>

      <div className="act-or"><span>or paste use-case description</span></div>

      <textarea
        className="act-textarea"
        rows={4}
        placeholder="e.g. We're building an AI tool that ranks job applicants..."
        value={pasted}
        onChange={(e) => setPasted(e.target.value)}
      />

      <div style={{ height: 10 }} />
      <button
        className="act-btn primary"
        disabled={!canRun || isRunning}
        onClick={() => onRun(files, pasted)}
      >
        ⚖ Open courtroom hearing
      </button>
      {isRunning && <div className="act-run-status">Six agents are deliberating...</div>}

      <div className="act-quickstart">
        <span className="act-quickstart-chip">💡 Try a demo case →</span>
      </div>
      <div className="act-demo-row">
        <button className="act-btn" onClick={onLoadA}>👤 AI hiring screener</button>
        <button className="act-btn" onClick={onLoadB}>📦 Inventory forecaster</button>
      </div>
    </div>
  );
}

// ============================================================ Case banner
export function CaseFileSummary({ caseFile }) {
  const v = caseFile.verdict;
  const tier = v?.tier ?? "unknown";
  const firstDoc = caseFile.documents[0]?.filename ?? caseFile.case_id;
  const status = v ? "Preliminary verdict ready" : "Intake";
  const docCount = caseFile.documents.length;
  const tierLabel = TIER_LABEL[tier];
  const tierColor = TIER_COLOR[tier];
  const tierSoft = TIER_SOFT[tier];

  return (
    <div className="act-case-banner">
      <div className="act-case-title">
        <div className="act-case-icon">⚖</div>
        <div style={{ display: "flex", flexDirection: "column", gap: 2, minWidth: 0 }}>
          <span className="filename">{firstDoc}</span>
          <span className="meta">
            {caseFile.case_id} · {docCount} doc{docCount === 1 ? "" : "s"}
          </span>
        </div>
        <span className="act-status-pill">● {status}</span>
      </div>
      <div className="act-case-actions">
        <span
          className="act-tier-pill"
          style={{
            "--tier-color": tierColor,
            "--tier-soft": tierSoft,
            color: tierColor,
            borderColor: tierColor,
            background: tierSoft,
          }}
        >
          <span className="dot" style={{ background: tierColor, boxShadow: `0 0 12px ${tierColor}` }} />
          {tierLabel}
        </span>
      </div>
    </div>
  );
}

// ============================================================ Agent stepper
export function AgentStepper({ caseFile }) {
  const byAgent = Object.fromEntries(caseFile.agent_activity.map((a) => [a.agent, a]));
  return (
    <>
      <div className="act-section-title">
        <span className="icon">{ICON_WORKFLOW}</span>Courtroom workflow
      </div>
      <div className="act-stepper">
        {AGENT_ORDER.map((agent) => {
          const act = byAgent[agent];
          const status = act?.status ?? "pending";
          let duration = "";
          if (act?.started_at && act?.completed_at) {
            const ms = (new Date(act.completed_at) - new Date(act.started_at));
            duration = `${ms.toFixed(0)} ms`;
          } else if (status === "running") {
            duration = "running…";
          }
          return (
            <div className={`act-step ${status}`} key={agent}>
              <div className="step-row">
                <div className="step-dot">{AGENT_INITIAL[agent]}</div>
                <div className="step-name">{AGENT_LABEL[agent]}</div>
              </div>
              <div className="step-action">{act?.action ?? "Awaiting trigger"}</div>
              <div className="step-duration">{duration}</div>
            </div>
          );
        })}
      </div>
    </>
  );
}

// ============================================================ Verdict card
function ConfidenceRing({ score, color, soft }) {
  const clamped = Math.max(0, Math.min(10, score));
  const radius = 36;
  const circumference = 2 * Math.PI * radius;
  const dash = (circumference * clamped) / 10;
  return (
    <div className="act-ring-block">
      <svg className="act-ring" viewBox="0 0 86 86">
        <circle className="track" cx="43" cy="43" r={radius} />
        <circle
          className="fill"
          cx="43"
          cy="43"
          r={radius}
          style={{ stroke: color, filter: `drop-shadow(0 0 6px ${soft})` }}
          strokeDasharray={`${dash.toFixed(2)} ${circumference.toFixed(2)}`}
        />
      </svg>
      <div className="act-ring-center">
        <span className="score">{clamped}</span>
        <span className="out-of">/ 10</span>
      </div>
    </div>
  );
}

export function VerdictCard({ caseFile }) {
  const v = caseFile.verdict;
  if (!v) {
    return <div className="act-empty">No verdict yet — upload documents and run the courtroom.</div>;
  }
  const color = TIER_COLOR[v.tier];
  const soft = TIER_SOFT[v.tier];
  const tierLabel = TIER_LABEL[v.tier];

  const missing = caseFile.missing_evidence.slice(0, 3);
  return (
    <div
      className="act-verdict-card"
      style={{ "--tier-color": color, "--tier-soft": soft }}
    >
      <div className="act-verdict-top">
        <div className="act-verdict-tier">
          <div className="act-label">Preliminary verdict</div>
          <span className="act-tier-pill">
            <span className="dot" />
            {tierLabel}
          </span>
        </div>
        <div className="act-ring-wrap">
          <ConfidenceRing score={v.confidence_score} color={color} soft={soft} />
          <div className="act-ring-info">
            <span className="lbl">Confidence</span>
            <span className="val">{v.confidence_label}</span>
            <span className="lbl" style={{ marginTop: 2 }}>{v.confidence_score} / 10</span>
          </div>
        </div>
      </div>
      <div className="act-reason">{v.reasoning_trail}</div>
      <div className="act-missing">
        <div className="act-missing-title">
          Missing evidence
          <span className="badge">{caseFile.missing_evidence.length}</span>
        </div>
        {missing.length ? (
          missing.map((m, i) => (
            <div className="act-missing-item" key={i}>
              <span className="checkbox" />
              <span>{m.description}</span>
            </div>
          ))
        ) : (
          <div className="act-missing-item ok">
            <span className="checkbox" />
            <span>No missing evidence recorded</span>
          </div>
        )}
      </div>
      <div className="act-guard">
        ⚠ Preliminary assessment only — not legal advice. Human legal review is recommended before deployment.
      </div>
    </div>
  );
}

// ============================================================ Evidence board
export function EvidenceBoard({ caseFile }) {
  const [tab, setTab] = React.useState("facts");
  const nE = caseFile.facts.length;
  const nR = caseFile.refs.length;
  const nA = caseFile.assumptions.length;

  let cards = [];
  if (tab === "facts") {
    cards = caseFile.facts.map((e) => (
      <div className="act-ev-card" key={e.code}>
        <div className="act-ev-head">
          <span className="act-code e">{e.code}</span>
          <span className={`act-strength ${strengthClass(e.relevance)}`}>
            {strengthLabel(e.relevance)}
          </span>
        </div>
        <div className="act-ev-body">{e.text}</div>
        <div className="act-ev-meta">
          <span>📄 {e.source_doc_id}</span>
          <span className="sep">·</span>
          <span>{humanize(e.category)}</span>
        </div>
      </div>
    ));
  } else if (tab === "refs") {
    cards = caseFile.refs.map((r) => (
      <div className="act-ev-card" key={r.code}>
        <div className="act-ev-head">
          <span className="act-code r">{r.code}</span>
          <span className="act-strength act-strong">Legal</span>
        </div>
        <div className="act-ev-body">{r.snippet || r.title}</div>
        <div className="act-ev-meta">
          <span>⚖ {r.source_label}</span>
          <span className="sep">·</span>
          <span>{r.article_no}</span>
        </div>
      </div>
    ));
  } else {
    cards = caseFile.assumptions.map((a) => {
      const cls = a.needs_confirmation ? "act-weak" : "act-medium";
      const label = a.needs_confirmation ? "Confirm" : "Medium";
      return (
        <div className="act-ev-card" key={a.code}>
          <div className="act-ev-head">
            <span className="act-code a">{a.code}</span>
            <span className={`act-strength ${cls}`}>{label}</span>
          </div>
          <div className="act-ev-body">{a.text}</div>
          <div className="act-ev-meta">
            <span>🧠 {a.reasoning.slice(0, 80)}{a.reasoning.length > 80 ? "…" : ""}</span>
          </div>
        </div>
      );
    });
  }

  return (
    <>
      <div className="act-section-title">
        <span className="icon">{ICON_CLIPBOARD}</span>Evidence board
        <span className="count">· {nE + nR + nA} items</span>
      </div>
      <div className="act-tabs">
        <button className={`act-tab ${tab === "facts" ? "active" : ""}`} onClick={() => setTab("facts")}>
          Facts · {nE}
        </button>
        <button className={`act-tab ${tab === "refs" ? "active" : ""}`} onClick={() => setTab("refs")}>
          References · {nR}
        </button>
        <button className={`act-tab ${tab === "assumptions" ? "active" : ""}`} onClick={() => setTab("assumptions")}>
          Assumptions · {nA}
        </button>
      </div>
      {cards.length ? (
        <div className="act-evidence-grid">{cards}</div>
      ) : (
        <div className="act-empty">No items in this view.</div>
      )}
    </>
  );
}

// ============================================================ Rules
export function SymbolicRulesPanel({ caseFile }) {
  const fired = caseFile.rule_firings.filter((r) => r.fired).length;
  const inactive = caseFile.rule_firings.length - fired;
  return (
    <>
      <div className="act-section-title">
        <span className="icon">{ICON_CPU}</span>Symbolic risk gate
        <span className="count">· deterministic &amp; inspectable</span>
      </div>
      <div className="act-rules-panel">
        <div className="act-rules-head">
          <span>Rule trace</span>
          <span className="summary">
            <span><b>{fired}</b> fired</span>
            <span>·</span>
            <span><b>{inactive}</b> inactive</span>
          </span>
        </div>
        <div className="act-rule-body">
          {caseFile.rule_firings.length === 0 ? (
            <div className="act-empty">No rules evaluated yet.</div>
          ) : (
            caseFile.rule_firings.map((rf) => {
              const cls = rf.fired ? "fired" : "inactive";
              const action = Object.keys(rf.then_actions || {}).length
                ? Object.entries(rf.then_actions).map(([k, v]) => `${k}=${v}`).join(", ")
                : Object.entries(rf.evaluated_against || {}).map(([k, v]) => `${k}=${v}`).join(", ") || rf.description;
              return (
                <div className={`act-rule-row ${cls}`} key={rf.rule_id}>
                  <div className={`act-rule-icon ${cls}`}>{rf.fired ? "✓" : "·"}</div>
                  <span className="act-rule-id">{rf.rule_id}</span>
                  <span className="act-rule-desc">{action}</span>
                  <span className={`act-strength ${rf.fired ? "act-strong" : "act-weak"}`}>
                    {rf.fired ? "Fired" : "Inactive"}
                  </span>
                </div>
              );
            })
          )}
        </div>
      </div>
    </>
  );
}

// ============================================================ Objections
export function ObjectionsSection({ caseFile }) {
  if (caseFile.objections.length === 0) return null;
  const open = caseFile.objections.filter((o) => !o.resolution);
  const closed = caseFile.objections.filter((o) => o.resolution);
  return (
    <>
      <div className="act-section-title">
        <span className="icon">{ICON_ALERT}</span>Critique objections
        <span className="count">· {open.length} open · {closed.length} resolved</span>
      </div>
      {open.map((ob) => {
        const evidence = ob.challenging_evidence_codes?.join(", ") || "weak evidence";
        return (
          <div className="act-obj-card" key={ob.objection_id}>
            <div className="act-obj-header">
              <span className="act-obj-gavel">⚖</span>
              Objection — {ob.target_type} {ob.target_id}
            </div>
            <div className="act-obj-body">{ob.reason}</div>
            <div className="act-obj-action">→ Reclassification review triggered by {evidence}</div>
          </div>
        );
      })}
      {closed.map((ob) => (
        <div className="act-obj-card resolved" key={ob.objection_id}>
          <div className="act-obj-header">
            <span className="act-obj-gavel">✓</span>
            Resolved — {ob.objection_id}
          </div>
          <div className="act-obj-body">{ob.resolution || ob.reason}</div>
        </div>
      ))}
    </>
  );
}

// ============================================================ Governance
export function MissingAndGovernance({ caseFile }) {
  const applies = caseFile.governance_checklist.filter((g) => g.applies).length;
  return (
    <>
      <div className="act-section-title">
        <span className="icon">{ICON_CHECK}</span>Governance checklist
        <span className="count">· {applies} required item{applies === 1 ? "" : "s"}</span>
      </div>
      {caseFile.governance_checklist.length === 0 ? (
        <div className="act-empty">Nothing required at this tier.</div>
      ) : (
        <div className="act-gov-grid">
          {caseFile.governance_checklist.map((g, i) => (
            <div className={`act-gov-item ${g.applies ? "required" : ""}`} key={i}>
              <span className="gov-check" />
              <span className="act-gov-text">
                <span>{g.item}</span>
                {g.ai_act_reference && <span className="act-gov-ref">{g.ai_act_reference}</span>}
              </span>
            </div>
          ))}
        </div>
      )}
    </>
  );
}

// ============================================================ Activity log
const STATUS_ICON = { completed: "✅", running: "⏳", failed: "❌", pending: "⚪", skipped: "⏭️" };

export function AgentActivityTimeline({ caseFile }) {
  if (!caseFile.agent_activity.length) return null;
  return (
    <div className="act-activity-log" style={{ marginTop: 14 }}>
      <details>
        <summary>🕒 Agent activity (detailed log)</summary>
        {caseFile.agent_activity.map((a, i) => {
          let dur = "";
          if (a.started_at && a.completed_at) {
            const ms = new Date(a.completed_at) - new Date(a.started_at);
            dur = ` · ${ms.toFixed(0)} ms`;
          }
          return (
            <div className="row" key={i}>
              <div>
                {STATUS_ICON[a.status] || "·"} <b>{humanize(a.agent)}</b> — {a.action}{dur}
              </div>
              {a.output_summary && <div className="summary">{a.output_summary}</div>}
            </div>
          );
        })}
      </details>
    </div>
  );
}

// ============================================================ Chat
export function ChatSection({ caseFile, onSubmit, disabled = false }) {
  const [draft, setDraft] = React.useState("");

  return (
    <>
      <div className="act-chat-head">
        <div className="act-chat-title">⚖ Cross-examine the verdict</div>
        <span className="act-chat-hint">Add a fact · challenge a claim · answer a follow-up</span>
      </div>

      {caseFile.follow_up_questions?.length > 0 && (
        <div style={{ display: "flex", flexDirection: "column", marginBottom: 10 }}>
          {caseFile.follow_up_questions.slice(0, 4).map((q, i) => (
            <span className="act-followup-chip" key={i}>
              ❓ {q.length > 120 ? q.slice(0, 120) + "…" : q}
            </span>
          ))}
        </div>
      )}

      {caseFile.chat_history.length === 0 ? (
        <div className="act-empty">
          No cross-examination turns yet. Drop a fact below or pick a follow-up.
        </div>
      ) : (
        caseFile.chat_history.map((turn, i) => (
          <div className={`act-chat-msg ${turn.role}`} key={i}>
            <div className="avatar">{turn.role === "user" ? "🧑" : "⚖️"}</div>
            <div>
              <div className="body">{turn.text}</div>
              {turn.triggered_updates?.length > 0 && (
                <div className="updates">
                  Updated: {turn.triggered_updates.map((u) => `\`${u}\``).join(", ")}
                </div>
              )}
            </div>
          </div>
        ))
      )}

      <form
        className="act-form"
        onSubmit={(e) => {
          e.preventDefault();
          if (draft.trim() && !disabled) {
            onSubmit(draft.trim());
            setDraft("");
          }
        }}
      >
        <textarea
          className="act-textarea"
          rows={3}
          placeholder="Answer a follow-up, add a fact, or challenge the verdict..."
          value={draft}
          disabled={disabled}
          onChange={(e) => setDraft(e.target.value)}
        />
        <button className="act-btn primary" type="submit" disabled={disabled}>
          {disabled ? "Judge is reviewing..." : "Submit to judge"}
        </button>
      </form>
    </>
  );
}
