"""
fusion.py — Person A, Zone 1 (Hour 4:15-5:15 of the plan). THE key new component.

Rule/score-based late fusion. NO MODEL. Combines:
  - image expert output              (contract #1)
  - text evidence output             (contract #3)
  - sensor output (livestock only)   (contract #4)

Rules (frozen, from the plan — do not let text arbitrarily override image):
  score = visual_confidence
  if text supports   -> +0.10   (config.FUSION_TEXT_SUPPORT_BONUS)
  if text conflicts   -> -0.20  (config.FUSION_TEXT_CONFLICT_PENALTY)
  if sensor supports  -> +0.08  (config.FUSION_SENSOR_SUPPORT_BONUS)
  if sensor conflicts -> -0.15  (config.FUSION_SENSOR_CONFLICT_PENALTY)
  cap at 0.99, floor at 0.01

Produces contract.md #5 (consumed by confidence_gate.py, and later by
Person B's cloud call + UI):

    {"prediction": str, "visual_confidence": float, "text_support": bool,
     "sensor_support": bool|null, "evidence_agreement": "high"|"medium"|"low",
     "final_confidence": float, "route": "local"|"cloud"}

NOTE: `route` here is a provisional value; the authoritative route decision
is finalized by confidence_gate.py (next stage), which also folds in input
quality. fusion.py sets a best-effort route so this module is independently
testable, and confidence_gate.py may override it.
"""

from __future__ import annotations

import json
from typing import Optional

from src.zone1_edge import config

# Minimal symptom -> condition keyword table used to decide "does the text
# evidence support or conflict with the image prediction". Extend as needed;
# kept intentionally simple/deterministic per the plan (rule-based only).
CONDITION_SYMPTOM_MAP = {
    "tomato_early_blight": {"brown_spots", "yellow_leaves", "wilting"},
    "tomato_late_blight": {"brown_spots", "black_spots", "wilting"},
    "potato_early_blight": {"brown_spots", "yellow_leaves"},
    "potato_late_blight": {"black_spots", "wilting"},
    "maize_common_rust": {"brown_spots", "yellow_leaves"},
    "pepper_bacterial_spot": {"black_spots", "brown_spots"},
    "lumpy_skin_disease": {"swelling", "fever"},
    "foot_and_mouth_disease": {"limping", "fever"},
    "mastitis_suspected": {"swelling", "loss_of_appetite"},
    "abnormal_temperature": {"fever"},
}

HEALTHY_LABELS = {"tomato_healthy", "maize_healthy", "healthy"}


def _text_agreement(prediction: str, symptoms: list) -> Optional[bool]:
    """Return True (supports), False (conflicts), or None (no signal)."""
    if not symptoms:
        return None
        
    tier = config.get_device_tier()
    
    norm_pred = prediction.lower().replace("___", "_").replace("__", "_")
    
    if norm_pred in HEALTHY_LABELS:
        # if farmer reports symptoms but model says healthy -> conflict;
        # checked BEFORE the CONDITION_SYMPTOM_MAP lookup since healthy
        # labels are never keys in that map.
        if tier == "low":
            return None # On low tier, don't penalize healthy predictions harshly based on text alone
        return len(symptoms) == 0
        
    expected = CONDITION_SYMPTOM_MAP.get(norm_pred)
    if expected is None:
        return None  # unknown label -> no opinion, don't penalize
        
    overlap = expected.intersection(set(symptoms))
    if tier == "low" and not overlap:
        return None # On low tier, if no overlap, just ignore rather than penalize
        
    return len(overlap) > 0


def _sensor_agreement(prediction: str, sensor: Optional[dict]) -> Optional[bool]:
    if not sensor:
        return None
    anomaly = sensor.get("anomaly", False)
    norm_pred = prediction.lower().replace("___", "_").replace("__", "_")
    predicted_sick = norm_pred not in HEALTHY_LABELS
    if predicted_sick and anomaly:
        return True
    if (not predicted_sick) and (not anomaly):
        return True
    if predicted_sick and not anomaly:
        return None  # ambiguous, no strong signal either way
    return False  # model says healthy but sensor shows anomaly -> conflict


def fuse(image_output: dict, text_evidence: Optional[dict] = None,
         sensor_output: Optional[dict] = None) -> dict:
    """
    image_output: contract #1 dict (required)
    text_evidence: contract #3 dict (optional)
    sensor_output: contract #4 dict (optional, livestock only)
    """
    prediction = image_output["prediction"]
    visual_confidence = float(image_output["confidence"])
    symptoms = text_evidence.get("symptoms", []) if text_evidence else []

    text_agree = _text_agreement(prediction, symptoms)
    sensor_agree = _sensor_agreement(prediction, sensor_output)

    score = visual_confidence
    if text_agree is True:
        score += config.FUSION_TEXT_SUPPORT_BONUS
    elif text_agree is False:
        score -= config.FUSION_TEXT_CONFLICT_PENALTY

    if sensor_agree is True:
        score += config.FUSION_SENSOR_SUPPORT_BONUS
    elif sensor_agree is False:
        score -= config.FUSION_SENSOR_CONFLICT_PENALTY

    final_confidence = max(config.FUSION_CONFIDENCE_FLOOR,
                            min(config.FUSION_CONFIDENCE_CAP, score))

    # evidence_agreement summary
    signals = [s for s in (text_agree, sensor_agree) if s is not None]
    if not signals:
        agreement = "medium"  # no corroborating evidence, image-only
    elif all(signals):
        agreement = "high"
    elif not any(signals):
        agreement = "low"
    else:
        agreement = "medium"  # mixed signals

    # provisional route (confidence_gate.py makes the final call)
    route = "local" if final_confidence >= config.GATE_CONFIDENCE_THRESHOLD and agreement != "low" else "cloud"

    return {
        "prediction": prediction,
        "visual_confidence": round(visual_confidence, 4),
        "text_support": text_agree,
        "sensor_support": sensor_agree,
        "evidence_agreement": agreement,
        "final_confidence": round(final_confidence, 4),
        "route": route,
        "sensor_data": sensor_output,
    }


if __name__ == "__main__":
    # quick manual smoke test
    demo_image = {"domain": "crop", "input_type": "image",
                  "prediction": "tomato_early_blight", "confidence": 0.81,
                  "top_k": [["tomato_early_blight", 0.81]]}
    demo_text = {"symptoms": ["brown_spots", "yellow_leaves"], "crop": "tomato",
                 "severity_hint": "medium"}
    print(json.dumps(fuse(demo_image, demo_text, None), indent=2))
