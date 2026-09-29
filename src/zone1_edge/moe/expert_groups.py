"""
expert_groups.py — Zone 1 intra-domain MoE sub-expert definitions.

Single source of truth for which classes each sub-expert owns. Used by the
runtime `moe_gate` / `moe_expert` AND by the offline training scripts, so the
gate and the sub-experts are always trained on identical group labels.

Terminology (do not confuse):
  * moe_gate        — picks ONE sub-expert inside an already-chosen domain.
  * confidence_gate — decides local vs cloud AFTER fusion. Unrelated.
"""

from __future__ import annotations

# PlantVillage (38 classes, canonical folder names), grouped by growth pattern.
# Annual row / vine crops.
CROP_ROW_CLASSES = [
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
    "Corn_(maize)___Common_rust_",
    "Corn_(maize)___Northern_Leaf_Blight",
    "Corn_(maize)___healthy",
    "Pepper,_bell___Bacterial_spot",
    "Pepper,_bell___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Soybean___healthy",
    "Squash___Powdery_mildew",
    "Tomato___Bacterial_spot",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot",
    "Tomato___Spider_mites Two-spotted_spider_mite",
    "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato___Tomato_mosaic_virus",
    "Tomato___healthy",
]

# Perennial tree / bush / vine crops.
CROP_PERENNIAL_CLASSES = [
    "Apple___Apple_scab",
    "Apple___Black_rot",
    "Apple___Cedar_apple_rust",
    "Apple___healthy",
    "Blueberry___healthy",
    "Cherry_(including_sour)___Powdery_mildew",
    "Cherry_(including_sour)___healthy",
    "Grape___Black_rot",
    "Grape___Esca_(Black_Measles)",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
    "Grape___healthy",
    "Orange___Haunglongbing_(Citrus_greening)",
    "Peach___Bacterial_spot",
    "Peach___healthy",
    "Raspberry___healthy",
    "Strawberry___Leaf_scorch",
    "Strawberry___healthy",
]

# Livestock: two binary experts sharing the "healthy" class.
LIVESTOCK_LSD_CLASSES = ["lumpy_skin_disease", "healthy"]
LIVESTOCK_FMD_CLASSES = ["foot_and_mouth_disease", "healthy"]

DOMAIN_GROUPS = {
    "crop": {"crop_row": CROP_ROW_CLASSES, "crop_perennial": CROP_PERENNIAL_CLASSES},
    "livestock": {"livestock_lsd": LIVESTOCK_LSD_CLASSES, "livestock_fmd": LIVESTOCK_FMD_CLASSES},
}


def group_names(domain: str) -> list[str]:
    return list(DOMAIN_GROUPS[domain].keys())


def group_of_class(domain: str, class_name: str) -> str | None:
    """Group owning `class_name` (first match; livestock 'healthy' is shared)."""
    for group, classes in DOMAIN_GROUPS[domain].items():
        if class_name in classes:
            return group
    return None
