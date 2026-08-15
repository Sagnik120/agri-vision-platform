# Unified AI Agri-Vision Platform — Prototype

Crop Disease ID + Livestock Monitoring + Historical Records, built for an
8-hour 2-person hackathon sprint. See `Agri_Vision_2Person_8Hour_Plan.docx`
for the original plan and `contract.md` for the frozen data contract.

- **Person A (Zone 1 — Edge/Vision/Fusion): COMPLETE.** Fully implemented,
  38 passing tests, 10/10 diagnostic checks. Runs fully offline.
- **Person B (Zone 2 — Cloud/RAG/Voice, Zone 3 — Farm Memory): SCAFFOLDED.**
  Clear stubs + build guide, not yet implemented (needs API keys, HF speech
  models, and your judgment calls).

See `docs/PROGRESS.md` for the detailed completion status and remaining work.

## Quick start (Mac, Apple Silicon)

```bash
bash setup/setup_venv.sh
source .venv/bin/activate

# Prove Person A's pipeline works right now, offline, no models needed:
AGRIVISION_EXPERT_MODE=mock python setup/diagnose_pipeline.py --mode mock
AGRIVISION_EXPERT_MODE=mock pytest tests/zone1 -v

# When ready to use real pretrained models:
huggingface-cli login                      # account: Sagnik120
python setup/download_crop_model.py
python setup/download_livestock_model.py
python setup/diagnose_pipeline.py --mode auto

# Run the UI:
streamlit run src/app/streamlit_app.py
```

## Repository structure

```
agri-vision-platform/
├── contract.md                  Frozen JSON data contract (read first)
├── requirements.txt
├── setup/
│   ├── setup_venv.sh             venv bootstrap for Mac
│   ├── download_crop_model.py    HF download (Sagnik120), crop model
│   ├── download_livestock_model.py
│   └── diagnose_pipeline.py      10-point pipeline health check
├── src/
│   ├── zone1_edge/                PERSON A — complete
│   │   ├── config.py
│   │   ├── experts/                crop_expert.py, livestock_expert.py
│   │   ├── multimodal/             text_evidence.py, sensor_expert.py, fusion.py, confidence_gate.py
│   │   ├── task_router/            task_router.py
│   │   ├── knowledge/              local_advisories.json, local_advisory.py
│   │   ├── demo_data/               sample images/audio go here
│   │   └── pipeline.py             end-to-end orchestrator
│   ├── zone2_cloud/                PERSON B — scaffolded (see PERSON_B_README.md)
│   │   ├── asr/hindi_asr.py
│   │   ├── tts/hindi_tts.py
│   │   ├── gemini/gemini_client.py
│   │   └── rag/{build_knowledge_base.py, retriever.py, knowledge_base/}
│   ├── zone3_memory/                PERSON B — scaffolded
│   │   ├── db/farm_memory.py
│   │   └── schema/schema.sql
│   └── app/streamlit_app.py         UI shell (Zone 1 wired, Zone 2/3 TODOs marked)
├── tests/
│   ├── zone1/                       38 passing tests + e2e diagnostic test
│   ├── zone2/                       placeholder, fill in as you build
│   └── zone3/                       placeholder, fill in as you build
├── results/
│   ├── zone1/{crop_model,livestock_model,fusion_runs}/   run logs + outputs
│   ├── zone2/{asr_runs,tts_runs,gemini_runs}/
│   └── zone3/db_snapshots/
└── docs/PROGRESS.md
```

## HF / Kaggle / GitHub accounts referenced in this repo
- Hugging Face: `Sagnik120`
- Kaggle: `chandrasagnik027`
- GitHub: `Sagnik120`
