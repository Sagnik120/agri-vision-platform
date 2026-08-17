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
    from src.zone1_edge import config
    
    # 1. If in mock mode, fallback to the old math comparison
    if mode == "mock" or config.EXPERT_MODE == "mock":
        crop_res = run_crop_expert(image_path, mode=mode)
        livestock_res = run_livestock_expert(image_path, mode=mode)
        if crop_res.get("confidence", 0.0) >= livestock_res.get("confidence", 0.0):
            return {"chosen_domain": "crop", "expert_output": crop_res}
        return {"chosen_domain": "livestock", "expert_output": livestock_res}
        
    # 2. Real AI Two-Stage Semantic Routing
    import torch
    from transformers import pipeline
    from PIL import Image
    
    try:
        # Load the zero-shot model purely for high-level domain classification
        classifier = pipeline(
            "zero-shot-image-classification",
            model=str(config.LIVESTOCK_MODEL_LOCAL_DIR),
            device="cuda" if torch.cuda.is_available() else "cpu"
        )
        img = Image.open(image_path).convert("RGB")
        # Ask it a balanced, high-level question
        res = classifier(img, candidate_labels=["a photo of a plant leaf or crop", "a photo of a cow or livestock animal"])
        
        if "plant" in res[0]["label"]:
            chosen = "crop"
            expert_res = run_crop_expert(image_path, mode=mode)
        else:
            chosen = "livestock"
            expert_res = run_livestock_expert(image_path, mode=mode)
            
    except Exception as e:
        # Fallback if pipeline fails
        print(f"Warning: Semantic router failed ({e}), falling back to math.")
        crop_res = run_crop_expert(image_path, mode=mode)
        livestock_res = run_livestock_expert(image_path, mode=mode)
        if crop_res.get("confidence", 0.0) >= livestock_res.get("confidence", 0.0):
            chosen = "crop"
            expert_res = crop_res
        else:
            chosen = "livestock"
            expert_res = livestock_res
        
    return {
        "chosen_domain": chosen,
        "expert_output": expert_res
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
