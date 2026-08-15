"""
retriever.py — STUB. Person B, Zone 2.

GOAL: Given a query string (e.g. "tomato brown spots wilting"), return the
top-k most relevant knowledge base snippets from the index built by
build_knowledge_base.py. This becomes the `retrieved_knowledge` field of
contract.md #6.

EXPECTED FUNCTION SIGNATURE:

    def retrieve(query: str, k: int = 3) -> str:
        ...
        return "concatenated top-k snippets as a single string"

TODO:
  1. Load the FAISS/Chroma index built by build_knowledge_base.py.
  2. Embed the query with the SAME model used at index time
     ('sentence-transformers/all-MiniLM-L6-v2').
  3. Return the top-k matching snippets, concatenated into a single string
     (or a list — pick one, but keep it consistent with what
     gemini_client.py expects for `retrieved_knowledge`).

Suggested agent prompt:
    "Write retrieve(query, k=3) that loads the FAISS index saved by
    build_knowledge_base.py, embeds the query with the same sentence
    transformer, and returns the top-k matching knowledge snippets
    concatenated as one string."
"""

from __future__ import annotations


def retrieve(query: str, k: int = 3) -> str:
    raise NotImplementedError(
        "TODO: implement retrieval. Load index from build_knowledge_base.py, "
        "embed query, return top-k snippets."
    )


if __name__ == "__main__":
    import sys

    q = sys.argv[1] if len(sys.argv) > 1 else "tomato brown spots"
    print(retrieve(q))
