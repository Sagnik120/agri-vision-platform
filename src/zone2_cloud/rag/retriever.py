"""
retriever.py — Person B, Zone 2.

Given a query, return the top-k knowledge-base documents, each tagged with a
stable `doc_id` so advisories can cite exactly which document they used.

Backends (RAG_BACKEND env: auto | faiss | lexical):
  faiss   — FAISS index + all-MiniLM-L6-v2 embeddings (build_knowledge_base.py).
  lexical — pure-Python BM25 over the KB markdown files. No torch, no index
            file, always in sync with the KB: used when sentence-transformers /
            faiss are not installed (e.g. a ~512MB serverless deployment) or the
            FAISS index/metadata is missing.
  auto    — faiss when available, else lexical.

Optional cross-encoder rerank (RAG_RERANK_MODEL) is OFF by default; it is only
worth enabling if eval/rag_eval.py shows a measured gain.

Public API:
  retrieve(query, k) -> str                      (legacy; contract #6 string)
  retrieve_docs(query, k, domain=None) -> list[dict]
"""

from __future__ import annotations

import json
import math
import os
import re
from collections import Counter
from pathlib import Path

from src.zone2_cloud.rag.kb_metadata import load_kb

INDEX_DIR = Path(__file__).resolve().parents[3] / "results" / "zone2" / "rag_index"
KB_DIR = Path(__file__).resolve().parent / "knowledge_base"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Loaded once per process.
_faiss_state = None   # (model, index, meta) or False when unavailable
_lexical_state = None  # _BM25
_reranker = None

_STOP = {"a", "an", "the", "and", "or", "of", "on", "in", "to", "is", "are", "with",
         "for", "my", "has", "have", "it", "its", "this", "that", "be", "at", "by", "from"}


def _tokens(text: str) -> list[str]:
    return [t for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in _STOP]


class _BM25:
    def __init__(self, docs: list[dict], k1: float = 1.5, b: float = 0.75):
        self.docs, self.k1, self.b = docs, k1, b
        # Condition name counted twice: it is the most discriminative field.
        self.tfs = [Counter(_tokens(d["condition"].replace("_", " ")) * 2 + _tokens(d["text"])) for d in docs]
        self.lens = [sum(tf.values()) for tf in self.tfs]
        self.avg = sum(self.lens) / max(len(self.lens), 1)
        df = Counter(t for tf in self.tfs for t in tf)
        n = len(docs)
        self.idf = {t: math.log(1 + (n - c + 0.5) / (c + 0.5)) for t, c in df.items()}

    def scores(self, query: str) -> list[float]:
        q = _tokens(query)
        out = []
        for tf, ln in zip(self.tfs, self.lens):
            s = 0.0
            for t in q:
                f = tf.get(t, 0)
                if f:
                    s += self.idf[t] * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * ln / self.avg))
            out.append(s)
        return out


def _backend() -> str:
    return os.environ.get("RAG_BACKEND", "auto").lower()


def _load_faiss():
    """Returns (model, index, meta) or False. Heavy imports stay lazy."""
    global _faiss_state
    if _faiss_state is not None:
        return _faiss_state
    _faiss_state = False
    meta_path = INDEX_DIR / "knowledge_meta.json"
    index_path = INDEX_DIR / "knowledge.index"
    if not (meta_path.exists() and index_path.exists()):
        return _faiss_state
    try:
        import faiss
        from sentence_transformers import SentenceTransformer
    except ImportError:
        return _faiss_state
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    by_id = {d["doc_id"]: d for d in load_kb(KB_DIR)}
    for m in meta:  # attach current body text; index rows follow meta order
        m["text"] = by_id.get(m["doc_id"], {}).get("text", "")
    index = faiss.read_index(str(index_path))
    if index.ntotal != len(meta):
        print("Warning: FAISS index/metadata size mismatch — rebuild the index; using lexical retrieval.")
        return _faiss_state
    _faiss_state = (SentenceTransformer(EMBED_MODEL), index, meta)
    return _faiss_state


def _lexical():
    global _lexical_state
    if _lexical_state is None:
        _lexical_state = _BM25(load_kb(KB_DIR))
    return _lexical_state


def _rerank(query: str, docs: list[dict]) -> list[dict]:
    global _reranker
    model_name = os.environ.get("RAG_RERANK_MODEL")
    if not model_name or not docs:
        return docs
    if _reranker is None:
        from sentence_transformers import CrossEncoder
        _reranker = CrossEncoder(model_name)
    scores = _reranker.predict([(query, d["text"]) for d in docs])
    for d, s in zip(docs, scores):
        d["rerank_score"] = float(s)
    return sorted(docs, key=lambda d: d["rerank_score"], reverse=True)


def retrieve_docs(query: str, k: int = 3, domain: str | None = None,
                  rerank: bool = False, backend: str | None = None) -> list[dict]:
    """Top-k docs: [{doc_id, condition, domain, source, text, score, backend}, ...]."""
    backend = (backend or _backend())
    candidates = []
    state = _load_faiss() if backend in ("auto", "faiss") else False
    if state:
        model, index, meta = state
        qv = model.encode([query], convert_to_numpy=True)
        dist, idx = index.search(qv, len(meta))  # KB is small: rank all, then filter
        for d, i in zip(dist[0], idx[0]):
            if 0 <= i < len(meta):
                candidates.append({**meta[i], "score": round(float(-d), 4), "backend": "faiss"})
    else:
        bm = _lexical()
        for doc, s in sorted(zip(bm.docs, bm.scores(query)), key=lambda t: t[1], reverse=True):
            if s > 0:
                candidates.append({**doc, "score": round(s, 4), "backend": "lexical"})
    if domain:
        candidates = [c for c in candidates if c.get("domain") == domain]
    pool = candidates[: max(k * 3, k)] if rerank else candidates[:k]
    if rerank:
        pool = _rerank(query, pool)
    return pool[:k]


def format_docs(docs: list[dict]) -> str:
    """Render docs with their citation IDs so the LLM can cite `[KB-...]`."""
    return "\n\n---\n\n".join(f"[{d['doc_id']}]\n{d['text']}" for d in docs)


def retrieve(query: str, k: int = 3) -> str:
    """Legacy API: top-k snippets concatenated as one string (each tagged with its doc_id)."""
    docs = retrieve_docs(query, k=k)
    if not docs:
        return "Mock retrieved knowledge for: " + query
    return format_docs(docs)


if __name__ == "__main__":
    import sys
    q = sys.argv[1] if len(sys.argv) > 1 else "tomato brown spots"
    for d in retrieve_docs(q):
        print(d["doc_id"], d["score"], d["backend"])
