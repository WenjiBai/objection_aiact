# OBJECTION! AI ACT — developer guide

**OBJECTION! AI ACT** is an evidence-based multi-agent system that puts an AI use case on trial under the EU AI Act. Users upload AI system documentation, and six specialized agents — Detective, Legal Clerk, Prosecutor, Defense, Critique, and Judge — extract facts, retrieve legal references, apply transparent symbolic rules, challenge weak claims, and produce an auditable preliminary compliance report. The system is designed as a first-pass decision-support tool, not legal advice: every verdict is grounded in evidence, rule traces, assumptions, missing information, and governance next steps.

**Author:** Wenji Bai & Hong Qin 

Track 3 submission for the Norrin Hackathon.


---

## 1. Run it

```bash
pip install -r requirements.txt
cp env.example .env                      # then paste your real ANTHROPIC_API_KEY into .env
python -m scripts.build_index            # one-off: build the RAG index (~80 MB model d/l)
streamlit run app.py                     # → http://localhost:8501
```

CLI smoke test (no UI):

```bash
python scripts/run_case_a.py             # also `--save` to write to case_storage/
```

Quick demo: in the sidebar click **Case A · HR** for the killer demo or
**Case B · Stock** for the contrast demo. Real LLM calls now back the pipeline;
end-to-end runs ~3–4 min on Case A and ~1 min on Case B.

---

## 2. Directory map

```
objection-ai-act/
├── app.py                          # Streamlit entry — sidebar + main layout
├── requirements.txt
├── README.md                       # ← you are here
├── env.example                     # template — copy to .env
│
├── shared/
│   ├── schema.py                   # CaseFile + all Pydantic types + enums
│   ├── agent_outputs.py            # 7 AgentOut wrappers (Detective/…/Chat)
│   ├── mock.py                     # make_mock_case_a/b + simulate_chat_response (legacy)
│   └── validators.py               # get_evidence / get_ref / snapshot / validate_codes
│
├── backend/
│   ├── api.py                      # run_courtroom / handle_chat — the contract surface
│   ├── orchestrator.py             # Sequential 6-agent + symbolic-gate state machine
│   ├── persistence.py              # save_case / load_case / list_cases (UI-invoked)
│   ├── exceptions.py               # BackendValidationError
│   │
│   ├── agents/
│   │   ├── base.py                 # BaseAgent abstract class (timing + bookkeeping)
│   │   ├── detective.py            # Facts Table extractor (LLM)
│   │   ├── legal_clerk.py          # RAG-driven Reference retrieval (no LLM)
│   │   ├── prosecutor.py           # Allegations grounded in E + R codes (LLM)
│   │   ├── defense.py              # Exemption / mitigation arguments (LLM)
│   │   ├── critique.py             # OBJECTION! cards (LLM)
│   │   ├── judge.py                # Verdict + missing + checklist + objection resolutions (LLM)
│   │   └── chat.py                 # Cross-examination Judge re-eval (LLM, diff-based)
│   │
│   ├── llm/
│   │   └── client.py               # Anthropic Messages wrapper + retry + validation
│   │
│   ├── symbolic/
│   │   ├── rules.yaml              # 13 symbolic-gate rules (R-HIRE-001 etc.)
│   │   ├── loader.py               # rules.yaml → RuleSpec, injects yaml_source
│   │   └── gate.py                 # evaluate_rules(case, rules) → list[RuleFiring]
│   │
│   └── prompts/                    # System prompts for each LLM agent
│       ├── detective.txt
│       ├── prosecutor.txt
│       ├── defense.txt
│       ├── critique.txt
│       ├── judge.txt
│       └── chat.txt
│
├── rag/
│   ├── corpus.py                   # 25 hand-curated Reference chunks
│   ├── retrieve.py                 # retrieve(query, top_k) → list[Reference]
│   └── chroma_store/               # persistent index (gitignored)
│
├── ui/
│   └── components.py               # All Streamlit render fns (read-only on CaseFile)
│
├── scripts/
│   ├── dump_schemas.py             # → schemas/*.json (for prompt embedding, if needed)
│   ├── build_index.py              # → rag/chroma_store/
│   └── run_case_a.py               # CLI smoke test
│
├── schemas/                        # 20 JSON Schema files (7 agent + 13 atomic)
│
├── cases/
│   ├── case_a/                     # 3 docs — HR screening (CV-Sage)
│   └── case_b/                     # 2 docs — inventory forecaster (StockGlance)
│
└── case_storage/                   # Runtime CaseFile JSON mirror (gitignored)
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
  → Detective       writes facts            (E-codes; structured_value controlled vocab)
  → Legal Clerk     writes refs             (R-codes, via rag.retrieve — no LLM call)
  → Symbolic Gate   writes rule_firings     (loads rules.yaml, injects yaml_source)
  → Prosecutor      writes allegations      (cites real E + R codes only)
  → Defense         writes defenses         (flags requires_documentation honestly)
  → Critique        writes objections       (OBJECTION! cards, resolution=None)
  → Judge           writes verdict + missing_evidence + governance_checklist
                          + follow_up_questions + assumptions
                          + fills every Objection.resolution (spec invariant)
```

