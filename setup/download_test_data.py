import argparse
import os
from pathlib import Path

def download_crop(n):
    from datasets import load_dataset
    print(f"Downloading {n} crop images from PlantVillage...")
    ds = load_dataset("mohanty/PlantVillage", split="train", streaming=True)
    out_dir = Path("demo_data/crop")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    count = 0
    for item in ds:
        if count >= n:
            break
        img = item["image"]
        img.save(out_dir / f"plantvillage_{count:02d}.jpg")
        count += 1
    print(f"Saved {count} crop images to {out_dir}/")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--crop", action="store_true")
    parser.add_argument("--n", type=int, default=12)
    args = parser.parse_args()
    
    if args.crop:
        download_crop(args.n)

