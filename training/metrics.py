"""
metrics.py — Classification metrics (numpy only; no sklearn needed).

accuracy, per-class precision/recall/F1/support, macro-F1, confusion matrix,
and calibration (reliability by confidence bucket + expected calibration error).
"""

from __future__ import annotations

import numpy as np


def classification_report(y_true: list[str], y_pred: list[str], confidences: list[float] | None = None,
                          labels: list[str] | None = None, n_buckets: int = 10) -> dict:
    labels = labels or sorted(set(y_true) | set(y_pred))
    idx = {l: i for i, l in enumerate(labels)}
    n = len(labels)
    cm = np.zeros((n, n), dtype=int)
    for t, p in zip(y_true, y_pred):
        if t in idx and p in idx:
            cm[idx[t], idx[p]] += 1
        elif t in idx:  # prediction outside label space counts as a miss
            pass
    per_class = {}
    f1s = []
    for l, i in idx.items():
        tp = cm[i, i]
        fp = cm[:, i].sum() - tp
        support = sum(1 for t in y_true if t == l)
        fn = support - tp
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
        per_class[l] = {"precision": round(prec, 4), "recall": round(rec, 4), "f1": round(f1, 4), "support": int(support)}
        if support:
            f1s.append(f1)
    correct = [t == p for t, p in zip(y_true, y_pred)]
    report = {
        "n": len(y_true),
        "accuracy": round(float(np.mean(correct)) if correct else 0.0, 4),
        "macro_f1": round(float(np.mean(f1s)) if f1s else 0.0, 4),
        "per_class": per_class,
        "labels": labels,
        "confusion_matrix": cm.tolist(),
    }
    if confidences is not None:
        report["calibration"] = calibration(correct, confidences, n_buckets)
    return report


def calibration(correct: list[bool], confidences: list[float], n_buckets: int = 10) -> dict:
    conf = np.asarray(confidences, dtype=float)
    corr = np.asarray(correct, dtype=float)
    edges = np.linspace(0, 1, n_buckets + 1)
    buckets, ece = [], 0.0
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (conf > lo) & (conf <= hi) if lo > 0 else (conf >= lo) & (conf <= hi)
        if m.sum() == 0:
            continue
        acc, avg_conf = corr[m].mean(), conf[m].mean()
        ece += m.sum() / len(conf) * abs(acc - avg_conf)
        buckets.append({"range": [round(lo, 2), round(hi, 2)], "count": int(m.sum()),
                        "accuracy": round(float(acc), 4), "avg_confidence": round(float(avg_conf), 4)})
    return {"ece": round(float(ece), 4), "buckets": buckets}


def to_markdown(title: str, report: dict) -> str:
    lines = [f"## {title}", "", f"- n: {report['n']}", f"- accuracy: {report['accuracy']}",
             f"- macro-F1: {report['macro_f1']}"]
    if "calibration" in report:
        lines.append(f"- ECE: {report['calibration']['ece']}")
    lines += ["", "| class | precision | recall | f1 | support |", "|---|---|---|---|---|"]
    for l, m in report["per_class"].items():
        lines.append(f"| {l} | {m['precision']} | {m['recall']} | {m['f1']} | {m['support']} |")
    return "\n".join(lines) + "\n"
