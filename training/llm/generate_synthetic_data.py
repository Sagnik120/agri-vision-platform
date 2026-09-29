"""
generate_synthetic_data.py — Build SYNTHETIC advisory training data (user-run).

Why synthetic: Zone 3 SQLite holds few, template-like records (local advisories
are lookup-table text), too small/rigid to fine-tune a generative LLM. Audit:
    python -m training.llm.generate_synthetic_data --audit-db

Each scenario = KB condition x region x season x weather x history x evidence,
rendered with the SAME format the runtime uses (advisory_format.py), with
retrieved docs tagged [KB-..] and history lines tagged [H..].

Step 1 (no API calls):   --dry-run  -> writes scenarios/prompts only
Step 2 (CALLS GEMINI, one call per scenario; user only) — safe to run in small daily batches, it resumes:
    GEMINI_ENABLED=true python -m training.llm.generate_synthetic_data --n 15 --i-understand-this-calls-gemini
    -> review the sample (review_sample.csv), then scale up --n.
Every record is tagged synthetic=true, review_status=pending. prepare_sft_dataset.py
only uses records a human marked `approved`.
"""

from __future__ import annotations

from training.paths import MODELS, RESULTS  # noqa: F401

import argparse
import csv
import json
import os
import random
import sqlite3
from pathlib import Path

from src.zone2_cloud.gemini.validator import validate_advisory, verify_citations
from src.zone2_cloud.llm.advisory_format import SYSTEM_INSTRUCTIONS, parse_json_output, user_message
from src.zone2_cloud.rag.kb_metadata import load_kb
from src.zone2_cloud.rag.retriever import KB_DIR, format_docs, retrieve_docs

OUT = RESULTS / "zone2" / "llm_data"
REGIONS = ["Maharashtra", "Punjab", "Uttar Pradesh", "Karnataka", "West Bengal", "Gujarat", "Tamil Nadu", "Bihar", None]
SEASONS = ["kharif", "rabi", "zaid"]
WEATHER = [None,
           {"temperature_c": 29, "relative_humidity_pct": 88, "precipitation_last_7d_mm": 95.0, "source": "synthetic"},
           {"temperature_c": 17, "relative_humidity_pct": 70, "precipitation_last_7d_mm": 3.0, "source": "synthetic"},
           {"temperature_c": 39, "relative_humidity_pct": 25, "precipitation_last_7d_mm": 0.0, "source": "synthetic"}]


def audit_db(db_path="results/zone3/farm_memory.db"):  # the farm DB stays in the repo
    if not Path(db_path).exists():
        print("No farm memory DB found -> 0 real records.")
        return
    with sqlite3.connect(db_path) as c:
        n_obs = c.execute("SELECT COUNT(*) FROM observations").fetchone()[0]
        n_adv = c.execute("SELECT COUNT(*) FROM advisories").fetchone()[0]
        by_src = c.execute("SELECT source, COUNT(*) FROM advisories GROUP BY source").fetchall()
    print(f"observations={n_obs} advisories={n_adv} by_source={by_src} (mock/demo runs included)")


def make_scenario(doc: dict, rng: random.Random, i: int) -> dict:
    confidence = round(rng.uniform(0.35, 0.79), 2)  # cloud path = low/ambiguous confidence cases
    history = ""
    if rng.random() < 0.5:
        hid = rng.randint(1, 500)
        past = rng.choice([doc["condition"], "healthy" if doc["domain"] == "livestock" else "crop_healthy"])
        history = f"[H{hid}] {rng.randint(3, 60)} days ago: {past} (possible), advised: follow-up check"
    query = f"{doc['condition'].replace('_', ' ')}"
    docs = retrieve_docs(query, k=3, backend="lexical")
    return {
        "scenario_id": f"syn-{i:05d}", "synthetic": True, "review_status": "pending",
        "condition": doc["condition"],
        "payload": {
            "domain": doc["domain"], "image_prediction": doc["condition"], "visual_confidence": confidence,
            "farmer_text": "", "text_evidence": [], "sensor_data": None,
            "farm_history": history or "No prior history for this farm.",
            "retrieved_knowledge": format_docs(docs),
            "region": rng.choice(REGIONS), "season": rng.choice(SEASONS), "weather": rng.choice(WEATHER),
        },
    }


