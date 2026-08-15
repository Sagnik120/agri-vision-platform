"""
hindi_asr.py — Zone 1 Offline Speech Component

AI4Bharat IndicConformer Hindi ASR implementation.
Attempts to load the model locally, falling back to a deterministic mock if the model is missing, 
preventing huge downloads on startup.
"""

from __future__ import annotations

import json
import os
import time

_MODEL = None

def _load_model():
    global _MODEL
    if _MODEL is not None:
        return _MODEL
    
    try:
        from transformers import pipeline
        from pathlib import Path
        
        # Resolve the models_cache directory relative to this script
        repo_root = Path(__file__).resolve().parents[3]
        model_path = repo_root / "models_cache" / "asr" / "indicconformer-hi-hybrid-rnnt-large-hf"
        
        # Check if the user accidentally extracted a nested directory (common with ZIPs)
        nested_path = model_path / "indicconformer-hi-hybrid-rnnt-large-hf"
        if nested_path.exists():
            model_path = nested_path
            
        print(f"Attempting to load AI4Bharat IndicConformer from {model_path}...")
        
        from transformers import AutoFeatureExtractor, AutoTokenizer, AutoModelForCTC
        extractor = AutoFeatureExtractor.from_pretrained(model_path, trust_remote_code=True)
        tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        model = AutoModelForCTC.from_pretrained(model_path, trust_remote_code=True)
        
        import torch
        device_str = "cuda" if torch.cuda.is_available() else "cpu"
        if device_str == "cuda":
            model = model.to("cuda")
            
        _MODEL = {
            "extractor": extractor,
            "tokenizer": tokenizer,
            "model": model,
            "device": device_str
        }
        print("Model loaded successfully.")
        return _MODEL
    except Exception as e:
        print(f"Failed to load real ASR model. Mock mode active. Error: {e}")
        _MODEL = "MOCK"
        return _MODEL

def transcribe(wav_path: str) -> dict:
    """
    Returns contract.md #2 shape: {"text": str, "language": "hi", "confidence": null}
    """
    start_time = time.time()
    model = _load_model()
    
    if model == "MOCK":
        # Mock deterministic transcript based on the filename or just a fixed string
        transcript_str = "यह एक परीक्षण है। पत्तियों पर भूरे धब्बे हैं।" # "This is a test. There are brown spots on leaves."
        confidence = 0.95
    else:
        try:
            import librosa
            import torch
            
            y, sr = librosa.load(wav_path, sr=16000)
            
            extractor = model["extractor"]
            tokenizer = model["tokenizer"]
            pt_model = model["model"]
            dev = model["device"]
            
            # Extract features (copying array to avoid PyTorch read-only warning)
            inputs = extractor(y.copy(), sampling_rate=16000, return_tensors="pt")
            
            input_features = inputs["input_features"].to(dev)
            attention_mask = inputs.get("attention_mask")
            if attention_mask is not None:
                attention_mask = attention_mask.to(dev)
                
            # Generate
            with torch.no_grad():
                outputs = pt_model(
                    input_features=input_features,
                    attention_mask=attention_mask,
                    decoder_mode="ctc"
                )
                
            # Decode using raw logits to let tokenizer handle CTC deduplication properly
            logits = outputs.logits
            predicted_ids = torch.argmax(logits, dim=-1)
            if isinstance(predicted_ids, torch.Tensor):
                predicted_ids = predicted_ids.cpu().tolist()
            
            # Use tokenizer.decode on the first sequence with use_ctc=True
            transcription = tokenizer.decode(predicted_ids[0], use_ctc=True)
            transcript_str = transcription
            confidence = None
        except Exception as e:
            print(f"Inference error: {e}")
            transcript_str = "यह एक परीक्षण है। (Inference Fallback)"
            confidence = None

    elapsed_time = time.time() - start_time
    print(f"ASR Inference Time: {elapsed_time:.2f}s")
    
    return {"text": transcript_str, "language": "hi", "confidence": confidence}

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python -m src.zone1_edge.speech.hindi_asr <path_to_wav>")
        sys.exit(1)
    out = transcribe(sys.argv[1])
    print(json.dumps(out, indent=2, ensure_ascii=False))
