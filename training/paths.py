"""
paths.py — Where big files live. Set AGRIVISION_DATA_ROOT (e.g. /DATA1/shrusti/agri-vision-platform) to keep
datasets, checkpoints, ONNX models, reports, synthetic data and logs OFF the repo/home disk.
Unset -> repo-relative paths (old behaviour). Layout under the root:

    data/        datasets (plantvillage/, cattle/)          -> DATA
    models_cache/  moe/<group>/, moe/*_moe_gate.json, llm/  -> MODELS   (same dir src/ reads via config.MODEL_CACHE_DIR)
    results/     eval reports, gate reports, llm_data, ...  -> RESULTS
    logs/        nohup logs (shell-level)
"""

import os
from pathlib import Path

ROOT = Path(os.environ["AGRIVISION_DATA_ROOT"]) if os.environ.get("AGRIVISION_DATA_ROOT") else None
DATA = (ROOT / "data") if ROOT else Path("data")
MODELS = (ROOT / "models_cache") if ROOT else Path("models_cache")
RESULTS = (ROOT / "results") if ROOT else Path("results")
