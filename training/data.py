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


def presplit_dirs(root: str) -> dict[str, Path] | None:
    """Datasets shipped as <root>/train + <root>/val[/test] (e.g. PlantVillage). None if not pre-split."""
    r = Path(root)
    found = {}
    for split, names in (("train", ("train",)), ("val", ("val", "valid", "validation")), ("test", ("test",))):
        for n in names:
            if (r / n).is_dir():
                found[split] = r / n
                break
    return found if "train" in found and ("val" in found or "test" in found) else None


def _list_flat(root: Path, class_map: dict | None) -> list[tuple[str, str]]:
    items = []
    for d in sorted(root.iterdir()):
        if not d.is_dir():
            continue
        cls = (class_map or {}).get(d.name, d.name)
        items += [(str(p), cls) for p in sorted(d.rglob("*")) if p.suffix.lower() in IMG_EXT]
    return items


def list_images(root: str, class_map: dict | None = None) -> list[tuple[str, str]]:
    """All images under root (all splits, when the dataset is pre-split) as (path, class)."""
    pre = presplit_dirs(root)
    if pre:
        return [it for d in pre.values() for it in _list_flat(d, class_map)]
    return _list_flat(Path(root), class_map)


def load_split(root: str, class_map: dict | None = None, allowed: set | None = None, seed: int = 42) -> dict:
    """
    train/val/test split honouring a dataset's own split when present:
      * <root>/train + <root>/val (+ optional test): train and test are used as shipped; with no test dir the
        shipped val is split 50/50 per class into val and test (so test is never seen in training or model selection).
      * otherwise: stratified 70/15/15.
    `allowed` restricts to a set of canonical class names.
    """
    keep = lambda items: [it for it in items if allowed is None or it[1] in allowed]  # noqa: E731
    pre = presplit_dirs(root)
    if not pre:
        return stratified_split(keep(list_images(root, class_map)), seed=seed)
    out = {"train": keep(_list_flat(pre["train"], class_map))}
    if "test" in pre:
        out["val"] = keep(_list_flat(pre["val"], class_map)) if "val" in pre else []
        out["test"] = keep(_list_flat(pre["test"], class_map))
    else:
        halves = stratified_split(keep(_list_flat(pre["val"], class_map)), ratios=(0.0, 0.5, 0.5), seed=seed)
        out["val"], out["test"] = halves["val"], halves["test"]
    return out


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
