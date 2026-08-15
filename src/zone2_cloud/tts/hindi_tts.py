"""
hindi_tts.py — STUB. Person B, Zone 2 (Hour 2:30-3:30 of the plan).

GOAL: Convert a Hindi advisory text string into speech audio, so the farmer
hears the recommendation, not just reads it.

STRATEGY (frozen from the plan — follow exactly):
  1. PRIMARY: AI4Bharat Hindi FastPitch + HiFi-GAN.
     - Clone github.com/AI4Bharat/Indic-TTS
     - Use the provided Hindi checkpoint + inference script
     - Budget ~45 minutes to get this working.
  2. FALLBACK: If FastPitch+HiFi-GAN setup stalls past ~45 min, switch
     immediately to IndicF5 (huggingface.co/ai4bharat/IndicF5) — simpler,
     single HF `pipeline()`-style call, ~0.4B params, MIT licensed.
  3. DO NOT attempt Indic Parler-TTS (huggingface.co/ai4bharat/indic-parler-tts)
     — it's ~3.75GB and gated, explicitly out of scope for an 8-hour budget
     (see plan Section 7).

EXPECTED FUNCTION SIGNATURE:

    def synthesize(text: str, out_wav_path: str) -> dict:
        ...
        return {"audio_path": out_wav_path, "engine": "fastpitch_hifigan" | "indicf5",
                "duration_seconds": float}

TODO:
  - Implement `synthesize()` trying FastPitch+HiFi-GAN first.
  - Wrap the whole primary attempt in try/except; on failure/timeout, call
    the IndicF5 fallback path automatically and set "engine" accordingly so
    the UI/logs can show which one actually ran.
  - Log every synthesis run's timing to results/zone2/tts_runs/.

Suggested agent prompt:
    "Write synthesize(text, out_wav_path) that tries AI4Bharat FastPitch +
    HiFi-GAN (from github.com/AI4Bharat/Indic-TTS) first; if that raises any
    exception, fall back to ai4bharat/IndicF5 from Hugging Face via a
    transformers or diffusers-style pipeline call. Return which engine was
    used and the output wav path."
"""

from __future__ import annotations


def _try_fastpitch_hifigan(text: str, out_wav_path: str) -> bool:
    """Return True on success, False to trigger fallback."""
    raise NotImplementedError(
        "TODO: clone AI4Bharat/Indic-TTS and call its Hindi FastPitch+HiFi-GAN "
        "inference script here."
    )


def _try_indicf5(text: str, out_wav_path: str) -> bool:
    """Fallback path — simpler HF pipeline call."""
    raise NotImplementedError(
        "TODO: load ai4bharat/IndicF5 from Hugging Face and synthesize here."
    )


def synthesize(text: str, out_wav_path: str) -> dict:
    """
    Returns: {"audio_path": str, "engine": "fastpitch_hifigan"|"indicf5", "duration_seconds": float}
    """
    raise NotImplementedError(
        "TODO: implement try-primary-then-fallback logic per module docstring."
    )


if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) < 2:
        print('Usage: python -m src.zone2_cloud.tts.hindi_tts "<hindi text>" [out.wav]')
        sys.exit(1)
    text = sys.argv[1]
    out_path = sys.argv[2] if len(sys.argv) > 2 else "/tmp/tts_out.wav"
    print(json.dumps(synthesize(text, out_path), indent=2, ensure_ascii=False))
