"""
confidence_gate.py — Person A, Zone 1 (Hour 5:15-5:45 of the plan).

3 inputs: model confidence, evidence agreement, input quality.
HIGH = confidence >= threshold AND evidence consistent AND quality OK
       -> route = 'local'
Else -> route = 'cloud'

Takes fusion.py's output (contract #5) plus an input_quality_ok flag (from
the Capture+Quality Check step in Zone 1) and returns the SAME contract #5
shape with `route` finalized (this is the authoritative route, overriding
fusion.py's provisional guess).
"""

from __future__ import annotations

import json
from typing import Optional

from src.zone1_edge import config
from src.zone1_edge.knowledge.kb_loader import get_safety_critical_conditions


def decide_route(fusion_output: dict, input_quality_ok: bool = True) -> dict:
    """
    fusion_output: contract #5 dict from fusion.fuse()
    input_quality_ok: bool from Capture+Quality Check (blur/lighting check).
    """
    prediction = fusion_output.get("prediction", "")
    base_confidence = fusion_output.get("final_confidence", 0.0)
    
    safety_critical = get_safety_critical_conditions()
    norm_pred = prediction.lower().replace("___", "_").replace("__", "_")
    is_critical = norm_pred in safety_critical
    
    tier = config.get_device_tier()
    base_threshold = config.GATE_CONFIDENCE_THRESHOLD
    
    if tier == "low":
        threshold = base_threshold + 0.10
    elif tier == "high":
        threshold = base_threshold - 0.05
    else:
        threshold = base_threshold
        
    if is_critical:
        threshold += 0.10
    confidence_ok = base_confidence >= threshold
    evidence_ok = fusion_output.get("evidence_agreement") in ("high", "medium")
    text_support = fusion_output.get("text_support")
    
    reasons = []
    
    if not confidence_ok:
        reasons.append(f"Confidence {base_confidence:.2f} below threshold {threshold:.2f}")
    if is_critical:
        reasons.append("Safety critical prediction")
    if text_support is False:
        reasons.append("Farmer symptoms conflict")
    if not input_quality_ok:
        reasons.append("Poor input quality (e.g., blurry/dark)")
    if not evidence_ok and fusion_output.get("evidence_agreement") == "low":
        reasons.append("Low evidence agreement")
        
    is_high_confidence = confidence_ok and evidence_ok and input_quality_ok and not is_critical and text_support is not False
    
    route = "local" if is_high_confidence else "cloud"
    
    if is_high_confidence:
        advisory_tier = "confident"
    elif is_critical or not input_quality_ok:
        advisory_tier = "refer_expert"
    else:
        advisory_tier = "possible"

    result = dict(fusion_output)  # copy, preserve contract #5 shape
    result["route"] = route
    result["advisory_tier"] = advisory_tier
    result["threshold_reason"] = reasons
    result["_debug_gate"] = {
        "confidence_ok": confidence_ok,
        "evidence_ok": evidence_ok,
        "input_quality_ok": input_quality_ok,
        "threshold_used": threshold,
        "is_safety_critical": is_critical
    }
    return result


if __name__ == "__main__":
    demo_fusion = {
        "prediction": "tomato_early_blight", "visual_confidence": 0.81,
        "text_support": True, "sensor_support": None,
        "evidence_agreement": "high", "final_confidence": 0.91, "route": "local",
    }
    print(json.dumps(decide_route(demo_fusion, input_quality_ok=True), indent=2))
