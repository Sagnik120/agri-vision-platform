# Project Memory & State

This file serves as a living memory for the project's current state.

**Current Phase:** Hackathon Prototype (Complete)
**Last Major Update:** Repository Restructuring (Consolidated structure, docs added, tests centralized).

**Key State Data:**
- Edge models are implemented via HuggingFace with efficient fallbacks.
- RAG relies on a generated FAISS index in `results/zone2/rag_index/`.
- Streamlit serves as the master UI wiring.

*(Update this file as new milestones are reached).*

## 2026-09-29 — AI upgrade (task_agrivision_improvements.md), code + tooling delivered
Plan/checklist: `docs/system/ai_upgrade_plan.md`. Training/eval runs are pending (user-run); no metrics claimed.

**Contract log (instructions/contract.md NOT edited).** All changes are additive keys appended at the END, which contract.md explicitly permits; no key removed/renamed/re-typed:
- #1 image expert output: optional trailing `_moe` debug dict (only when MoE is active).
- #6 cloud payload: trailing `region` (str|null), `season` ("kharif"|"rabi"|"zaid"), `weather` (dict|null, filled cloud-side). `farm_history` stays a string, now with `[H<id>]` line tags; `retrieved_knowledge` stays a string, now with `[KB-<id>]` block tags.
- Advisory response (Zone 2 internal schema, not in contract.md): adds `cited_doc_ids`, `farm_history_refs`; `advisory_service` appends `_citation_check`, `_backend`, `_weather_used`.
If the team wants these formalised in contract.md, that requires explicit approval (Rule 3).

**Deployment note:** runtime additions are numpy/stdlib/optional onnxruntime only; torch/transformers/peft live in `training/requirements-train.txt`.
