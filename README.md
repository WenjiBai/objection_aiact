# OBJECTION! AI ACT

Track 3 — AI Act Compliance Assistant.
Norrin Hackathon, May 2026.

A neuro-symbolic multi-agent system that puts your AI use case on trial under the EU AI Act.

## Setup

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then paste your ANTHROPIC_API_KEY into .env
```

## Frontend (B)

```bash
streamlit run frontend/app.py
```

## Backend (A) — CLI smoke test

```bash
python scripts/run_case_a.py
```

## Public backend API

```python
from backend.api import run_courtroom, handle_chat, BackendValidationError
```

Everything else under `backend/` is internal.

## Project docs

- `ActScout_Hybrid_Concept_v2.md` — product concept (authoritative)
- `Frontend_Backend_Sync_v1.md` — frontend/backend contract
- `Backend_Architecture_v1.md` — backend architecture & tech stack
