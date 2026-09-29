"""
compare_backends.py — Fine-tuned LLM vs Gemini on the SAME held-out SFT test split.

Metrics per backend: schema-validity rate, validator pass rate, citation
correctness rate, farm-history-reference correctness rate. Raw outputs are logged
to JSONL so humans can do qualitative review. No winner is declared by this
script — it only reports what the run produced.

User-run (gemini CALLS the paid API; local_llm calls your LOCAL_LLM_URL server):
    GEMINI_ENABLED=true python -m training.llm.compare_backends --backend gemini --i-understand-this-calls-gemini
    ADVISORY_BACKEND=local_llm LOCAL_LLM_URL=http://localhost:8000/v1 python -m training.llm.compare_backends --backend local_llm
Offline plumbing check (no network):  python -m training.llm.compare_backends --backend mock --limit 5
"""

from __future__ import annotations

from training.paths import MODELS, RESULTS  # noqa: F401

import argparse
import json
import os
from pathlib import Path

from src.zone2_cloud.gemini.validator import validate_advisory

DATA = RESULTS / "zone2" / "llm_data"
OUT = RESULTS / "zone2" / "llm_compare"
REQUIRED = {"diagnosis", "advisory", "expert_consultation_recommended", "cited_knowledge",
            "farm_history_acknowledged", "cited_doc_ids", "farm_history_refs"}


def run_backend(name: str, payload: dict) -> dict:
    if name == "local_llm":
        from src.zone2_cloud.llm.local_llm_client import LocalLLMClient
        return LocalLLMClient().generate(payload)
    from src.zone2_cloud.gemini import gemini_client
    if name == "mock":
        os.environ["GEMINI_ENABLED"] = "false"
    return gemini_client.call_gemini(payload)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", choices=["gemini", "local_llm", "mock"], required=True)
    ap.add_argument("--test", default=str(DATA / "sft_test.jsonl"))
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--i-understand-this-calls-gemini", action="store_true")
    a = ap.parse_args()
    if a.backend == "gemini" and not a.i_understand_this_calls_gemini:
        raise SystemExit("Refusing to call Gemini without --i-understand-this-calls-gemini.")

    recs = [json.loads(l) for l in Path(a.test).read_text(encoding="utf-8").splitlines() if l.strip()]
    if a.limit:
        recs = recs[: a.limit]
    OUT.mkdir(parents=True, exist_ok=True)
    log_path = OUT / f"{a.backend}.jsonl"
    n = schema_ok = valid = 0
    with open(log_path, "w", encoding="utf-8") as f:
        for r in recs:
            n += 1
            try:
                resp = run_backend(a.backend, r["payload"])
            except Exception as e:  # noqa: BLE001
                resp = {"_error": type(e).__name__}
            schema_ok += isinstance(resp, dict) and REQUIRED.issubset(resp)
            ok, _ = validate_advisory(resp, [r["payload"]["retrieved_knowledge"]], r["payload"]) if "_error" not in resp else (False, [])
            valid += ok
            f.write(json.dumps({"scenario_id": r.get("scenario_id"), "payload": r["payload"], "response": resp}, ensure_ascii=False) + "\n")

    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from eval.rag_eval import citation_metrics
    rep = {"backend": a.backend, "n": n, "schema_validity_rate": round(schema_ok / max(n, 1), 4),
           "validator_pass_rate": round(valid / max(n, 1), 4), **citation_metrics(str(log_path))}
    (OUT / f"{a.backend}_report.json").write_text(json.dumps(rep, indent=1), encoding="utf-8")
    print(json.dumps(rep, indent=1))


if __name__ == "__main__":
    main()
