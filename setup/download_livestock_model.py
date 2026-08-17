"""
download_livestock_model.py — Run this ONCE on your Mac to fetch the
livestock/cattle disease model from Hugging Face.

Cattle-disease-specific checkpoints are scarce on the Hub. This script tries
config.LIVESTOCK_MODEL_CANDIDATES in order; if the first (cattle-specific)
repo isn't available, it falls back to a general vision backbone
(microsoft/resnet-50) — per the plan's explicit fallback instruction:
"if unavailable in time, use a general animal-health image classifier and
clearly relabel classes in local_advisories.json".

Usage:
    python setup/download_livestock_model.py
    python setup/download_livestock_model.py --repo <your-own-hf-model-id>
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.zone1_edge import config


def download_and_verify(repo_id: str) -> bool:
    from huggingface_hub import snapshot_download
    from transformers import pipeline
    from PIL import Image

    print(f"\n--- Trying: {repo_id} ---")
    try:
        local_path = snapshot_download(repo_id=repo_id,
                                        local_dir=str(config.LIVESTOCK_MODEL_LOCAL_DIR),
                                        local_dir_use_symlinks=False)
        print(f"Downloaded to: {local_path}")
    except Exception as e:  # noqa: BLE001
        print(f"FAILED to download {repo_id}: {e}")
        return False

    try:
        if "clip" in repo_id.lower():
            clf = pipeline("zero-shot-image-classification", model=str(config.LIVESTOCK_MODEL_LOCAL_DIR))
            dummy = Image.new("RGB", (224, 224), color=(180, 140, 100))
            preds = clf(dummy, candidate_labels=["healthy", "sick"])
        else:
            clf = pipeline("image-classification", model=str(config.LIVESTOCK_MODEL_LOCAL_DIR))
            dummy = Image.new("RGB", (224, 224), color=(180, 140, 100))
            preds = clf(dummy, top_k=3)
        print("Sanity inference OK. Sample output:")
        for p in preds:
            print(f"  {p['label']}: {p['score']:.4f}")
        return True
    except Exception as e:  # noqa: BLE001
        print(f"Downloaded but FAILED sanity inference: {e}")
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=str, default=None)
    args = parser.parse_args()

    candidates = [args.repo] if args.repo else config.LIVESTOCK_MODEL_CANDIDATES

    for repo_id in candidates:
        if download_and_verify(repo_id):
            print(f"\n[OK] Livestock model ready: {repo_id}")
            print(f"   Cached at: {config.LIVESTOCK_MODEL_LOCAL_DIR}")
            return
    print("\n[FAILED] All candidate livestock models failed to download/verify.")
    print("   The pipeline will keep using the MOCK predictor until this is fixed.")
    sys.exit(1)


if __name__ == "__main__":
    main()
