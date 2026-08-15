"""
hindi_asr.py — STUB. Person B, Zone 2 (Hour 0:15-1:30 of the plan).

GOAL: Load AI4Bharat IndicConformer (Hindi, ~30M params) from
huggingface.co/collections/ai4bharat/indicconformer and transcribe a .wav
file, returning contract.md #2:

    {"text": str, "language": "hi", "confidence": null}

TODO (in order):
  1. `pip install` whatever IndicConformer needs (check the HF model card —
     likely `nemo_toolkit` or a `transformers`-compatible wrapper; the HF
     collection page will specify).
  2. Download the checkpoint once (either via huggingface_hub.snapshot_download
     into a local cache dir, mirroring setup/download_crop_model.py's pattern,
     or via NeMo's `.from_pretrained()` if that's what the model card says).
  3. Implement `transcribe(wav_path: str) -> dict` below.
  4. Standalone test FIRST: record 3-4 fixed Hindi sentences yourself
     (crop / livestock / healthy / ambiguous) into demo_data/audio/*.wav and
     run this file directly to confirm transcript quality before wiring into
     anything else (per the plan's explicit instruction: "Prove load time,
     inference time, and transcript quality BEFORE wiring into anything else").
  5. Log timing: model load time and per-utterance inference time — these
     matter for the "offline, real-time on-device" pitch of the demo.

EXPECTED FUNCTION SIGNATURE (do not change — text_evidence.py depends on it
indirectly via the returned dict shape):

    def transcribe(wav_path: str) -> dict:
        ...
        return {"text": transcript_str, "language": "hi", "confidence": None}

Suggested agent prompt:
    "Write a Python function transcribe(wav_path) that loads AI4Bharat
    IndicConformer Hindi from Hugging Face (collection:
    ai4bharat/indicconformer), runs inference on the given wav file, and
    returns {"text": str, "language": "hi", "confidence": None}. Cache the
    loaded model at module level so repeated calls don't reload it."
"""

from __future__ import annotations

# TODO: import whatever the IndicConformer HF model card requires, e.g.:
# from transformers import AutoModel, AutoProcessor
# or NeMo's nemo.collections.asr as nemo_asr

_MODEL = None  # cache the loaded model here so it's only loaded once per process


def _load_model():
    global _MODEL
    if _MODEL is not None:
        return _MODEL
    raise NotImplementedError(
        "TODO: load AI4Bharat IndicConformer Hindi here. "
        "See huggingface.co/collections/ai4bharat/indicconformer for the "
        "correct loading API (NeMo or transformers-based)."
    )


def transcribe(wav_path: str) -> dict:
    """
    Returns contract.md #2 shape: {"text": str, "language": "hi", "confidence": null}
    """
    raise NotImplementedError(
        "TODO: implement transcription. See module docstring for the plan."
    )


if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) < 2:
        print("Usage: python -m src.zone2_cloud.asr.hindi_asr <path_to_wav>")
        sys.exit(1)
    out = transcribe(sys.argv[1])
    print(json.dumps(out, indent=2, ensure_ascii=False))
