# Progress — Agri-Vision Platform

Last updated: audit session on 2026-08-15 (by Antigravity AI agent).

---

## ✅ COMPLETED — Person A (Zone 1: Edge / Vision / Fusion)

| Component | File | Status |
|---|---|---|
| Data contract | `contract.md` | Frozen, all 6 shapes defined |
| Config | `src/zone1_edge/config.py` | Done |
| Crop expert | `experts/crop_expert.py` | Done — HF model + offline mock fallback |
| Livestock expert | `experts/livestock_expert.py` | Done — HF model + offline mock fallback |
| Text evidence | `multimodal/text_evidence.py` | Done — Hindi+English keyword dict |
| Sensor expert | `multimodal/sensor_expert.py` | Done — threshold rules |
| Task router | `task_router/task_router.py` | Done — explicit UI-driven dispatch (see note below) |
| Fusion | `multimodal/fusion.py` | Done — rule-based scoring, bug found+fixed |
| Confidence gate | `multimodal/confidence_gate.py` | Done |
| Local advisory | `knowledge/local_advisory.py` + `local_advisories.json` | Done — 13 entries |
| Full pipeline | `pipeline.py` | Done — `run_zone1_pipeline()` |
| Zone 1 tests | `tests/zone1/*.py` | **38/38 passing** |
| Diagnostics | `setup/diagnose_pipeline.py` | **10/10 checks passing** |
| Model download scripts | `setup/download_crop_model.py`, `download_livestock_model.py` | Done, untested against live HF (sandbox has no HF network access — test on your Mac) |

**Bug found and fixed during testing:** `fusion.py`'s `_text_agreement()` had
an unreachable healthy-label check (it looked up `CONDITION_SYMPTOM_MAP`
before checking `HEALTHY_LABELS`, and healthy labels are never in that map,
so the branch never ran). Reordered — confirmed by the
previously-failing `test_text_conflict_decreases_confidence` now passing.

**Task Router Design Question — RESOLVED:** The `task_router.py` IS implemented
as intended per the plan. The architecture diagram shows a "Task Router" box, and
the implementation honours it via explicit UI-driven domain selection (Crop/Livestock
buttons). The plan (Implementation Details Section 13) explicitly says:
> "For your prototype, the easiest reliable mechanism is Explicit UI selection [Crop] [Livestock]."
The router prints "Detected task → Expert selected" exactly as required by the demo script.
This is BY DESIGN, not an error. ✅

---

## ✅ COMPLETED — Audit & Test Infrastructure (2026-08-15)

| Component | File | Status |
|---|---|---|
| Full codebase audit | `docs/AUDIT_REPORT.md` | Done — no implementation errors found |
| Zone 2 diagnostic tests | `tests/zone2/test_zone2_stubs.py` | **19 tests, all passing** |
| Zone 3 diagnostic tests | `tests/zone3/test_zone3_stubs.py` | **20 tests, all passing** |
| results/zone2/ sub-folders | `results/zone2/{asr_runs,tts_runs,gemini_runs}/` | Created |
| results/zone3/ sub-folders | `results/zone3/db_snapshots/` | Created |

**Total test count across all zones: 78/78 passing.**

---

## ✅ COMPLETED — Person B (Zone 2 + Zone 3 + UI)

All files below are fully implemented, wired together, and integrated into the Streamlit app. Mock fallbacks are provided for cloud/models to ensure offline capabilities.

| Component | File | Status |
|---|---|---|
| Confidence Gate | `zone1_edge/confidence_gate.py` | **Done** — Returns a route (`local` or `cloud`) based on evidence agreement. |
| Farm Memory (Zone 3) | `zone3_memory/db/farm_memory.py` | **Done** — SQLite logic for CRUD. |
| Hindi ASR | `zone1_edge/speech/hindi_asr.py` | **Done** — Uses Hugging Face IndicConformer locally. |
| Hindi TTS | `zone1_edge/speech/hindi_tts.py` | **Done** — Uses FastPitch+HiFi-GAN or HF TTS (e.g., vits_rasa_13) or safe mock. |
| Gemini client | `zone2_cloud/gemini/gemini_client.py` | **Done** — Uses google-genai SDK with secure `.env` mock mode. |
| RAG knowledge base | `zone2_cloud/rag/knowledge_base/*.md` | **Done** — 8 entries written |
| RAG builder | `zone2_cloud/rag/build_knowledge_base.py` | **Done** — FAISS + sentence-transformers implemented |
| RAG retriever | `zone2_cloud/rag/retriever.py` | **Done** — FAISS retrieval implemented |
| Farm memory schema | `zone3_memory/schema/schema.sql` | **Done** — tables defined |
| Streamlit UI | `app/streamlit_app.py` | **Done** — All tabs, cloud branch, TTS playback, and memory integrated. |
| Zone 2 tests (real) | `tests/zone2/test_zone2_stubs.py` | **Done** — Real tests added for mocks and logic flow. |
| Zone 3 tests (real) | `tests/zone3/test_zone3_stubs.py` | **Done** — real functional tests added and passing |
| UI/App Integration tests | `tests/app/test_app_integration.py` | **Done** — Mock tests for UI logic passing |
| Overall Diagnostic | `setup/diagnose_overall_pipeline.py` | **Done** — End-to-end multi-zone offline test passing |

## ✅ COMPLETED — Recent Iterative Improvements (2026-08-15)

- **Local Advisory Normalization:** Fixed issue where edge vision models output raw dataset class names (e.g. `Potato___Early_Blight`) which did not map to `local_advisories.json`. Added programmatic string normalization.
- **Farm History UI:** Implemented SQLite query function to fetch the complete ledger of inferences and added a new "📖 Farm History" tab to the Streamlit UI to display it dynamically.
- **TTS Backend Fix:** Programmatically patched the missing `pad_token_id` in AI4Bharat's `IndicVitsConfig` and injected `trust_remote_code=True` to allow seamless local Hugging Face `vits_rasa_13` model loading.
- **Streamlit State Loss Fix:** Removed nested TTS buttons that caused script reruns and text disappearance. Automated TTS playback during analysis instead.

---

## Not started at all
- Recording actual demo audio (3-4 fixed Hindi sentences) into `demo_data/audio/`
- Sourcing actual demo crop/livestock images into `demo_data/crop|livestock/`
- Live testing of `download_crop_model.py` / `download_livestock_model.py`
  against real Hugging Face (build sandbox has no internet access to
  huggingface.co — must be run and verified on your Mac)
- Hindi to English Translation Pipeline for RAG retrieval

---

## How to resume work (Person B)
1. Proceed with implementing the Hindi-to-English translation component so the RAG English vector DB can properly consume Hindi Voice queries.
2. Record real audio/image demo data for final prototype showcasing.
