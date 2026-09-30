"""English -> Hindi translation of advisory text with IndicTrans2 (AI4Bharat), fully offline.

Only the model's own text is translated. Chemical/product names, doses and numbers are
swapped for placeholders first so the translator can never alter them, then restored.
If the model can't load, callers get None and keep showing the English original —
a wrong safety translation is worse than none (MarianMT was tested and rejected for this).
"""

from __future__ import annotations

import logging
import os
import re
import threading
import time

logger = logging.getLogger(__name__)

MODEL_ID = os.environ.get("TRANSLATION_MODEL", "ai4bharat/indictrans2-en-indic-dist-200M")
_ENABLED = os.environ.get("TRANSLATION_ENABLED", "true").lower() in ("1", "true", "yes", "on")

_lock = threading.Lock()
_state: dict = {"model": None, "tok": None, "error": None, "failed_at": 0.0}
_RETRY_AFTER_S = 60  # e.g. licence just accepted on Hugging Face — try again without a restart

# Agrochemicals, fertilisers and drugs that appear in advice. Kept verbatim (Latin script)
# so a farmer can match them against the label on the packet.
_PROTECTED_TERMS = [
    "mancozeb", "chlorothalonil", "propiconazole", "tebuconazole", "tricyclazole", "carbendazim", "metalaxyl",
    "copper oxychloride", "copper hydroxide", "streptocycline", "imidacloprid", "thiamethoxam", "emamectin benzoate",
    "chlorpyrifos", "neem oil", "urea", "DAP", "superphosphate", "MOP", "NPK", "propylene glycol", "ivermectin",
    "oxytetracycline", "KVK", "PPR", "FMD", "LSD",
]
_TERM_RE = re.compile(r"\b(" + "|".join(sorted(map(re.escape, _PROTECTED_TERMS), key=len, reverse=True)) + r")\b", re.I)
# Doses, ranges, percentages, units: "2.5 g/L", "7-10 days", "50%", "24 hours"
_NUM_RE = re.compile(r"(?<![A-Za-z\d])\d+(?:[.,]\d+)?(?:\s*[-–]\s*\d+(?:[.,]\d+)?)?\s*(?:%|°C|ml/l|g/l|kg/ha|kg|g|ml|l|mm|km/h)?(?![A-Za-z\d])", re.I)


def enabled() -> bool:
    return _ENABLED


class _IndicTokenizer:
    """Minimal port of IndicTrans2's tokenizer (its remote code targets transformers 4.x):
    source = [src_tag, tgt_tag] + SentencePiece pieces + </s>, left-padded; target decoded via dict.TGT."""

    def __init__(self, path: str):
        import json

        from sentencepiece import SentencePieceProcessor

        with open(f"{path}/dict.SRC.json", encoding="utf-8") as f:
            self.src = json.load(f)
        with open(f"{path}/dict.TGT.json", encoding="utf-8") as f:
            self.tgt_inv = {v: k for k, v in json.load(f).items()}
        self.spm = SentencePieceProcessor(model_file=f"{path}/model.SRC")
        self.pad, self.unk, self.eos = self.src["<pad>"], self.src["<unk>"], self.src["</s>"]

    def encode(self, sentences: list[str], src: str = "eng_Latn", tgt: str = "hin_Deva", max_len: int = 256):
        import torch

        rows = []
        for s in sentences:
            pieces = [src, tgt] + self.spm.EncodeAsPieces(s)
            rows.append([self.src.get(p, self.unk) for p in pieces][: max_len - 1] + [self.eos])
        width = max(len(r) for r in rows)
        ids = [[self.pad] * (width - len(r)) + r for r in rows]
        mask = [[0] * (width - len(r)) + [1] * len(r) for r in rows]
        return {"input_ids": torch.tensor(ids), "attention_mask": torch.tensor(mask)}

    def decode(self, row) -> str:
        toks = [self.tgt_inv.get(int(i), "") for i in row]
        toks = [t for t in toks if t and not (t.startswith("<") and t.endswith(">"))]
        return "".join(toks).replace("\u2581", " ").strip()


def _patch_model_class(path: str) -> None:
    """transformers 5 calls tie_weights(recompute_mapping=...); IndicTrans2's override takes no args."""
    from transformers.dynamic_module_utils import get_class_from_dynamic_module

    cls = get_class_from_dynamic_module("modeling_indictrans.IndicTransForConditionalGeneration", path)
    if getattr(cls, "_agrivision_patched", False):
        return

    def tie_weights(self, *args, **kwargs):
        if self.config.share_decoder_input_output_embed:
            self.lm_head.weight = self.model.decoder.embed_tokens.weight

    cls.tie_weights = tie_weights
    cls._agrivision_patched = True