def call_gemini_raw(payload: dict) -> dict:
    from google import genai  # user-run only

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    resp = client.models.generate_content(
        model=os.environ.get("GEMINI_MODEL", "gemini-2.5-flash-lite"),
        contents=SYSTEM_INSTRUCTIONS + "\n\n" + user_message(payload),
        config=genai.types.GenerateContentConfig(response_mime_type="application/json", temperature=0.7),
    )
    return parse_json_output(resp.text)


def main():
    from dotenv import load_dotenv

    load_dotenv()  # reads GEMINI_* / LOCAL_LLM_* from .env in the current directory (never printed)
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=15, help="MAX number of NEW Gemini calls this run (= one call per scenario)")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--dry-run", action="store_true", help="build scenarios only; NO Gemini call, writes scenarios_dry_run.jsonl")
    ap.add_argument("--audit-db", action="store_true")
    ap.add_argument("--max-consecutive-failures", type=int, default=3,
                    help="stop early (quota/key problem) instead of burning more calls")
    ap.add_argument("--i-understand-this-calls-gemini", action="store_true")
    a = ap.parse_args()
    if a.audit_db:
        return audit_db()
    if not a.dry_run and not a.i_understand_this_calls_gemini:
        raise SystemExit("Refusing to call Gemini without --i-understand-this-calls-gemini (or use --dry-run).")

    docs = load_kb(KB_DIR)
    OUT.mkdir(parents=True, exist_ok=True)

    if a.dry_run:  # never touches the real data / review files
        with open(OUT / "scenarios_dry_run.jsonl", "w", encoding="utf-8") as f:
            for i in range(a.n):
                rec = make_scenario(docs[i % len(docs)], random.Random(f"{a.seed}:{i}"), i)
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(f"[dry-run] wrote {a.n} scenarios to {OUT / 'scenarios_dry_run.jsonl'} (0 Gemini calls).")
        return

    out_path, csv_path = OUT / "synthetic_advisories.jsonl", OUT / "review_sample.csv"
    done = set()  # resume: scenarios already generated in earlier runs are skipped (no repeat API cost)
    if out_path.exists():
        done = {json.loads(l)["scenario_id"] for l in out_path.read_text(encoding="utf-8").splitlines() if l.strip()}
    new_csv = not csv_path.exists() or csv_path.stat().st_size == 0
    calls = fails_in_row = 0
    with open(out_path, "a", encoding="utf-8") as f, open(csv_path, "a", newline="", encoding="utf-8") as rf:
        rw = csv.writer(rf)
        if new_csv:
            rw.writerow(["scenario_id", "condition", "region", "season", "summary", "actions", "cited_doc_ids",
                         "auto_valid", "review_status(approved/rejected)", "reviewer_notes"])
        i = 0
        while calls < a.n:
            sid = f"syn-{i:05d}"
            rec = make_scenario(docs[i % len(docs)], random.Random(f"{a.seed}:{i}"), i)
            i += 1
            if sid in done:
                continue
            calls += 1  # counts every attempt, successful or not
            try:
                resp = call_gemini_raw(rec["payload"])
                fails_in_row = 0
            except Exception as e:  # noqa: BLE001
                fails_in_row += 1
                print(f"{sid}: generation failed ({type(e).__name__})")
                if fails_in_row >= a.max_consecutive_failures:
                    print("Too many consecutive failures (quota, key or network?). Stopping to avoid wasting calls.")
                    break
                continue
            ok, reasons = validate_advisory(resp, [rec["payload"]["retrieved_knowledge"]], rec["payload"])
            rec.update({"response": resp, "auto_valid": ok, "auto_reasons": reasons,
                        "citation_check": verify_citations(resp, rec["payload"])})
            adv = resp.get("advisory", {})
            rw.writerow([rec["scenario_id"], rec["condition"], rec["payload"]["region"], rec["payload"]["season"],
                         adv.get("summary", ""), " | ".join(adv.get("actions", [])),
                         ",".join(resp.get("cited_doc_ids", [])), ok, "", ""])
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            f.flush()
            rf.flush()
    print(f"Gemini calls made this run: {calls}. "
          f"Review {csv_path} before any training.")


if __name__ == "__main__":
    main()
