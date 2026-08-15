"""
gemini_client.py — STUB. Person B, Zone 2 (Hour 5:15-6:15 of the plan).

GOAL: Take contract.md #6 (cloud request payload) + RAG-retrieved snippets,
send to Gemini with a strict safety system prompt, get back a structured
advisory JSON.

Contract #6 input shape (built by YOU from Person A's fusion/gate output —
see src.zone1_edge.pipeline.build_cloud_payload_stub for a shape-matching
reference implementation):

    {"domain": str, "image_prediction": str, "visual_confidence": float,
     "farmer_text": str, "text_evidence": [str,...], "sensor_data": obj|null,
     "farm_history": str, "retrieved_knowledge": str}

TODO:
  1. `pip install google-generativeai`
  2. Get a Gemini API key, set it as env var GEMINI_API_KEY (never commit it —
     see .env.example at repo root and .gitignore).
  3. Implement `call_gemini(payload: dict) -> dict` below using the
     SYSTEM_PROMPT_TEMPLATE (tighten the safety rules as you see fit, but
     keep the core constraints — they came from the plan directly).
  4. Ask Gemini to return STRICT JSON (use response_mime_type="application/json"
     if using the google-generativeai SDK, or instruct it explicitly in the
     prompt and parse defensively with a try/except json.loads).
  5. Log every raw response to results/zone2/gemini_runs/ for prompt debugging.

Suggested advisory response shape (design this to be genuinely useful for
the UI — adjust freely, this is not part of the frozen contract.md):

    {
      "diagnosis": {"condition": str, "certainty": "possible"|"confirmed"|"insufficient_evidence"},
      "advisory": {"summary": str, "actions": [str,...], "warning": str},
      "expert_consultation_recommended": bool,
      "cited_knowledge": [str,...]
    }
"""

from __future__ import annotations

import json
import os

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


def build_prompt(payload: dict) -> str:
    return SYSTEM_PROMPT_TEMPLATE.format(context_json=json.dumps(payload, ensure_ascii=False, indent=2))


def call_gemini(payload: dict, model_name: str = "gemini-1.5-flash") -> dict:
    """
    TODO: implement the actual Gemini call.

    Reference sketch (fill in / adjust to the current google-generativeai SDK):

        import google.generativeai as genai
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        model = genai.GenerativeModel(model_name)
        prompt = build_prompt(payload)
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"},
        )
        return json.loads(response.text)
    """
    raise NotImplementedError(
        "TODO: wire up the real Gemini API call. See docstring for a reference sketch."
    )


if __name__ == "__main__":
    demo_payload = {
        "domain": "crop", "image_prediction": "tomato_early_blight",
        "visual_confidence": 0.67, "farmer_text": "पत्तियों पर भूरे धब्बे हैं",
        "text_evidence": ["brown_spots"], "sensor_data": None,
        "farm_history": "No prior visits recorded.",
        "retrieved_knowledge": "Tomato early blight: fungal, concentric brown spots...",
    }
    print(build_prompt(demo_payload))
