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


def decide_route(fusion_output: dict, input_quality_ok: bool = True) -> dict:
    """
    fusion_output: contract #5 dict from fusion.fuse()
    input_quality_ok: bool from Capture+Quality Check (blur/lighting check).
                       Defaults True (assume good capture) for pipelines
                       that haven't wired the quality check yet.
    """
    confidence_ok = fusion_output["final_confidence"] >= config.GATE_CONFIDENCE_THRESHOLD
    evidence_ok = fusion_output["evidence_agreement"] in ("high", "medium")

    is_high_confidence = confidence_ok and evidence_ok and input_quality_ok
    route = "local" if is_high_confidence else "cloud"

    result = dict(fusion_output)  # copy, preserve contract #5 shape
    result["route"] = route
    result["_debug_gate"] = {
        "confidence_ok": confidence_ok,
        "evidence_ok": evidence_ok,
        "input_quality_ok": input_quality_ok,
        "threshold_used": config.GATE_CONFIDENCE_THRESHOLD,
    }
    return result


if __name__ == "__main__":
    demo_fusion = {
        "prediction": "tomato_early_blight", "visual_confidence": 0.81,
        "text_support": True, "sensor_support": None,
        "evidence_agreement": "high", "final_confidence": 0.91, "route": "local",
    }
    print(json.dumps(decide_route(demo_fusion, input_quality_ok=True), indent=2))
