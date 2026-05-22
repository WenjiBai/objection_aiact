
# OBJECTION! AI ACT — developer guide

A neuro-symbolic multi-agent courtroom that turns messy AI use-case documents
into a Preliminary EU AI Act assessment. Internal codename `ActScout Hybrid`.
Track 3 submission for the Norrin Hackathon, deadline **2026-05-24 11:00**.

> **Preliminary — not legal advice.** Every output is tagged as such.

---

## 1. Run it

```bash
pip install -r requirements.txt
python -m scripts.build_index            # one-off: build the RAG index (~80 MB model d/l)
streamlit run app.py                     # → http://localhost:8501
```

Quick demo: in the sidebar click **Case A · HR** for the killer demo or
**Case B · Stock** for the contrast demo. Upload-flow uses the same backend
stub and routes by keyword in the doc content.

Sub-second responses are mock data. Real LLM calls land when Person A swaps
the stub in `backend/api.py`; the demo path will then run ≤ 30 s end-to-end
(Sync v1 §3.1).

---

## 2. Directory map

```
objection-ai-act/
├── app.py                          # Streamlit entry — sidebar + main layout
├── requirements.txt
├── README.md                       # ← you are here
│
├── shared/
│   ├── schema.py                   # CaseFile + all Pydantic types + enums
│   ├── agent_outputs.py            # 7 AgentOut wrappers (Detective/…/Chat)
│   ├── mock.py                     # make_mock_case_a/b + simulate_chat_response
│   └── validators.py               # get_evidence / get_ref / snapshot / validate_codes
│
├── backend/
│   ├── api.py                      # run_courtroom / handle_chat + BackendValidationError
│   └── symbolic/
│       └── rules.yaml              # 13 symbolic-gate rules (R-HIRE-001 etc.)
│
├── rag/
│   ├── corpus.py                   # 25 hand-curated Reference chunks
│   ├── retrieve.py                 # retrieve(query, top_k) → list[Reference]
│   └── chroma_store/               # persistent index (created by build_index)
│
├── ui/
│   └── components.py               # All Streamlit render fns (read-only on CaseFile)
│
├── scripts/
│   ├── dump_schemas.py             # → schemas/*.json for A's prompts
│   └── build_index.py              # → rag/chroma_store/
│
├── schemas/                        # 20 JSON Schema files (7 agent + 13 atomic)
│
└── cases/
    ├── case_a/                     # 3 docs — HR screening (CV-Sage)
    └── case_b/                     # 2 docs — inventory forecaster (StockGlance)
```

---

## 3. The contract

Only two functions cross the A↔B boundary. Both are **synchronous**:

```python
# backend/api.py
def run_courtroom(case: CaseFile) -> CaseFile: ...
def handle_chat(case: CaseFile, user_text: str) -> CaseFile: ...
```

`CaseFile` is the **single source of truth** (`shared/schema.py`). UI renders
from it; UI only mutates `chat_history` (Sync v1 §2.2). Backend retries schema
validation once internally; second failure raises `BackendValidationError`,
frontend rolls back to the pre-call snapshot.

### Agent flow inside `run_courtroom`

```
documents
  → Detective       writes facts            (E-codes)
  → Legal Clerk     writes refs             (R-codes, via rag.retrieve)
  → Symbolic Gate   writes rule_firings     (loads rules.yaml, injects yaml_source)
  → Prosecutor      writes allegations
  → Defense         writes defenses
  → Critique        writes objections       (OBJECTION! cards)
  → Judge           writes verdict + missing_evidence + governance_checklist
                          + follow_up_questions + assumptions
```

`agent_activity` accumulates one row per step (Sync v1 §3.2). `chat_history`
appends user + judge turns inside `handle_chat`.

### Code naming (globally unique within a CaseFile)

