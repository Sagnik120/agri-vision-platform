import json
import os
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.zone1_edge.pipeline import run_zone1_pipeline
import cv2
import numpy as np

def run_eval():
    gold_set_path = Path("eval/gold_set.json")
    with open(gold_set_path, "r") as f:
        cases = json.load(f)

    # We will use mock mode
    results = {"total": len(cases), "route_correct": 0, "tier_correct": 0, "schema_valid": 0}

    for case in cases:
        print(f"Evaluating {case['id']}...")
        
        img_path = case["image_path"]
        
        try:
            res = run_zone1_pipeline(
                domain=case["domain"],
                image_path=img_path,
                farmer_text=case["farmer_audio_text"],
                sensor_reading=case["sensor_reading"],
                mode="mock"
            )
            
            # Since it's mock, check structure
            route = res.get("gate", {}).get("route")
            if route == case["expected_route"]:
                results["route_correct"] += 1
                
            tier = res.get("gate", {}).get("advisory_tier")
            if tier == case.get("expected_advisory_tier"):
                results["tier_correct"] += 1
                
            results["schema_valid"] += 1
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error evaluating case {case['id']}: {e}")

    print("\n--- Evaluation Results ---")
    print(f"Total Cases: {results['total']}")
    print(f"Route Accuracy: {results['route_correct']}/{results['total']}")
    print(f"Schema valid: {results['schema_valid']}/{results['total']}")
    
if __name__ == "__main__":
    run_eval()
