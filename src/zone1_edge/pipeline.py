"""
pipeline.py — Person A, Zone 1. THE end-to-end orchestrator.

Wires together, in order:
  1. task_router.route()              -> image expert output   (contract #1)
  2. multimodal.text_evidence.run()   -> text evidence output   (contract #3)
  3. multimodal.sensor_expert.run()   -> sensor output           (contract #4)  [livestock only, optional]
  4. multimodal.fusion.fuse()         -> fusion output           (contract #5)
  5. multimodal.confidence_gate.decide_route() -> final route + gate debug info
  6. knowledge.local_advisory.get_advisory()   -> ONLY if route == 'local'

This is exactly "Person A's whole pipeline" referenced in the plan
(Hour 6:45-7:30: "Wire Person A's whole pipeline into Streamlit tabs").
Person B's UI/cloud code calls `run_zone1_pipeline(...)` and branches on
`result["gate"]["route"]`.

Run the built-in self-test:
    python -m src.zone1_edge.pipeline --selftest
"""

from __future__ import annotations

import argparse
import json
from typing import Optional

from src.zone1_edge.task_router import task_router
from src.zone1_edge.multimodal import text_evidence, sensor_expert, fusion, confidence_gate
from src.zone1_edge.knowledge import local_advisory


def run_zone1_pipeline(
    domain: str,
    image_path: str,
    farmer_text: Optional[str] = None,
    sensor_reading: Optional[dict] = None,
    input_quality_ok: bool = True,
    mode: str = None,
) -> dict:
    """
    domain: "crop" | "livestock"
    image_path: path to the farmer's photo
    farmer_text: raw ASR text string from Person B's Hindi ASR (already
                 transcribed) OR None if no voice input was given
    sensor_reading: contract #4 dict, or None (crop domain never uses this)
    input_quality_ok: bool from the Capture+Quality Check step
    mode: "auto"|"real"|"mock" — forwarded to the image experts

    Returns a dict bundling every intermediate contract output PLUS the
    final advisory (if routed local) so both debugging and the UI can use
    whichever piece they need:

        {
          "image_output": {...contract #1...},
          "text_evidence": {...contract #3...} | None,
          "sensor_output": {...contract #4...} | None,
          "fusion": {...contract #5, pre-gate...},
          "gate": {...contract #5, post-gate, authoritative route...},
          "local_advisory": {...} | None   # None when route == "cloud"
        }
    """
    image_output = task_router.route(domain, image_path, mode=mode)

    text_ev = None
    if farmer_text:
        text_ev = text_evidence.run({"text": farmer_text, "language": "hi", "confidence": None})

    sensor_out = None
    if domain == "livestock" and sensor_reading is not None:
        sensor_out = sensor_expert.run(
            temperature=sensor_reading.get("temperature"),
            activity=sensor_reading.get("activity"),
            feed_intake=sensor_reading.get("feed_intake"),
            previous_reading=sensor_reading.get("previous_reading"),
        )

    fusion_out = fusion.fuse(image_output, text_ev, sensor_out)
    gate_out = confidence_gate.decide_route(fusion_out, input_quality_ok=input_quality_ok)

    local_adv = None
    if gate_out["route"] == "local":
        local_adv = local_advisory.get_advisory(gate_out["prediction"])

    return {
        "image_output": image_output,
        "text_evidence": text_ev,
        "sensor_output": sensor_out,
        "fusion": fusion_out,
        "gate": gate_out,
        "local_advisory": local_adv,
    }


def build_cloud_payload_stub(pipeline_result: dict, farm_history: str = "",
                              retrieved_knowledge: str = "") -> dict:
    """
    Convenience helper matching contract.md #6 shape, so Person B can see
    exactly what Zone 1 hands over when route == 'cloud'. Person B's real
    gemini_client.py will build this for real (with actual RAG retrieval +
    farm history from SQLite) — this stub just proves the shape is correct.
    """
    gate = pipeline_result["gate"]
    text_ev = pipeline_result["text_evidence"] or {"symptoms": []}
    sensor_out = pipeline_result["sensor_output"]
    return {
        "domain": pipeline_result["image_output"]["domain"],
        "image_prediction": gate["prediction"],
        "visual_confidence": gate["visual_confidence"],
        "farmer_text": "",  # Person B fills raw farmer text here
        "text_evidence": text_ev.get("symptoms", []),
        "sensor_data": sensor_out,
        "farm_history": farm_history,
        "retrieved_knowledge": retrieved_knowledge,
    }


def _selftest():
    """Runs a few synthetic scenarios through the whole pipeline, offline."""
    import os
    from PIL import Image

    tmp_dir = "/tmp/agrivision_selftest"
    os.makedirs(tmp_dir, exist_ok=True)
    crop_img = os.path.join(tmp_dir, "crop.jpg")
    livestock_img = os.path.join(tmp_dir, "livestock.jpg")
    Image.new("RGB", (64, 64), color=(120, 200, 80)).save(crop_img)
    Image.new("RGB", (64, 64), color=(200, 150, 100)).save(livestock_img)

    print("=" * 70)
    print("SCENARIO 1: Crop, with supporting Hindi text -> expect route=local")
    r1 = run_zone1_pipeline("crop", crop_img,
                              farmer_text="पत्तियों पर भूरे धब्बे और पीली पत्तियां हैं",
                              mode="mock")
    print(json.dumps(r1, indent=2, ensure_ascii=False))

    print("=" * 70)
    print("SCENARIO 2: Livestock, with anomalous sensor -> may escalate to cloud")
    r2 = run_zone1_pipeline("livestock", livestock_img,
                              farmer_text="गाय को बुखार है और लंगड़ा रही है",
                              sensor_reading={"temperature": 40.5, "activity": "low",
                                              "feed_intake": "very_low"},
                              mode="mock")
    print(json.dumps(r2, indent=2, ensure_ascii=False))

    print("=" * 70)
    print("SCENARIO 3: Crop, no text/sensor at all (image-only) -> ambiguous evidence")
    r3 = run_zone1_pipeline("crop", crop_img, mode="mock")
    print(json.dumps(r3, indent=2, ensure_ascii=False))

    print("=" * 70)
    print("SELFTEST PASSED: all 3 scenarios ran end-to-end with no exceptions.")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--selftest", action="store_true")
    p.add_argument("--domain", choices=["crop", "livestock"])
    p.add_argument("--image", type=str)
    p.add_argument("--text", type=str, default=None)
    args = p.parse_args()

    if args.selftest:
        _selftest()
    elif args.domain and args.image:
        result = run_zone1_pipeline(args.domain, args.image, farmer_text=args.text)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        p.print_help()