def _shim_transformers_onnx() -> None:
    """IndicTrans2's remote config imports ONNX-export helpers that transformers 5 removed.
    They're only used for ONNX export, never for translation, so empty stand-ins suffice."""
    import importlib.util
    import sys
    import types

    if importlib.util.find_spec("transformers.onnx") is not None or "transformers.onnx" in sys.modules:
        return
    onnx = types.ModuleType("transformers.onnx")
    utils = types.ModuleType("transformers.onnx.utils")

    class OnnxConfig:  # noqa: D401 - placeholder base class
        def __init__(self, *args, **kwargs):
            pass

    class OnnxSeq2SeqConfigWithPast(OnnxConfig):
        pass

    onnx.OnnxConfig = OnnxConfig
    onnx.OnnxSeq2SeqConfigWithPast = OnnxSeq2SeqConfigWithPast
    utils.compute_effective_axis_dimension = lambda dimension, fixed_dimension, num_token_to_add=0: dimension
    onnx.utils = utils
    sys.modules["transformers.onnx"] = onnx
    sys.modules["transformers.onnx.utils"] = utils


def _load() -> bool:
    if _state["model"] is not None:
        return True
    if not _ENABLED or (_state["error"] is not None and time.time() - _state["failed_at"] < _RETRY_AFTER_S):
        return False
    with _lock:
        if _state["model"] is not None:
            return True
        try:
            _shim_transformers_onnx()
            from transformers import AutoModelForSeq2SeqLM

            from huggingface_hub import snapshot_download

            path = snapshot_download(MODEL_ID, allow_patterns=["*.json", "*.py", "model.SRC", "model.TGT", "*.safetensors"])
            tok = _IndicTokenizer(path)
            _patch_model_class(path)
            model = AutoModelForSeq2SeqLM.from_pretrained(path, trust_remote_code=True)
            # transformers 5 builds models on the meta device, so these non-persistent sinusoidal
            # buffers (never stored in the checkpoint) come back uninitialised — rebuild them.
            for mod in model.modules():
                if type(mod).__name__ == "IndicTransSinusoidalPositionalEmbedding":
                    mod.weights = mod.get_embedding(mod.weights.shape[0], mod.embedding_dim, mod.padding_idx)
            model.eval()
            _state.update(model=model, tok=tok, error=None)
            logger.info("Translation model loaded: %s", MODEL_ID)
            return True
        except Exception as e:  # noqa: BLE001 - any failure means "no translation"
            _state.update(error=str(e).splitlines()[0][:300], failed_at=time.time())
            logger.warning("Translation model unavailable (%s): %s", MODEL_ID, e)
            return False


def warm_up() -> None:
    """Load in the background at startup so the first Hindi view doesn't wait for it."""
    if _ENABLED:
        threading.Thread(target=_load, name="translation-warmup", daemon=True).start()


def status() -> dict:
    return {"enabled": _ENABLED, "model": MODEL_ID, "loaded": _state["model"] is not None, "error": _state["error"]}


def _protect(text: str) -> tuple[str, list[str]]:
    kept: list[str] = []

    def keep(m: re.Match) -> str:
        kept.append(m.group(0))
        return f"X{len(kept) - 1}X"

    text = _TERM_RE.sub(keep, text)
    text = _NUM_RE.sub(lambda m: keep(m) if m.group(0).strip() else m.group(0), text)
    return text, kept


def _restore(text: str, kept: list[str]) -> str:
    for i, v in enumerate(kept):
        text = re.sub(rf"X\s*{i}\s*X", v, text, count=1)
    return text


def _sentences(text: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s]


def translate_many(texts: list[str]) -> list[str] | None:
    """Translate a batch of English strings to Hindi. None if the model is unavailable."""
    if not texts:
        return []
    if not _load():
        return None
    import torch

    tok, model = _state["tok"], _state["model"]
    # Split into sentences (the model is trained sentence-level), remember where each came from.
    pieces: list[tuple[int, str, list[str]]] = []
    for idx, t in enumerate(texts):
        for s in _sentences(t or ""):
            prot, kept = _protect(s)
            pieces.append((idx, prot, kept))
    if not pieces:
        return list(texts)

    with _lock, torch.inference_mode():
        batch = tok.encode([p for _, p, _ in pieces])
        # use_cache=False: the remote decoder expects legacy tuple caches, transformers 5 passes Cache objects.
        out = model.generate(**batch, max_length=256, num_beams=4, use_cache=False)
        decoded = [tok.decode(row) for row in out]

    result = ["" for _ in texts]
    for (idx, _, kept), hi in zip(pieces, decoded):
        result[idx] = (result[idx] + " " + _restore(hi.strip(), kept)).strip()
    return result
