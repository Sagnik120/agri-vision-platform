"""
finetune_expert.py — Fine-tune ONE MoE sub-expert (user-run on a GPU; CPU works but is slow).

Strategy (task.md Phase 1): gradual unfreezing + differential learning rates
  Stage A  backbone frozen, train classifier head only                    (lr_head)
  Stage B  unfreeze top-N backbone blocks                                  head: lr_head*0.5, top: lr_head*0.1
  Stage C  unfreeze everything, end-to-end                                 head: lr_head*0.1, top: lr_head*0.03,
                                                                           rest of blocks: lr_head*0.01, stem: lr_head*0.003
Class-weighted cross-entropy (inverse frequency). Checkpoint = best validation
macro-F1 across ALL stages. Exact N / LRs are CLI flags: tune per backbone on val.

Outputs (default models_cache/moe/<group>/): model.onnx + meta.json (runtime,
torch-free), best.pt, split manifest, training log, test report.

    pip install -r training/requirements-train.txt
    python -m training.finetune_expert --root D:/data/plantvillage --group crop_row
    python -m training.finetune_expert --root D:/data/cattle --group livestock_lsd --class-map training/configs/cattle_class_map.json
Smoke test (tiny, CPU): add  --max-per-class 8 --epochs-a 1 --epochs-b 1 --epochs-c 1 --img 128
"""

from __future__ import annotations

import argparse
import csv
import os
import json
from collections import Counter
from pathlib import Path

from src.zone1_edge.moe.expert_groups import DOMAIN_GROUPS
from training.paths import MODELS
from training.data import list_images, load_class_map, save_manifest, stratified_split
from training.metrics import classification_report, to_markdown


def group_domain(group: str) -> str:
    return next(d for d, gs in DOMAIN_GROUPS.items() if group in gs)


class ImageDS:  # module-level so DataLoader workers can pickle it (Windows spawn)
    def __init__(self, items, idx, data_cfg, train):
        from timm.data import create_transform
        self.items, self.idx, self.size = items, idx, data_cfg["input_size"][-1]
        self.tf = create_transform(**data_cfg, is_training=train)

    def __len__(self):
        return len(self.items)

    def __getitem__(self, i):
        from PIL import Image
        p, c = self.items[i]
        img = Image.open(p)
        img.draft("RGB", (self.size * 2,) * 2)  # JPEG: decode at reduced size (big CPU saving on phone photos)
        return self.tf(img.convert("RGB")), self.idx[c]


def build_loaders(split, labels, data_cfg, batch, workers):
    import torch

    idx = {l: i for i, l in enumerate(labels)}
    mk = lambda items, train: torch.utils.data.DataLoader(  # noqa: E731
        ImageDS(items, idx, data_cfg, train), batch_size=batch, shuffle=train, num_workers=workers,
        pin_memory=torch.cuda.is_available(), persistent_workers=workers > 0,
        prefetch_factor=4 if workers > 0 else None, drop_last=train and len(items) > batch)
    return mk(split["train"], True), mk(split["val"], False), mk(split["test"], False)


def param_groups(model, stage: str, top_n: int, lr: float):
    """Differential LR groups; params not listed are frozen for the stage."""
    head = list(model.get_classifier().parameters())
    head_ids = {id(p) for p in head}
    blocks = list(model.blocks) if hasattr(model, "blocks") else []
    top = [p for b in blocks[-top_n:] for p in b.parameters()] if top_n else []
    rest_blocks = [p for b in blocks[:-top_n or None] for p in b.parameters()] if top_n else [p for b in blocks for p in b.parameters()]
    used = head_ids | {id(p) for p in top} | {id(p) for p in rest_blocks}
    # Non-block, non-classifier params after the blocks (e.g. conv_head) are treated as "top".
    stem, tail = [], []
    seen_blocks = False
    for name, p in model.named_parameters():
        if name.startswith("blocks."):
            seen_blocks = True
        elif id(p) not in used:
            (tail if seen_blocks else stem).append(p)
    top = top + tail
    for p in model.parameters():
        p.requires_grad = False
    if stage == "A":
        groups = [(head, lr)]
    elif stage == "B":
        groups = [(head, lr * 0.5), (top, lr * 0.1)]
    else:
        groups = [(head, lr * 0.1), (top, lr * 0.03), (rest_blocks, lr * 0.01), (stem, lr * 0.003)]
    out = []
    for ps, g_lr in groups:
        for p in ps:
            p.requires_grad = True
        if ps:
            out.append({"params": ps, "lr": g_lr})
    return out


