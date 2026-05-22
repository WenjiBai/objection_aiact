"""Save / load CaseFile to / from a JSON disk mirror.

Spec: Backend_Architecture_v1.md §2.6.

Called from B's UI layer (`st.session_state.case_file` is the live primary;
this module mirrors to `./case_storage/{case_id}.json` so a page reload can
recover the working session). Backend `api.run_courtroom` / `handle_chat`
must NOT call these — they stay pure functions.
"""
from __future__ import annotations

from pathlib import Path

from shared.schema import CaseFile

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CASE_DIR = PROJECT_ROOT / "case_storage"
CASE_DIR.mkdir(exist_ok=True)


def save_case(case: CaseFile) -> Path:
    """Write the CaseFile JSON to `case_storage/{case_id}.json`; return the path."""
    path = CASE_DIR / f"{case.case_id}.json"
    path.write_text(case.model_dump_json(indent=2))
    return path


def load_case(case_id: str) -> CaseFile | None:
    """Return the persisted CaseFile, or None if `case_id` was never saved."""
    path = CASE_DIR / f"{case_id}.json"
    if not path.exists():
        return None
    return CaseFile.model_validate_json(path.read_text())


def list_cases() -> list[str]:
    """Return all known `case_id`s on disk (sorted, deterministic)."""
    return sorted(p.stem for p in CASE_DIR.glob("*.json"))


__all__ = ["save_case", "load_case", "list_cases", "CASE_DIR", "PROJECT_ROOT"]
