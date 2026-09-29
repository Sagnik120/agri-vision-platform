"""
label_aliases.py — Map raw model labels to local knowledge-base keys.

Model checkpoints emit labels like "Corn___Common_Rust" or
"Corn_(maize)___Common_rust_" while the KB uses "maize_common_rust".
Without this, such predictions never match the offline KB and always escalate.
"""

from __future__ import annotations

import re

# Prefix aliases applied after generic normalisation.
_PREFIX_ALIASES = {
    "corn_maize_": "maize_",
    "corn_": "maize_",
    "pepper_bell_": "pepper_",
    "cherry_including_sour_": "cherry_",
}


# Whole-key aliases (after prefix aliasing): verbose dataset names -> KB keys.
_KEY_ALIASES = {
    "maize_cercospora_leaf_spot_gray_leaf_spot": "maize_gray_leaf_spot",
    "tomato_spider_mites_two_spotted_spider_mite": "tomato_spider_mites",
    "tomato_tomato_yellow_leaf_curl_virus": "tomato_yellow_leaf_curl_virus",
    "tomato_tomato_mosaic_virus": "tomato_mosaic_virus",
    "apple_apple_scab": "apple_scab",
    "apple_cedar_apple_rust": "apple_cedar_rust",
    "grape_esca_black_measles": "grape_esca",
    "grape_leaf_blight_isariopsis_leaf_spot": "grape_leaf_blight",
    "orange_haunglongbing_citrus_greening": "citrus_greening",
    "rice_leaf_blast": "rice_blast",
    "wheat_brown_rust": "wheat_rust",
    "wheat_yellow_rust": "wheat_rust",
}

# Crops whose healthy class has no crop-specific KB entry share `crop_healthy`.
_GENERIC_HEALTHY_CROPS = {
    "potato", "pepper", "soybean", "apple", "blueberry", "cherry", "grape", "peach",
    "raspberry", "strawberry", "wheat", "rice",
}


def normalize_condition(label: str) -> str:
    key = re.sub(r"[^a-z0-9]+", "_", (label or "").lower()).strip("_")
    for src, dst in _PREFIX_ALIASES.items():
        if key.startswith(src):
            key = dst + key[len(src):]
            break
    key = _KEY_ALIASES.get(key, key)
    if key.endswith("_healthy") and key[: -len("_healthy")] in _GENERIC_HEALTHY_CROPS:
        key = "crop_healthy"
    return key
