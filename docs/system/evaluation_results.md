# Evaluation Results & Report

Living document. **Every number here was produced by a run you executed on the GPU workstation** (files copied into
`results/zone1/` and `models_cache/moe/`), except where a row is marked *(local draft)*. Sections marked ⏳ are filled in
after the corresponding run. Commands to reproduce: [`test_to_do.md`](../../test_to_do.md).

Last updated: 2026-09-30 · Status: **Part B (vision experts + MoE) evaluated. RAG label review and Qwen LLM (Part C) pending.**

## 1. Summary (read this first)

| Component | Before | After | Verdict |
|---|---|---|---|
| Crop sub-experts (each on its own group) | - | accuracy **0.975** (row) / **0.9846** (perennial); macro-F1 0.9643 / 0.9788 | ✅ Very good, well calibrated (ECE < 0.01) |
| Livestock sub-experts (each vs healthy) | - | accuracy **0.936** (LSD) / **0.951** (FMD) | ✅ Good |
| **moe_gate** (picks the sub-expert) | - | crop routing **0.7447**, livestock **0.8191** | ⚠️ **Weak: this is the bottleneck** |
| Crop end-to-end (gate → expert) | 0.1135 (not comparable yet, see 3.1) | **0.7731** (macro-F1 0.7512) | 🟡 Big gain vs baseline, but ~20 points below what the experts alone reach |
| Livestock end-to-end | 0.5298 (CLIP zero-shot) | **0.8357** (macro-F1 0.8341) | 🟡 Large gain, but see the safety note in 3.2 |
| RAG retrieval (draft labels, local) | - | recall@3 1.0, MRR 0.92 (FAISS) *(local draft)* | ⏳ needs your reviewed labels |
| Qwen LoRA advisory model | - | - | ⏳ Part C |

**Main conclusion.** The fine-tuned experts themselves are excellent. Overall accuracy is held back almost entirely by the
`moe_gate`, which sends only ~74% (crop) and ~82% (livestock) of images to the correct expert. An image sent to the wrong
expert is forced into that expert's label set, and the expert is usually *confident* (over-confident). Recommended fix: section 5.

