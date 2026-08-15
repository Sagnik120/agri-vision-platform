"""
build_knowledge_base.py — Person B, Zone 2.

GOAL: Write 8-10 short knowledge entries as .md files in `rag/knowledge_base/`, 
then embed them with a small sentence-transformer and index with FAISS.
"""

from __future__ import annotations

import os
import pickle
from pathlib import Path

try:
    import faiss
    from sentence_transformers import SentenceTransformer
except ImportError:
    pass  # Allow import for diagnostic tests even if not installed yet

KNOWLEDGE_BASE_DIR = Path(__file__).resolve().parent / "knowledge_base"
INDEX_DIR = Path(__file__).resolve().parents[3] / "results" / "zone2" / "rag_index"


def load_knowledge_entries() -> list[str]:
    """Read every .md file in KNOWLEDGE_BASE_DIR and return a list of plain-text chunks."""
    entries = []
    for md_file in KNOWLEDGE_BASE_DIR.glob("*.md"):
        if md_file.name == "README.md":
            continue
        with open(md_file, "r", encoding="utf-8") as f:
            entries.append(f.read().strip())
    return entries


def build_index():
    """Embed entries + build FAISS index, persist to disk."""
    entries = load_knowledge_entries()
    if not entries:
        print("No knowledge base entries found to index.")
        return

    print(f"Loading SentenceTransformer model... (embedding {len(entries)} entries)")
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    
    embeddings = model.encode(entries, convert_to_numpy=True)
    
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    
    faiss.write_index(index, str(INDEX_DIR / "knowledge.index"))
    
    with open(INDEX_DIR / "knowledge_texts.pkl", "wb") as f:
        pickle.dump(entries, f)
        
    print(f"Successfully built FAISS index at {INDEX_DIR}")


if __name__ == "__main__":
    build_index()
