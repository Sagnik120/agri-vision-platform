"""
evaluation_tool.py — Section 5 Baseline Evaluation Tooling

Usage:
    python tests/zone1/evaluation_tool.py --data_dir path/to/images --labels path/to/labels.json --domain crop

Expected labels.json format:
{
    "image1.jpg": "tomato_early_blight",
    "image2.jpg": "tomato_healthy",
    ...
}
"""

import argparse
import json
import os
import logging
from collections import defaultdict

# Suppress some verbose logging from transformers/experts unless requested
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def run_evaluation(data_dir: str, labels_path: str, domain: str, mode: str = "auto"):
    if not os.path.exists(data_dir):
        print(f"Error: Directory {data_dir} does not exist.")
        return
        
    if not os.path.exists(labels_path):
        print(f"Error: Labels file {labels_path} does not exist.")
        return

    with open(labels_path, 'r') as f:
        ground_truth = json.load(f)

    if domain == "crop":
        from src.zone1_edge.experts.crop_expert import CropExpert
        expert = CropExpert(mode=mode)
    elif domain == "livestock":
        from src.zone1_edge.experts.livestock_expert import LivestockExpert
        expert = LivestockExpert(mode=mode)
    else:
        print("Invalid domain. Choose 'crop' or 'livestock'.")
        return

    print(f"Starting evaluation for {domain} expert...")
    print(f"Target inference backend: {expert.backend_info}")
    
    correct = 0
    total = 0
    y_true = []
    y_pred = []
    
    results_log = []

    for img_name, true_label in ground_truth.items():
        img_path = os.path.join(data_dir, img_name)
        if not os.path.exists(img_path):
            print(f"Warning: Image {img_name} not found in {data_dir}. Skipping.")
            continue
            
        try:
            res = expert.predict(img_path)
            pred_label = res["prediction"]
            confidence = res["confidence"]
            
            is_match = (pred_label == true_label)
            if is_match:
                correct += 1
            total += 1
            
            y_true.append(true_label)
            y_pred.append(pred_label)
            
            results_log.append({
                "image": img_name,
                "true_label": true_label,
                "pred_label": pred_label,
                "confidence": confidence,
                "correct": is_match,
                "inference_source": expert.backend_info
            })
            
        except Exception as e:
            print(f"Error processing {img_name}: {e}")

    if total == 0:
        print("No valid images processed. Exiting.")
        return

    accuracy = correct / total
    
    print("\n" + "="*50)
    print(f"EVALUATION RESULTS ({domain.upper()})")
    print("="*50)
    print(f"Total images evaluated: {total}")
    print(f"Accuracy: {accuracy:.2%} ({correct}/{total})")
    print(f"Inference Source Used: {expert.backend_info}")
    print("="*50)
    
    # Per-class metrics
    class_correct = defaultdict(int)
    class_total = defaultdict(int)
    for t, p in zip(y_true, y_pred):
        class_total[t] += 1
        if t == p:
            class_correct[t] += 1
            
    print("\nPer-class accuracy:")
    for c, count in class_total.items():
        acc = class_correct[c] / count
        print(f"  - {c}: {acc:.2%} ({class_correct[c]}/{count})")
        
    # Save detailed report
    report_path = f"evaluation_report_{domain}.json"
    with open(report_path, 'w') as f:
        json.dump({"summary": {"accuracy": accuracy, "total": total, "source": expert.backend_info}, "details": results_log}, f, indent=2)
    print(f"\nDetailed report saved to {report_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate Zone 1 image experts.")
    parser.add_argument("--data_dir", type=str, required=True, help="Path to directory containing test images.")
    parser.add_argument("--labels", type=str, required=True, help="Path to JSON file containing ground truth labels.")
    parser.add_argument("--domain", type=str, choices=["crop", "livestock"], required=True, help="Which expert to evaluate.")
    parser.add_argument("--mode", type=str, choices=["auto", "mock", "real"], default="auto", help="Inference mode.")
    
    args = parser.parse_args()
    run_evaluation(args.data_dir, args.labels, args.domain, args.mode)
