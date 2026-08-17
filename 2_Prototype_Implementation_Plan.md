## Agri-Vision Platform — 2-Day Prototype Improvement Plan

Step-by-step implementation guide: what to build now, what to defer, and why

Agri-Vision Team

August 2026

## Contents

## 0. Scope of This Document

This document turns the verdicts from PDF 1 (Architecture Improvement Analysis) into a concrete, buildable 2-day plan on top of the existing, working Zone 1/2/3 codebase (38 passing Zone 1 pytest tests, Zone 2/3 stubs). It assumes the reader has both people available across roughly 2 working days (~14–16 focused hours total per person, ~28–32 person-hours).

In scope for these 2 days (ADOPT / ADOPT-SCOPED items from PDF 1): 1. Capture qual- ity check 2. Zero-train confidence/entropy dual-backbone task router 3. Dynamic confidence & safety gate (quality/agreement/domain/safety-list) 4. Symbolic text-evidence fusion expansion + embedding-based fusion (medium/high tier only) 5. Sensor feature/rule upgrade + top-k first-aid output 6. Expanded curated RAG knowledge base (25–40 entries) 7. Bounded 1-step clarification loop (stretch, only if time remains) 8. Gemini


output validator + small offline gold-set eval harness 9. Minimal farmer login (PIN/phone) + farmer-scoped Zone 3 + PII stripping 10. Docker-Compose for Zone 2 (+ documentation of the broader MLOps story) 11. Explainability layer: top-3 display + Grad-CAM overlay (crop only) + reason strings 12. Device-tier gating reaf- firmed (mostly already designed — wire the two new tier-gated behaviors from #4) 13. Hindi+English offline TTS as already planned, + cloud multilingual text output for 2–3 extra languages 14. 3-tier honesty ladder (confident / possible+first-aid / refer-to-expert) 15. RAG engine hardening — treated as the cross-cutting top priority, threaded through 6/7/8/11/14

Explicitly NOT built in these 2 days (documented only, see PDF 1 Section 3.3 for full reasoning): - Trained neural task-router model (kept as zero-train ensemble instead) - Full agentic-AI framework for Zone 2 - Real OAuth/production auth - CI/CD pipelines, Kubernetes, autoscaling - Fully offline multilingual TTS beyond Hindi+English - VLM backbone for on-device inference - Real IoT hardware integration (sensor stays simulated, just smarter)

## 1. Pre-Work: Before Touching Any Code (30–45 min, both people together)

- 1. Re-freeze the contract additions. The original contract.md (Section 2 of the 8-hour plan) needs four additive fields — additive only, so nothing already-working breaks:

- Image expert output gains: "quality_score": float, "quality_flag": "ok"|"warn"|"reject"

- Fusion output gains: "threshold_used": float, "threshold_reason": [str,...], "advisory_tier": "confident"|"possible"|"refer_expert"

- Cloud request payload gains: "farmer_id": str (replaces any implicit global), "clarification_answer": str|null

- A new top-level contract: Sensor top-k output — {"domain":"livestock", "candidates": [{"condition": str, "score": float, "first_aid": [str,...]}], "trend": "rising"|"falling"|"stable Paste this addendum into contract.md and commit before writing any new code.

- 2. Branch strategy: create two long-lived branches, feature/zone1-enhancements (Person A) and feature/zone2-zone3-enhancements (Person B), both off main, merged back at the two checkpoints defined in PDF 3.

- 3. Confirm test baseline: run the existing 38 Zone 1 pytest tests once, confirm all green, tag this commit pre-improvement-baseline — this is the rollback point if anything goes wrong.

## 2. Zone 1 Improvements — Step-by-Step (Owner: Person A, refer- ences PDF 1 §1.1–1.5, 1.11, 1.12, 1.14)

## 2.1 Capture Quality Check — edge/quality_check.py (new file)

Why this order: every downstream Zone 1 improvement (router, gate, tiering) can consume quality_score, so this must be built first.

Steps: 1. Add opencv-python-headless to requirements.txt (headless avoids GUI deps on a server/CI box). 2. Write compute_blur_score(img: np.ndarray) -> float using Laplacian variance on a resized (max-dim 512px) grayscale copy. 3. Write compute_exposure_score(img) -> float using a luminance histogram check (fraction of pixels in extreme bins). 4. Write compute_quality(img) -> dict returning {"quality_score": float, "quality_flag": "ok"|"warn"|"reject", "reasons": [str,...]}, combining blur+exposure with simple weights (start 0.6*blur_norm + 0.4*exposure_norm, tune thresholds against 5–10 sample real/blurry photos you take yourself in the first hour). 5. Wire into the pipeline orchestrator before the task router call: if quality_flag == "reject", short-circuit and return a farmer-facing message immediately (from reasons), never call any expert model. 6. Test file: tests/test_quality_check.py — feed a sharp fixture image (pass), an artificially Gaussian-blurred copy of it (reject), and an artificially over/under-exposed copy (reject/warn).


Add 4–6 tests; keep pytest green. 7. Streamlit UX: on reject, show a clear message + a “Retake Photo” button that clears the uploader widget state; on warn, show a small non-blocking banner but proceed.

- 2.2 Zero-Train Dual-Backbone Task Router — edge/task_router.py (modify exist- ing)

Depends on: crop expert and livestock expert both already loadable (they are, from the existing codebase). Steps: 1. Add a new function auto_route(img) -> dict that runs both experts’ forward pass once each (they’re already small; ~<150ms combined on CPU for MobileNetV3+EfficientNet-B3-sized models) and com- putes softmax entropy for each: entropy = -sum(p * log(p)). 2. Decision rule: choose the domain with higher max-confidence AND lower entropy; if the two experts disagree on which one “wins” between the two signals, default to whichever has the higher max-confidence (confidence is the primary signal, entropy is a tie- breaker/sanity check). 3. Keep the existing manual Crop/Livestock tab buttons as an override, not a removal — this is safer for the demo (a judge or farmer can still force a domain) and takes zero extra work since the buttons already exist; auto_route just becomes the new default path when no explicit tab click has occurred, e.g. via a single “Auto-detect” tab added alongside the existing two. 4. Test file: extend tests/test_task_router.py with fixture images already used by the crop/livestock expert tests — assert auto_route picks the correct do- main on at least 4 clear fixture cases, and returns both scores for inspection. 5. This explicitly does not touch crop_expert.py or livestock_expert.py internals — it only adds a new orchestration function that calls both, so risk to already-passing tests is minimal.

- 2.3 Sensor Feature/Rule Upgrade — edge/sensor_expert.py (modify existing)

Steps: 1. Replace the flat simulated-value dict with a small realistic generator: sample temperature around a breed-normal baseline (e.g., 38.5°C ± noise), with an injectable “anomaly mode” toggle for demo purposes (so you can show both a normal and an anomalous reading on demand). 2. Add a two-reading trend check: store the last reading in a small in-memory/session state, compute trend = "rising"|"falling"|"stable" by comparing to the previous value. 3. Implement top_k_first_aid(sensor_reading, trend) -> list[dict] returning up to 3 ranked candidate conditions from a small hand-written mapping (e.g., high_temp + rising + low_activity → [heat_stress, early_infection]), each with a generic, always-safe first-aid action string (isolate animal, ensure shade/water, monitor, do not medicate without vet confirmation) — pull the action text from local_advisories.json-style entries you already have a pattern for. 4. Update the sen- sor contract per Section 1 above; update any consumers (fusion.py) to accept the new shape. 5. Test file: tests/test_sensor_expert.py — assert trend detection over 2 synthetic readings, assert top_k_first_aid returns 1–3 ranked candidates with non-empty first-aid lists, assert generic-only actions (no drug names) via a simple keyword denylist check in the test itself (cheap regression guard against the prompt/logic drifting later).

- 2.4 Text Evidence Fusion Upgrade— multimodal/text_evidence.py + multimodal/fusion.py (modify existing)

Steps: 1. Expand the Hindi/English symptom keyword dictionary from the current small set to 25–35 entries (add common terms for the new KB conditions from Section 3 below) — this alone strengthens the existing symbolic path with no architecture change. 2. Add device-tier gating scaffolding even though the actual tier probe may already exist from prior work: a config flag enable_embedding_fusion: bool read from the cached device-tier result (medium/high → true, low → false). 3. When enable_embedding_fusion is true, load sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 lazily (only on first use, only on qualifying tiers, never on low tier) and compute cosine similarity between the extracted symp- tom text and the predicted condition’s canonical description (add a canonical_description field to each local_advisories.json entry if not already present). Blend: final_text_support_score = symbolic_match ? max(0.10, embedding_score*0.10) : (embedding_score > 0.6 ? 0.05 : -0.20) — i.e., embedding similarity can partially rescue a case the symbolic matcher missed, but never overrides an explicit symbolic conflict. 4. Update fusion.py’s existing +0.10 / -0.20 rule to call this new blended function instead of the raw keyword-overlap boolean, keeping the same output contract shape. 5. Test file: extend tests/test_fusion.py — add cases for symbolic-only (existing), symbolic+embedding agreeing (low tier should skip embedding and


still pass via symbolic), and a case where only embedding rescues a paraphrased symptom (medium/high tier only — mock the tier flag in the test rather than requiring the real model download in CI, to keep tests fast).

## 2.5 Dynamic Confidence & Safety Gate — edge/confidence_gate.py (modify exist- ing)

Steps: 1. Replace the fixed scalar threshold with the additive rule from PDF 1 §1.3: threshold = base(0.75) + delta_quality + delta_agreement + delta_domain − delta_history_match, clipped to [0.60, 0.90]. 2. Add a hard-coded safety list: SAFETY_OVERRIDE_CONDITIONS = {"lumpy_skin_disease", "fmd", ...} (from local_advisories.json keys) — if the predicted condition is in this set, force route = "cloud" and advisory_tier at most "possible", regardless of numeric confidence. 3. Populate threshold_reason: [str,...] with human-readable strings (“image quality borderline: +0.05”, “evidence disagreement: +0.08”, “livestock domain: +0.03”) — this list is what powers the transparency UI in Section 2.6. 4. Assign advisory_tier here (confident / possible / refer_expert) per the 3-tier ladder from PDF 1 §1.14: final_confidence >= threshold → confident; final_confidence < threshold but not in safety list and quality not rejected → possible; in safety list, or quality was "warn"/"reject" and no strong corroborating evidence → refer_expert. 5. Test file: extend tests/test_confidence_gate.py — table-driven tests covering: safety-list override fires regardless of confidence; low quality raises effective threshold; high evidence agreement lowers it; tier assignment matches expectation for a handful of constructed input combinations.

## 2.6 Explainability Layer — edge/explainability.py (new file) + Streamlit wiring

Steps: 1. Top-3 display: already available from top_k in the contract — just needs a Streamlit bar-chart/list widget, ~15 minutes. 2. Reason string: directly render threshold_reason + advisory_tier from Section 2.5 — no new computation needed. 3. Grad-CAM overlay (crop expert only, to bound scope): use pytorch-grad-cam’s GradCAM (or EigenCAM if the crop backbone isn’t directly compatible) targeting the last convolutional block of the crop MobileNetV3, produce a heatmap, alpha-blend over the original image with OpenCV, return as a PIL image for Streamlit st.image. 4. Gate this behind a try/except with a graceful skip (“explainability overlay unavailable for this model”) so a library/version mismatch never breaks the main demo path — this must degrade gracefully, not raise. 5. Test file: tests/test_explainability.py — assert the overlay function returns an image of the same dimensions as the input on a fixture image, and doesn’t raise given a valid model + image (skip/mark-xfail gracefully in CI if GPU/heavy deps aren’t available, so it doesn’t block the main suite).

## 3. Zone 2 Improvements — Step-by-Step (Owner: Person B, refer- ences PDF 1 §1.6–1.9, 1.13, 1.15)

## 3.1 Expanded RAG Knowledge Base — knowledge/kb/*.json (expand existing)

Steps: 1. Grow from 8–10 to 25–40 entries. Source content from ICAR/state agricultural-extension published advisories and standard livestock disease references (write these by hand/curated, do not let the LLM invent them — this is exactly the hallucination risk the validator in 3.3 exists to catch, so the KB itself must be clean). 2. Each entry keeps the existing schema (Condition / Symptoms / Visual indicators / Recommended actions / Prevention / When to seek expert / Source) and gains one new field: canonical_description (a single clean sentence, used by the embedding fusion in Section 2.4) and is_safety_critical: bool (feeds the safety list in Section 2.5 — Zone 1 and Zone 2 should read this same flag from a shared knowledge/local_advisories.json / KB source of truth rather than duplicating a hardcoded list in two places). 3. Re-run the embedding + FAISS index build script against the expanded KB; confirm index size/latency is still trivial (should be, at this corpus size). 4. Test file: tests/test_rag_kb.py — schema validation for every entry (all required fields present, is_safety_critical is boolean, no entry duplicated), plus a retrieval smoke test (a known symptom-heavy query returns the expected entry in the top-3 results).


## 3.2 Farmer Login + Farmer-Scoped Zone 3 — zone3/auth.py (new), zone3/memory.py (modify existing)

Steps: 1. Add a minimal Streamlit login screen: phone number + 4-digit PIN, stored/checked against the farm table (add a pin column if not present — plaintext acceptable for a demo, clearly commented # DEMO ONLY — production must hash + salt, and stated as such in the architecture doc so this is a documented, not missed, gap). 2. On successful login, store farmer_id in st.session_state for the rest of the session; every Streamlit page/tab reads it from there rather than a global. 3. Update save_observation() and get_farm_history() (already scaffolded) to accept and filter by farmer_id — this is a small, mechanical change (WHERE farmer_id = ?), not a rebuild. 4. Add strip_pii(payload: dict) -> dict in zone2/gemini_client.py’s request-building path: ensure only farmer_id (opaque) and derived summaries go to Gemini — never raw phone number/name. 5. Test file: tests/test_auth.py + extend tests/test_memory.py — assert two different farmer_ids never see each other’s history; assert strip_pii removes phone/name keys from a sample payload.

## 3.3 Gemini Output Validator + Offline Eval Harness — zone2/validator.py, eval/gold_set.json, eval/run_eval.py (new)

Steps: 1. validator.py: validate_advisory(response_json, retrieved_snippets, input_evidence) -> (bool, list[str]) — checks (a) JSON schema conformance against the agreed cloud-response shape, (b) every named condition/action in the response appears in retrieved_snippets or input_evidence (crude ground- ing check — flag, don’t necessarily hard-block, since some paraphrase is expected; log a warning and lower advisory_tier if this fails rather than fully discarding a possibly-fine answer), (c) a keyword denylist scan for specific drug names/dosage patterns (regex for common dosage units like “mg”, “ml/kg” appearing near a drug- like proper noun) — if found, hard-block and fall back to the safe templated response. 2. Wire the validator into gemini_client.py immediately after the API call, before returning to the UI. 3. eval/gold_set.json: hand-write 15–20 cases (mix crop/livestock, mix clear/ambiguous, at least 2 safety-list conditions) with expected advisory_tier and expected “must mention / must not mention” keyword lists (not full expected text — full- text matching is brittle). 4. eval/run_eval.py: runs the full pipeline against each gold-set case, reports: schema-valid %, correct-tier %, safety-list-correctly-escalated %, drug-mention-violations count. Run once at the end of each of the 2 days; save the report as a markdown/JSON artifact to cite in the final submission. 5. Test file: tests/test_validator.py — unit tests for each of the three validator checks independently, using constructed fixture responses (one clean pass, one ungrounded claim, one drug-dosage violation).

## 3.4 Bounded Clarification Loop (stretch — only after everything else above is done)

Steps (only attempt if both people finish Sections 2 and 3.1–3.3 with time remaining): 1. In fusion.py’s output, when evidence_agreement == "low" and no farmer_text was provided at all, set a new flag needs_clarification: true instead of proceeding straight to cloud escalation. 2. Zone 2’s Streamlit flow checks this flag: if true, ask one fixed, domain-appropriate follow-up question (e.g., livestock: “Is the animal still eating and drinking normally?”; crop: “Has this spread to other plants nearby?”) via a simple text/voice input, then re-run fusion once with the answer folded in as additional farmer_text, and proceed normally — capped at exactly one round, never looping. 3. This is a plain if/else branch, not an agent framework — reaffirms the PDF 1 §1.7 verdict. 4. Test file: tests/test_clarification.py — assert the flag fires only under the exact low-agreement+no-text condition, and that a second fusion call with added text does not re-trigger clarification (loop-termination guard).

## 3.5 Multilingual Text Output + Existing Hindi/English TTS (leave TTS as-is, add text routing)

Steps: 1. No change to the already-working Hindi ASR/TTS pipeline — leave it exactly as built. 2. Add a target_language selector in the Streamlit UI (Hindi / English / 2–3 others, e.g., Marathi, Tamil) that is passed into the Gemini prompt as an explicit output-language instruction — this requires no new model, just a prompt parameter and a UI dropdown. 3. Document clearly in-app (“Voice output available in Hindi/English; text advisory available in additional languages when online”) so the offline/online capability difference is honest and visible to the user, not a silent gap. 4. Test file: tests/test_language_routing.py — assert the prompt- building function correctly injects the selected language string; this doesn’t require actually calling the live


Gemini API in CI (mock the client).

## 4. Docker-Compose for Zone 2 (Owner: whoever finishes their Section 3 items first)

Steps: 1. Dockerfile for the FastAPI backend (Zone 2): standard slim Python base, install requirements.txt, expose the API port. 2. docker-compose.yml: one service for the FastAPI backend, mount the SQLite file and the FAISS index directory as volumes so data persists across container restarts, pass the Gemini API key via an environment variable / .env file (never hardcoded, never committed). 3. Confirm docker compose up gives a working backend that the Streamlit app (run separately, not containerized, to keep the demo simple) can hit — this is the only goal, not a production deployment. 4. No CI/CD, no k8s — this is documented as Phase 2/3 in PDF 1 §3.3, not attempted here.

## 5. Final Integration & Re-Test (last 3–4 hours of Day 2, both people)

- 1. Merge both feature branches into main.

- 2. Re-run the full pytest suite (original 38 + all new test files from Sections 2–4) — target: all green. Any red test is either fixed or the corresponding feature is feature-flagged off for the demo (never ship a red-tested feature live).

- 3. Run eval/run_eval.py one final time; save the report — this is a required artifact for both the PDF 1 credibility story and the actual submission.

- 4. Run the original plan’s “4 fixed Hindi sentences end-to-end” test, now extended to also cover: one deliber- ately blurry photo (expect reject), one safety-list condition case (expect forced cloud escalation regardless of confidence), one repeat farmer login showing farm history recall, and one clarification-loop trigger if that stretch item was built.

- 5. Record a short backup demo video in case of live connectivity failure during judging — this is standard hackathon risk mitigation and costs 15 minutes.

## 6. Explicit “Do Not Do” List for These 2 Days

To keep scope honest and prevent last-minute scope creep eating into testing time:

- Do not train any new neural network from scratch or fine-tune the task router — use the zero-train ensemble approach (Section 2.2).

- Do not add a second/third LLM call chain or any agent framework — one Gemini call + validator only.

- Do not implement real password hashing, OAuth, or session tokens — PIN-based demo login only, docu- mented gap.

- Do not attempt offline TTS for any language beyond Hindi/English.

- Do not integrate a VLM or swap any backbone model family.

- Do not build CI/CD or containerize anything beyond the single Zone 2 Docker-Compose file.

- Do not let the RAG knowledge base grow past ~40 entries without re-validating retrieval quality — bigger is not strictly better past this point for a demo-scale corpus, and the remaining time is better spent on the validator/eval harness (Section 3.3), which is the highest-leverage remaining item per PDF 1 §1.15.

See PDF 3 for the exact parallel work breakdown, dependency map, and function/interface names each person must expose for the other to consume.
