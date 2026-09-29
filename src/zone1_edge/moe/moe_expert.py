"""
moe_expert.py — Domain-level MoE: moe_gate (top-1) -> one fine-tuned sub-expert.

Sub-experts are ONNX exports produced by training/finetune_expert.py:
    models_cache/moe/<group>/model.onnx
    models_cache/moe/<group>/meta.json  {"labels": [...], "image_size": 224,
                                         "mean": [..3], "std": [..3]}
ONNX + onnxruntime keeps inference torch-free (serverless/edge friendly).

Output is contract #1 exactly, plus a trailing `_moe` debug key (allowed by
contract.md: extra debug keys appended at the END).
"""

from __future__ import annotations

import json
import logging

import numpy as np
from PIL import Image

from src.zone1_edge import config
from src.zone1_edge.experts.base_image_expert import MockPredictor
from src.zone1_edge.moe.expert_groups import DOMAIN_GROUPS, group_names
from src.zone1_edge.moe.moe_gate import MoEGate, softmax

logger = logging.getLogger(__name__)


def sub_expert_dir(group: str):
    return config.MOE_DIR / group


def sub_experts_available(domain: str) -> bool:
    return all((sub_expert_dir(g) / "model.onnx").exists() for g in group_names(domain))


class OnnxSubExpert:
    def __init__(self, group: str):
        import onnxruntime as ort  # optional runtime dependency

        d = sub_expert_dir(group)
        with open(d / "meta.json", "r", encoding="utf-8") as f:
            self.meta = json.load(f)
        self.labels = self.meta["labels"]
        self.session = ort.InferenceSession(str(d / "model.onnx"), providers=["CPUExecutionProvider"])
        self.input_name = self.session.get_inputs()[0].name

    def predict(self, image_path: str) -> list[tuple[str, float]]:
        # Mirrors timm's eval transform: resize shorter side to size/crop_pct, centre-crop.
        size = int(self.meta.get("image_size", 224))
        img = Image.open(image_path).convert("RGB")
        scale = size / float(self.meta.get("crop_pct", 0.875)) / min(img.size)
        img = img.resize((max(size, round(img.width * scale)), max(size, round(img.height * scale))), Image.BICUBIC)
        left, top = (img.width - size) // 2, (img.height - size) // 2
        img = img.crop((left, top, left + size, top + size))
        x = np.asarray(img, dtype=np.float32) / 255.0
        x = (x - np.asarray(self.meta["mean"], np.float32)) / np.asarray(self.meta["std"], np.float32)
        x = x.transpose(2, 0, 1)[None]
        logits = self.session.run(None, {self.input_name: x})[0][0]
        p = softmax(logits.astype(np.float64))
        return sorted(zip(self.labels, p.tolist()), key=lambda t: t[1], reverse=True)


class MockSubExpert:
    def __init__(self, group: str, domain: str):
        self.predictor = MockPredictor(DOMAIN_GROUPS[domain][group])

    def predict(self, image_path: str) -> list[tuple[str, float]]:
        with open(image_path, "rb") as f:
            return self.predictor.predict(f.read())


class MoEDomainExpert:
    """Runs the moe_gate then exactly one sub-expert (top-1 hard routing)."""

    def __init__(self, domain: str, mock: bool = False):
        self.domain = domain
        self.mock = mock
        self.gate = MoEGate(domain, mock=mock)
        self._experts = {}

    def _expert(self, group: str):
        if group not in self._experts:
            self._experts[group] = MockSubExpert(group, self.domain) if self.mock else OnnxSubExpert(group)
        return self._experts[group]

    def predict(self, image_path: str) -> dict:
        group, gate_probs = self.gate.select(image_path)
        top_k = [[label, round(float(p), 4)] for label, p in self._expert(group).predict(image_path)[:3]]
        prediction, confidence = top_k[0]
        return {
            "domain": self.domain,
            "input_type": "image",
            "prediction": prediction,
            "confidence": round(float(confidence), 4),
            "top_k": top_k,
            "_moe": {
                "component": "moe_gate",
                "gate_kind": self.gate.kind,
                "selected_expert": group,
                "gate_probs": gate_probs,
                "sub_expert_backend": "mock" if self.mock else "onnx",
            },
        }


def moe_enabled(domain: str, mode: str | None) -> bool:
    """
    AGRIVISION_MOE_ENABLED:
      false -> never; true -> always (mock sub-experts when mode == mock);
      auto (default) -> only when a trained gate AND all sub-expert ONNX files exist.
    """
    flag = config.MOE_ENABLED
    if flag == "false":
        return False
    if flag == "true":
        return True
    if (mode or config.EXPERT_MODE) == "mock":
        return False
    return MoEGate.available(domain) and sub_experts_available(domain)


def run(domain: str, image_path: str, mode: str | None = None) -> dict:
    return MoEDomainExpert(domain, mock=((mode or config.EXPERT_MODE) == "mock")).predict(image_path)