## 2. Setup used
- Hardware: 1 × 24 GB GPU; backbone `mobilenetv3_large_100`, 224 px, mixed precision; 3-stage gradual unfreezing (A head-only, B top-2 blocks, C full network) with differential learning rates; best epoch chosen by validation macro-F1.
- Data: PlantVillage (38 classes, the dataset's own `train/` + `val/`; `val/` split 50/50 per class into validation and **test**), cattle "Cows datasets" (`lumpy`, `foot-and-mouth`, `healthy`; stratified 70/15/15, seed 42).
- Crop groups: `crop_row` = 21 classes, `crop_perennial` = 17. Livestock: `livestock_lsd` (LSD vs healthy), `livestock_fmd` (FMD vs healthy).
- Labels are compared after name normalisation, so the 38 PlantVillage folders appear as 29 classes below (healthy classes of crops without their own KB entry merge into `crop_healthy`).
- Test-set sizes: crop end-to-end 5433 images, livestock 487 images.
- Saved artifacts (`models_cache/moe/`): one folder per sub-expert (`model.onnx`, `meta.json`, `best.pt`, reports, ≈ 33-39 MB each), `crop_moe_gate.json` and `livestock_moe_gate.json` (8 KB each).

## 3. Results in detail

### 3.1 Crop
**Sub-experts on their own test images (gate not involved):**

| Expert | n | accuracy | macro-F1 | ECE | best val macro-F1 |
|---|---|---|---|---|---|
| crop_row | 3359 | 0.9741 | 0.965 | 0.0043 | 0.9703 |
| crop_perennial | 2074 | 0.9778 | 0.9693 | 0.0059 | 0.9695 |

Training curves (`training_log.csv`) show validation macro-F1 rising through stages A → B → C and plateauing near 0.96-0.97, with no sign of overfitting. Hardest `crop_row` classes: maize gray leaf spot (F1 0.86), tomato early blight (0.92), tomato target spot (0.93).

**Baseline (the original checkpoint) vs MoE, crop:**

| | n | accuracy | macro-F1 | ECE |
|---|---|---|---|---|
| Baseline (original 13-class checkpoint) | 6517 | 0.1135 | 0.0989 | 0.886 |
| MoE end-to-end | 5433 | 0.7731 | 0.7512 | 0.1359 |

⚠️ **The baseline row is not like-for-like yet.** It was scored on 6517 images while every MoE report uses 5433 (the sum of the two sub-expert test sets). The baseline count matches about 15% of the `train/` folder, so it was very likely run against a different root or split (this is an inference, not verified). It also cannot predict most classes (its 13-class head has no tomato, apple, grape...) and is ~100% confident on everything (ECE 0.886). **Action: re-run the crop baseline with `--root "$PV"` (test_to_do.md, step B3) so both use the same 5433 images, then update this row.**

MoE end-to-end per class (worst first):

| class | precision | recall | F1 | support |
|---|---|---|---|---|
| cherry_powdery_mildew | 0.2807 | 0.4571 | 0.3478 | 105 |
| pepper_bacterial_spot | 0.3216 | 0.64 | 0.4281 | 100 |
| strawberry_leaf_scorch | 0.3074 | 0.7838 | 0.4416 | 111 |
| apple_black_rot | 0.4625 | 0.5968 | 0.5211 | 62 |
| tomato_septoria_leaf_spot | 0.7037 | 0.4294 | 0.5333 | 177 |
| apple_scab | 0.5833 | 0.6667 | 0.6222 | 63 |
| tomato_yellow_leaf_curl_virus | 0.921 | 0.5 | 0.6481 | 536 |
| tomato_early_blight | 0.7079 | 0.63 | 0.6667 | 100 |
| apple_cedar_rust | 0.7037 | 0.6786 | 0.6909 | 28 |
| peach_bacterial_spot | 0.6486 | 0.8348 | 0.73 | 230 |
| tomato_spider_mites | 0.9273 | 0.6071 | 0.7338 | 168 |
| grape_leaf_blight | 0.6619 | 0.8519 | 0.7449 | 108 |
| tomato_late_blight | 0.8675 | 0.6859 | 0.7661 | 191 |
| tomato_bacterial_spot | 0.8701 | 0.7264 | 0.7918 | 212 |
| potato_late_blight | 0.7961 | 0.82 | 0.8079 | 100 |
| maize_gray_leaf_spot | 0.8367 | 0.7885 | 0.8119 | 52 |
| tomato_leaf_mold | 0.9577 | 0.7083 | 0.8144 | 96 |
| citrus_greening | 0.9031 | 0.7441 | 0.8159 | 551 |
| grape_esca | 0.844 | 0.8623 | 0.853 | 138 |
| tomato_target_spot | 0.8676 | 0.8429 | 0.8551 | 140 |
| maize_northern_leaf_blight | 0.9022 | 0.8469 | 0.8737 | 98 |
| potato_early_blight | 0.8364 | 0.92 | 0.8762 | 100 |
| crop_healthy | 0.8285 | 0.9327 | 0.8775 | 1233 |
| tomato_mosaic_virus | 0.9688 | 0.8378 | 0.8986 | 37 |
| maize_healthy | 0.9897 | 0.8276 | 0.9014 | 116 |
| grape_black_rot | 0.8992 | 0.9068 | 0.903 | 118 |
| squash_powdery_mildew | 0.9527 | 0.875 | 0.9122 | 184 |
| tomato_healthy | 0.9438 | 0.9497 | 0.9467 | 159 |
| maize_common_rust | 0.9748 | 0.9667 | 0.9707 | 120 |

Calibration of the MoE (accuracy should match confidence):

| confidence bucket | images | actual accuracy | average confidence |
|---|---|---|---|
| 0.1-0.2 | 2 | 0.0 | 0.1863 |
| 0.2-0.3 | 19 | 0.3158 | 0.2673 |
| 0.3-0.4 | 102 | 0.2353 | 0.3521 |
| 0.4-0.5 | 174 | 0.2241 | 0.4548 |
| 0.5-0.6 | 233 | 0.2275 | 0.5516 |
| 0.6-0.7 | 223 | 0.2646 | 0.6536 |
| 0.7-0.8 | 245 | 0.3265 | 0.7513 |
| 0.8-0.9 | 306 | 0.4052 | 0.852 |
| 0.9-1.0 | 4129 | 0.924 | 0.9922 |

Reading: of the 4129 predictions with confidence ≥ 0.9, only 0.924 are right although the model says ~0.9922. Those errors are most likely misrouted images that the wrong expert classified confidently (inferred, not separately verified), so the app's confidence gate cannot catch them.

### 3.2 Livestock
| | n | accuracy | macro-F1 | ECE |
|---|---|---|---|---|
| Baseline (CLIP zero-shot) | 487 | 0.5298 | 0.5135 | 0.0763 |
| livestock_lsd alone | 375 | 0.936 | 0.936 | 0.0488 |
| livestock_fmd alone | 306 | 0.951 | 0.9482 | 0.0398 |
| MoE end-to-end | 487 | 0.8357 | 0.8341 | 0.1452 |

Baseline and MoE were scored on the same 487 images (fair comparison): **+30.6 points accuracy**.

MoE confusion matrix (rows = truth):

| true / predicted | foot_and_mouth_disease | healthy | lumpy_skin_disease |
|---|---|---|---|
| **foot_and_mouth_disease** | 99 | 5 | 8 |
| **healthy** | 8 | 177 | 9 |
| **lumpy_skin_disease** | 16 | 34 | 131 |

Per class:

| class | precision | recall | F1 | support |
|---|---|---|---|---|
| lumpy_skin_disease | 0.8851 | 0.7238 | 0.7964 | 181 |
| foot_and_mouth_disease | 0.8049 | 0.8839 | 0.8426 | 112 |
| healthy | 0.8194 | 0.9124 | 0.8634 | 194 |

Calibration:

| confidence bucket | images | actual accuracy | average confidence |
|---|---|---|---|
| 0.5-0.6 | 2 | 0.0 | 0.5288 |
| 0.6-0.7 | 7 | 0.4286 | 0.6581 |
| 0.7-0.8 | 8 | 0.5 | 0.7508 |
| 0.8-0.9 | 14 | 0.6429 | 0.8583 |
| 0.9-1.0 | 456 | 0.8575 | 0.9957 |

🚨 **Safety note.** 34 of 181 lumpy-skin-disease images (18.8%) were predicted **healthy**. Most likely cause (inferred from the gate routing errors, not separately tested): when the gate sends a lumpy image to the FMD expert, that expert only knows {FMD, healthy} and answers "healthy". The LSD expert on its own catches 94.5% of lumpy cases. LSD and FMD are notifiable diseases, so missed cases matter more than overall accuracy.

### 3.3 moe_gate (routing)
| Gate | test images | routing accuracy | macro-F1 | val routing accuracy |
|---|---|---|---|---|
| crop (row vs perennial) | 4737 (max 300 imgs/class) | 0.7606 | 0.7545 | 0.7637 |
| livestock (LSD vs FMD; `healthy` excluded) | 293 | 0.8191 | 0.816 | 0.8362 |

Crop gate confusion (rows = truth):

| true / predicted | crop_row | crop_perennial |
|---|---|---|
| **crop_row** | 2175 | 739 |
| **crop_perennial** | 395 | 1428 |

The gate is a logistic regression on 54 hand-made colour/texture statistics. Crop groups look alike at that level (a green leaf on a plain background), so about a quarter of images go to the wrong expert. End-to-end accuracy is roughly routing accuracy × expert accuracy (0.745 × 0.98 ≈ 0.73; measured 0.7731 because some misrouted images still land on a correct label such as `crop_healthy`).

## 4. Caveats (important when quoting these numbers)
1. **PlantVillage is a lab dataset** (single leaf, plain background). Field photos from farmers' phones will score lower, so the 97-98% figures are upper bounds.
2. **Possible near-duplicates between train and val** (PlantVillage has many shots of the same leaf, and some copies contain augmented images). If present, test accuracy is optimistic. Not verified.
3. The cattle set is small; the livestock test set has 487 images, so differences of ±3 points are within noise.
4. The crop baseline row is not comparable yet (section 3.1). The livestock baseline is fair.
5. No independent field test set exists yet.

## 5. Recommended next steps (not implemented yet; awaiting your decision)
1. **Fix routing (highest impact).** Run *both* sub-experts of the domain (each ONNX MobileNet takes tens of milliseconds on CPU, about 35 MB each) and keep the more confident answer, using the gate probability only as a tie-breaker. The task plan allowed this "top-k" fallback if top-1 routing proved poor; the data above is that justification. For livestock, if either expert reports a disease with confidence above a threshold, report the disease. Expected effect: end-to-end accuracy should move toward the sub-expert level (~97% crop, ~93-95% livestock), but this **must be measured** with an evaluation run before it is claimed.
2. Re-run the crop baseline on the same 5433-image test set.
3. Optionally replace the colour-statistics gate with CNN embeddings (only needed if you keep top-1 routing).
4. Re-check calibration after any routing change, because the app's confidence gate depends on it.

## 6. Other components
### 6.1 RAG retrieval (local draft run, before your review)
Knowledge base: 49 documents (22 new drafts flagged `draft_needs_expert_review`). 22 draft queries, k = 3:

| Backend | precision@3 | recall@3 | hit@3 | MRR |
|---|---|---|---|---|
| Lexical BM25 (no torch) | 0.3333 | 0.9545 | 1.0 | 0.9545 |
| FAISS + MiniLM | 0.3636 | 1.0 | 1.0 | 0.9242 |
| FAISS + bge reranker | 0.3636 | 1.0 | 1.0 | 0.9773 |

Precision@3 is capped near 0.33-0.36 because most queries have exactly one relevant document. **These labels were written by the coding agent, not a domain expert.** ⏳ Re-run after you review `eval/rag_queries.json` and set `"reviewed": true`.

### 6.2 Automated tests (laptop, CPU)
120 passed, 13 skipped (Windows OpenCV import skips, pre-existing).

### 6.3 ⏳ Synthetic data, Qwen LoRA, comparison with Gemini
Pending Part C. To fill in: number of approved training examples, QLoRA training time and eval loss, and the comparison table (schema validity, validator pass, citation correctness, farm-history citation correctness) for `local_llm` vs `gemini`.

### 6.4 ⏳ App-level checks with real models
Pending: confirm the `MoE expert: <group> (onnx)` caption in Streamlit, and that the app's predictions match `evaluate_expert` on a few images.
