"""Citation IDs, hallucination checks, lexical RAG, weather degradation, LocalLLMClient. No network."""

import json

import pytest

from src.zone2_cloud import advisory_service
from src.zone2_cloud.context import weather_client
from src.zone2_cloud.gemini.validator import validate_advisory, verify_citations
from src.zone2_cloud.llm.advisory_format import chat_messages, parse_json_output
from src.zone2_cloud.llm.local_llm_client import LocalLLMClient
from src.zone2_cloud.rag.kb_metadata import parse_frontmatter
from src.zone2_cloud.rag.retriever import format_docs, retrieve_docs

PAYLOAD = {
    "domain": "crop", "image_prediction": "tomato_late_blight", "visual_confidence": 0.6,
    "farmer_text": "", "text_evidence": [], "sensor_data": None,
    "farm_history": "[H7] 2026-09-01: tomato_late_blight (possible)",
    "retrieved_knowledge": "[KB-tomato_late_blight]\nTomato Late Blight ...",
    "region": "Punjab", "season": "kharif", "weather": None,
}


def _resp(**kw):
    r = {"diagnosis": {"condition": "tomato_late_blight", "certainty": "possible"},
         "advisory": {"summary": "s", "actions": ["a"], "warning": "w"},
         "expert_consultation_recommended": True, "cited_knowledge": [],
         "farm_history_acknowledged": True, "cited_doc_ids": ["KB-tomato_late_blight"], "farm_history_refs": ["H7"]}
    r.update(kw)
    return r


def test_citations_valid():
    chk = verify_citations(_resp(), PAYLOAD)
    assert chk["citations_valid"] and chk["has_citation"]


def test_hallucinated_doc_and_history_detected():
    resp = _resp(cited_doc_ids=["KB-made_up"], farm_history_refs=["H99"])
    chk = verify_citations(resp, PAYLOAD)
    assert chk["hallucinated_doc_ids"] == ["KB-made_up"] and chk["hallucinated_history_refs"] == ["H99"]
    ok, reasons = validate_advisory(resp, [PAYLOAD["retrieved_knowledge"]], PAYLOAD)
    assert not ok and any("KB-made_up" in r for r in reasons)


def test_frontmatter_parse():
    meta, body = parse_frontmatter("---\ndoc_id: KB-x\ndomain: crop\n---\n\n# X\nbody")
    assert meta == {"doc_id": "KB-x", "domain": "crop"} and body.startswith("# X")


def test_lexical_retrieval_returns_tagged_docs():
    docs = retrieve_docs("cow with lumps on skin nodules fever", k=3, backend="lexical")
    assert docs and docs[0]["doc_id"] == "KB-lumpy_skin_disease"
    assert format_docs(docs).startswith("[KB-")
    assert all(d["domain"] == "crop" for d in retrieve_docs("brown spots", k=3, domain="crop", backend="lexical"))


def test_weather_disabled_returns_none(monkeypatch):
    monkeypatch.setenv("WEATHER_ENABLED", "false")
    assert weather_client.get_weather("Punjab") is None


def test_weather_failure_degrades(monkeypatch):
    monkeypatch.setenv("WEATHER_ENABLED", "true")
    weather_client._cache.clear()

    def boom(url):
        raise TimeoutError()
    assert weather_client.get_weather("Punjab", fetch=boom) is None
    assert weather_client.get_weather("Atlantis", fetch=boom) is None


def test_weather_summary(monkeypatch):
    monkeypatch.setenv("WEATHER_ENABLED", "true")
    weather_client._cache.clear()
    fake = {"current": {"temperature_2m": 30.1, "relative_humidity_2m": 85},
            "daily": {"precipitation_sum": [10.0, 5.5, None]}}
    w = weather_client.get_weather("Kerala", fetch=lambda url: fake)
    assert w == {"temperature_c": 30.1, "relative_humidity_pct": 85, "precipitation_last_7d_mm": 15.5, "source": "open-meteo"}


def test_local_llm_client_parses_openai_response(monkeypatch):
    captured = {}

    def fake_post(body):
        captured.update(body)
        return {"choices": [{"message": {"content": "```json\n" + json.dumps(_resp()) + "\n```"}}]}
    out = LocalLLMClient(base_url="http://x/v1", model="m").generate(PAYLOAD, post=fake_post)
    assert out["cited_doc_ids"] == ["KB-tomato_late_blight"]
    assert [m["role"] for m in captured["messages"]] == ["system", "user"]


def test_chat_messages_exclude_pii():
    msgs = chat_messages({**PAYLOAD, "phone": "999", "farmer_name": "X", "image_path": "/tmp/a"})
    assert "999" not in msgs[1]["content"] and "image_path" not in msgs[1]["content"]


def test_parse_json_output_with_prose():
    assert parse_json_output('Sure: {"a": 1} done')["a"] == 1


def test_advisory_service_local_llm_falls_back_to_mock(monkeypatch):
    monkeypatch.setenv("ADVISORY_BACKEND", "local_llm")
    monkeypatch.delenv("LOCAL_LLM_URL", raising=False)
    monkeypatch.setenv("GEMINI_ENABLED", "false")
    monkeypatch.setenv("WEATHER_ENABLED", "false")
    out = advisory_service.generate_advisory(PAYLOAD)
    assert out["_backend"] == "gemini_fallback(MOCK-client)"
    assert out["_citation_check"]["citations_valid"]
    assert out["cited_doc_ids"] == ["KB-tomato_late_blight"] and out["farm_history_refs"] == ["H7"]
