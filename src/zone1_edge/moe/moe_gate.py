"""
moe_gate.py — Learned intra-domain Mixture-of-Experts gate (Zone 1).

NOT the confidence_gate. This gate runs BEFORE any sub-expert, inside an
already-chosen domain (crop | livestock), and selects exactly one sub-expert
(top-1 hard routing). The confidence_gate runs AFTER fusion and decides
local-vs-cloud; the two never share code or state.

Model: multinomial logistic regression (softmax) over the 54-dim descriptor
from image_features.py. Weights are a small JSON file produced by
training/train_moe_gate.py:
    {"domain": "crop", "groups": [...], "feature_dim": 54,
     "mean": [...], "std": [...], "W": [[...]], "b": [...], "trained_on": "..."}
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

from src.zone1_edge import config
from src.zone1_edge.moe.expert_groups import group_names
from src.zone1_edge.moe.image_features import FEATURE_DIM, extract_features


def gate_weights_path(domain: str) -> Path:
    return config.MOE_DIR / f"{domain}_moe_gate.json"


def softmax(z: np.ndarray) -> np.ndarray:
    z = z - z.max(axis=-1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=-1, keepdims=True)


class MoEGate:
    def __init__(self, domain: str, weights: dict | None = None, mock: bool = False):
        self.domain = domain
        self.mock = mock
        self.groups = group_names(domain)
        if mock:
            self.kind = "mock"
            return
        if weights is None:
            with open(gate_weights_path(domain), "r", encoding="utf-8") as f:
                weights = json.load(f)
        if weights["feature_dim"] != FEATURE_DIM:
            raise ValueError("moe_gate weights feature_dim mismatch")
        self.groups = list(weights["groups"])
        self.mean = np.asarray(weights["mean"], dtype=np.float64)
        self.std = np.asarray(weights["std"], dtype=np.float64)
        self.W = np.asarray(weights["W"], dtype=np.float64)  # (n_groups, dim)
        self.b = np.asarray(weights["b"], dtype=np.float64)
        self.kind = "learned"

    @classmethod
    def available(cls, domain: str) -> bool:
        return gate_weights_path(domain).exists()

    def probs(self, image_path: str) -> dict[str, float]:
        if self.mock:
            # Deterministic stand-in for tests: hash-based, NOT a learned decision.
            with open(image_path, "rb") as f:
                h = int(hashlib.sha256(f.read()).hexdigest()[:8], 16)
            p0 = 0.5 + (h % 45) / 100.0
            p = [p0, 1.0 - p0] if h % 2 == 0 else [1.0 - p0, p0]
            return {g: round(v, 4) for g, v in zip(self.groups, p)}
        x = (extract_features(image_path) - self.mean) / self.std
        p = softmax(self.W @ x + self.b)
        return {g: round(float(v), 4) for g, v in zip(self.groups, p)}

    def select(self, image_path: str) -> tuple[str, dict[str, float]]:
        p = self.probs(image_path)
        return max(p, key=p.get), p
