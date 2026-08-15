"""
crop_expert.py — Person A, Zone 1.

Loads a pretrained PlantVillage-style HF image-classification model and
returns predictions in the frozen contract shape (contract.md #1):

    {"domain":"crop", "input_type":"image", "prediction": str,
     "confidence": float, "top_k": [[label, prob], ...]}

Usage:
    python -m src.zone1_edge.experts.crop_expert path/to/image.jpg
"""

from __future__ import annotations

import json
import sys

from src.zone1_edge import config
from src.zone1_edge.experts.base_image_expert import BaseImageExpert

# Fallback label set used ONLY by the mock predictor (no internet / no model
# downloaded yet). Mirrors the entries we write in local_advisories.json.
CROP_MOCK_LABELS = [
    "tomato_early_blight",
    "tomato_late_blight",
    "tomato_healthy",
    "potato_early_blight",
    "potato_late_blight",
    "maize_common_rust",
    "maize_healthy",
    "pepper_bacterial_spot",
]


class CropExpert(BaseImageExpert):
    domain = "crop"
    model_candidates = config.CROP_MODEL_CANDIDATES
    local_dir = config.CROP_MODEL_LOCAL_DIR
    labels = CROP_MOCK_LABELS


def run(image_path: str, mode: str = None) -> dict:
    expert = CropExpert(mode=mode)
    result = expert.predict(image_path)
    result["_debug_backend"] = expert.backend_info
    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m src.zone1_edge.experts.crop_expert <image_path>")
        sys.exit(1)
    out = run(sys.argv[1])
    print(json.dumps(out, indent=2))
