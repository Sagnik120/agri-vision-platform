# Zone 2 Cloud Details

## 1. Purpose
Provides expert-level agronomic escalation using Gemini and local RAG.

## 2. Responsibilities
- Retrieves context from a FAISS vector index.
- Packages images, text, sensors, and history into a prompt.
- Validates the JSON schema returned by Gemini, enforcing cited knowledge grounding and farm history acknowledgement.

## 3. Architecture Role
The escalation layer (triggered when Zone 1 lacks confidence).

## 4. Inputs
Contract 6 (Cloud Request Payload).

## 5. Outputs
Valid JSON schema dict containing diagnosis and advisory.

## 6. Important files
- `gemini_client.py`: API integration and fallback mock.
- `retriever.py`: RAG logic.

## 7. Dependencies
`google-genai`, `faiss-cpu`, `sentence-transformers`.

## 8. Runtime flow
Called by `streamlit_app.py` when `route == 'cloud'`.

## 9. Contracts/interfaces
Consumes Contract 6.

## 10. Current implementation status
IMPLEMENTED.

## 11. Important assumptions
Assumes `results/zone2/rag_index` exists. Assumes valid Gemini API key if `GEMINI_ENABLED=true`.

## 12. Known limitations
RAG is currently restricted to small local Markdown files.

## 13. AI upgrade (Phases 2–4)
**Weather (`context/weather_client.py`)** — Open-Meteo (free, no API key, India coverage). `WEATHER_ENABLED=false` by default; any failure → `None`, advisory still generated. 30-min in-memory cache; coarse state centroids (no geocoding API).

**RAG (`rag/`)**
- KB docs carry frontmatter metadata (`kb_metadata.py`): `doc_id` (= `KB-<file stem>`, stable even if regenerated), condition, domain, source, region, last_updated, review_status. 22 gap-fill docs are `draft_needs_expert_review`.
- Chunking unchanged (1 short doc = 1 chunk) and embeddings unchanged (MiniLM): the draft eval showed no deficiency.
- `retriever.retrieve_docs(query, k, domain=None, rerank=False)` returns tagged docs; `retrieve()` still returns a string (now each block prefixed `[KB-...]`). `RAG_BACKEND=auto|faiss|lexical`; lexical = pure-Python BM25, torch-free, used automatically when sentence-transformers/faiss/index metadata are absent (serverless deploys). Heavy imports are lazy.
- Rerank: optional `RAG_RERANK_MODEL`, off by default (bge-reranker-v2-m3 needs >1GB RAM; draft-set gain was MRR only).
- **Vector DB decision: keep local FAISS.** 49 docs, flat index is instant; RAG is Zone-2-only so there is no offline-first conflict; a cloud vector DB adds cost, latency and another key to manage with no measured benefit. Revisit only if the KB grows to tens of thousands of chunks.

**Citations** — Retrieved docs are tagged `[KB-...]`, farm history lines `[H<observation_id>]` (Zone 3 `format_farm_history`). Response schema adds `cited_doc_ids` and `farm_history_refs`. `validator.verify_citations()` flags any ID not present in what was sent (hallucinated citation); `validate_advisory` fails on them when those fields are present.

**Backends (`advisory_service.generate_advisory`)** — `ADVISORY_BACKEND=gemini` (default) | `local_llm` | `mock`. `llm/local_llm_client.py::LocalLLMClient` calls an OpenAI-compatible server (vLLM / llama.cpp / Ollama) over HTTP; the model is served out-of-process (does not fit a 512MB function). On any local-LLM error → Gemini/mock fallback. `llm/advisory_format.py` is the single input/output format shared by runtime and fine-tuning.
