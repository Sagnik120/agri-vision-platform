"""
gemini_client.py — Person B, Zone 2

Cloud escalation client using the official google-genai SDK.
Supports a MockGeminiClient for local testing when GEMINI_ENABLED=false.
"""

from __future__ import annotations

import json
import os
from typing import Any

from google import genai

SYSTEM_PROMPT_TEMPLATE = """You are an agricultural and veterinary advisory assistant \
helping smallholder farmers in India. You will be given: an image-based \
model prediction, farmer-reported symptoms (voice-transcribed), optional \
sensor data, this farm's prior history, and retrieved knowledge-base \
snippets.

STRICT RULES — follow all of them:
1. Use ONLY the image prediction, farmer text, sensor data, farm history, \
   and retrieved knowledge provided below. Do not invent facts not present \
   in this context.
2. NEVER invent a diagnosis that isn't supported by the evidence given.
3. NEVER invent specific drug names, dosages, or treatment quantities not \
   present in the retrieved knowledge.
4. Clearly distinguish between "possible" and "confirmed" diagnoses based on \
   evidence strength.
5. If the evidence is insufficient or contradictory, say so explicitly \
   rather than guessing.
6. Always recommend consulting a local agricultural/veterinary expert when \
   the situation is severe, ambiguous, or the disease is reportable \
   (e.g. Foot-and-Mouth Disease, Lumpy Skin Disease).
7. Return ONLY valid JSON matching the schema below — no prose, no markdown \
   fences.

Context:
{context_json}

Return JSON with this exact shape:
{{
  "diagnosis": {{"condition": "...", "certainty": "possible|confirmed|insufficient_evidence"}},
  "advisory": {{"summary": "...", "actions": ["..."], "warning": "..."}},
  "expert_consultation_recommended": true|false,
  "cited_knowledge": ["..."]
}}
"""


def strip_pii(payload: dict) -> dict:
    """Removes sensitive farmer PII before sending to cloud."""
    cleaned = payload.copy()
    cleaned.pop("farmer_name", None)
    cleaned.pop("phone", None)
    return cleaned

def build_prompt(payload: dict) -> str:
    cleaned_payload = strip_pii(payload)
    return SYSTEM_PROMPT_TEMPLATE.format(context_json=json.dumps(cleaned_payload, ensure_ascii=False, indent=2))


class MockGeminiClient:
    """A deterministic mock client that returns a valid structured advisory for offline testing."""
    def __init__(self):
        class MockModels:
            def generate_content(self, model: str, contents: str, config: Any = None):
                class MockResponse:
                    @property
                    def text(self):
                        return json.dumps({
                            "diagnosis": {"condition": "mock_disease", "certainty": "possible"},
                            "advisory": {
                                "summary": "This is a mock advisory from MockGeminiClient.",
                                "actions": ["Isolate affected mock plants/animals.", "Consult local mock expert."],
                                "warning": "Mock warning: handle with care."
                            },
                            "expert_consultation_recommended": True,
                            "cited_knowledge": ["Mock knowledge snippet about mock_disease"]
                        })
                return MockResponse()
        self.models = MockModels()


def call_gemini(payload: dict) -> dict:
    """
    Calls the Gemini API (or Mock if GEMINI_ENABLED=false) to get a structured advisory.
    """
    gemini_enabled = os.environ.get("GEMINI_ENABLED", "false").lower() == "true"
    model_name = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash-lite")
    
    prompt = build_prompt(payload)
    
    if gemini_enabled:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY must be set when GEMINI_ENABLED=true")
        client = genai.Client(api_key=api_key)
    else:
        client = MockGeminiClient()
        
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                response_mime_type="application/json",
            )
        )
        parsed = json.loads(response.text)
        
        # Validation
        from src.zone2_cloud.gemini.validator import validate_advisory
        retrieved_snippets = payload.get("retrieved_knowledge", [])
        if isinstance(retrieved_snippets, str):
            retrieved_snippets = [retrieved_snippets]
            
        is_valid, reasons = validate_advisory(parsed, retrieved_snippets, payload)
        if not is_valid:
            print(f"Validation failed for Gemini output: {reasons}")
            parsed["advisory"]["warning"] = parsed["advisory"].get("warning", "") + f"\nSystem Note: {reasons[0]}"
            if "drug" in reasons[0].lower():
                parsed["advisory"]["actions"] = ["Please consult a local expert for safe treatment guidelines."]
                
        return parsed
    except Exception as e:
        print(f"Error calling Gemini: {e}")
        # Safe fallback in case of malformed JSON or API failure
        return {
            "diagnosis": {"condition": "unknown", "certainty": "insufficient_evidence"},
            "advisory": {
                "summary": "Error generating advisory.", 
                "actions": ["Consult an expert locally."], 
                "warning": "Cloud service unavailable or malformed response."
            },
            "expert_consultation_recommended": True,
            "cited_knowledge": []
        }


if __name__ == "__main__":
    demo_payload = {
        "domain": "crop", "image_prediction": "tomato_early_blight",
        "visual_confidence": 0.67, "farmer_text": "पत्तियों पर भूरे धब्बे हैं",
        "text_evidence": ["brown_spots"], "sensor_data": None,
        "farm_history": "No prior visits recorded.",
        "retrieved_knowledge": "Tomato early blight: fungal, concentric brown spots...",
    }
    
    # Test Mock Client
    os.environ["GEMINI_ENABLED"] = "false"
    res = call_gemini(demo_payload)
    print("Mock Output:", json.dumps(res, indent=2))
