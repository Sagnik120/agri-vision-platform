# Person B — Build Guide (Zone 2: Cloud/RAG/Voice + Zone 3: Farm Memory + UI Shell)

> **Read this whole file before writing code.** It is written so you can paste
> it directly into an AI coding agent (Claude Code / Cursor) as context. Every
> file below is currently a STUB with a docstring describing exactly what it
> must do, its exact function signature, and which contract shape
> (see `/contract.md` at repo root) it must produce/consume. Nothing here is
> wired together yet — that is your job, following the hour-by-hour plan in
> `Agri_Vision_2Person_8Hour_Plan.docx` Section 4.

## Why boilerplate, not full code
Person A's Zone 1 (edge/vision/fusion) is fully implemented, tested (38
passing pytest tests + a 10-point diagnostic script), and callable via a
single function: `src.zone1_edge.pipeline.run_zone1_pipeline(...)`. Zone 2/3
depends on external paid APIs (Gemini), large speech models (IndicConformer,
FastPitch/HiFi-GAN, IndicF5), and persistent state (SQLite) — these need your
own API keys, your own downloaded checkpoints, and real judgment about
trade-offs (e.g. TTS fallback timing), so they're intentionally left as
scaffolding for you (or your agent) to fill in per the plan's hour-by-hour
schedule.

## Folder map

```
src/zone2_cloud/
├── PERSON_B_README.md          <- this file
├── asr/
│   └── hindi_asr.py             STUB — AI4Bharat IndicConformer wrapper
├── tts/
│   └── hindi_tts.py             STUB — FastPitch+HiFi-GAN primary, IndicF5 fallback
├── gemini/
│   └── gemini_client.py         STUB — cloud escalation call + strict safety prompt
└── rag/
    ├── build_knowledge_base.py  STUB — embeds 8-10 knowledge entries
    ├── retriever.py              STUB — FAISS/Chroma similarity search
    └── knowledge_base/           empty — put your .md/.json knowledge entries here

src/zone3_memory/
├── db/
│   └── farm_memory.py           STUB — SQLite schema + save/get functions
└── schema/
    └── schema.sql                STUB — table definitions (farm, observations, diagnoses, advisories, livestock)

src/app/
└── streamlit_app.py             STUB — 3-tab UI shell (Crop / Livestock / Voice) wiring Zone 1 + Zone 2 + Zone 3

tests/zone2/                      empty test folder — write pytest tests here as you build each Zone 2 module
tests/zone3/                      empty test folder — same for Zone 3

results/zone2/
├── asr_runs/                     drop transcription outputs + timing here
├── tts_runs/                     drop synthesized audio + timing here
└── gemini_runs/                  drop raw Gemini responses (for debugging prompts) here

results/zone3/
└── db_snapshots/                 drop periodic .db file copies / query outputs here
```

## Build order (matches Section 4 of the plan — do in this sequence)

1. **0:15–1:30** `asr/hindi_asr.py` — load IndicConformer, transcribe a .wav,
   return contract #2 shape. Test standalone BEFORE wiring into anything.
2. **1:30–2:00** wrap it so its return value exactly matches
   `{"text": str, "language": "hi", "confidence": null}` — Person A's
   `text_evidence.py` consumes this directly.
3. **2:00–2:30** Checkpoint 1 — confirm your ASR JSON shape against
   `contract.md #2`. Run `python -m src.zone1_edge.multimodal.text_evidence "<your transcript>"` to prove Person A's side accepts it.
4. **2:30–3:30** `tts/hindi_tts.py` — try FastPitch+HiFi-GAN first, fall back
   to IndicF5 if setup stalls past ~45 min (see docstring for exact fallback logic).
5. **3:30–4:15** `zone3_memory/db/farm_memory.py` + `schema/schema.sql` —
   SQLite tables + `save_observation()` / `get_farm_history(farm_id)`.
6. **4:15–5:15** `rag/build_knowledge_base.py` + `rag/retriever.py` — embed
   8-10 knowledge entries (put them in `rag/knowledge_base/`) with
   `sentence-transformers/all-MiniLM-L6-v2`, index with FAISS or Chroma.
7. **5:15–6:15** `gemini/gemini_client.py` — build contract #6 payload,
   call Gemini with the strict safety system prompt (see docstring), parse
   structured JSON response.
8. **6:15–6:45** Checkpoint 2 — call `run_zone1_pipeline(...)` from Person A,
   branch on `result["gate"]["route"]`: if `"cloud"`, build the contract #6
   payload (there's a stub helper: `zone1_edge.pipeline.build_cloud_payload_stub`)
   and call your Gemini client.
9. **6:45–7:30** `app/streamlit_app.py` — wire it all together, 3 tabs +
   🟢/🟡 banner + "Why cloud?" panel.
10. **7:30–8:00** Final end-to-end test — 4 fixed Hindi sentences through the
    whole thing (Zone 1 + Zone 2 + Zone 3), confirm farm memory recall on
    second run of a similar case.

## Contract reminder (full detail in `/contract.md` at repo root)
- You **produce** contract #2 (ASR output) — Person A's `text_evidence.py` consumes it.
- You **consume** contract #5 (fusion+gate output) from Person A — that's what
  drives your local-vs-cloud branch.
- You **build** contract #6 (cloud request payload) FROM contract #5 plus your
  own RAG retrieval + farm history — then send it to Gemini.

## What NOT to build (per plan Section 7)
- No federated/privacy-preserving learning.
- No learned fusion or learned task router (Person A's side is rule-based only).
- No training any model — pretrained checkpoints / API calls only.
- No physical IoT hardware — Person A's sensor data is simulated.
- Do NOT use Indic Parler-TTS (3.75GB, gated) — FastPitch+HiFi-GAN → IndicF5 only.
