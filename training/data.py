"""
data.py — Dataset listing + stratified splitting shared by training/eval scripts.

Expected layout (ImageFolder): <root>/<class_folder>/*.jpg|png
Optional --class-map JSON renames folders to canonical class names, e.g.
    {"lumpy": "lumpy_skin_disease", "normal": "healthy", "fmd": "foot_and_mouth_disease"}
"""

from __future__ import annotations

import json
import random
from collections import defaultdict
from pathlib import Path

IMG_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def list_images(root: str, class_map: dict | None = None) -> list[tuple[str, str]]:
    items = []
    for d in sorted(Path(root).iterdir()):
        if not d.is_dir():
            continue
        cls = (class_map or {}).get(d.name, d.name)
        items += [(str(p), cls) for p in sorted(d.rglob("*")) if p.suffix.lower() in IMG_EXT]
    return items


def load_class_map(path: str | None) -> dict | None:
    if not path:
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def stratified_split(items: list[tuple[str, str]], ratios=(0.70, 0.15, 0.15), seed: int = 42) -> dict:
    by_cls = defaultdict(list)
    for it in items:
        by_cls[it[1]].append(it)
    out = {"train": [], "val": [], "test": []}
    for cls, lst in sorted(by_cls.items()):
        # Per-class RNG: an image lands in the same split whichever class subset
        # is loaded, so sub-expert, moe_gate and domain-level test sets never leak.
        rng = random.Random(f"{seed}:{cls}")
        lst = sorted(lst)
        rng.shuffle(lst)
        n = len(lst)
        n_val = max(1, round(n * ratios[1])) if n >= 3 else 0
        n_test = max(1, round(n * ratios[2])) if n >= 3 else 0
        out["test"] += lst[:n_test]
        out["val"] += lst[n_test:n_test + n_val]
        out["train"] += lst[n_test + n_val:]
    return out


def save_manifest(split: dict, path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(split, f, indent=1)


def load_manifest(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return {k: [tuple(x) for x in v] for k, v in json.load(f).items()}
