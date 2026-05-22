"""
CLI smoke test for Case A (HR Screening AI).

Goals at this stage:
  1. Prove backend.api imports cleanly.
  2. Prove the orchestrator can be instantiated.
  3. If shared/schema.py + shared/mock.py exist, run the dummy pipeline
     end-to-end and dump the resulting CaseFile JSON to stdout.
  4. If they don't exist yet, exit cleanly with a clear "waiting on B" note.

Usage:
    python scripts/run_case_a.py
    python scripts/run_case_a.py --save   # also write to case_storage/

Once B ships shared/schema.py + shared/mock.make_mock_case_a(),
this script becomes the full end-to-end dummy run for the Fri 23:30 milestone.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Ensure project root is on sys.path so `from backend.api ...` works
# regardless of where the script is invoked from.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def main() -> int:
    parser = argparse.ArgumentParser(description="Case A smoke test")
    parser.add_argument(
        "--save",
        action="store_true",
        help="Also persist the resulting CaseFile to case_storage/",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("OBJECTION! AI ACT - Case A smoke test")
    print("=" * 60)

    # Step 1: prove backend.api imports
    print("\n[1/4] Importing backend.api ...")
    try:
        from backend.api import run_courtroom, handle_chat, BackendValidationError
    except ImportError as e:
        print(f"  FAIL: backend.api import broken: {e}")
        return 1
    print(f"  OK: run_courtroom = {run_courtroom.__name__}")
    print(f"  OK: handle_chat   = {handle_chat.__name__}")
    print(f"  OK: BackendValidationError = {BackendValidationError.__name__}")

    # Step 2: check whether B has shipped the schema yet
    print("\n[2/4] Checking shared/schema.py + shared/mock.py ...")
    try:
        from shared.schema import CaseFile  # noqa: F401
        from shared.mock import make_mock_case_a
    except ImportError as e:
        print(f"  WAITING: {e}")
        print("  B has not shipped shared/schema.py + shared/mock.py yet.")
        print("  Backend skeleton is ready; smoke test will resume once B delivers.")
        print("\n[3/4] Skipped (no schema).")
        print("[4/4] Skipped (no schema).")
        print("\nResult: PARTIAL - import surface OK, awaiting B's deliverable.")
        return 0

    # Step 3: build a mock CaseFile for Case A and run the dummy pipeline
    print("  OK: schema and mocks available")

    print("\n[3/4] Building mock Case A CaseFile ...")
    case = make_mock_case_a()
    print(f"  OK: case_id = {case.case_id}")
    print(f"  OK: initial status = {case.status}")
    print(f"  OK: documents = {len(case.documents)}")

    print("\n[4/4] Running run_courtroom() (dummy pipeline) ...")
    try:
        result = run_courtroom(case)
    except BackendValidationError as e:
        print(f"  FAIL: agent validation error: {e.agent} -> {e.errors}")
        return 2
    except Exception as e:
        print(f"  FAIL: unexpected error: {type(e).__name__}: {e}")
        return 3

    print(f"  OK: final status = {result.status}")
    print(f"  OK: agent_activity entries = {len(result.agent_activity)}")
    for entry in result.agent_activity:
        print(f"       - {entry.agent}: {entry.status}")

    # Pretty-print the resulting CaseFile JSON
    print("\n" + "=" * 60)
    print("Resulting CaseFile JSON:")
    print("=" * 60)
    print(result.model_dump_json(indent=2))

    if args.save:
        from backend.persistence import save_case  # noqa: WPS433 - lazy import
        path = save_case(result)
        print(f"\nSaved to: {path}")

    print("\nResult: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())