"""
train_moe_gate.py — Train the learned intra-domain moe_gate (CPU, numpy only).

Labels = MoE group of each image's class (same groups the sub-experts use).
Model  = class-balanced multinomial logistic regression with L2, full-batch
         gradient descent on the 54-dim descriptor (src/zone1_edge/moe/image_features.py).
Livestock: the shared `healthy` class belongs to both experts (either expert can
answer "healthy"), so it is excluded from gate training/routing accuracy.

Output: models_cache/moe/<domain>_moe_gate.json + results/zone1/moe/<domain>_gate_report.json

    python -m training.train_moe_gate --root D:/data/plantvillage --domain crop
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from src.zone1_edge.moe.expert_groups import DOMAIN_GROUPS, group_of_class
from src.zone1_edge.moe.image_features import FEATURE_DIM, extract_features
from src.zone1_edge.moe.moe_gate import softmax
from training.paths import MODELS, RESULTS
from training.data import load_class_map, load_split
from training.metrics import classification_report

SHARED_CLASSES = {"livestock": {"healthy"}}


def fit_softmax(X, y, n_cls, l2=1e-3, lr=0.5, epochs=500):
    w_cls = np.bincount(y, minlength=n_cls).astype(float)
    sw = (len(y) / (n_cls * np.maximum(w_cls, 1)))[y]  # class-balanced sample weights
    W, b = np.zeros((n_cls, X.shape[1])), np.zeros(n_cls)
    Y = np.eye(n_cls)[y]
    for _ in range(epochs):
        P = softmax(X @ W.T + b)
        G = (P - Y) * sw[:, None] / len(y)
        W -= lr * (G.T @ X + l2 * W)
        b -= lr * G.sum(axis=0)
    return W, b


def featurize(items, groups):
    X = np.stack([extract_features(p) for p, _ in items]) if items else np.zeros((0, FEATURE_DIM))
    return X, np.array([groups.index(g) for g in [c for _, c in items]], dtype=int)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--domain", choices=["crop", "livestock"], required=True)
    ap.add_argument("--class-map")
    ap.add_argument("--max-per-class", type=int, default=300, help="gate needs few images; caps feature extraction time")
    ap.add_argument("--out-dir", default=str(MODELS / "moe"))
    a = ap.parse_args()

    groups = list(DOMAIN_GROUPS[a.domain])
    shared = SHARED_CLASSES.get(a.domain, set())
    allowed = {c for cl in DOMAIN_GROUPS[a.domain].values() for c in cl} - shared
    split = load_split(a.root, load_class_map(a.class_map), allowed=allowed)
    for k in split:  # cap per class to bound feature-extraction time
        per = {}
        capped = []
        for p, c in split[k]:
            per[c] = per.get(c, 0) + 1
            if per[c] <= a.max_per_class:
                capped.append((p, c))
        split[k] = capped
    to_group = lambda lst: [(p, group_of_class(a.domain, c)) for p, c in lst]  # noqa: E731

    Xtr, ytr = featurize(to_group(split["train"]), groups)
    Xva, yva = featurize(to_group(split["val"]), groups)
    Xte, yte = featurize(to_group(split["test"]), groups)
    mean, std = Xtr.mean(axis=0), Xtr.std(axis=0) + 1e-6
    norm = lambda X: (X - mean) / std  # noqa: E731

    best = None
    for l2 in (1e-4, 1e-3, 1e-2):  # pick L2 on validation routing accuracy
        W, b = fit_softmax(norm(Xtr), ytr, len(groups), l2=l2)
        acc = float((softmax(norm(Xva) @ W.T + b).argmax(1) == yva).mean()) if len(yva) else 0.0
        if best is None or acc > best[0]:
            best = (acc, l2, W, b)
    val_acc, l2, W, b = best

    P = softmax(norm(Xte) @ W.T + b)
    rep = classification_report([groups[i] for i in yte], [groups[i] for i in P.argmax(1)],
                                P.max(1).tolist(), labels=groups)
    rep.update({"component": "moe_gate", "val_routing_accuracy": round(val_acc, 4), "l2": l2,
                "n_train": len(ytr), "excluded_shared_classes": sorted(shared)})

    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    weights = {"domain": a.domain, "groups": groups, "feature_dim": FEATURE_DIM,
               "mean": mean.tolist(), "std": std.tolist(), "W": W.tolist(), "b": b.tolist(),
               "trained_on": a.root, "l2": l2}
    (out / f"{a.domain}_moe_gate.json").write_text(json.dumps(weights), encoding="utf-8")
    rdir = RESULTS / "zone1" / "moe"
    rdir.mkdir(parents=True, exist_ok=True)
    (rdir / f"{a.domain}_gate_report.json").write_text(json.dumps(rep, indent=1), encoding="utf-8")
    print(f"moe_gate test routing accuracy: {rep['accuracy']} (macro-F1 {rep['macro_f1']}), val {val_acc:.4f}")


if __name__ == "__main__":
    main()
