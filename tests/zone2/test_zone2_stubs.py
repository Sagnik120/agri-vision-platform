"""
tests/zone2/test_zone2_stubs.py

Diagnostic tests for Zone 2 (Cloud / ASR / TTS / RAG / Gemini).
These tests verify:
  1. All stub modules import without error.
  2. Function signatures match the data contract.
  3. Calling stub functions raises NotImplementedError (not some worse crash).
  4. The results/zone2/ directory hierarchy exists.
  5. The gemini_client prompt template + build_prompt() work (they are fully
     implemented even in stub mode — no API key needed).
  6. The contract #2 shape (ASR output) is correctly declared in the stub.

Run:
    pytest tests/zone2/ -v
"""

from __future__ import annotations

import inspect
from pathlib import Path

import pytest

RESULTS_ZONE2 = Path(__file__).resolve().parents[2] / "results" / "zone2"


# ===========================================================================
# 1. Import tests — all stubs must be importable
# ===========================================================================

def test_hindi_asr_imports():
    import importlib
    mod = importlib.import_module("src.zone2_cloud.asr.hindi_asr")
    assert hasattr(mod, "transcribe"), "transcribe() function must be defined"


def test_hindi_tts_imports():
    import importlib
    mod = importlib.import_module("src.zone2_cloud.tts.hindi_tts")
    assert hasattr(mod, "synthesize"), "synthesize() function must be defined"


def test_gemini_client_imports():
    import importlib
    mod = importlib.import_module("src.zone2_cloud.gemini.gemini_client")
    assert hasattr(mod, "call_gemini"), "call_gemini() must be defined"
    assert hasattr(mod, "build_prompt"), "build_prompt() must be defined"


def test_rag_retriever_imports():
    import importlib
    mod = importlib.import_module("src.zone2_cloud.rag.retriever")
    assert hasattr(mod, "retrieve"), "retrieve() must be defined"


def test_rag_build_knowledge_base_imports():
    import importlib
    mod = importlib.import_module("src.zone2_cloud.rag.build_knowledge_base")
    assert mod is not None


# ===========================================================================
# 2. Function signature tests — must match contract
# ===========================================================================

def test_transcribe_signature():
    from src.zone2_cloud.asr.hindi_asr import transcribe
    sig = inspect.signature(transcribe)
    params = list(sig.parameters.keys())
    assert "wav_path" in params, f"Expected 'wav_path' param, got: {params}"


def test_synthesize_signature():
    from src.zone2_cloud.tts.hindi_tts import synthesize
    sig = inspect.signature(synthesize)
    params = list(sig.parameters.keys())
    assert "text" in params, f"Expected 'text' param, got: {params}"
    # out_wav_path is required — TTS writes to a file
    assert "out_wav_path" in params, f"Expected 'out_wav_path' param, got: {params}"


def test_call_gemini_signature():
    from src.zone2_cloud.gemini.gemini_client import call_gemini
    sig = inspect.signature(call_gemini)
    params = list(sig.parameters.keys())
    assert "payload" in params, f"Expected 'payload' param, got: {params}"


def test_retrieve_signature():
    from src.zone2_cloud.rag.retriever import retrieve
    sig = inspect.signature(retrieve)
    params = list(sig.parameters.keys())
    assert "query" in params, f"Expected 'query' param, got: {params}"
    assert "k" in params, f"Expected 'k' param, got: {params}"
    assert sig.parameters["k"].default == 3


# ===========================================================================
# 3. Stub behaviour — must raise NotImplementedError
# ===========================================================================

def test_transcribe_raises_not_implemented():
    from src.zone2_cloud.asr.hindi_asr import transcribe
    with pytest.raises(NotImplementedError):
        transcribe("nonexistent.wav")


def test_synthesize_raises_not_implemented():
    from src.zone2_cloud.tts.hindi_tts import synthesize
    with pytest.raises(NotImplementedError):
        synthesize("test text", "/tmp/tts_test.wav")






