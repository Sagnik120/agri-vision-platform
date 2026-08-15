"""
download_crop_model.py — Run this ONCE on your Mac to fetch the real crop
disease model from Hugging Face and cache it locally, so crop_expert.py can
load it in "real" mode without hitting the network every run.

Prerequisites (see README.md "Setup" section):
    pip install -r requirements.txt
    huggingface-cli login          # paste a token from https://huggingface.co/settings/tokens
                                    # (log in with your account: Sagnik120)

Usage:
    python setup/download_crop_model.py
    python setup/download_crop_model.py --repo linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification

This tries each candidate in config.CROP_MODEL_CANDIDATES in order and stops
at the first one that downloads successfully, saving it to
models_cache/crop_model/. It also runs ONE quick sanity inference on a
synthetic image to prove the checkpoint actually loads and predicts.
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
                                        local_dir=str(config.CROP_MODEL_LOCAL_DIR),
                                        local_dir_use_symlinks=False)
        print(f"Downloaded to: {local_path}")
    except Exception as e:  # noqa: BLE001
        print(f"FAILED to download {repo_id}: {e}")
        return False

    # sanity inference check
    try:
        clf = pipeline("image-classification", model=str(config.CROP_MODEL_LOCAL_DIR))
        dummy = Image.new("RGB", (224, 224), color=(120, 180, 90))
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
    parser.add_argument("--repo", type=str, default=None,
                         help="Force a specific HF repo id instead of trying the candidate list")
    args = parser.parse_args()

    candidates = [args.repo] if args.repo else config.CROP_MODEL_CANDIDATES

    for repo_id in candidates:
        if download_and_verify(repo_id):
            print(f"\n✅ Crop model ready: {repo_id}")
            print(f"   Cached at: {config.CROP_MODEL_LOCAL_DIR}")
            print("   crop_expert.py will now use this automatically (mode='auto' or 'real').")
            return
    print("\n❌ All candidate crop models failed to download/verify.")
    print("   The pipeline will keep using the MOCK predictor until this is fixed.")
    print("   Try: python setup/download_crop_model.py --repo <your-own-hf-model-id>")
    sys.exit(1)


if __name__ == "__main__":
    main()