| Prefix | Meaning | Example |
|---|---|---|
| `E-NN` | Evidence — extracted fact | `E-01` |
| `R-…` | Reference — AI Act citation | `R-Art-14`, `R-Annex-III-4`, `R-Recital-71`, `R-Guide-…`, `R-FI-…` |
| `A-NN` | Assumption | `A-01` |
| `ALL-NN` | Allegation | `ALL-01` |
| `DEF-NN` | Defense | `DEF-01` |
| `OBJ-NN` | Objection | `OBJ-01` |

`validate_codes(case)` checks integrity post-mutation — used by `app.py` after
every chat turn to catch hallucinated references.

---

## 4. What is real vs. stub

| Layer | Status | Where |
|---|---|---|
| `shared/schema.py` (full CaseFile contract) | ✅ real | matches `CaseFile_Schema_Spec.md` v2 |
| `shared/agent_outputs.py` (7 wrappers) | ✅ real | enables `schemas/*.json` for A's prompts |
| `shared/mock.py` (Case A + B mocks) | ✅ real | hits §7 acceptance criteria |
| `backend/api.py` — `run_courtroom` | 🟡 **stub** | routes by keyword to mock A or B |
| `backend/api.py` — `handle_chat` | 🟡 **stub** | bumps confidence on "override" / "appeal" |
| `backend/symbolic/rules.yaml` | ✅ real | 13 rules; loader not yet written (A's task) |
| `rag/retrieve.py` | ✅ real | Chroma + ONNX `all-MiniLM-L6-v2`; keyword fallback |
| `rag/corpus.py` | 🟡 seed | 25 chunks covering the demo; expand with full Act later |
| `ui/*` | ✅ real | renders everything from CaseFile |
| Symbolic Gate evaluator (Python) | ❌ not started | A writes; reads `rules.yaml`, fills `RuleFiring` |
| LangGraph / agent orchestration | ❌ not started | A's primary task |
| 6 agent prompts | ❌ not started | A writes; each embeds the matching `schemas/*.json` |
| PDF export | ❌ not started | nice-to-have (Sync v1 §9.2); markdown → weasyprint |

---

## 5. How to extend

Common changes, in order of frequency:

### 5.1 Change CaseFile shape
1. Edit `shared/schema.py`.
2. Run `python -m scripts.dump_schemas` — regenerates the 20 JSON Schema files A embeds in prompts.
3. Update affected mock data in `shared/mock.py`.
4. If you added a field that the UI should render, edit `ui/components.py`.

> Breaking changes need a commit + Slack-equivalent to the other side (Sync v1 §12).

### 5.2 Add a new symbolic rule
1. Append a YAML block to `backend/symbolic/rules.yaml` (Sync v1 §4.2 shape).
2. A's loader will pick it up; `yaml_source` gets injected automatically into
   the `RuleFiring` so the UI shows the source.

### 5.3 Add a new R-code (AI Act passage) to RAG
1. Append a `Reference(...)` to `SEED_CHUNKS` in `rag/corpus.py`.
2. Run `python -m scripts.build_index` to rebuild the persistent index.

### 5.4 Add a new demo case
1. Drop docs under `cases/case_<x>/`.
2. Optional: add a `make_mock_case_<x>()` in `shared/mock.py` and a sidebar
   button in `app.py`.

### 5.5 Replace the backend stub with the real pipeline
The only file you need to touch is `backend/api.py`. Keep the function
signatures identical and the UI doesn't need to change. Recommended skeleton:

```python
def run_courtroom(case: CaseFile) -> CaseFile:
    case.status = CaseStatus.INGESTING
    case = run_detective(case)            # facts
    case.status = CaseStatus.RETRIEVING
    case = run_legal_clerk(case)          # refs (uses rag.retrieve)
    case = apply_symbolic_gate(case)      # rule_firings
    case.status = CaseStatus.DELIBERATING
    case = run_prosecutor(case)
    case = run_defense(case)
    case = run_critique(case)
    case = run_judge(case)                # verdict + missing_evidence + checklist
    case.status = CaseStatus.VERDICT_READY
    return case
```

Each `run_<agent>` calls Claude with the matching schema embedded
(`schemas/<Agent>Output.json`), validates the response with
`AgentOutput.model_validate_json(raw)`, retries once on `ValidationError`,
raises `BackendValidationError` on the second failure.

---

## 6. Hand-off — what's whose

| Owner | Done | Owns next |
|---|---|---|
| **B (Frontend / RAG / cases / PPT)** | schema, mocks, schemas/, RAG, rules.yaml v1, demo docs, UI | PPT, speaker notes, PDF export, polish, smoke tests |
| **A (Backend / Agents / Symbolic Gate)** | (in progress) | LangGraph orchestration, 6 agent prompts, real symbolic-gate evaluator, prompt tuning so Case A hits POTENTIAL_HIGH_RISK and Case B hits MINIMAL_RISK |

### B → A specifically blocking

All of these are now delivered:

- `shared/schema.py` ✅
- `shared/mock.py` (Case A + B) ✅
- `schemas/*.json` (7 agent outputs + 13 bonus) ✅
- `retrieve(query, top_k) -> list[Reference]` ✅
- Demo case docs (`cases/case_a/`, `cases/case_b/`) ✅
- `backend/symbolic/rules.yaml` v1 (13 rules) ✅

### A → B blocking (not yet started, watch list)

- Symbolic-gate evaluator that loads `rules.yaml`, evaluates against
  `case.facts`, and populates `case.rule_firings` with `yaml_source` injected.
- Real `run_courtroom` so Case A hits the §7.1 acceptance criteria with live
  LLM output (currently passes via mock).

---

## 7. Key invariants (don't break)

From Sync v1 §2:

1. Every code (`E-…`, `R-…`, `A-…`, etc.) globally unique within a CaseFile.
2. `Allegation.basis_evidence_codes` / `basis_ref_codes` must reference codes
   that actually exist. `validate_codes()` enforces post-mutation.
3. `Evidence.structured_value` is required for
   `category ∈ {SECTOR, OUTPUT, GPAI_USAGE}` and must match the right enum.
4. `RuleFiring.yaml_source` carries the raw YAML — UI shows it verbatim. **B
   does not parse `rules.yaml`.**
5. `Verdict.confidence_label` must agree with `confidence_score`:
   - 0–3 → LOW · 4–6 → MEDIUM · 7–10 → HIGH.
6. UI is read-only on CaseFile except `chat_history`. `handle_chat` is the
   only user-triggered mutator and is wrapped in snapshot/rollback.

The schema enforces #1, #3, #5 at parse time (Pydantic validators); the others
are runtime checks in `shared/validators.py` and `app.py`.

---

## 8. Known issues / TODO

- `rag/corpus.py` is hand-curated (25 chunks). Once the full
  Regulation 2024/1689 text is chunked, append to `SEED_CHUNKS` and run
  `python -m scripts.build_index`.
- `rules.yaml` evaluator not yet written — A's task. Spec: read YAML →
  evaluate `when` block against `case.facts` (structured_value where present,
  text otherwise) → emit `RuleFiring` with `evaluated_against` filled in.
- No PDF export. Sync v1 §9.2 lists it as Should-Have; markdown → weasyprint
  is the simplest path.
- Streamlit auto-reload requires the user to click "Rerun" in the browser
  after backend edits (works fine, just a UX note).
- ChromaDB install pulled `click 8.4.1` which conflicts with `semgrep 1.143.1`
  (unrelated to this project — system-wide pip env). Use a venv for clean
  isolation if it bites.

---

## 9. Reference docs

- `../documents/ActScout_Hybrid_Concept_v2.md` — concept, agent design, demo plan
- `../documents/Frontend_Backend_Sync_v1.md` — the contract (invariants, codes, deliverables, timeline)
- `../documents/CaseFile_Schema_Spec.md` — schema spec (v2, A approved)
- `../documents/OBJECTION_AI_ACT_Brief.md` — overview + Person B's timeline

---

*Preliminary — not legal advice. Built to be honest.*
>>>>>>> B
