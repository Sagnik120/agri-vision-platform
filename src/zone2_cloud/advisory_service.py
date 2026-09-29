"""
advisory_service.py — Zone 2 entry point for cloud advisories.

1. Adds cloud-only weather context (graceful: None on any failure / disabled).
2. Dispatches to the configured backend (ADVISORY_BACKEND):
     gemini    (default) -> call_gemini()  (itself mock when GEMINI_ENABLED=false)
     local_llm           -> LocalLLMClient, falling back to call_gemini() on error
     mock                -> MockGeminiClient path regardless of GEMINI_ENABLED
3. Runs post-generation citation verification and attaches `_citation_check`
   and `_backend` (trailing debug keys).
"""

from __future__ import annotations

import os

from src.zone2_cloud.context.weather_client import get_weather
from src.zone2_cloud.gemini import gemini_client
from src.zone2_cloud.gemini.validator import validate_advisory, verify_citations

SAFE_FALLBACK = {
    "diagnosis": {"condition": "unknown", "certainty": "insufficient_evidence"},
    "advisory": {"summary": "Error generating advisory.", "actions": ["Consult an expert locally."],
                 "warning": "Advisory service unavailable or malformed response."},
    "expert_consultation_recommended": True,
    "cited_knowledge": [],
}


def selected_backend() -> str:
    return os.environ.get("ADVISORY_BACKEND", "gemini").lower()


def _call_local_llm(payload: dict) -> dict:
    from src.zone2_cloud.llm.local_llm_client import LocalLLMClient

    parsed = LocalLLMClient().generate(payload)
    if not isinstance(parsed, dict) or "advisory" not in parsed:
        raise ValueError("local LLM returned a response without 'advisory'")
    snippets = payload.get("retrieved_knowledge", [])
    snippets = [snippets] if isinstance(snippets, str) else snippets
    ok, reasons = validate_advisory(parsed, snippets, payload)
    if not ok:
        parsed["advisory"]["warning"] = parsed["advisory"].get("warning", "") + f"\nSystem Note: {reasons[0]}"
        if any("dosage" in r.lower() for r in reasons):
            parsed["advisory"]["actions"] = ["Please consult a local expert for safe treatment guidelines."]
    return parsed


def generate_advisory(payload: dict) -> dict:
    payload = dict(payload)
    if payload.get("weather") is None:
        payload["weather"] = get_weather(payload.get("region"))

    backend = selected_backend()
    used = backend
    if backend == "local_llm":
        try:
            result = _call_local_llm(payload)
        except Exception as e:  # noqa: BLE001 - Gemini/mock stays the fallback
            print(f"Local LLM backend failed ({type(e).__name__}); falling back to Gemini/mock.")
            result, used = gemini_client.call_gemini(payload), "gemini_fallback"
    elif backend == "mock":
        prev = os.environ.get("GEMINI_ENABLED")
        os.environ["GEMINI_ENABLED"] = "false"
        try:
            result = gemini_client.call_gemini(payload)
        finally:
            if prev is None:
                os.environ.pop("GEMINI_ENABLED", None)
            else:
                os.environ["GEMINI_ENABLED"] = prev
    else:
        result = gemini_client.call_gemini(payload)

    result = result or dict(SAFE_FALLBACK)
    result["_citation_check"] = verify_citations(result, payload)
    if used in ("gemini", "gemini_fallback", "mock") and os.environ.get("GEMINI_ENABLED", "false").lower() != "true":
        used = f"{used}(MOCK-client)"
    result["_backend"] = used
    result["_weather_used"] = payload.get("weather")
    return result
