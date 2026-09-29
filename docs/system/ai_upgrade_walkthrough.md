# AI Upgrade Walkthrough (2026-09-29)

Scope: all 5 phases of `task_agrivision_improvements.md`, delivered as code + user-run tooling.
Checklist: `docs/system/ai_upgrade_plan.md`. No model accuracy is claimed anywhere: every
training and evaluation number must come from your own runs.

## 1. What was implemented
| Phase | Delivered |
|---|---|
| 0 MoE design | Audit findings and group definitions (`src/zone1_edge/moe/expert_groups.py`); `moe_gate` named and kept separate from `confidence_gate` |
| 1 Experts | `moe_gate` (learned softmax regression, numpy), ONNX sub-expert runtime, router integration with auto-fallback; `training/` audit, 3-stage fine-tune, gate trainer, evaluator, metrics |
| 2 Context | Region/season into the local advisory (`context_note`) and cloud payload; Open-Meteo weather (cloud-only, off by default); region selector in the UI, saved to `farm.location` |
| 3 RAG | KB metadata + stable doc IDs, 22 gap-fill docs (49 total), BM25 lexical fallback, `retrieve_docs()`, `[KB-..]` / `[H..]` citation tags, hallucinated-citation checks, retrieval + citation evaluation |
| 4 LLM | Shared advisory format, `LocalLLMClient` (OpenAI-compatible HTTP), `ADVISORY_BACKEND` selector with Gemini/mock fallback, synthetic-data / SFT-prep / QLoRA / comparison scripts |

Bug fixed along the way: labels such as `Corn___Common_Rust` never matched the KB key `maize_common_rust`, so every corn prediction escalated to cloud. They now go through `normalize_condition()`.

## 2. Key decisions
- **Crop groups:** `crop_row` has 21 classes and `crop_perennial` has 17. The task's 20/18 split moved Squash (an annual vine) into the perennial group, so it was corrected by growth pattern.
- **Current checkpoints:** the crop runtime model has 13 classes (Corn/Wheat/Potato/Rice) and cannot be forked into PlantVillage heads, so it needs 2 separate fine-tuning runs. Livestock currently uses CLIP zero-shot.
- **FMD:** it ships only if `dataset_audit` does not flag it (at least 200 images per class by default). If it is flagged, FMD stays on the existing zero-shot + cloud path as future scope.
- **Gate:** a learned logistic-regression gate with top-1 hard routing. It runs in microseconds with no torch, so it is edge- and serverless-friendly.
- **Backbone:** `mobilenetv3_large_100` by default (timm; `--backbone efficientnet_b0` is the alternative). Check the license and availability on the model card before training.
- **Weather:** Open-Meteo. It needs no API key, has a free tier and covers India.
- **Vector DB:** keep local FAISS (reasons in `src/zone2_cloud/docs/details.md` §13).
- **Rerank:** off by default. It needs more than 1GB of RAM.
- **LLM:** Qwen2.5-1.5B-Instruct (Apache-2.0) with QLoRA (4-bit NF4, r=16). Prompts use the tokenizer's own chat template. Re-confirm the license on the model card.

## 3. Verification run locally (CPU, offline, no API calls)
| Check | Result |
|---|---|
| `pytest tests` (mock mode, HF offline) | 119 passed, 13 skipped (baseline before changes: 96 passed, 13 skipped) |
| `python -m compileall src training eval tests` | OK |
| `python -m src.zone1_edge.pipeline --selftest` | passed |
| `eval/kb_coverage_audit.py` | 0 RAG KB gaps. 21 conditions have no offline advisory and escalate to cloud, on purpose |
| `eval/rag_eval.py` on the **unreviewed draft** labels, k=3 | lexical: recall 0.95, MRR 0.95 · FAISS: recall 1.0, MRR 0.92 · FAISS+bge-rerank: recall 1.0, MRR 0.98 |
| Fine-tune smoke test (synthetic images, no pretrained weights) | stages A/B/C ran and the checkpoint was saved. ONNX export needs `onnxscript` (added to `training/requirements-train.txt`, not installed) |
| Gate training smoke test (synthetic) | trained and routed correctly. This only proves the plumbing, it is not a metric |
Not verified locally: ONNX sub-expert inference (needs `onnxruntime`), real datasets, GPU training, Gemini, the local LLM server, and live weather.

