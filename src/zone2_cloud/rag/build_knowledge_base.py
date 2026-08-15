"""
build_knowledge_base.py — STUB. Person B, Zone 2 (Hour 4:15-5:15 of the plan).

GOAL: Write 8-10 short knowledge entries (Condition / Symptoms / Visual
indicators / Recommended actions / Prevention / When to seek expert /
Source) as .md or .json files in `rag/knowledge_base/`, then embed them with
a small sentence-transformer and index with FAISS or Chroma.

Cover (per the plan): tomato early/late blight, potato early/late blight,
maize rust, maize leaf blight, lumpy skin disease, FMD, abnormal
temperature/activity. This deliberately overlaps with Person A's
knowledge/local_advisories.json (Zone 1, offline) — the RAG version is
richer/longer-form and used ONLY on the cloud-escalation path.

TODO:
  1. Write 8-10 entries into rag/knowledge_base/*.md (one file per condition,
     or one combined .json — your choice, just document it here once decided).
  2. `pip install sentence-transformers faiss-cpu` (or chromadb — pick one).
  3. Embed each entry with 'sentence-transformers/all-MiniLM-L6-v2'.
  4. Build and persist a FAISS index (or Chroma collection) to disk so it
     doesn't need rebuilding every app restart — save it under
     `results/zone2/` or a dedicated `rag/index/` folder (git-ignore the
     binary index file, keep the source .md/.json entries in git).

Suggested agent prompt:
    "Write a script that reads all .md files in rag/knowledge_base/, embeds
    them with sentence-transformers/all-MiniLM-L6-v2, and builds a FAISS
    IndexFlatL2 index, saving both the index and a parallel list of source
    texts to disk for later retrieval."
"""

from __future__ import annotations

from pathlib import Path

KNOWLEDGE_BASE_DIR = Path(__file__).resolve().parent / "knowledge_base"


def load_knowledge_entries() -> list:
    """TODO: read every .md/.json file in KNOWLEDGE_BASE_DIR and return a
    list of plain-text chunks ready for embedding."""
    raise NotImplementedError("TODO: implement knowledge entry loading.")


def build_index():
    """TODO: embed entries + build FAISS/Chroma index, persist to disk."""
    raise NotImplementedError("TODO: implement index building. See module docstring.")


if __name__ == "__main__":
    build_index()
