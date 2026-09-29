"""
image_features.py — Fixed, numpy-only image descriptor for the moe_gate.

Deliberately torch-free so the gate runs inside a ~512MB serverless function.
The SAME function is used at training time (training/train_moe_gate.py) and
at inference time, so there is no train/serve skew.

Descriptor (54 dims, L1-normalised histograms):
  16 hue + 8 saturation + 8 value histogram bins     (colour: leaf vs fruit vs hide)
  8 gradient-magnitude bins + 8 gradient-orientation (texture: lesions, lumps, veins)
  6 per-channel RGB mean/std
"""

from __future__ import annotations

import numpy as np
from PIL import Image

FEATURE_DIM = 54
_SIZE = 64


def _hist(values: np.ndarray, bins: int, lo: float, hi: float) -> np.ndarray:
    h, _ = np.histogram(values, bins=bins, range=(lo, hi))
    h = h.astype(np.float64)
    return h / max(h.sum(), 1.0)


def extract_features(image: "Image.Image | str") -> np.ndarray:
    if isinstance(image, str):
        image = Image.open(image)
    img = image.convert("RGB").resize((_SIZE, _SIZE))
    rgb = np.asarray(img, dtype=np.float64) / 255.0
    hsv = np.asarray(img.convert("HSV"), dtype=np.float64) / 255.0

    gray = rgb.mean(axis=2)
    gy, gx = np.gradient(gray)
    mag = np.hypot(gx, gy)
    ang = np.arctan2(gy, gx)  # [-pi, pi]

    feats = np.concatenate([
        _hist(hsv[..., 0], 16, 0, 1),
        _hist(hsv[..., 1], 8, 0, 1),
        _hist(hsv[..., 2], 8, 0, 1),
        _hist(mag, 8, 0, 0.5),
        _hist(ang, 8, -np.pi, np.pi),
        rgb.reshape(-1, 3).mean(axis=0),
        rgb.reshape(-1, 3).std(axis=0),
    ])
    assert feats.shape[0] == FEATURE_DIM
    return feats
