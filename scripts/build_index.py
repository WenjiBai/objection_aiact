"""Build (or rebuild) the persistent ChromaDB index for the seed corpus.

Run from the project root:
    python -m scripts.build_index
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from rag import retrieve as rag


def main() -> None:
    print("Rebuilding RAG index from rag/corpus.py …")
    rag.reindex()
    backend = rag.backend_in_use()
    sample = rag.retrieve("employment screening of job applicants", top_k=3)
    print(f"Backend: {backend}")
    print(f"Sample query → {len(sample)} hits:")
    for r in sample:
        score = f"{r.relevance_score:.3f}" if r.relevance_score is not None else "—"
        print(f"  [{score}]  {r.code}  {r.title}")


if __name__ == "__main__":
    main()
