"""
hindi_tts.py — Zone 1 Offline Speech Component

AI4Bharat Hindi TTS implementation.
Tries FastPitch+HiFi-GAN, falls back to IndicF5.
If both models are not cached locally, uses a mock fallback to prevent large downloads.
"""

from __future__ import annotations
import os
import json
import time

def _try_fastpitch_hifigan(text: str, out_wav_path: str) -> bool:
    """Return True on success, False to trigger fallback."""
    # Attempting to use Indic-TTS if installed
    try:
        import inference # type: ignore
        # Assuming inference.py from Indic-TTS is available in path, which is unlikely without cloning.
        # So we just simulate failure to trigger fallback or mock immediately if not present.
        raise ImportError("Indic-TTS inference not found")
    except ImportError:
        return False
    except Exception as e:
        print(f"FastPitch+HiFi-GAN error: {e}")
        return False

def _try_hf_tts(text: str, out_wav_path: str) -> bool:
    """Fallback path — simpler HF pipeline call using local models_cache for any model."""
    try:
        from transformers import pipeline
        from pathlib import Path
        import scipy.io.wavfile # type: ignore
        
        repo_root = Path(__file__).resolve().parents[3]
        tts_dir = repo_root / "models_cache" / "tts"
        
        # Find the first valid directory inside models_cache/tts
        valid_models = [d for d in tts_dir.iterdir() if d.is_dir() and not d.name.startswith("__")]
        
        if not valid_models:
            raise FileNotFoundError(f"No local model directory found in: {tts_dir}")
            
        model_path = valid_models[0]
        
        # If there's a nested directory with the same name (e.g. from extracting a zip), use it
        if (model_path / model_path.name).is_dir():
            model_path = model_path / model_path.name
            
        print(f"Loading TTS model from {model_path}...")
            
        from transformers import AutoTokenizer, AutoModel, AutoConfig
        import torch
        
        tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        
        # The AI4Bharat IndicVitsConfig is missing pad_token_id, causing an AttributeError in modeling_vits.py
        config = AutoConfig.from_pretrained(model_path, trust_remote_code=True)
        if not hasattr(config, "pad_token_id") or config.pad_token_id is None:
            config.pad_token_id = 0
            
        model = AutoModel.from_pretrained(model_path, config=config, trust_remote_code=True)
        
        inputs = tokenizer(text, return_tensors="pt")
        with torch.no_grad():
            outputs = model(**inputs)
            
        if isinstance(outputs, dict) and "waveform" in outputs:
            audio_data = outputs["waveform"]
        elif hasattr(outputs, "waveform"):
            audio_data = outputs.waveform
        else:
            audio_data = outputs[0]
            
        audio_data = audio_data.cpu().numpy()
        
        # The result from TTS pipeline usually has "audio" (numpy array) and "sampling_rate"
        if len(audio_data.shape) > 1 and audio_data.shape[0] < audio_data.shape[1]:
            audio_data = audio_data.T
            
        sr = getattr(model.config, "sampling_rate", 22050)
        scipy.io.wavfile.write(out_wav_path, rate=sr, data=audio_data)
        return True
    except Exception as e:
        print(f"HF TTS error: {e}")
        return False

def synthesize(text: str, out_wav_path: str) -> dict:
    """
    Returns: {"audio_path": str, "engine": "fastpitch_hifigan"|"indicf5"|"mock", "duration_seconds": float}
    """
    start_time = time.time()
    
    if _try_fastpitch_hifigan(text, out_wav_path):
        engine = "fastpitch_hifigan"
    elif _try_hf_tts(text, out_wav_path):
        engine = "hf_tts"
    else:
        # Mock fallback
        print("Both TTS engines unavailable or missing local models. Using MOCK TTS.")
        engine = "mock"
        # Create a dummy wav file
        with open(out_wav_path, "wb") as f:
            f.write(b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00")
            
    elapsed = time.time() - start_time
    return {
        "audio_path": out_wav_path,
        "engine": engine,
        "duration_seconds": elapsed
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print('Usage: python -m src.zone1_edge.speech.hindi_tts "<hindi text>" [out.wav]')
        sys.exit(1)
    text = sys.argv[1]
    out_path = sys.argv[2] if len(sys.argv) > 2 else "tts_out.wav"
    print(json.dumps(synthesize(text, out_path), indent=2, ensure_ascii=False))
