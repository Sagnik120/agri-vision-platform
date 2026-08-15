"""
config.py — Single source of truth for Zone 1 (Person A).

Change model repo IDs, thresholds, and paths here ONLY. Every other module
imports from this file so nothing is hard-coded in two places.

Author: Person A track — Agri-Vision Platform
HF namespace used for any model mirrors/checkpoints re-uploaded by us: Sagnik120
"""

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]          # repo root
ZONE1_ROOT = Path(__file__).resolve().parent                # src/zone1_edge
DEMO_DATA_DIR = ZONE1_ROOT / "demo_data"
KNOWLEDGE_DIR = ZONE1_ROOT / "knowledge"
RESULTS_DIR = PROJECT_ROOT / "results" / "zone1"
MODEL_CACHE_DIR = Path(
    os.environ.get("AGRIVISION_MODEL_CACHE", PROJECT_ROOT / "models_cache")
)

for d in [RESULTS_DIR / "crop_model", RESULTS_DIR / "livestock_model",
          RESULTS_DIR / "fusion_runs", MODEL_CACHE_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Hugging Face model IDs (pretrained, NOT trained by us)
# ---------------------------------------------------------------------------
# Crop disease classifier — PlantVillage-finetuned MobileNetV3 / similar ViT.
# NOTE: exact HF repo availability changes; download_crop_model.py tries this
# ordered list and falls back to the next one if a repo 404s.
CROP_MODEL_CANDIDATES = [
    "linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification",
    "wambugu71/crop_leaf_diseases_vit",
    "nateraw/plant-disease-vit-b16",
]
CROP_MODEL_LOCAL_DIR = MODEL_CACHE_DIR / "crop_model"

# Livestock / cattle disease classifier — EfficientNet-B3 class model.
# Cattle-disease-specific checkpoints are scarce on HF; we try a couple of
# candidates and the download script clearly logs which one actually loaded.
# If none work, expert falls back to a general animal/skin-condition model —
# relabel classes in knowledge/local_advisories.json as instructed in the plan.
LIVESTOCK_MODEL_CANDIDATES = [
    "Diginsa/Cattle-Disease-Classifier-EfficientNetB3",
    "microsoft/resnet-50",  # generic fallback vision backbone (relabel classes)
]
LIVESTOCK_MODEL_LOCAL_DIR = MODEL_CACHE_DIR / "livestock_model"

# ---------------------------------------------------------------------------
# Runtime mode
# ---------------------------------------------------------------------------
# "auto"  -> try to load real HF model; if unavailable (no internet / not
#            downloaded yet / import error) silently use MockPredictor so the
#            REST of the pipeline (fusion, gate, advisory, tests) can still be
#            proven end-to-end. This is what lets us test today, offline.
# "real"  -> force real model, raise if unavailable.
# "mock"  -> force deterministic mock predictor (used by pytest).
EXPERT_MODE = os.environ.get("AGRIVISION_EXPERT_MODE", "auto")

# ---------------------------------------------------------------------------
# Fusion rules (Section 3, hour 4:15-5:15 of the plan)
# ---------------------------------------------------------------------------
FUSION_TEXT_SUPPORT_BONUS = 0.10
FUSION_TEXT_CONFLICT_PENALTY = 0.20
FUSION_SENSOR_SUPPORT_BONUS = 0.08
FUSION_SENSOR_CONFLICT_PENALTY = 0.15
FUSION_CONFIDENCE_CAP = 0.99
FUSION_CONFIDENCE_FLOOR = 0.01

# ---------------------------------------------------------------------------
# Confidence & Safety Gate thresholds (Section 3, hour 5:15-5:45)
# ---------------------------------------------------------------------------
GATE_CONFIDENCE_THRESHOLD = 0.75
GATE_MIN_QUALITY_OK = True  # placeholder toggle wired from capture+quality check

# ---------------------------------------------------------------------------
# Misc
# ---------------------------------------------------------------------------
RANDOM_SEED = 42
