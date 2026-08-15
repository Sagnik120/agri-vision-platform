"""
retriever.py — Person B, Zone 2.

GOAL: Given a query string, return the top-k most relevant knowledge base snippets 
from the index built by build_knowledge_base.py.
"""

from __future__ import annotations

import os
import pickle
from pathlib import Path

try:
    import faiss
    from sentence_transformers import SentenceTransformer
except ImportError:
    pass

INDEX_DIR = Path(__file__).resolve().parents[3] / "results" / "zone2" / "rag_index"

# Keep the model and index loaded globally so we don't reload on every retrieval
_model = None
_index = None
_texts = None

def _load_resources():
    global _model, _index, _texts
    if _model is not None:
        return
        
    index_path = INDEX_DIR / "knowledge.index"
    texts_path = INDEX_DIR / "knowledge_texts.pkl"
    
    if not index_path.exists() or not texts_path.exists():
        raise FileNotFoundError(f"Index or texts not found in {INDEX_DIR}. Did you run build_knowledge_base.py?")
        
    _model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    _index = faiss.read_index(str(index_path))
    
    with open(texts_path, "rb") as f:
        _texts = pickle.load(f)

def retrieve(query: str, k: int = 3) -> str:
    """Load index, embed query, return top-k snippets concatenated as one string."""
    _load_resources()
    
    query_vector = _model.encode([query], convert_to_numpy=True)
    
    # Check if k is greater than total available texts
    actual_k = min(k, len(_texts))
    if actual_k == 0:
        return ""
        
    distances, indices = _index.search(query_vector, actual_k)
    
    results = []
    for idx in indices[0]:
        if idx >= 0 and idx < len(_texts):
            results.append(_texts[idx])
            
    return "\n\n---\n\n".join(results)


if __name__ == "__main__":
    import sys
    q = sys.argv[1] if len(sys.argv) > 1 else "tomato brown spots"
    print(retrieve(q))
