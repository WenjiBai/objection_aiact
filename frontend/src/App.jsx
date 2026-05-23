import React from "react";
import {
  Sidebar,
  LandingHero,
  UploadTopbar,
  UploadPane,
  CaseFileSummary,
  AgentStepper,
  VerdictCard,
  EvidenceBoard,
  SymbolicRulesPanel,
  ObjectionsSection,
  MissingAndGovernance,
  AgentActivityTimeline,
  ChatSection,
} from "./components.jsx";
import { AI_ACT_CORPUS } from "./corpusData.js";
import { makeCaseA, makeCaseB, simulateChat } from "./mock.js";

function CorpusDialog({ onClose }) {
  const [query, setQuery] = React.useState("");
  const normalizedQuery = query.trim().toLowerCase();
  const shown = React.useMemo(() => {
    if (!normalizedQuery) return AI_ACT_CORPUS;
    return AI_ACT_CORPUS.filter((ref) => {
      const haystack = [
        ref.code,
        ref.article_no,
        ref.title,
        ref.snippet,
        ref.full_text,
        ref.source_label,
        ref.source_type,
      ].join(" ").toLowerCase();
      return haystack.includes(normalizedQuery);
    });
  }, [normalizedQuery]);

  return (
    <div className="act-modal-backdrop" role="presentation" onClick={onClose}>
      <div className="act-modal act-corpus-modal" role="dialog" aria-modal="true" aria-labelledby="corpus-title" onClick={(e) => e.stopPropagation()}>
        <div className="act-modal-head">
          <div>
            <h2 id="corpus-title">AI Act corpus</h2>
            <p>{AI_ACT_CORPUS.length} curated chunks from Regulation (EU) 2024/1689 and related guidance.</p>
          </div>
          <button className="act-icon-btn" type="button" aria-label="Close dialog" onClick={onClose}>x</button>
        </div>
        <div className="act-modal-body">
          <input
            className="act-input act-corpus-search"
            type="search"
            placeholder="article number, keyword, or R-code"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            autoFocus
          />
          <div className="act-corpus-count">
            Showing <b>{shown.length}</b> of {AI_ACT_CORPUS.length}
          </div>
          <div className="act-corpus-list">
            {shown.length ? (
              shown.map((ref) => (
                <details className="act-corpus-item" key={ref.code}>
                  <summary>
                    <span className="act-code r">{ref.code}</span>
                    <span className="title">{ref.title}</span>
                  </summary>
                  <div className="act-corpus-meta">
                    Article {ref.article_no} · {ref.source_label} · {ref.source_type}
                  </div>
                  <p>{ref.snippet}</p>
                  <details className="act-full-text">
                    <summary>Full text</summary>
                    <p>{ref.full_text}</p>
                  </details>
                  {ref.url && (
                    <a className="act-source-link" href={ref.url} target="_blank" rel="noreferrer">
                      Open source
                    </a>
                  )}
                </details>
              ))
            ) : (
              <div className="act-empty">No matching references.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function App() {
  const [mode, setMode] = React.useState("dark");
  const [caseFile, setCaseFile] = React.useState(null);
  const [errorToast, setErrorToast] = React.useState(null);
  const [modal, setModal] = React.useState(null);

  React.useEffect(() => {
    document.documentElement.dataset.theme = mode;
  }, [mode]);

  const buildNewCaseFromUploads = (files, pasted) => {
    // The Python backend builds a CaseFile then runs the courtroom. The React
    // demo can't run the LLM pipeline, so we fall back to Case A's mock so the
    // workspace still renders meaningfully when the user clicks "Open hearing".
    // (Real wiring would POST to a FastAPI endpoint here.)
    const mock = makeCaseA();
    if (files.length || pasted.trim()) {
      mock.documents = [
        ...files.map((f, i) => ({
          doc_id: `doc_${(i + 1).toString().padStart(2, "0")}`,
          filename: f.name,
          mime_type: f.type || "text/plain",
          content: "",
        })),
        ...(pasted.trim()
          ? [{
              doc_id: `doc_${(files.length + 1).toString().padStart(2, "0")}`,
              filename: "pasted_use_case.md",
              mime_type: "text/markdown",
              content: pasted.trim(),
            }]
          : []),
      ];
    }
    return mock;
  };

  const handleRun = (files, pasted) => {
    try {
      setCaseFile(buildNewCaseFromUploads(files, pasted));
    } catch (err) {
      setErrorToast(`Could not start the hearing: ${err.message}`);
    }
  };

  const handleChat = (text) => {
    setCaseFile((cur) => (cur ? simulateChat(cur, text) : cur));
  };

  const loadCase = (factory) => {
    setCaseFile(factory());
    setErrorToast(null);
    setModal(null);
  };

  const handleExport = () => {
    window.print();
  };

  return (
    <div className="act-app">
      <Sidebar
        mode={mode}
        setMode={setMode}
        onNewCase={() => { setCaseFile(null); setErrorToast(null); setModal(null); }}
        onSearch={() => setModal("search")}
        onLoadA={() => loadCase(makeCaseA)}
        onLoadB={() => loadCase(makeCaseB)}
      />

      <main className="act-main">
        {errorToast && <div className="act-alert">{errorToast}</div>}

        {caseFile === null ? (
          <>
            <UploadTopbar
              onOpenCorpus={() => setModal("corpus")}
              onOpenGuide={() => setModal("guide")}
            />
            <LandingHero />
            <UploadPane
              onRun={handleRun}
              onLoadA={() => loadCase(makeCaseA)}
              onLoadB={() => loadCase(makeCaseB)}
            />
          </>
        ) : (
          <>
            <CaseFileSummary caseFile={caseFile} />
            <div style={{ display: "flex", justifyContent: "flex-end", margin: "0 0 8px" }}>
              <button className="act-btn" onClick={handleExport}>
                ⬇ Export Preliminary Verdict (PDF)
              </button>
            </div>
            <AgentStepper caseFile={caseFile} />
            <VerdictCard caseFile={caseFile} />
            <EvidenceBoard caseFile={caseFile} />
            <SymbolicRulesPanel caseFile={caseFile} />
            <ObjectionsSection caseFile={caseFile} />
            <MissingAndGovernance caseFile={caseFile} />
            <AgentActivityTimeline caseFile={caseFile} />
            <ChatSection caseFile={caseFile} onSubmit={handleChat} />
          </>
        )}
      </main>

      {modal === "search" && (
        <div className="act-modal-backdrop" role="presentation" onClick={() => setModal(null)}>
          <div className="act-modal" role="dialog" aria-modal="true" aria-labelledby="search-title" onClick={(e) => e.stopPropagation()}>
            <div className="act-modal-head">
              <h2 id="search-title">Search cases</h2>
              <button className="act-icon-btn" type="button" aria-label="Close dialog" onClick={() => setModal(null)}>x</button>
            </div>
            <div className="act-modal-body">
              <button className="act-case-option" type="button" onClick={() => loadCase(makeCaseA)}>
                <span className="name">AI hiring screener</span>
                <span className="meta">Employment ranking, missing oversight evidence, potential high risk.</span>
              </button>
              <button className="act-case-option" type="button" onClick={() => loadCase(makeCaseB)}>
                <span className="name">Inventory forecaster</span>
                <span className="meta">Internal logistics forecast, no affected persons, minimal risk.</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {modal === "corpus" && <CorpusDialog onClose={() => setModal(null)} />}

      {modal === "guide" && (
        <div className="act-modal-backdrop" role="presentation" onClick={() => setModal(null)}>
          <div className="act-modal" role="dialog" aria-modal="true" aria-labelledby="guide-title" onClick={(e) => e.stopPropagation()}>
            <div className="act-modal-head">
              <h2 id="guide-title">Guide</h2>
              <button className="act-icon-btn" type="button" aria-label="Close dialog" onClick={() => setModal(null)}>x</button>
            </div>
            <div className="act-modal-body">
              <div className="act-guide-steps">
                <span>1. Upload or paste a use-case description.</span>
                <span>2. Open a hearing to generate a preliminary risk verdict.</span>
                <span>3. Inspect facts, legal references, assumptions, and fired rules.</span>
                <span>4. Cross-examine the verdict with new facts or answers.</span>
                <span>5. Export the current assessment through the browser print dialog.</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