## 4. Commands for you to run
```bash
pip install -r training/requirements-train.txt                      # training machine only
# Phase 0/1: audit, baseline, fine-tune, gate, evaluate
python -m training.dataset_audit --root <plantvillage_dir> --domain crop
python -m training.dataset_audit --root <cattle_dir> --domain livestock --class-map training/configs/cattle_class_map.json
python -m training.evaluate_expert --root <plantvillage_dir> --domain crop --target baseline     # "before"
python -m training.finetune_expert --root <plantvillage_dir> --group crop_row
python -m training.finetune_expert --root <plantvillage_dir> --group crop_perennial
python -m training.finetune_expert --root <cattle_dir> --group livestock_lsd --class-map training/configs/cattle_class_map.json
python -m training.finetune_expert --root <cattle_dir> --group livestock_fmd --class-map ...     # only if audit OK
python -m training.train_moe_gate --root <plantvillage_dir> --domain crop
python -m training.evaluate_expert --root <plantvillage_dir> --domain crop --target moe          # "after" + routing acc
pip install onnxruntime   # app machine, to activate MoE (AGRIVISION_MOE_ENABLED=auto picks it up)
# Phase 3
python -m src.zone2_cloud.rag.build_knowledge_base
python eval/rag_eval.py --backend faiss        # after reviewing eval/rag_queries.json and setting reviewed=true
# Phase 4 (the Gemini steps cost quota)
python -m training.llm.generate_synthetic_data --dry-run --n 20
GEMINI_ENABLED=true python -m training.llm.generate_synthetic_data --n 40 --i-understand-this-calls-gemini
python -m training.llm.prepare_sft_dataset --reviewed results/zone2/llm_data/review_sample.csv
python -m training.llm.finetune_qlora                                                            # GPU
python -m training.llm.compare_backends --backend local_llm      # and --backend gemini --i-understand-this-calls-gemini
python eval/rag_eval.py --citations results/zone2/llm_compare/local_llm.jsonl
# Tests / app
pytest tests/ -v
streamlit run src/app/streamlit_app.py
```

## 5. Streamlit flows to test
1. **Sidebar:** pick a Region and Season. The region is saved and comes back after you log in again.
2. **Local route (crop, high confidence):** a blue 🗓️ note shows season- and region-aware timing guidance. The diagnosis and actions are the same as without context.
3. **Cloud route:** the caption shows `Cited docs: KB-...`, `History refs: H...` and "Citations verified ✅". In mock mode these are real IDs taken from the prompt.
4. **Weather:** with `WEATHER_ENABLED=true` and a network, a weather caption appears. Disconnect and the advisory still appears, just without weather.
5. **Local LLM fallback:** `ADVISORY_BACKEND=local_llm` with no server still produces an advisory, because it falls back to Gemini/mock.

## 6. Deployment note (Vercel, ~512MB)
- New runtime code is light: numpy, stdlib and optional onnxruntime. The lexical RAG backend removes the need for torch in Zone 2.
- **Blockers that were already there before this work:** (a) Streamlit needs a long-running websocket server and does not run on Vercel serverless functions. (b) The current Zone 1 HF experts, the zero-shot router and sentence-transformers all import torch and transformers, which exceed Vercel's bundle and memory limits. (c) SQLite on Vercel lives only in ephemeral `/tmp`.
- Options: host the UI on Streamlit Community Cloud, HF Spaces or Render. Or put an API on Vercel that uses the ONNX sub-experts, the numpy gate, lexical RAG and a hosted DB, running with `AGRIVISION_EXPERT_MODE=mock` or ONNX-only. The LLM always runs on a separate server.

## 7. Known limitations / remaining work
- The 22 gap-fill KB docs, `seasonal_guidance.json` and `eval/rag_queries.json` are drafts. They need expert review.
- The gate's hand-crafted colour/texture features may confuse visually similar groups. Measure routing accuracy, and if it underperforms, report that honestly before changing anything.
- MoE is inactive until the trained artifacts exist.
- Future scope (task §16) is untouched.
