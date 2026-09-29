"""
prepare_sft_dataset.py — Turn HUMAN-APPROVED synthetic advisories into SFT splits.

Quality gates (all must pass): review_status == approved (from the reviewed CSV),
validator passes, citations verify (no hallucinated doc IDs / history refs).
Split: stratified by condition, 80/10/10; the test split is never used for
training or validation and is what compare_backends.py evaluates on.

    python -m training.llm.prepare_sft_dataset --reviewed results/zone2/llm_data/review_sample.csv
"""

from __future__ import annotations

from training.paths import MODELS, RESULTS  # noqa: F401

import argparse
import csv
import json
import random
from collections import defaultdict
from pathlib import Path

from src.zone2_cloud.gemini.validator import validate_advisory, verify_citations
from src.zone2_cloud.llm.advisory_format import chat_messages

DATA = RESULTS / "zone2" / "llm_data"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default=str(DATA / "synthetic_advisories.jsonl"))
    ap.add_argument("--reviewed", required=True, help="review CSV with review_status column filled")
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()

    approved = set()
    with open(a.reviewed, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("review_status(approved/rejected)", "").strip().lower() == "approved":
                approved.add(row["scenario_id"])

    by_cond, dropped = defaultdict(list), defaultdict(int)
    for line in Path(a.input).read_text(encoding="utf-8").splitlines():
        rec = json.loads(line)
        if rec["scenario_id"] not in approved:
            dropped["not_approved"] += 1
            continue
        ok, _ = validate_advisory(rec["response"], [rec["payload"]["retrieved_knowledge"]], rec["payload"])
        if not ok:
            dropped["validator"] += 1
            continue
        if not verify_citations(rec["response"], rec["payload"])["citations_valid"]:
            dropped["citations"] += 1
            continue
        target = {k: v for k, v in rec["response"].items() if not k.startswith("_")}
        by_cond[rec["condition"]].append({
            "scenario_id": rec["scenario_id"], "condition": rec["condition"], "synthetic": True,
            "payload": rec["payload"],
            "messages": chat_messages(rec["payload"]) + [{"role": "assistant", "content": json.dumps(target, ensure_ascii=False)}],
        })

    splits = {"train": [], "val": [], "test": []}
    for cond, recs in sorted(by_cond.items()):
        random.Random(f"{a.seed}:{cond}").shuffle(recs)
        n_test = max(1, len(recs) // 10) if len(recs) >= 3 else 0
        n_val = max(1, len(recs) // 10) if len(recs) >= 3 else 0
        splits["test"] += recs[:n_test]
        splits["val"] += recs[n_test:n_test + n_val]
        splits["train"] += recs[n_test + n_val:]
    for name, recs in splits.items():
        with open(DATA / f"sft_{name}.jsonl", "w", encoding="utf-8") as f:
            f.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in recs)
    print({k: len(v) for k, v in splits.items()}, "dropped:", dict(dropped))


if __name__ == "__main__":
    main()
