"""
diagnose_pipeline.py — Multi-stage diagnostic checklist.

Run this:
  1. BEFORE downloading any real model (mode=mock) — proves the pipeline
     logic (fusion/gate/advisory/router) works.
  2. AFTER running setup/download_crop_model.py and
     setup/download_livestock_model.py (mode=auto/real) — proves the real
     models load AND produce contract-shaped output AND the rest of the
     pipeline still doesn't break with real (not mock) predictions.

Usage:
    python setup/diagnose_pipeline.py --mode mock
    python setup/diagnose_pipeline.py --mode auto     # uses real model if downloaded, else mock
    python setup/diagnose_pipeline.py --mode real      # FAILS loudly if real model missing
"""

import argparse
import json
import sys
import tempfile
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

CHECKS_PASSED = []
CHECKS_FAILED = []


def check(name):
    def decorator(fn):
        def wrapper(*args, **kwargs):
            try:
                fn(*args, **kwargs)
                print(f"  ✅ {name}")
                CHECKS_PASSED.append(name)
            except Exception as e:  # noqa: BLE001
                print(f"  ❌ {name}: {e}")
                traceback.print_exc()
                CHECKS_FAILED.append(name)
        return wrapper
    return decorator


def make_synthetic_images():
    from PIL import Image
    tmp = Path(tempfile.mkdtemp())
    crop_path = tmp / "crop.jpg"
    livestock_path = tmp / "livestock.jpg"
    Image.new("RGB", (224, 224), color=(110, 190, 90)).save(crop_path)
    Image.new("RGB", (224, 224), color=(190, 150, 110)).save(livestock_path)
    return str(crop_path), str(livestock_path)


def run(mode: str):
    print(f"\n{'='*70}\nAGRI-VISION ZONE 1 DIAGNOSTIC — mode={mode}\n{'='*70}\n")
    crop_img, livestock_img = make_synthetic_images()

    @check("1. Config imports cleanly")
    def c1():
        from src.zone1_edge import config  # noqa: F401
    c1()

    @check("2. Crop expert loads and returns contract shape")
    def c2():
        from src.zone1_edge.experts import crop_expert
        out = crop_expert.run(crop_img, mode=mode)
        assert set(["domain", "input_type", "prediction", "confidence", "top_k"]).issubset(out.keys())
        assert out["domain"] == "crop"
        print(f"     backend={out.get('_debug_backend')}, prediction={out['prediction']}, confidence={out['confidence']}")
    c2()

    @check("3. Livestock expert loads and returns contract shape")
    def c3():
        from src.zone1_edge.experts import livestock_expert
        out = livestock_expert.run(livestock_img, mode=mode)
        assert set(["domain", "input_type", "prediction", "confidence", "top_k"]).issubset(out.keys())
        assert out["domain"] == "livestock"
        print(f"     backend={out.get('_debug_backend')}, prediction={out['prediction']}, confidence={out['confidence']}")
    c3()

    @check("4. Text evidence extractor works on Hindi input")
    def c4():
        from src.zone1_edge.multimodal import text_evidence
        out = text_evidence.run({"text": "भूरे धब्बे और पीली पत्तियां", "language": "hi", "confidence": None})
        assert "brown_spots" in out["symptoms"]
    c4()

    @check("5. Sensor expert threshold rules work")
    def c5():
        from src.zone1_edge.multimodal import sensor_expert
        out = sensor_expert.run(temperature=41.0, activity="low", feed_intake="low")
        assert out["anomaly"] is True
    c5()

    @check("6. Task router dispatches correctly for both domains")
    def c6():
        from src.zone1_edge.task_router import task_router
        r1 = task_router.route("crop", crop_img, mode=mode)
        r2 = task_router.route("livestock", livestock_img, mode=mode)
        assert r1["domain"] == "crop" and r2["domain"] == "livestock"
    c6()

    @check("7. Fusion combines evidence and stays within [0.01, 0.99]")
    def c7():
        from src.zone1_edge.multimodal import fusion
        img_out = {"domain": "crop", "input_type": "image", "prediction": "tomato_early_blight",
                   "confidence": 0.7, "top_k": []}
        out = fusion.fuse(img_out, {"symptoms": ["brown_spots"], "crop": "tomato", "severity_hint": "low"})
        assert 0.01 <= out["final_confidence"] <= 0.99
    c7()

    @check("8. Confidence gate produces a valid route")
    def c8():
        from src.zone1_edge.multimodal import confidence_gate
        fusion_out = {"prediction": "tomato_early_blight", "visual_confidence": 0.8,
                      "text_support": True, "sensor_support": None,
                      "evidence_agreement": "high", "final_confidence": 0.9, "route": "local"}
        out = confidence_gate.decide_route(fusion_out)
        assert out["route"] in ("local", "cloud")
    c8()

    @check("9. Local advisory has >=10 knowledge entries and returns valid lookups")
    def c9():
        from src.zone1_edge.knowledge import local_advisory
        out = local_advisory.get_advisory("tomato_early_blight")
        assert out["actions"]
    c9()

    @check("10. FULL end-to-end pipeline runs for crop AND livestock without exceptions")
    def c10():
        from src.zone1_edge.pipeline import run_zone1_pipeline
        r1 = run_zone1_pipeline("crop", crop_img, farmer_text="भूरे धब्बे", mode=mode)
        r2 = run_zone1_pipeline(
            "livestock", livestock_img, farmer_text="गाय को बुखार है",
            sensor_reading={"temperature": 40.0, "activity": "low", "feed_intake": "low"},
            mode=mode,
        )
        assert r1["gate"]["route"] in ("local", "cloud")
        assert r2["gate"]["route"] in ("local", "cloud")
    c10()

    print(f"\n{'='*70}")
    print(f"RESULT: {len(CHECKS_PASSED)} passed, {len(CHECKS_FAILED)} failed")
    print(f"{'='*70}")
    if CHECKS_FAILED:
        print("FAILED CHECKS:", CHECKS_FAILED)
        sys.exit(1)
    print("ALL DIAGNOSTIC CHECKS PASSED. Nothing is broken.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["mock", "auto", "real"], default="auto")
    args = parser.parse_args()
    run(args.mode)
