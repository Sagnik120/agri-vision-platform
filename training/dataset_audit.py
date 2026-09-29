"""
dataset_audit.py — Phase 0 data audit (user-run, CPU, no downloads).

Counts images per class, maps classes to MoE groups (src/zone1_edge/moe/expert_groups.py),
and FLAGS under-supported classes. An expert whose classes are flagged must not ship
(e.g. FMD -> documented future scope; FMD cases keep the existing zero-shot + cloud path).

    python -m training.dataset_audit --root D:/data/plantvillage --domain crop
    python -m training.dataset_audit --root D:/data/cattle --domain livestock --class-map training/configs/cattle_class_map.json
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from src.zone1_edge.moe.expert_groups import DOMAIN_GROUPS
from training.paths import RESULTS
from training.data import list_images, load_class_map, presplit_dirs


def audit(root: str, domain: str, class_map: dict | None, min_per_class: int) -> dict:
    counts = Counter(c for _, c in list_images(root, class_map))
    groups = {}
    for group, classes in DOMAIN_GROUPS[domain].items():
        per = {c: counts.get(c, 0) for c in classes}
        flagged = [c for c, n in per.items() if n < min_per_class]
        groups[group] = {"counts": per, "total": sum(per.values()), "under_supported": flagged,
                         "ship": not flagged}
    known = {c for cl in DOMAIN_GROUPS[domain].values() for c in cl}
    return {"root": root, "domain": domain, "min_per_class": min_per_class, "groups": groups,
            "unmapped_folders": sorted(set(counts) - known)}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--domain", choices=["crop", "livestock"], required=True)
    ap.add_argument("--class-map")
    ap.add_argument("--min-per-class", type=int, default=200)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    rep = audit(a.root, a.domain, load_class_map(a.class_map), a.min_per_class)
    out = Path(a.out.format(domain=a.domain)) if a.out else RESULTS / "zone1" / "moe" / f"dataset_audit_{a.domain}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rep, indent=1), encoding="utf-8")
    for g, info in rep["groups"].items():
        status = "OK" if info["ship"] else f"UNDER-SUPPORTED: {info['under_supported']}"
        print(f"{g}: total={info['total']} -> {status}")
    if rep["unmapped_folders"]:
        print("Unmapped folders (add to --class-map or ignore):", rep["unmapped_folders"])
    print("Report:", out)
