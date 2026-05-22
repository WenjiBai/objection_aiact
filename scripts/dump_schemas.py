"""Dump JSON Schema for every agent output type → schemas/<Name>.json.

Run from the project root:
    python -m scripts.dump_schemas

Person A embeds each schema into the corresponding agent prompt:

    Respond with valid JSON matching this schema:
    {schema_json}
    Do not include any text outside the JSON object.

LLM output is then one-shot validated with `<Name>.model_validate_json(raw)`.
On first failure, A retries with the error message appended (Sync v1 §6.1);
second failure raises BackendValidationError.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Make sure we can run this from anywhere — add project root to sys.path.
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from shared.agent_outputs import (
    ChatOutput, CritiqueOutput, DefenseOutput, DetectiveOutput,
    JudgeOutput, LegalClerkOutput, ProsecutorOutput,
)
from shared.schema import (
    Allegation, Assumption, CaseFile, ChatTurn, ChecklistItem, Defense,
    Document, Evidence, MissingEvidenceItem, Objection, Reference,
    RuleFiring, Verdict,
)


# Sync v1 §5 — these seven are what A embeds in agent prompts.
AGENT_OUTPUTS = [
    DetectiveOutput,
    LegalClerkOutput,
    ProsecutorOutput,
    DefenseOutput,
    CritiqueOutput,
    JudgeOutput,
    ChatOutput,
]

# Bonus dumps — atomic types for sub-validation or documentation.
ATOMIC_TYPES = [
    Document, Evidence, Reference, Assumption,
    RuleFiring, Allegation, Defense, Objection,
    Verdict, MissingEvidenceItem, ChecklistItem, ChatTurn,
    CaseFile,
]


def _dump(cls, out_dir: Path) -> Path:
    path = out_dir / f"{cls.__name__}.json"
    schema = cls.model_json_schema()
    path.write_text(json.dumps(schema, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def main(out_dir: Path | None = None) -> None:
    out_dir = out_dir or (_ROOT / "schemas")
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Writing schemas to {out_dir}\n")

    print("Agent outputs (7) — embed these in prompts:")
    for cls in AGENT_OUTPUTS:
        p = _dump(cls, out_dir)
        print(f"  {p.relative_to(_ROOT)}")

    print("\nAtomic types (bonus, for sub-validation):")
    for cls in ATOMIC_TYPES:
        p = _dump(cls, out_dir)
        print(f"  {p.relative_to(_ROOT)}")

    print(f"\nDone — {len(AGENT_OUTPUTS) + len(ATOMIC_TYPES)} files written.")


if __name__ == "__main__":
    main()
