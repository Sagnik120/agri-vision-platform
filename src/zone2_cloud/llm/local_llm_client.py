"""
local_llm_client.py — Fine-tuned open LLM backend (Zone 2), sibling of Gemini.

Talks to any OpenAI-compatible chat endpoint over HTTP (vLLM, llama.cpp
server, Ollama `/v1`, HF TGI/Inference Endpoints). The model itself is NOT
loaded in this process: a 1.5B model needs >1GB RAM, far above a ~512MB
serverless function, so it is served separately (GPU box, Colab tunnel, or a
quantized GGUF on a small VM) and this client stays stdlib-only.

The server applies the model's OWN chat template to the role-based messages
(same messages used in training via tokenizer.apply_chat_template).

Env:
  LOCAL_LLM_URL      base URL, e.g. http://localhost:8000/v1   (required)
  LOCAL_LLM_MODEL    served model/adapter name                  (default: agrivision-advisor)
  LOCAL_LLM_API_KEY  optional bearer token (read from env only, never logged)
  LOCAL_LLM_TIMEOUT_S request timeout                           (default: 60)
"""

from __future__ import annotations

import json
import os
import urllib.request

from src.zone2_cloud.llm.advisory_format import chat_messages, parse_json_output


class LocalLLMClient:
    def __init__(self, base_url: str | None = None, model: str | None = None, timeout_s: float | None = None):
        self.base_url = (base_url or os.environ.get("LOCAL_LLM_URL", "")).rstrip("/")
        self.model = model or os.environ.get("LOCAL_LLM_MODEL", "agrivision-advisor")
        self.timeout_s = timeout_s or float(os.environ.get("LOCAL_LLM_TIMEOUT_S", "60"))
        if not self.base_url:
            raise ValueError("LOCAL_LLM_URL must be set to use the local_llm advisory backend")

    def _post(self, body: dict) -> dict:
        headers = {"Content-Type": "application/json"}
        key = os.environ.get("LOCAL_LLM_API_KEY")
        if key:
            headers["Authorization"] = f"Bearer {key}"
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions", data=json.dumps(body).encode("utf-8"),
            headers=headers, method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:  # noqa: S310 - configured endpoint
            return json.loads(resp.read().decode("utf-8"))

    def generate(self, payload: dict, post=None) -> dict:
        body = {
            "model": self.model,
            "messages": chat_messages(payload),
            "temperature": 0.2,
            "max_tokens": 700,
        }
        raw = (post or self._post)(body)
        return parse_json_output(raw["choices"][0]["message"]["content"])