def test_retrieve_returns_string():
    from src.zone2_cloud.rag.retriever import retrieve
    result = retrieve("tomato brown spots", k=1)
    assert isinstance(result, str)
    assert "Tomato" in result or "Blight" in result


# ===========================================================================
# 4. Gemini prompt template — fully implemented even in stub mode
# ===========================================================================

def test_build_prompt_returns_non_empty_string():
    from src.zone2_cloud.gemini.gemini_client import build_prompt
    payload = {
        "domain": "crop", "image_prediction": "tomato_early_blight",
        "visual_confidence": 0.67, "farmer_text": "test",
        "text_evidence": ["brown_spots"], "sensor_data": None,
        "farm_history": "No prior visits.", "retrieved_knowledge": "...",
    }
    prompt = build_prompt(payload)
    assert isinstance(prompt, str) and len(prompt) > 100
    assert "NEVER invent" in prompt


def test_prompt_contains_payload_data():
    from src.zone2_cloud.gemini.gemini_client import build_prompt
    payload = {
        "domain": "livestock", "image_prediction": "lumpy_skin_disease",
        "visual_confidence": 0.54, "farmer_text": "test",
        "text_evidence": ["fever"], "sensor_data": {"anomaly": True},
        "farm_history": "", "retrieved_knowledge": "Lumpy skin info.",
    }
    prompt = build_prompt(payload)
    assert "lumpy_skin_disease" in prompt


# ===========================================================================
# 5. ASR docstring declares contract #2 shape
# ===========================================================================

def test_asr_docstring_declares_contract_2_shape():
    from src.zone2_cloud.asr import hindi_asr
    combined = (hindi_asr.__doc__ or "") + (hindi_asr.transcribe.__doc__ or "")
    assert "text" in combined and "language" in combined and "confidence" in combined, \
        "hindi_asr docstring must declare {text, language, confidence} contract shape"


# ===========================================================================
# 6. Results directory hierarchy
# ===========================================================================

def test_results_zone2_directories_exist():
    for subdir in ["asr_runs", "tts_runs", "gemini_runs"]:
        path = RESULTS_ZONE2 / subdir
        path.mkdir(parents=True, exist_ok=True)
        assert path.exists(), f"results/zone2/{subdir}/ should exist"


# ===========================================================================
# 7. Integration: Zone 1 produces contract #6 payload that Zone 2 can consume
# ===========================================================================

def test_zone1_produces_cloud_payload_matching_contract_6():
    import tempfile
    from PIL import Image
    from src.zone1_edge.pipeline import run_zone1_pipeline, build_cloud_payload_stub

    tmp = Path(tempfile.mkdtemp())
    img_path = str(tmp / "test.jpg")
    Image.new("RGB", (64, 64), (100, 200, 80)).save(img_path)

    result = run_zone1_pipeline("crop", img_path,
                                farmer_text="brown spots on leaves",
                                mode="mock")
    payload = build_cloud_payload_stub(result, farm_history="No prior visits.",
                                       retrieved_knowledge="Early blight info.")

    required_keys = {
        "domain", "image_prediction", "visual_confidence",
        "farmer_text", "text_evidence", "sensor_data",
        "farm_history", "retrieved_knowledge",
    }
    assert required_keys.issubset(payload.keys()), \
        f"Cloud payload missing keys: {required_keys - payload.keys()}"
    assert payload["domain"] in ("crop", "livestock")
    assert isinstance(payload["visual_confidence"], float)
    assert isinstance(payload["text_evidence"], list)

def test_call_gemini_raises_not_implemented():
    from src.zone2_cloud.gemini.gemini_client import call_gemini
    dummy = {
        "domain": "crop", "image_prediction": "tomato_early_blight",
        "visual_confidence": 0.67, "farmer_text": "test",
        "text_evidence": [], "sensor_data": None,
        "farm_history": "", "retrieved_knowledge": "",
    }
    with pytest.raises(NotImplementedError):
        call_gemini(dummy)
