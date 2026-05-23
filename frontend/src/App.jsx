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
import { makeCaseA, makeCaseB } from "./mock.js";

const fileToBase64 = (file) =>
  new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const result = String(reader.result || "");
      resolve(result.includes(",") ? result.split(",")[1] : result);
    };
    reader.onerror = () => reject(reader.error || new Error(`Could not read ${file.name}`));
    reader.readAsDataURL(file);
  });

async function postJson(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.error || `Request failed with ${response.status}`);
  }
  return data;
}

async function postBlob(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.error || `Request failed with ${response.status}`);
  }
  return {
    blob: await response.blob(),
    contentDisposition: response.headers.get("Content-Disposition") || "",
  };
}

function filenameFromContentDisposition(value) {
  const encodedMatch = value.match(/filename\*=UTF-8''([^;]+)/i);
  if (encodedMatch) {
    return decodeURIComponent(encodedMatch[1]);
  }
  const match = value.match(/filename="([^"]+)"/i) || value.match(/filename=([^;]+)/i);
  return match ? match[1].trim() : "objection_verdict.pdf";
}

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

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
  const [mode, setMode] = React.useState("light");
  const [caseFile, setCaseFile] = React.useState(null);
  const [errorToast, setErrorToast] = React.useState(null);
  const [isRunning, setIsRunning] = React.useState(false);
  const [isChatting, setIsChatting] = React.useState(false);
  const [isExporting, setIsExporting] = React.useState(false);
  const [modal, setModal] = React.useState(null);

  React.useEffect(() => {
    document.documentElement.dataset.theme = mode;
  }, [mode]);

  const handleRun = async (files, pasted) => {
    setIsRunning(true);
    setErrorToast(null);
    try {
      const encodedFiles = await Promise.all(
        files.map(async (file) => ({
          name: file.name,
          type: file.type || "application/octet-stream",
          data_base64: await fileToBase64(file),
        }))
      );
      const data = await postJson("/api/run-courtroom", {
        files: encodedFiles,
        pasted_text: pasted,
      });
      setCaseFile(data.case_file);
      if (data.warnings?.length) {
        setErrorToast(data.warnings.join(" "));
      }
    } catch (err) {
      setErrorToast(`Could not start the hearing: ${err.message}`);
    } finally {
      setIsRunning(false);
    }
  };

  const handleChat = async (text) => {
    if (!caseFile || isChatting) return;
    const snapshot = caseFile;
    setIsChatting(true);
    setErrorToast(null);
    try {
      const data = await postJson("/api/chat", {
        case_file: snapshot,
        user_text: text,
      });
      setCaseFile(data.case_file);
    } catch (err) {
      setCaseFile(snapshot);
      setErrorToast(`Could not cross-examine the verdict: ${err.message}`);
    } finally {
      setIsChatting(false);
    }
  };

  const loadCase = (factory) => {
    setCaseFile(factory());
    setErrorToast(null);
    setModal(null);
  };

  const handleExport = async () => {
    if (!caseFile || isExporting) return;
    setIsExporting(true);
    setErrorToast(null);
    try {
      const { blob, contentDisposition } = await postBlob("/api/export-pdf", {
        case_file: caseFile,
      });
      downloadBlob(blob, filenameFromContentDisposition(contentDisposition));
    } catch (err) {
      setErrorToast(`PDF export failed: ${err.message}`);
    } finally {
      setIsExporting(false);
    }
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
              isRunning={isRunning}
              onLoadA={() => loadCase(makeCaseA)}
              onLoadB={() => loadCase(makeCaseB)}
            />
          </>
        ) : (
          <>
            <CaseFileSummary caseFile={caseFile} />
            <div style={{ display: "flex", justifyContent: "flex-end", margin: "0 0 8px" }}>
              <button className="act-btn" onClick={handleExport} disabled={isExporting}>
                {isExporting ? "Exporting PDF..." : "⬇ Export Preliminary Verdict (PDF)"}
              </button>
            </div>
            <AgentStepper caseFile={caseFile} />
            <VerdictCard caseFile={caseFile} />
            <EvidenceBoard caseFile={caseFile} />
            <SymbolicRulesPanel caseFile={caseFile} />
            <ObjectionsSection caseFile={caseFile} />
            <MissingAndGovernance caseFile={caseFile} />
            <AgentActivityTimeline caseFile={caseFile} />
            <ChatSection caseFile={caseFile} onSubmit={handleChat} disabled={isChatting} />
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
                <span>5. Export the current assessment as a structured PDF report.</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
