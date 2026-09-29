# AI Upgrade Plan & Checklist (task_agrivision_improvements.md)

Status legend: `[x]` implemented in repo (code/scripts), `[ ]` requires a user-executed run
(training / evaluation / API calls) — no metric in this repo is claimed until the user runs it.

## Cross-cutting constraints
- **Vercel (~512MB RAM, ~250MB bundle):** every new *runtime* path is numpy / stdlib / optional
  `onnxruntime` only. torch, timm, transformers, peft, bitsandbytes live only in
  `training/requirements-train.txt` and offline scripts. The MoE gate is a numpy softmax
  regression (<10KB JSON); sub-experts run as ONNX; the LLM backend is reached over HTTP.
- **No external calls by the agent:** weather (Open-Meteo) is `WEATHER_ENABLED=false` by default;
  Gemini / synthetic-data scripts are user-run only.
- **Contracts:** `instructions/contract.md` untouched. All new fields are *additive keys appended
  at the end* (explicitly permitted by contract.md header). Logged in `docs/spec/06_Memory.md`.

## Phase 0 — MoE design (audit findings)
- Current crop checkpoint (`models_cache/crop_model`) is a 13-class Corn/Wheat/Potato/Rice model,
  NOT PlantVillage-38 → it cannot be forked into row/tree heads; **two separate fine-tuning runs**
  from a shared ImageNet backbone are required (one per group).
- Current livestock runtime is CLIP zero-shot (no trained head). An unused Keras EfficientNet-B3
  lumpy-skin model exists in the cache; it is not wired (TF dependency, not Vercel-feasible).
- PlantVillage groups (by growth pattern, `src/zone1_edge/moe/expert_groups.py`):
  - `crop_row` (annual row/vine crops, 21): Corn×4, Pepper×2, Potato×3, Soybean×1, Squash×1, Tomato×10
  - `crop_perennial` (tree/bush/perennial, 17): Apple×4, Blueberry×1, Cherry×2, Grape×4, Orange×1,
    Peach×2, Raspberry×1, Strawberry×2
  - Correction vs task.md's 20/18: Squash (annual cucurbit vine) belongs with row crops.
- Livestock groups: `livestock_lsd` (lumpy_skin_disease vs healthy), `livestock_fmd`
  (foot_and_mouth_disease vs healthy). **FMD support is unverified** — `training/dataset_audit.py`
  flags any class below `--min-per-class` (default 200) and the FMD expert must not ship if flagged
  (documented future-scope fallback: FMD stays on the existing CLIP zero-shot path + cloud escalation).
- `moe_gate`: learned multinomial logistic regression over a fixed 54-dim numpy image descriptor
  (HSV histograms + gradient stats), trained on the same group labels. Top-1 hard routing.
  Named `moe_gate` everywhere; never related to `confidence_gate` (local-vs-cloud).
- Per inference: domain router (unchanged) + moe_gate (µs, numpy) + 1 sub-expert.

## Checklist
### Phase 0/1 — MoE + fine-tuning
- [x] `src/zone1_edge/moe/` (expert_groups, image_features, moe_gate, moe_expert)
- [x] Integration in `task_router` behind `AGRIVISION_MOE_ENABLED` (auto = only if trained gate exists)
- [x] Label→KB normalization (`knowledge/label_aliases.py`) fixing corn/maize mismatch
- [x] `training/dataset_audit.py`, `training/finetune_expert.py` (3-stage gradual unfreezing +
      differential LR, class-weighted loss, macro-F1 checkpointing, ONNX export),
      `training/train_moe_gate.py`, `training/evaluate_expert.py`, `training/metrics.py`
- [ ] User: baseline eval of current experts, dataset audit, 4 fine-tuning runs, gate training, eval

### Phase 2 — Region / season / weather
- [x] `zone1_edge/context/` (Indian season inference, region normalization, seasonal guidance)
- [x] Local advisory `context_note`; pipeline `region`/`season` params; additive payload keys
- [x] `zone2_cloud/context/weather_client.py` (Open-Meteo, no key, off by default, graceful None)
- [x] UI region/season inputs, farm location persisted
- [ ] User: toggle `WEATHER_ENABLED=true` and verify degradation offline

### Phase 3 — RAG
- [x] KB frontmatter metadata (doc_id, condition, domain, source, region, last_updated, review_status)
- [x] Coverage gap audit + draft docs for gaps (flagged `draft_needs_expert_review`)
- [x] Index stores doc metadata; `retrieve_docs()` with doc_ids + filters; lexical BM25 fallback
      (Vercel-friendly, no torch); legacy `retrieve()` string API preserved
- [x] Citation IDs in prompt, `cited_doc_ids` / `farm_history_refs`, hallucinated-citation checks
- [x] `eval/rag_eval.py` + draft relevance set (user must review labels)
- [x] Decision: keep local FAISS (see zone2 details.md)
- [ ] User: rebuild index, review relevance labels, run eval with/without rerank

### Phase 4 — LLM fine-tuning
- [x] `zone2_cloud/llm/advisory_format.py` (shared input/output template)
- [x] `LocalLLMClient` (OpenAI-compatible HTTP) + `ADVISORY_BACKEND` selector with Gemini/mock fallback
- [x] `training/llm/` synthetic data gen (user-run), SFT prep with review gate, QLoRA script
      using the tokenizer's own chat template, backend comparison script
- [ ] User: generate + review data, QLoRA train on GPU, serve, run comparison