def predict(model, loader, labels, device):
    import torch
    model.eval()
    y_true, y_pred, conf = [], [], []
    with torch.no_grad(), torch.autocast(device_type="cuda", enabled=device == "cuda"):
        for x, y in loader:
            p = torch.softmax(model(x.to(device, non_blocking=True).contiguous(memory_format=torch.channels_last)).float(), dim=1).cpu()
            c, i = p.max(dim=1)
            y_true += [labels[j] for j in y.tolist()]
            y_pred += [labels[j] for j in i.tolist()]
            conf += c.tolist()
    return y_true, y_pred, conf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--group", required=True, choices=[g for gs in DOMAIN_GROUPS.values() for g in gs])
    ap.add_argument("--backbone", default="mobilenetv3_large_100")
    ap.add_argument("--class-map")
    ap.add_argument("--img", type=int, default=224)
    ap.add_argument("--batch", type=int, default=32)
    ap.add_argument("--workers", type=int, default=min(8, os.cpu_count() or 2), help="dataloader processes (CPU-bound JPEG decode)")
    ap.add_argument("--epochs-a", type=int, default=3)
    ap.add_argument("--epochs-b", type=int, default=5)
    ap.add_argument("--epochs-c", type=int, default=5)
    ap.add_argument("--lr-head", type=float, default=1e-3)
    ap.add_argument("--top-blocks", type=int, default=2)
    ap.add_argument("--max-per-class", type=int, default=0, help="cap images/class (smoke tests)")
    ap.add_argument("--out")
    ap.add_argument("--no-pretrained", action="store_true", help="offline smoke test only")
    a = ap.parse_args()

    import timm
    import torch

    labels = DOMAIN_GROUPS[group_domain(a.group)][a.group]
    items = [it for it in list_images(a.root, load_class_map(a.class_map)) if it[1] in labels]
    if a.max_per_class:
        cnt = Counter()
        items = [it for it in items if (cnt.update([it[1]]) or cnt[it[1]] <= a.max_per_class)]
    present = sorted({c for _, c in items})
    missing = [l for l in labels if l not in present]
    if missing:
        print(f"WARNING: no images for {missing}; training on present classes only.")
        labels = [l for l in labels if l in present]
    split = stratified_split(items)
    out = Path(a.out) if a.out else MODELS / "moe" / a.group
    out.mkdir(parents=True, exist_ok=True)
    save_manifest(split, str(out / "split_manifest.json"))

    device = "cuda" if torch.cuda.is_available() else "cpu"
    torch.backends.cudnn.benchmark = True  # fixed input size -> autotune fastest conv kernels
    model = timm.create_model(a.backbone, pretrained=not a.no_pretrained, num_classes=len(labels)).to(device)
    model = model.to(memory_format=torch.channels_last)
    scaler = torch.amp.GradScaler("cuda", enabled=device == "cuda")  # mixed precision: ~2x speed, ~half activation memory
    data_cfg = timm.data.resolve_data_config({"input_size": (3, a.img, a.img)}, model=model)
    train_dl, val_dl, test_dl = build_loaders(split, labels, data_cfg, a.batch, a.workers)

    freq = Counter(c for _, c in split["train"])
    w = torch.tensor([len(split["train"]) / (len(labels) * max(freq[l], 1)) for l in labels], dtype=torch.float)
    loss_fn = torch.nn.CrossEntropyLoss(weight=w.to(device))

    best_f1, best_state, log = -1.0, None, []
    for stage, epochs in (("A", a.epochs_a), ("B", a.epochs_b), ("C", a.epochs_c)):
        opt = torch.optim.AdamW(param_groups(model, stage, a.top_blocks, a.lr_head), weight_decay=1e-4)
        sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max(epochs, 1))
        for ep in range(epochs):
            model.train()
            total = 0.0
            for x, y in train_dl:
                opt.zero_grad(set_to_none=True)
                x = x.to(device, non_blocking=True).contiguous(memory_format=torch.channels_last)
                with torch.autocast(device_type="cuda", enabled=device == "cuda"):
                    loss = loss_fn(model(x).float(), y.to(device, non_blocking=True))
                scaler.scale(loss).backward()
                scaler.step(opt)
                scaler.update()
                total += loss.item() * len(y)
            sched.step()
            rep = classification_report(*predict(model, val_dl, labels, device)[:2], labels=labels)
            row = {"stage": stage, "epoch": ep, "train_loss": round(total / max(len(split["train"]), 1), 4),
                   "val_acc": rep["accuracy"], "val_macro_f1": rep["macro_f1"]}
            log.append(row)
            print(row)
            if rep["macro_f1"] > best_f1:
                best_f1 = rep["macro_f1"]
                best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}

    model.load_state_dict(best_state)
    torch.save(best_state, out / "best.pt")
    with open(out / "training_log.csv", "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(log[0].keys()))
        wr.writeheader()
        wr.writerows(log)

    yt, yp, cf = predict(model, test_dl, labels, device)
    test_rep = classification_report(yt, yp, cf, labels=labels)
    (out / "test_report.json").write_text(json.dumps(test_rep, indent=1), encoding="utf-8")
    (out / "test_report.md").write_text(to_markdown(f"{a.group} ({a.backbone}) — test split", test_rep), encoding="utf-8")

    model.eval().cpu().to(memory_format=torch.contiguous_format)
    torch.onnx.export(model, torch.zeros(1, 3, a.img, a.img), str(out / "model.onnx"),
                      input_names=["input"], output_names=["logits"],
                      dynamic_axes={"input": {0: "batch"}, "logits": {0: "batch"}}, opset_version=17)
    meta = {"group": a.group, "backbone": a.backbone, "labels": labels, "image_size": a.img,
            "mean": list(data_cfg["mean"]), "std": list(data_cfg["std"]),
            "crop_pct": data_cfg.get("crop_pct", 0.875), "best_val_macro_f1": best_f1}
    (out / "meta.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    print(f"Saved ONNX sub-expert to {out}. Test report: {out / 'test_report.md'}")


if __name__ == "__main__":
    main()
