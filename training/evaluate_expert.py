"""
evaluate_expert.py — Before/after evaluation on the SAME held-out test split.

Targets:
  baseline      current runtime single expert (CropExpert / LivestockExpert), i.e. the "before" number
  sub:<group>   one ONNX sub-expert on its own group's test split
  moe           full domain MoE (moe_gate top-1 -> sub-expert), plus gate routing accuracy

Labels are compared after normalize_condition() so checkpoints with differently
spelled labels are scored fairly. Classes a checkpoint cannot output simply count
as errors — reported, not hidden.

    python -m training.evaluate_expert --root D:/data/plantvillage --domain crop --target baseline
    python -m training.evaluate_expert --root D:/data/plantvillage --domain crop --target moe
    python -m training.evaluate_expert --root D:/data/plantvillage --domain crop --target sub:crop_row
Reports -> results/zone1/eval/<domain>_<target>.{json,md}
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.zone1_edge.knowledge.label_aliases import normalize_condition
from src.zone1_edge.moe.expert_groups import DOMAIN_GROUPS, group_of_class
from training.paths import RESULTS
from training.data import load_class_map, load_split
from training.metrics import classification_report, to_markdown


def domain_test_items(root, domain, class_map, groups=None):
    allowed = {c for g, cl in DOMAIN_GROUPS[domain].items() if groups is None or g in groups for c in cl}
    return load_split(root, class_map, allowed=allowed)["test"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--domain", choices=["crop", "livestock"], required=True)
    ap.add_argument("--target", required=True, help="baseline | moe | sub:<group>")
    ap.add_argument("--class-map")
    ap.add_argument("--limit", type=int, default=0, help="evaluate first N test images (quick check)")
    a = ap.parse_args()
    cmap = load_class_map(a.class_map)

    extra = {}
    if a.target.startswith("sub:"):
        group = a.target[4:]
        from src.zone1_edge.moe.moe_expert import OnnxSubExpert
        items = domain_test_items(a.root, a.domain, cmap, groups={group})
        expert = OnnxSubExpert(group)
        predict = lambda p: expert.predict(p)[0]  # noqa: E731
    elif a.target == "moe":
        from src.zone1_edge.moe.moe_expert import MoEDomainExpert
        items = domain_test_items(a.root, a.domain, cmap)
        moe = MoEDomainExpert(a.domain)
        routed = []

        def predict(p):
            out = moe.predict(p)
            routed.append(out["_moe"]["selected_expert"])
            return out["prediction"], out["confidence"]
    elif a.target == "baseline":
        items = domain_test_items(a.root, a.domain, cmap)
        if a.domain == "crop":
            from src.zone1_edge.experts.crop_expert import CropExpert as E
        else:
            from src.zone1_edge.experts.livestock_expert import LivestockExpert as E
        expert = E(mode="real")
        predict = lambda p: (lambda o: (o["prediction"], o["confidence"]))(expert.predict(p))  # noqa: E731
    else:
        raise SystemExit("unknown --target")

    if a.limit:
        items = items[: a.limit]
    y_true, y_pred, conf = [], [], []
    for path, cls in items:
        label, c = predict(path)
        y_true.append(normalize_condition(cls))
        y_pred.append(normalize_condition(label))
        conf.append(float(c))
    rep = classification_report(y_true, y_pred, conf)

    if a.target == "moe":
        shared = {"healthy"} if a.domain == "livestock" else set()
        pairs = [(group_of_class(a.domain, c), r) for (_, c), r in zip(items, routed) if c not in shared]
        extra["moe_gate_routing_accuracy"] = round(sum(g == r for g, r in pairs) / max(len(pairs), 1), 4)
        rep.update(extra)

    out = RESULTS / "zone1" / "eval"
    out.mkdir(parents=True, exist_ok=True)
    name = f"{a.domain}_{a.target.replace(':', '_')}"
    (out / f"{name}.json").write_text(json.dumps(rep, indent=1), encoding="utf-8")
    md = to_markdown(f"{a.domain} / {a.target}", rep) + "".join(f"- {k}: {v}\n" for k, v in extra.items())
    (out / f"{name}.md").write_text(md, encoding="utf-8")
    print(f"accuracy={rep['accuracy']} macro_f1={rep['macro_f1']} ece={rep['calibration']['ece']} {extra} -> {out / name}.md")


if __name__ == "__main__":
    main()
