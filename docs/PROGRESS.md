# Progress — Agri-Vision Platform

Last updated: build session on 2026-08-15.

## ✅ COMPLETED — Person A (Zone 1: Edge / Vision / Fusion)

| Component | File | Status |
|---|---|---|
| Data contract | `contract.md` | Frozen, all 6 shapes defined |
| Config | `src/zone1_edge/config.py` | Done |
| Crop expert | `experts/crop_expert.py` | Done — HF model + offline mock fallback |
| Livestock expert | `experts/livestock_expert.py` | Done — HF model + offline mock fallback |
| Text evidence | `multimodal/text_evidence.py` | Done — Hindi+English keyword dict |
| Sensor expert | `multimodal/sensor_expert.py` | Done — threshold rules |
| Task router | `task_router/task_router.py` | Done |
| Fusion | `multimodal/fusion.py` | Done — rule-based scoring, bug found+fixed |
| Confidence gate | `multimodal/confidence_gate.py` | Done |
| Local advisory | `knowledge/local_advisory.py` + `local_advisories.json` | Done — 13 entries |
| Full pipeline | `pipeline.py` | Done — `run_zone1_pipeline()` |
| Tests | `tests/zone1/*.py` | **38/38 passing** |
| Diagnostics | `setup/diagnose_pipeline.py` | **10/10 checks passing** |
| Model download scripts | `setup/download_crop_model.py`, `download_livestock_model.py` | Done, untested against live HF (sandbox has no HF network access — test on your Mac) |

**Bug found and fixed during testing:** `fusion.py`'s `_text_agreement()` had
an unreachable healthy-label check (it looked up `CONDITION_SYMPTOM_MAP`
before checking `HEALTHY_LABELS`, and healthy labels are never in that map,
so the branch never ran). Reordered — checked and confirmed by the
previously-failing `test_text_conflict_decreases_confidence` now passing.

## 🚧 SCAFFOLDED, NOT YET IMPLEMENTED — Person B (Zone 2 + Zone 3 + UI)

All files below exist as STUBS with full docstrings, exact expected function
signatures, and agent-ready prompts. None have real logic yet.

| Component | File | What's needed |
|---|---|---|
| Hindi ASR | `zone2_cloud/asr/hindi_asr.py` | Load AI4Bharat IndicConformer, implement `transcribe()` |
| Hindi TTS | `zone2_cloud/tts/hindi_tts.py` | FastPitch+HiFi-GAN primary, IndicF5 fallback, implement `synthesize()` |
| Gemini client | `zone2_cloud/gemini/gemini_client.py` | Prompt template written; implement actual API call in `call_gemini()` |
| RAG knowledge base | `zone2_cloud/rag/knowledge_base/*.md` | Write 8-10 entries (template provided in folder README) |
| RAG builder | `zone2_cloud/rag/build_knowledge_base.py` | Implement embedding + FAISS/Chroma indexing |
| RAG retriever | `zone2_cloud/rag/retriever.py` | Implement `retrieve()` |
| Farm memory schema | `zone3_memory/schema/schema.sql` | **Done** — tables defined |
| Farm memory functions | `zone3_memory/db/farm_memory.py` | Implement `init_db`, `save_observation`, `save_diagnosis`, `save_advisory`, `get_farm_history` |
| Streamlit UI | `app/streamlit_app.py` | Crop tab wired to Person A; Livestock/Voice tabs + cloud branch + TTS playback + farm-memory writes still TODO |
| Zone 2 tests | `tests/zone2/*` | Placeholder only |
| Zone 3 tests | `tests/zone3/*` | Placeholder only |

## Not started at all
- Recording actual demo audio (3-4 fixed Hindi sentences) into `demo_data/audio/`
- Sourcing actual demo crop/livestock images into `demo_data/crop|livestock/`
- Live testing of `download_crop_model.py` / `download_livestock_model.py`
  against real Hugging Face (build sandbox has no internet access to
  huggingface.co — must be run and verified on your Mac)
- End-to-end test with real (non-mock) models

## How to resume work
1. Read `src/zone2_cloud/PERSON_B_README.md` — it has the exact build order
   matching the original plan's hour-by-hour schedule.
2. Each stub file's docstring has a ready-to-paste prompt for an AI coding
   agent (Claude Code / Cursor).
3. After implementing each Zone 2/3 module, add real tests to
   `tests/zone2/` or `tests/zone3/` following the pattern in `tests/zone1/`.
4. Re-run `python setup/diagnose_pipeline.py --mode auto` periodically to
   confirm Zone 1 still isn't broken by any integration changes.
