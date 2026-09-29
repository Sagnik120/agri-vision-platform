"""Offline checks for training/eval helpers (no torch training, no datasets downloaded)."""

import numpy as np
from PIL import Image

from training.data import list_images, stratified_split
from training.metrics import classification_report
from training.train_moe_gate import fit_softmax
from src.zone1_edge.moe.moe_gate import softmax


def test_metrics_basic():
    rep = classification_report(["a", "a", "b", "b"], ["a", "b", "b", "b"], [0.9, 0.6, 0.8, 0.7])
    assert rep["accuracy"] == 0.75
    assert rep["per_class"]["a"]["recall"] == 0.5 and rep["per_class"]["b"]["precision"] == round(2 / 3, 4)
    assert rep["confusion_matrix"] == [[1, 1], [0, 2]]
    assert 0 <= rep["calibration"]["ece"] <= 1


def test_split_is_stratified_and_stable_per_class(tmp_path):
    for cls, n in (("x", 20), ("y", 10)):
        (tmp_path / cls).mkdir()
        for i in range(n):
            Image.new("RGB", (8, 8)).save(tmp_path / cls / f"{i}.png")
    items = list_images(str(tmp_path))
    s_all = stratified_split(items)
    s_x = stratified_split([it for it in items if it[1] == "x"])
    assert sum(len(v) for v in s_all.values()) == 30
    assert {p for p, c in s_all["test"] if c == "x"} == {p for p, _ in s_x["test"]}


def test_gate_trainer_learns_separable_data():
    rng = np.random.default_rng(0)
    X = np.vstack([rng.normal(-2, 1, (50, 5)), rng.normal(2, 1, (50, 5))])
    y = np.array([0] * 50 + [1] * 50)
    W, b = fit_softmax(X, y, 2)
    assert (softmax(X @ W.T + b).argmax(1) == y).mean() > 0.95


def test_presplit_dataset_layout(tmp_path):
    from training.data import list_images, load_split, presplit_dirs
    for split, n in (("train", 6), ("val", 8)):
        for cls in ("A___x", "B___y"):
            d = tmp_path / split / cls
            d.mkdir(parents=True)
            for i in range(n):
                Image.new("RGB", (8, 8)).save(d / f"{i}.png")
    assert set(presplit_dirs(str(tmp_path))) == {"train", "val"}
    assert {c for _, c in list_images(str(tmp_path))} == {"A___x", "B___y"}  # train/val are NOT classes
    s = load_split(str(tmp_path))
    assert len(s["train"]) == 12 and len(s["val"]) == 8 and len(s["test"]) == 8
    assert not {p for p, _ in s["val"]} & {p for p, _ in s["test"]}
    assert all("/train/" in p.replace("\\", "/") for p, _ in s["train"])
    assert all("/val/" in p.replace("\\", "/") for p, _ in s["test"] + s["val"])
