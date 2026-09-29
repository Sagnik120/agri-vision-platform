"""
build_knowledge_base.py — Person B, Zone 2.

Embeds every KB markdown document (one chunk per document — docs are short,
single-condition entries, so splitting would only fragment them) with
sentence-transformers/all-MiniLM-L6-v2 and indexes with FAISS.

Persists to results/zone2/rag_index/:
  knowledge.index       FAISS IndexFlatL2 (MiniLM vectors are L2-normalised,
                        so L2 ranking == cosine ranking)
  knowledge_texts.pkl   list[str]  (legacy, kept for backwards compatibility)
  knowledge_meta.json   list[dict] doc_id/condition/domain/source/... per row
"""

from __future__ import annotations

import json
import pickle
from pathlib import Path

try:
    import faiss
    from sentence_transformers import SentenceTransformer
except ImportError:
    pass  # Allow import for diagnostic tests even if not installed yet

from src.zone2_cloud.rag.kb_metadata import load_kb

KNOWLEDGE_BASE_DIR = Path(__file__).resolve().parent / "knowledge_base"
INDEX_DIR = Path(__file__).resolve().parents[3] / "results" / "zone2" / "rag_index"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def load_knowledge_entries() -> list[str]:
    """Plain-text bodies of every KB document (frontmatter stripped)."""
    return [d["text"] for d in load_kb(KNOWLEDGE_BASE_DIR)]


def build_index():
    """Embed entries + build FAISS index, persist to disk."""
    docs = load_kb(KNOWLEDGE_BASE_DIR)
    if not docs:
        print("No knowledge base entries found to index.")
        return
    entries = [d["text"] for d in docs]

    print(f"Loading SentenceTransformer model... (embedding {len(entries)} entries)")
    model = SentenceTransformer(EMBED_MODEL)
    embeddings = model.encode(entries, convert_to_numpy=True)

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(INDEX_DIR / "knowledge.index"))
    with open(INDEX_DIR / "knowledge_texts.pkl", "wb") as f:
        pickle.dump(entries, f)
    with open(INDEX_DIR / "knowledge_meta.json", "w", encoding="utf-8") as f:
        json.dump([{k: v for k, v in d.items() if k != "text"} for d in docs], f, indent=1)

    print(f"Successfully built FAISS index at {INDEX_DIR} ({len(docs)} docs)")


if __name__ == "__main__":
    build_index()
