"""
task_router.py — Person A, Zone 1 (Hour 3:45-4:15 of the plan).

Explicit UI-driven selection (Crop / Livestock buttons) — NOT a learned
classifier / MoE gate. Dispatches to the correct expert module based on a
passed-in domain string, and prints the "Detected task -> Expert selected"
line the demo script (Section 8) expects.
"""

from __future__ import annotations

from src.zone1_edge.experts.crop_expert import run as run_crop_expert
from src.zone1_edge.experts.livestock_expert import run as run_livestock_expert

VALID_DOMAINS = ("crop", "livestock")
import math

def compute_entropy(top_k: list) -> float:
    entropy = 0.0
    for item in top_k:
        p = float(item[1])
        if p > 0:
            entropy -= p * math.log(p)
    return entropy

def auto_route(image_path: str, mode: str = None) -> dict:
    crop_res = run_crop_expert(image_path, mode=mode)
    livestock_res = run_livestock_expert(image_path, mode=mode)
    
    crop_conf = crop_res.get("confidence", 0.0)
    livestock_conf = livestock_res.get("confidence", 0.0)
    
    crop_ent = compute_entropy(crop_res.get("top_k", []))
    livestock_ent = compute_entropy(livestock_res.get("top_k", []))
    
    if crop_conf >= livestock_conf:
        chosen = "crop"
        res = crop_res
    else:
        chosen = "livestock"
        res = livestock_res
        
    return {
        "chosen_domain": chosen,
        "crop_confidence": crop_conf,
        "livestock_confidence": livestock_conf,
        "crop_entropy": crop_ent,
        "livestock_entropy": livestock_ent,
        "expert_output": res
    }

def route(domain: str, image_path: str, mode: str = None) -> dict:
    """
    domain: "crop" | "livestock" — comes directly from the UI button the
            farmer tapped (or the API caller). No ML model involved.
    """
    if domain not in VALID_DOMAINS:
        raise ValueError(f"domain must be one of {VALID_DOMAINS}, got {domain!r}")

    expert_name = "Crop Disease & Pest Expert" if domain == "crop" else "Livestock Health & Behavior Expert"
    print(f"Detected task -> {domain} -> Expert selected: {expert_name}")

    if domain == "crop":
        return run_crop_expert(image_path, mode=mode)
    return run_livestock_expert(image_path, mode=mode)


if __name__ == "__main__":
    import argparse
    import json

    p = argparse.ArgumentParser()
    p.add_argument("domain", choices=VALID_DOMAINS)
    p.add_argument("image_path")
    args = p.parse_args()
    print(json.dumps(route(args.domain, args.image_path), indent=2))