`agent_activity` accumulates one row per step (Sync v1 §3.2 — Symbolic Gate is
an internal step and pushes NO entry). `chat_history` appends user + judge
turns inside `handle_chat`.

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

### Detective's controlled vocabulary (drives the symbolic gate)

Detective is instructed to populate `Evidence.structured_value` with specific
tokens for these categories so the symbolic gate's `when` blocks match
correctly (see `backend/prompts/detective.txt`):

| Category | Required? | Allowed values |
|---|---|---|
| `sector` | **required** | `Sector` enum values (`employment`, `education`, …) |
| `output` | **required** | `OutputType` enum values (`ranking`, `screening`, `forecast`, …) |
| `gpai_usage` | **required** | `"true"` / `"false"` / `"unknown"` |
| `affected_persons` | recommended | `job_applicants`, `workers`, `students`, `citizens`, … |
| `human_oversight` | recommended | `verified`, `unverified`, `documented`, `absent`, `n_a` |
| `automation_level` | optional | `narrow_procedural`, `improves_human_activity`, `fully_automated`, `advisory_only` |
| `ai_generated_content` | optional | `"true"` / `"false"` |

---

## 5. How to extend

### 5.1 Change CaseFile shape
1. Edit `shared/schema.py`.
2. Run `python -m scripts.dump_schemas` — regenerates the 20 JSON Schema files.
3. Update affected mock data in `shared/mock.py`.
4. If you added a field the UI should render, edit `ui/components.py`.

### 5.2 Add a new symbolic rule
1. Append a YAML block to `backend/symbolic/rules.yaml` (Sync v1 §4.2 shape).
2. `loader.py` will pick it up; `yaml_source` is injected automatically into
   the `RuleFiring` so the UI shows the source.
3. If the rule uses a new `when` key (e.g. `system_type`), bridge it in
   `backend/symbolic/gate.py`'s `KEY_TO_CATEGORY` map OR teach Detective to
   emit a matching `structured_value` (see Detective controlled vocab above).

### 5.3 Add a new R-code (AI Act passage) to RAG
1. Append a `Reference(...)` to `SEED_CHUNKS` in `rag/corpus.py`.
2. Run `python -m scripts.build_index` to rebuild the persistent index.

### 5.4 Add a new demo case
1. Drop docs under `cases/case_<x>/`.
2. Optional: add a sidebar button in `app.py`.

### 5.5 Tune an agent's behaviour
Each agent has a system prompt in `backend/prompts/<agent>.txt`. Edit the file
and restart — no code change needed. Prompts already include schema
instructions and case-specific examples.

---

## 6. Key invariants (don't break)

1. Every code (`E-…`, `R-…`, `A-…`, etc.) globally unique within a CaseFile.
2. `Allegation.basis_evidence_codes` / `basis_ref_codes` must reference codes
   that actually exist. `validate_codes()` enforces post-mutation.
3. `Evidence.structured_value` is required for
   `category ∈ {SECTOR, OUTPUT, GPAI_USAGE}` and must match the right enum.
4. `RuleFiring.yaml_source` carries the raw YAML — UI shows it verbatim. **B
   does not parse `rules.yaml`.**
5. `Verdict.confidence_label` must agree with `confidence_score`:
   0–3 → LOW · 4–6 → MEDIUM · 7–10 → HIGH.
6. **Every `Objection.resolution` is non-None after `run_courtroom`.**
   Judge prompt + a defensive fallback in `orchestrator.run_courtroom`
   guarantee this.
7. UI is read-only on CaseFile except `chat_history`. `handle_chat` is the
   only user-triggered mutator and is wrapped in snapshot/rollback.

The schema enforces #1, #3, #5 at parse time (Pydantic validators); the others
are runtime checks in `shared/validators.py`, `orchestrator.py`, and `app.py`.

