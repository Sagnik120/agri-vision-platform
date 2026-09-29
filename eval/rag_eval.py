"""
rag_eval.py — Retrieval quality + citation-correctness evaluation (Phase 3).

Retrieval: precision@k / recall@k / hit@k / MRR over eval/rag_queries.json,
per backend (lexical BM25 vs FAISS) and optionally with cross-encoder rerank.

    python eval/rag_eval.py --backend lexical
    python eval/rag_eval.py --backend faiss            (needs rebuilt index: python -m src.zone2_cloud.rag.build_knowledge_base)
    RAG_RERANK_MODEL=BAAI/bge-reranker-v2-m3 python eval/rag_eval.py --backend faiss --rerank

Citation correctness over logged advisories (JSONL of {"payload":..., "response":...},
written by training/llm/compare_backends.py):
    python eval/rag_eval.py --citations results/zone2/llm_compare/gemini.jsonl

Reports -> results/zone2/rag_eval/
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.zone2_cloud.gemini.validator import verify_citations  # noqa: E402
from src.zone2_cloud.rag.retriever import retrieve_docs  # noqa: E402

from training.paths import RESULTS  # noqa: E402

OUT = RESULTS / "zone2" / "rag_eval"


def retrieval_metrics(queries: list[dict], k: int, backend: str, rerank: bool) -> dict:
    p_sum = r_sum = hit_sum = mrr_sum = 0.0
    rows = []
    for item in queries:
        got = [d["doc_id"] for d in retrieve_docs(item["q"], k=k, backend=backend, rerank=rerank)]
        rel = set(item["relevant"])
        tp = sum(1 for d in got if d in rel)
        rank = next((i + 1 for i, d in enumerate(got) if d in rel), None)
        p_sum += tp / k
        r_sum += tp / len(rel)
        hit_sum += 1.0 if tp else 0.0
        mrr_sum += 1.0 / rank if rank else 0.0
        rows.append({"q": item["q"], "retrieved": got, "relevant": sorted(rel), "hit": bool(tp)})
    n = max(len(queries), 1)
    return {"k": k, "backend": backend, "rerank": rerank, "n_queries": len(queries),
            f"precision@{k}": round(p_sum / n, 4), f"recall@{k}": round(r_sum / n, 4),
            f"hit@{k}": round(hit_sum / n, 4), "mrr": round(mrr_sum / n, 4), "per_query": rows}


def citation_metrics(jsonl_path: str) -> dict:
    n = valid = with_cit = hist_needed = hist_ok = 0
    for line in Path(jsonl_path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        chk = verify_citations(rec.get("response") or {}, rec.get("payload") or {})
        n += 1
        with_cit += chk["has_citation"]
        valid += chk["has_citation"] and not chk["hallucinated_doc_ids"]
        if "[H" in str((rec.get("payload") or {}).get("farm_history", "")):
            hist_needed += 1
            hist_ok += bool(chk["farm_history_refs"]) and not chk["hallucinated_history_refs"]
    return {"file": jsonl_path, "n": n,
            "citation_presence_rate": round(with_cit / max(n, 1), 4),
            "citation_correctness_rate": round(valid / max(n, 1), 4),
            "farm_history_citation_correctness_rate": round(hist_ok / hist_needed, 4) if hist_needed else None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--queries", default="eval/rag_queries.json")
    ap.add_argument("--backend", default="auto", choices=["auto", "faiss", "lexical"])
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--rerank", action="store_true")
    ap.add_argument("--citations", help="JSONL of logged advisories to score instead of retrieval")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    if a.citations:
        rep = citation_metrics(a.citations)
        name = f"citations_{Path(a.citations).stem}.json"
    else:
        spec = json.loads(Path(a.queries).read_text(encoding="utf-8"))
        rep = retrieval_metrics(spec["queries"], a.k, a.backend, a.rerank)
        rep["labels_reviewed"] = spec.get("reviewed", False)
        name = f"retrieval_{a.backend}_k{a.k}{'_rerank' if a.rerank else ''}.json"
    (OUT / name).write_text(json.dumps(rep, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in rep.items() if k != "per_query"}, indent=1))
    if not a.citations and not rep["labels_reviewed"]:
        print("NOTE: relevance labels are an unreviewed draft — treat numbers as provisional.")


if __name__ == "__main__":
    main()
