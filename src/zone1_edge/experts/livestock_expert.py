"""
livestock_expert.py — Person A, Zone 1.

Loads a pretrained cattle-disease-style HF image-classification model
(EfficientNet-B3 class) and returns predictions in the frozen contract shape
(contract.md #1):

    {"domain":"livestock", "input_type":"image", "prediction": str,
     "confidence": float, "top_k": [[label, prob], ...]}

If no cattle-specific checkpoint is available in time (per the plan), a
general-purpose vision backbone is loaded instead and its output classes are
treated as opaque labels — relabel them in knowledge/local_advisories.json.

Usage:
    python -m src.zone1_edge.experts.livestock_expert path/to/image.jpg
"""

from __future__ import annotations

import json
import sys

from src.zone1_edge import config
from src.zone1_edge.experts.base_image_expert import BaseImageExpert

# Fallback label set used ONLY by the mock predictor.
LIVESTOCK_MOCK_LABELS = [
    "lumpy_skin_disease",
    "foot_and_mouth_disease",
    "healthy",
    "mastitis_suspected",
    "abnormal_temperature",
]


class LivestockExpert(BaseImageExpert):
    domain = "livestock"
    model_candidates = config.LIVESTOCK_MODEL_CANDIDATES
    local_dir = config.LIVESTOCK_MODEL_LOCAL_DIR
    labels = LIVESTOCK_MOCK_LABELS


def run(image_path: str, mode: str = None) -> dict:
    expert = LivestockExpert(mode=mode)
    result = expert.predict(image_path)
    result["_debug_backend"] = expert.backend_info
    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m src.zone1_edge.experts.livestock_expert <image_path>")
        sys.exit(1)
    out = run(sys.argv[1])
    print(json.dumps(out, indent=2))
