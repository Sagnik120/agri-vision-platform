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
| Farm memory functions | `zone3_memory/db/farm_memory.py` | **Done** — implemented SQLite CRUD and tested |
| Streamlit UI | `app/streamlit_app.py` | Crop tab wired to Person A; Livestock/Voice tabs + cloud branch + TTS playback + farm-memory writes still TODO |
| Zone 2 tests (real) | `tests/zone2/test_zone2_stubs.py` | Add real functional tests AFTER each stub is implemented (currently validates scaffold shape) |
| Zone 3 tests (real) | `tests/zone3/test_zone3_stubs.py` | **Done** — real functional tests added and passing |

---

## Not started at all
- Recording actual demo audio (3-4 fixed Hindi sentences) into `demo_data/audio/`
- Sourcing actual demo crop/livestock images into `demo_data/crop|livestock/`
- Live testing of `download_crop_model.py` / `download_livestock_model.py`
  against real Hugging Face (build sandbox has no internet access to
  huggingface.co — must be run and verified on your Mac)
- End-to-end test with real (non-mock) models

---

## How to resume work (Person B)
1. Read `src/zone2_cloud/PERSON_B_README.md` — it has the exact build order
   matching the original plan's hour-by-hour schedule.
2. Each stub file's docstring has a ready-to-paste prompt for an AI coding
   agent (Claude Code / Cursor).
3. After implementing each Zone 2/3 module, update the real logic in
   `tests/zone2/test_zone2_stubs.py` or `tests/zone3/test_zone3_stubs.py`
   — replace `pytest.raises(NotImplementedError)` assertions with real functional tests.
4. Re-run `python setup/diagnose_pipeline.py --mode auto` periodically to
   confirm Zone 1 still isn't broken by any integration changes.
5. Run `pytest tests/ -v` to see the full picture — currently **78/78 passing**.
