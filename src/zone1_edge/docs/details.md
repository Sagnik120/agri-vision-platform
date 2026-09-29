# Zone 1 Edge Details

## 1. Purpose
Provides the offline-first edge AI reasoning.

## Key Responsibilities
- **Quality Gate:** Checks image blur (Laplacian variance), exposure, resolution (>= 50px), and contrast. Rejects invalid images immediately.
- **Task Router:** Identifies whether the input is a crop, livestock, or "none" (irrelevant image). If "none", it short-circuits the pipeline before invoking any expert.
- **Multimodal Experts:** Dedicated submodules for image, text, and sensor data.
  - Image experts embed transparent tracking (real vs. mock backend).
- **Fusion:** Deterministic weighted fusion using `WEIGHT_VISUAL` (0.6), `WEIGHT_TEXT_SUPPORT` (0.2), and `WEIGHT_SENSOR_SUPPORT` (0.2) to calculate the final confidence score. Confidence is strictly bounded [0.01, 0.99] unless maxed.

## 3. Architecture Role
The primary inference engine. Determines if cloud escalation is necessary.

## 4. Inputs
Image paths, simulated sensor dictionaries, transcribed Hindi text.

## 5. Outputs
Returns the finalized Contract 5 (Fusion Output + Gate Routing Decision).

## 6. Important files
- `pipeline.py`: Orchestrator.
- `fusion.py`: Rule-based combination.
- `confidence_gate.py`: Gateway threshold checks.

## 7. Dependencies
`torch`, `transformers`, `huggingface_hub`.

## 8. Runtime flow
Called by `streamlit_app.py`. Dispatches to router, then experts, then fusion, then gate.

## 9. Contracts/interfaces
Produces Contracts 1, 3, 4. Outputs Contract 5.

## 10. Current implementation status
IMPLEMENTED (with mock fallbacks heavily utilized).

## 11. Important assumptions
Assumes local models are downloaded in `setup/`.

## 12. Known limitations
Fusion is rule-based, not a learned vector embedding space.

## 13. Intra-domain Mixture-of-Experts (`moe/`) — AI upgrade Phase 0/1
**Terminology (do not confuse):**
- `moe_gate` (`moe/moe_gate.py`) — runs BEFORE any sub-expert, inside an already-chosen domain, and picks exactly ONE sub-expert (top-1 hard routing). Learned multinomial logistic regression over a 54-dim numpy image descriptor (`moe/image_features.py`). Weights: `models_cache/moe/<domain>_moe_gate.json`.
- `confidence_gate` (`multimodal/confidence_gate.py`) — runs AFTER fusion and decides local vs cloud. Unchanged mechanism.

Flow: domain router (unchanged) → `moe_gate` → 1 ONNX sub-expert (`models_cache/moe/<group>/model.onnx`) → fusion → confidence_gate.
Groups (`moe/expert_groups.py`): `crop_row` (21 PlantVillage annual row/vine classes), `crop_perennial` (17 tree/bush/perennial classes), `livestock_lsd` (LSD vs healthy), `livestock_fmd` (FMD vs healthy — ships only if `training/dataset_audit.py` does not flag FMD as under-supported).
Activation: `AGRIVISION_MOE_ENABLED=auto` (default) uses MoE only when a trained gate + all sub-expert ONNX files exist; otherwise the original single expert runs. Any MoE failure falls back to the single expert. Output = contract #1 + trailing `_moe` debug key.
Routing modes (`AGRIVISION_MOE_ROUTING`): `top1` (default; gate picks one expert) or `both` (all experts of the domain run; crop = most confident wins, livestock = disease-first). `both` exists because the measured gate routing accuracy was low (see `docs/system/evaluation_results.md`); it costs one extra ONNX inference and may raise false alarms, so enable only after measuring with `training.evaluate_expert --routing both`.
Runtime deps: numpy + optional `onnxruntime` (torch-free; serverless-friendly). Training: `training/` (user-run).

## 14. Label normalisation & region/season context — Phase 2
- `knowledge/label_aliases.py::normalize_condition()` maps checkpoint labels to KB keys (e.g. `Corn___Common_Rust` → `maize_common_rust`; healthy classes of crops without their own entry → `crop_healthy`). Used by `local_advisory` and `confidence_gate`. Before this, corn predictions never matched the KB and always escalated.
- `context/farm_context.py`: `build_context(region, season)`; season inferred from date if not given (kharif Jun–Oct, rabi Nov–Mar, zaid Apr–May).
- `run_zone1_pipeline(..., region=None, season=None)` returns `context`; the local advisory gains `context_note` (from `knowledge/seasonal_guidance.json`, draft guidance by disease-driver category). Context NEVER affects the visual prediction, the moe_gate or the confidence_gate.
- Zone 1 never calls weather (offline-first); `build_cloud_payload_stub` appends `region`, `season`, `weather: null` at the end.
