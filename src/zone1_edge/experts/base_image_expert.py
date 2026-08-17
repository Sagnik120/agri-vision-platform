"""
base_image_expert.py — Shared logic for crop_expert.py and livestock_expert.py.

Both experts have the IDENTICAL interface (per contract.md #1):
    {"domain": "...", "input_type": "image", "prediction": str,
     "confidence": float, "top_k": [[label, prob], ...]}

This base class handles:
  1. Trying to load a real Hugging Face image-classification pipeline.
  2. Falling back to a deterministic MockPredictor if the model isn't
     downloaded / no internet / transformers not installed — controlled by
     config.EXPERT_MODE ("auto" | "real" | "mock").
  3. Formatting whatever the model returns into the frozen contract shape.

Why a mock fallback matters: it lets the WHOLE downstream pipeline (fusion,
confidence gate, advisory, Streamlit UI) be built, tested and demoed even
before/without the real HF checkpoint downloaded — exactly what "test the
pipeline end-to-end, nothing breaking" requires.
"""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import List, Tuple

from src.zone1_edge import config

logger = logging.getLogger(__name__)


class MockPredictor:
    """
    Deterministic, seedless fake classifier.

    Same image bytes -> same prediction every run (hash-based), so tests are
    reproducible. This is NOT a real model — it exists purely so the pipeline
    contract can be exercised without a GPU / internet connection.
    """

    def __init__(self, labels: List[str]):
        self.labels = labels

    def predict(self, image_bytes: bytes) -> List[Tuple[str, float]]:
        digest = hashlib.sha256(image_bytes).hexdigest()
        seed_int = int(digest[:8], 16)
        n = len(self.labels)
        # deterministic ranking of labels based on the hash
        order = sorted(range(n), key=lambda i: (seed_int >> i) & 0xFF)
        top_label_idx = order[0]
        base_conf = 0.55 + ((seed_int % 40) / 100.0)  # 0.55 - 0.94
        results = []
        remaining = 1.0 - base_conf
        for rank, idx in enumerate(order):
            if idx == top_label_idx:
                results.append((self.labels[idx], round(base_conf, 4)))
            else:
                share = round(remaining / (n - 1), 4) if n > 1 else 0.0
                results.append((self.labels[idx], share))
        results.sort(key=lambda x: x[1], reverse=True)
        return results


class BaseImageExpert:
    """Override `labels`, `model_candidates`, `local_dir`, `domain` in subclass."""

    domain: str = "crop"
    model_candidates: List[str] = []
    local_dir: Path = None
    labels: List[str] = []  # used only by MockPredictor / fallback relabeling

    def __init__(self, mode: str = None):
        self.mode = mode or config.EXPERT_MODE
        self._hf_pipeline = None
        self._active_model_id = None
        self._backend = None  # "hf" or "mock"
        self._load()

    # -- loading -------------------------------------------------------
    def _load(self):
        if self.mode == "mock":
            self._backend = "mock"
            self._predictor = MockPredictor(self.labels)
            logger.info("[%s] Loaded MOCK predictor (forced by mode=mock)", self.domain)
            return

        if self.mode in ("auto", "real"):
            try:
                self._try_load_hf_pipeline()
                self._backend = "hf"
                return
            except Exception as e:  # noqa: BLE001
                if self.mode == "real":
                    raise RuntimeError(
                        f"[{self.domain}] Forced real mode but HF model failed to "
                        f"load: {e}"
                    ) from e
                logger.warning(
                    "[%s] Real HF model unavailable (%s). Falling back to "
                    "MOCK predictor so the pipeline still runs end-to-end. "
                    "Run setup/download_%s_model.py once you have internet.",
                    self.domain, e, self.domain,
                )
                self._backend = "mock"
                self._predictor = MockPredictor(self.labels)

    def _try_load_hf_pipeline(self):
        from transformers import pipeline  # local import: optional dependency

        # 1. Prefer an already-downloaded local snapshot
        if self.local_dir and self.local_dir.exists() and any(self.local_dir.iterdir()):
            is_clip = False
            for cand in self.model_candidates:
                if "clip" in cand.lower():
                    is_clip = True
                    break
            
            task = "zero-shot-image-classification" if is_clip else "image-classification"
            self._hf_pipeline = pipeline(
                task, model=str(self.local_dir), device="cpu"
            )
            self._active_model_id = str(self.local_dir)
            logger.info("[%s] Loaded local checkpoint: %s", self.domain, self.local_dir)
            return

        # 2. Try each candidate repo id directly from the Hub (needs internet)
        last_err = None
        for repo_id in self.model_candidates:
            try:
                task = "zero-shot-image-classification" if "clip" in repo_id.lower() else "image-classification"
                self._hf_pipeline = pipeline(task, model=repo_id, device="cpu")
                self._active_model_id = repo_id
                logger.info("[%s] Loaded HF hub model: %s", self.domain, repo_id)
                return
            except Exception as e:  # noqa: BLE001
                last_err = e
                continue
        raise RuntimeError(f"No candidate model could be loaded: {last_err}")

    # -- inference -------------------------------------------------------
    def predict(self, image_path: str) -> dict:
        """Run inference and return the EXACT contract JSON (dict)."""
        with open(image_path, "rb") as f:
            image_bytes = f.read()

        if self._backend == "hf":
            from PIL import Image
            import io

            img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            
            if self._hf_pipeline.task == "zero-shot-image-classification":
                raw = self._hf_pipeline(img, candidate_labels=self.labels)
            else:
                raw = self._hf_pipeline(img, top_k=3)
                
            # transformers pipeline returns [{"label":..., "score":...}, ...]
            top_k = [[r["label"], round(float(r["score"]), 4)] for r in raw]
        else:
            top_k = self._predictor.predict(image_bytes)
            top_k = [[label, round(float(prob), 4)] for label, prob in top_k]

        top_k = sorted(top_k, key=lambda x: x[1], reverse=True)[:3]
        prediction, confidence = top_k[0]

        return {
            "domain": self.domain,
            "input_type": "image",
            "prediction": prediction,
            "confidence": round(float(confidence), 4),
            "top_k": top_k,
        }

    @property
    def backend_info(self) -> str:
        if self._backend == "hf":
            return f"hf:{self._active_model_id}"
        return "mock"
