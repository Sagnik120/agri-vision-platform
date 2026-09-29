"""
advisory_format.py — Fixed input/output format shared by every advisory backend
(Gemini, LocalLLMClient, mock) AND by the LLM fine-tuning scripts, so a
fine-tuned model sees at inference exactly what it saw in training.

Citation IDs:
  * Knowledge docs are rendered as `[KB-<condition>]` blocks by the retriever.
  * Farm history lines are rendered as `[H<observation_id>] ...` by Zone 3.
The model must return the IDs it used in `cited_doc_ids` / `farm_history_refs`;
the validator checks they exist in what was actually sent (hallucination check).
"""

from __future__ import annotations

import json
import re

KB_ID_RE = re.compile(r"\[(KB-[A-Za-z0-9_\-]+)\]")
HISTORY_REF_RE = re.compile(r"\[(H\d+)\]")

# Keys forwarded to the model (PII such as farmer_name/phone/image_path excluded).
MODEL_INPUT_KEYS = (
    "domain", "image_prediction", "visual_confidence", "farmer_text", "text_evidence",
    "sensor_data", "farm_history", "retrieved_knowledge", "region", "season", "weather",
)

OUTPUT_SCHEMA = """{
  "diagnosis": {"condition": "...", "certainty": "possible|confirmed|insufficient_evidence"},
  "advisory": {"summary": "...", "actions": ["..."], "warning": "..."},
  "expert_consultation_recommended": true|false,
  "cited_knowledge": ["..."],
  "farm_history_acknowledged": true|false,
  "cited_doc_ids": ["KB-..."],
  "farm_history_refs": ["H..."]
}"""

SYSTEM_INSTRUCTIONS = """You are an agricultural and veterinary advisory assistant for smallholder farmers in India.
Use ONLY the provided context. Never invent diagnoses, drug names, dosages or quantities.
Distinguish "possible" from "confirmed"; say so when evidence is insufficient or contradictory.
Recommend a local agriculture/veterinary expert for severe, ambiguous or reportable diseases.
Knowledge snippets are tagged [KB-...]; list every one you used in "cited_doc_ids".
Farm history lines are tagged [H...]; list every one you used in "farm_history_refs" and set
"farm_history_acknowledged" true when history is provided. Use region/season/weather only to
adapt timing and preventive advice, never to change the diagnosis.
Return ONLY valid JSON with this exact shape:
""" + OUTPUT_SCHEMA


def model_input(payload: dict) -> dict:
    return {k: payload.get(k) for k in MODEL_INPUT_KEYS if k in payload}


def user_message(payload: dict) -> str:
    return "Context:\n" + json.dumps(model_input(payload), ensure_ascii=False, indent=2)


def chat_messages(payload: dict) -> list[dict]:
    """Role-based messages; the model's OWN chat template is applied by the server/tokenizer."""
    return [
        {"role": "system", "content": SYSTEM_INSTRUCTIONS},
        {"role": "user", "content": user_message(payload)},
    ]


def retrieved_doc_ids(payload: dict) -> list[str]:
    ids = list(payload.get("retrieved_doc_ids") or [])
    rk = payload.get("retrieved_knowledge") or ""
    rk = " ".join(rk) if isinstance(rk, list) else str(rk)
    return list(dict.fromkeys(ids + KB_ID_RE.findall(rk)))


def history_refs(payload: dict) -> list[str]:
    return list(dict.fromkeys(HISTORY_REF_RE.findall(str(payload.get("farm_history") or ""))))


def parse_json_output(text: str) -> dict:
    """Parse model output, tolerating markdown fences / leading prose."""
    text = (text or "").strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
    try:
        return json.loads(text)
    except ValueError:
        start, end = text.find("{"), text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start:end + 1])
        raise
