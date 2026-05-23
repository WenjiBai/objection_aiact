# OBJECTION! AI ACT — React frontend

A React + Vite rewrite of the Streamlit UI in `../app.py` + `../ui/`.

This is a **standalone, static UI**: it ships the Case A / Case B mocks from
`shared/mock.py` (ported to `src/mock.js`) and the same visual theme tokens
from `ui/theme.py` (ported to `src/index.css`). No backend is wired up —
clicking "Open courtroom hearing" loads the Case A mock so the workspace
renders end-to-end.

## Layout

```
frontend/
├── index.html
├── package.json
├── vite.config.js
├── public/
│   └── Objection_AI_ACT.png   # copied from ../assets/
└── src/
    ├── main.jsx
    ├── App.jsx
    ├── index.css              # dark/light tokens + .act-* component CSS
    ├── components.jsx         # all UI sections
    └── mock.js                # Case A / B mock CaseFiles + chat sim
```

## Run

```bash
cd frontend
npm install
npm run dev      # opens http://localhost:5173
```

`npm run build` writes a production bundle to `frontend/dist/`.

## What's included

- Sidebar with dark/light toggle and demo-case buttons.
- Landing hero, drag-drop file zone, paste-text area, demo case quick start.
- Case banner with sticky tier pill.
- 6-agent stepper with running/completed states.
- Verdict card with SVG confidence ring.
- Evidence Board (Facts / References / Assumptions tabs).
- Symbolic Risk Gate panel with rule firings.
- OBJECTION! cards (open + resolved).
- Governance checklist.
- Collapsible agent activity timeline.
- Cross-examine chat (powered by the same `simulate_chat_response` logic as
  `shared/mock.py`).

## What's not included

- No real backend wiring. To connect to the Python `run_courtroom` /
  `handle_chat` API, replace the body of `handleRun` and `handleChat` in
  `src/App.jsx` with `fetch()` calls to a FastAPI / Flask shim.
- PDF export uses the browser print dialog.
- AI Act corpus / Guide / Search cases are static frontend dialogs.
