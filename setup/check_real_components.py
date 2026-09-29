"""
check_real_components.py — Tell me what is REAL vs MOCK right now. Offline: makes NO network/API calls
and never prints secrets (only whether GEMINI_ENABLED is true).

    python setup/check_real_components.py
"""
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("HF_HUB_OFFLINE", "1")  # never download during a check
from dotenv import load_dotenv  # noqa: E402

load_dotenv()

from PIL import Image  # noqa: E402

from src.zone1_edge import config  # noqa: E402

print(f"AGRIVISION_EXPERT_MODE = {config.EXPERT_MODE}   (mock = fake predictor; auto = real if loadable else SILENT mock)")
img = Path(tempfile.gettempdir()) / "agri_check.jpg"
Image.new("RGB", (224, 224), (60, 140, 60)).save(img)
for name, mod in (("crop", "crop_expert"), ("livestock", "livestock_expert")):
    try:
        m = __import__(f"src.zone1_edge.experts.{mod}", fromlist=["x"])
        out = m.run(str(img), mode="real")
        print(f"[OK  ] {name} expert REAL -> {out['_backend']}")
    except Exception as e:  # noqa: BLE001
        print(f"[MOCK] {name} expert cannot load a real model: {str(e)[:120]}")
from src.zone1_edge.moe import moe_expert  # noqa: E402

for d in ("crop", "livestock"):
    print(f"[{'OK  ' if moe_expert.moe_enabled(d, 'auto') else 'off '}] MoE {d}: {'active' if moe_expert.moe_enabled(d, 'auto') else 'inactive (no trained gate/ONNX in models_cache/moe)'}")
from src.zone2_cloud.rag.retriever import retrieve_docs  # noqa: E402

d = retrieve_docs("tomato brown spots", k=1)
print(f"[OK  ] RAG backend = {d[0]['backend']} ({d[0]['doc_id']})" if d else "[FAIL] RAG returned nothing")
g = os.environ.get("GEMINI_ENABLED", "false").lower() == "true"
print(f"[{'OK  ' if g else 'MOCK'}] Gemini: GEMINI_ENABLED={g}")
print(f"ADVISORY_BACKEND={os.environ.get('ADVISORY_BACKEND', 'gemini')}  WEATHER_ENABLED={os.environ.get('WEATHER_ENABLED', 'false')}")
