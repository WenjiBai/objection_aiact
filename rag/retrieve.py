"""RAG retrieval interface.

Public contract (Sync v1 §10.4 — A blocks on this):
    def retrieve(query: str, top_k: int = 5) -> list[Reference]

Backed by a persistent ChromaDB collection with sentence-transformers
embeddings (per spec: all-MiniLM-L6-v2). Falls back to a keyword-rank baseline
if Chroma isn't installed yet so unit tests + Person A's mocked path keep
working.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from shared.schema import Reference

from .corpus import SEED_CHUNKS

_PERSIST_DIR = Path(__file__).resolve().parent / "chroma_store"
_COLLECTION_NAME = "ai_act_v1"

# Lazy-built singletons.
_collection = None
_chroma_available: Optional[bool] = None


# --------------------------------------------------------------- chroma path

def _try_init_chroma():
    """Return (client, collection) or None if Chroma isn't usable."""
    global _chroma_available
    try:
        import chromadb  # noqa: F401
    except ImportError:
        _chroma_available = False
        return None

    try:
        from chromadb import PersistentClient
        from chromadb.utils import embedding_functions

        client = PersistentClient(path=str(_PERSIST_DIR))
        # DefaultEmbeddingFunction = ONNX all-MiniLM-L6-v2 (bundled, offline-friendly).
        ef = embedding_functions.DefaultEmbeddingFunction()

        try:
            col = client.get_collection(_COLLECTION_NAME, embedding_function=ef)
        except Exception:
            col = client.create_collection(
                _COLLECTION_NAME,
                embedding_function=ef,
                # Cosine distance ∈ [0, 2]; we'll convert to similarity ∈ [0, 1] below.
                metadata={"description": "EU AI Act seed corpus v1",
                          "hnsw:space": "cosine"},
            )
            _seed_collection(col)

        _chroma_available = True
        return col
    except Exception as e:
        # Any embedding/persistence failure → fall back rather than crashing.
        print(f"[rag] Chroma init failed ({type(e).__name__}: {e}); using keyword fallback.")
        _chroma_available = False
        return None


def _seed_collection(col):
    """Index the seed corpus into a fresh collection."""
    ids = [c.code for c in SEED_CHUNKS]
    docs = [f"{c.title}\n\n{c.full_text}" for c in SEED_CHUNKS]
    metadatas = [
        {
            "code": c.code,
            "title": c.title,
            "article_no": c.article_no,
            "source_type": c.source_type.value,
            "source_label": c.source_label,
            "url": c.url or "",
        }
        for c in SEED_CHUNKS
    ]
    col.add(ids=ids, documents=docs, metadatas=metadatas)


def _get_collection():
    global _collection
    if _collection is None:
        _collection = _try_init_chroma()
    return _collection


# -------------------------------------------------------------- public API

def retrieve(query: str, top_k: int = 5) -> list[Reference]:
    """Return up to `top_k` Reference objects ranked by similarity to `query`."""
    col = _get_collection()
    if col is not None:
        try:
            return _retrieve_chroma(col, query, top_k)
        except Exception as e:
            print(f"[rag] Chroma query failed ({type(e).__name__}: {e}); falling back.")
    return _retrieve_keyword(query, top_k)


def _retrieve_chroma(col, query: str, top_k: int) -> list[Reference]:
    res = col.query(query_texts=[query], n_results=top_k)
    ids = res.get("ids", [[]])[0]
    distances = res.get("distances", [[]])[0] if res.get("distances") else [None] * len(ids)

    by_code = {c.code: c for c in SEED_CHUNKS}
    out: list[Reference] = []
    for code, dist in zip(ids, distances):
        ref = by_code.get(code)
        if not ref:
            continue
        # Chroma cosine distance is in [0, 2]; map to similarity ∈ [0, 1].
        score = max(0.0, 1.0 - float(dist) / 2.0) if dist is not None else None
        out.append(ref.model_copy(update={"relevance_score": score}))
    return out


# ------------------------------------------------------------ keyword fallback

_STOP = {
    "a", "an", "and", "or", "the", "is", "are", "of", "to", "for", "in", "on",
    "with", "by", "this", "that", "be", "as", "it", "we", "our", "any", "from",
}


def _tokens(s: str) -> set[str]:
    return {t for t in re.findall(r"[a-zA-Z][a-zA-Z\-]+", s.lower()) if t not in _STOP}


def _retrieve_keyword(query: str, top_k: int) -> list[Reference]:
    qt = _tokens(query)
    if not qt:
        return list(SEED_CHUNKS[:top_k])
    scored: list[tuple[float, Reference]] = []
    for ref in SEED_CHUNKS:
        haystack = f"{ref.title} {ref.snippet} {ref.full_text}"
        overlap = qt & _tokens(haystack)
        if not overlap:
            continue
        score = len(overlap) / max(len(qt), 1)
        scored.append((score, ref.model_copy(update={"relevance_score": score})))
    scored.sort(key=lambda t: t[0], reverse=True)
    return [r for _, r in scored[:top_k]]


# -------------------------------------------------------- utility / debug

def backend_in_use() -> str:
    """Returns 'chroma' or 'keyword' — for the UI/debug page."""
    _get_collection()  # trigger init if not yet done
    return "chroma" if _chroma_available else "keyword"


def reindex() -> None:
    """Drop and rebuild the persisted Chroma collection from SEED_CHUNKS."""
    global _collection
    _collection = None
    try:
        import chromadb
        from chromadb import PersistentClient
        client = PersistentClient(path=str(_PERSIST_DIR))
        try:
            client.delete_collection(_COLLECTION_NAME)
        except Exception:
            pass
    except ImportError:
        pass
    _collection = _try_init_chroma()
