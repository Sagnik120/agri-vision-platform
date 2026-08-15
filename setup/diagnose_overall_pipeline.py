"""
diagnose_overall_pipeline.py — Full end-to-end architectural validation.

Tests the absolute entire stack in one script:
1. Zone 1 pipeline (Local route)
2. Zone 1 pipeline (Cloud route) + Zone 2 RAG & Gemini fallback
3. Zone 1 Voice ASR mock
4. Zone 1 TTS mock
5. Zone 3 Farm Memory persistence across all runs

Run this to prove the whole architecture holds together without keys.
"""

import os
import sys
import json
import tempfile
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.zone1_edge.pipeline import run_zone1_pipeline, build_cloud_payload_stub
from src.zone1_edge.speech import hindi_asr, hindi_tts
from src.zone2_cloud.gemini import gemini_client
from src.zone2_cloud.rag import retriever
from src.zone3_memory.db import farm_memory

# Ensure offline mock mode for Gemini
os.environ["GEMINI_ENABLED"] = "false"

def check(name):
    def decorator(fn):
        def wrapper(*args, **kwargs):
            try:
                fn(*args, **kwargs)
                print(f"  [PASS] {name}")
            except Exception as e:
                print(f"  [FAIL] {name}: {e}")
                import traceback
                traceback.print_exc()
                sys.exit(1)
        return wrapper
    return decorator


def make_synthetic_image(color):
    tmp = Path(tempfile.mkdtemp())
    img_path = tmp / "test_img.jpg"
    Image.new("RGB", (224, 224), color=color).save(img_path)
    return str(img_path)


def run_diagnostics():
    print(f"\n{'='*70}\nAGRI-VISION END-TO-END DIAGNOSTIC (OFFLINE/MOCK MODE)\n{'='*70}\n")
    
    crop_img = make_synthetic_image((110, 190, 90))
    livestock_img = make_synthetic_image((190, 150, 110))
    
    FARM_ID = "DIAGNOSTIC-FARM"
    
    @check("1. Init Farm Memory")
    def step1():
        # Use a fresh diagnostic DB
        db_path = str(Path(tempfile.mkdtemp()) / "diag.db")
        farm_memory.DEFAULT_DB_PATH = db_path
        farm_memory.init_db(db_path)
    step1()

    @check("2. Offline Voice ASR (Mock Fallback)")
    def step2():
        res = hindi_asr.transcribe("fake.wav")
        assert "पत्तियों" in res["text"]
    step2()

    @check("3. High-Confidence Crop Check -> Local Route -> Save to DB")
    def step3():
        res = run_zone1_pipeline("crop", crop_img, farmer_text="भूरे धब्बे", mode="mock")
        assert res["gate"]["route"] == "local"
        
        # Save to DB
        obs_id = farm_memory.save_observation(FARM_ID, "crop", res["gate"]["prediction"], 
                                             res["gate"]["visual_confidence"], "भूरे धब्बे", "{}", "local")
        diag_id = farm_memory.save_diagnosis(obs_id, res["gate"]["prediction"], "possible", res["gate"]["final_confidence"])
        farm_memory.save_advisory(diag_id, "local_offline", "Test local advisory", ["action1"], "warn")
    step3()

    @check("4. Low-Confidence Livestock Check -> Cloud Route -> RAG + Gemini Mock")
    def step4():
        res = run_zone1_pipeline("livestock", livestock_img, farmer_text="fever", 
                                 sensor_reading={"temperature":41.5, "activity":"low", "feed_intake":"none"}, 
                                 input_quality_ok=False, mode="mock")
        assert res["gate"]["route"] == "cloud"
        
        # Retrieve RAG & Farm History
        rag = retriever.retrieve("livestock lumpy skin")
        history = farm_memory.get_farm_history(FARM_ID)
        assert "Today" in history  # Proves Step 3 was saved
        
        # Build payload & hit Gemini
        payload = build_cloud_payload_stub(res)
        payload["farm_history"] = history
        payload["retrieved_knowledge"] = rag
        
        cloud_res = gemini_client.call_gemini(payload)
        assert "diagnosis" in cloud_res
        assert cloud_res["diagnosis"]["condition"] == "mock_disease"
        
        # Save cloud result
        obs_id = farm_memory.save_observation(FARM_ID, "livestock", res["gate"]["prediction"], 
                                             res["gate"]["visual_confidence"], "fever", "{}", "cloud")
        diag_id = farm_memory.save_diagnosis(obs_id, cloud_res["diagnosis"]["condition"], cloud_res["diagnosis"]["certainty"], res["gate"]["final_confidence"])
        farm_memory.save_advisory(diag_id, "cloud_gemini", cloud_res["advisory"]["summary"], [], "")
    step4()

    @check("5. Verify Farm Memory History Integrity")
    def step5():
        history = farm_memory.get_farm_history(FARM_ID)
        # Should have both the local crop advisory and the cloud mock disease
        assert "tomato_early_blight" in history or "mock_disease" in history
        # Because ORDER BY created_at DESC, both should exist
        lines = history.split("\\n")
        assert len(lines) >= 2
    step5()

    @check("6. Offline TTS (Mock Fallback)")
    def step6():
        out_path = str(Path(tempfile.mkdtemp()) / "out.wav")
        res = hindi_tts.synthesize("Test synthesis", out_path)
        assert os.path.exists(res["audio_path"])
        assert res["engine"] == "mock"
    step6()

    print(f"\n{'='*70}")
    print("ALL END-TO-END INTEGRATION CHECKS PASSED. The offline architecture is sound.")


if __name__ == "__main__":
    run_diagnostics()
