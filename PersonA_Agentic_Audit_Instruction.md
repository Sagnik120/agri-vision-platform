# AGENTIC INSTRUCTION PROMPT — Person A Codebase Audit, Pipeline Stress-Test & Unification Narrative Fix

**Target agent:** Claude Code (or equivalent coding agent) with full filesystem + shell access to the Person A (Zone 1) repository.
**Scope:** This instruction is for ONE person's codebase only — Person A, owner of Zone 1 (Capture & Quality Check, Task Router, Crop Expert, Livestock Expert, Sensor Expert, Text-Evidence Extractor, Fusion, Confidence & Safety Gate, Local Advisory, and the Streamlit surfaces Person A plugs into).
**Tone required from the agent:** No flattery, no reassurance-first language, no "great job" padding. Treat every finding as a defect until proven otherwise. If something works, say so in one line and move on — don't dwell on it. If something is fragile, mislabeled, hardcoded, stubbed, or inconsistent with the frozen data contract, say so explicitly, cite the file and line, and say what a judge would ask about it.

---

## 0. Non-Negotiable Ground Rules for the Agent

1. **Do not summarize without reading.** Every claim in every output file must be traceable to an actual file path + line range you opened. If you did not open the file, do not describe its behavior.
2. **Do not assume the plan was followed.** The build plan (`Agri_Vision_2Person_8Hour_Plan.docx`) is the *intended* design. The actual repo is the *ground truth*. Your job is to diff these two, not to describe the plan as if it were the code.
3. **Do not editorialize positively.** Words like "excellent," "impressive," "solid work," "well done" are banned from your outputs. Describe what exists, what it does, what breaks, and what a skeptical evaluator would say about it.
4. **Every module must be independently executed**, not just read. Static review is not sufficient — you must run scripts, feed them synthetic and edge-case inputs, and capture actual stdout/stderr/tracebacks.
5. **Two separate deliverables are required at the end** (see Sections 4 and 5). Do not merge them into one file.

---

## 1. Context to Load Before Starting

Load and hold in working memory:

- The literal SIH problem statement:
  > "Unified AI Agri-Vision Platform for Crop Advisory and Livestock Management. Marginal farmers often lack access to specialized veterinary and agricultural expertise through a single unified platform. Existing solutions are fragmented, requiring farmers to use separate systems for crop management and livestock monitoring, resulting in lower adoption and operational inefficiencies. Develop a digital platform that enables farmers to access crop disease identification, livestock monitoring, historical farm records, and actionable advisory services through an intuitive and accessible interface suitable for rural environments."
- The frozen Section 2 data contract (image expert output, ASR output, text evidence output, sensor output, fusion output, cloud request payload) — treat any deviation from these exact JSON shapes anywhere in Person A's code as a defect, not a stylistic choice.
- The known active issues at last checkpoint: livestock analysis not functioning correctly in Zone 1; Streamlit UI has no separate upload/analysis routes for crop vs. livestock; `streamlit_app.py` was being read when the last session ended.
- The core judging criteria this whole exercise is optimizing for: **"innovation" and "relevance to problem statement."** The single word that matters most is **fragmentation** — the problem statement's own complaint. Every downstream section of this instruction exists to make sure the demo visibly *kills* fragmentation instead of just demonstrating two disconnected detectors.

---

## 2. Phase 1 — Zone-and-Module-Wise Ground-Truth Audit

For each module below, the agent must:
(a) open every file that implements it,
(b) state what it actually does in 2–4 factual sentences,
(c) state the pretrained model / library actually loaded (name, source, checkpoint, param count if discoverable) — not what the plan says should be loaded,
(d) compare that against the plan's Section 1 tech-stack row and Section 3 hour-by-hour spec for the same module,
(e) mark status as one of: `MATCHES PLAN`, `DEVIATES FROM PLAN (describe how)`, `STUBBED/MOCKED`, `BROKEN`, `MISSING ENTIRELY`.

Modules to audit, in this order:

1. **Capture & Quality Check** (image ingestion, blur/exposure/size checks before inference)
2. **Task Router** (UI-driven crop/livestock dispatch per plan — confirm it is NOT a learned classifier; flag it if it silently became one, or if it's just an if/else with no visible "Detected task → Expert selected" trace)
3. **Crop Expert** (`crop_expert.py` or equivalent) — model identity, checkpoint source, preprocessing pipeline, output shape vs contract
4. **Livestock Expert** — same, and this is the KNOWN BROKEN module. Do not just say "broken." Run it directly with 3+ real or synthetic livestock images, capture the full traceback or the wrong-output pattern, and determine root cause: wrong checkpoint / wrong class mapping / preprocessing mismatch / label-relabeling gap called out in the plan ("if unavailable in time, use a general animal-health image classifier and clearly relabel classes") / import or shape error.
5. **Sensor Expert** (simulated values + threshold rules) — confirm no model is loaded (per plan, this should be pure rules); flag it if a model dependency crept in.
6. **Text-Evidence Extractor** — confirm it is deterministic dictionary matching (Hindi + English keyword map), not a model call; check the actual keyword dictionary against the plan's example set (भूरे धब्बे, पीली पत्तियां, सफेद पाउडर, पत्तियां मुड़, कीड़े, मुरझा) and report which of these exist, which are missing, which are silently different.
7. **Fusion Module** — verify the exact scoring rule from the plan is implemented: `score = visual_confidence; +0.10 if text supports; −0.20 if text conflicts; cap at 0.99`. Run it with hand-built inputs for all four combinations (support+high conf, support+low conf, conflict+high conf, conflict+low conf) and confirm output matches expected arithmetic exactly. Confirm output JSON shape matches the Section 2 fusion contract field-for-field, including `evidence_agreement` bucketing logic (what thresholds map to "high"/"medium"/"low" — this is NOT specified numerically in the plan, so if the code invented its own thresholds, flag that as an undocumented design decision a judge could probe).
8. **Confidence & Safety Gate** — verify the 3-input rule (model confidence, evidence agreement, input quality) and the `route='local'` vs `route='cloud'` branching threshold (plan says ~0.75). Flag the known cross-zone blocker: does `knowledge/kb_loader.py::get_safety_critical_conditions()` exist yet? If not, confirm exactly how the gate currently behaves in its absence (does it silently no-op the safety-critical check, hardcode a placeholder list, or crash?). This is a real landmine — a safety gate that can't actually check safety-critical conditions is a legitimate judge question about a platform advising farmers on livestock/crop health.
9. **Local Advisory** (`knowledge/local_advisories.json`) — count actual entries, list actual condition keys, compare against the plan's target list (tomato early/late blight, potato blight, maize rust, lumpy skin disease, FMD, abnormal temperature). Report gaps.
10. **Streamlit Integration (Person A's side)** — this is the other known-broken area. Read `streamlit_app.py` fully. Determine: is there one shared upload widget doing double duty for crop and livestock, or two distinct routes? Trace exactly what happens when a livestock image is uploaded through whatever the crop-shaped code path currently is. This is very likely the actual root cause tangled with the livestock bug — confirm or rule this out explicitly by tracing the call path, not by guessing.

**Output of Phase 1:** `zone1_pipeline_audit.md` — one section per module above, using the status taxonomy in step (e). End this file with a single markdown table: `Module | Status | File(s) | One-line risk`.

---

## 3. Phase 2 — Adversarial Pipeline Execution (Break It On Purpose)

The agent must now try to break the pipeline, not just run the happy path. For each of the following, actually execute and capture real output:

1. Run all 38 existing pytest tests fresh; report pass/fail counts and any skipped tests, and read the skipped/xfail ones — a judge asking "how many tests actually run" and getting "38 passing, but 6 are skipped" is a real risk if unexamined.
2. Run the existing 10-point diagnostic script end-to-end and capture full output, not a summary.
3. Feed the crop expert a livestock image and vice versa — confirm what the model does with out-of-domain input (confident wrong prediction is worse than a low-confidence one; report which happens).
4. Feed the fusion module conflicting/missing fields (e.g., `sensor_support: null` when domain is "crop") and confirm it doesn't crash — this exact null-handling path is explicitly in the Section 2 contract and easy to miss.
5. Simulate a low-connectivity failure for any Person-A-side call that assumes Person B's ASR text-evidence output is present — confirm graceful degradation exists, since "connectivity graceful degradation" was already flagged as a missing concern in prior architecture review.
6. Trace one full synthetic farmer session end-to-end through the actual code (not the plan): image in → expert → fusion → gate → advisory out. Print every intermediate JSON object actually produced, and diff each one against the Section 2 contract shape field-by-field.
7. Attempt the same trace for livestock specifically, since this is the one most likely to be live-demoed and questioned.

**Output of Phase 2:** append a `## Adversarial Test Log` section to the same `zone1_pipeline_audit.md`, with real captured stdout/tracebacks in fenced code blocks, not paraphrased descriptions.

---

## 4. Phase 3 — The Unification Fix (This Is the Actual Point of the Exercise)

Everything above exists to support this section. The problem statement's complaint is **fragmentation**: farmers juggling separate crop and livestock *systems*. A demo that shows "here's crop detection, and separately, here's livestock detection" **restates the problem instead of solving it**. The fix is cheap and mostly a scripting/UI-flow change, not new modeling work. The agent must produce a concrete, buildable plan (and, where in Person A's control, actual code) for the following:

### 4.1 One login / one farmer identity
- Confirm (via Zone 3 SQLite schema, even though Person B owns it) that a single `farm_id` is the anchor for both crop and livestock records, not two parallel tables the UI happens to render side by side.
- If Person A's code ever branches farmer identity by domain (e.g., separate session state for "crop farmer" vs "livestock farmer"), flag it as a fragmentation leak and fix it: one `farm_id` in Streamlit session state, used identically by both flows.

### 4.2 One history timeline, not two
- Verify (or specify, if missing) that `get_farm_history(farm_id)` returns a single interleaved timeline mixing crop and livestock events chronologically, not two separate lists the UI concatenates under separate headers.
- Specify the exact UI component: a single "My Farm Timeline" panel, sortable by date, with a domain tag (🌾 crop / 🐄 livestock) per row — visually proving one record store, two domains, at a glance.

### 4.3 One advisory flow, not two code paths that happen to look similar
- Confirm the fusion → confidence gate → (local advisory OR cloud/Gemini) path is **one function signature** that takes a `domain` parameter, not two near-duplicate functions (`handle_crop()` / `handle_livestock()`) that drifted apart — this drift is very likely *why* livestock is currently broken while crop works. Specify a refactor target: a single `run_advisory_pipeline(domain: str, evidence: dict) -> AdvisoryResult` that both domains call identically, with domain-specific behavior isolated only inside the expert-selection step.

### 4.4 The 60-second demo script (write this out verbatim, cue by cue)
Produce an actual word-for-word presenter script, timed, that makes unification the headline claim in the first 15 seconds, not an afterthought at the end. Structure:
- 0:00–0:15 — Presenter states the fragmentation problem in the judges' own language ("farmers today run one app for crops, a different app or vet visit for livestock — we built one farmer, one login, one history, one advisory engine for both"), while the screen shows the single login + single timeline view with both a crop and a livestock entry already present from a prior session.
- 0:15–0:35 — Live crop upload → local decision, but the presenter explicitly narrates "this writes to the same farm record as livestock" and glances at the timeline updating.
- 0:35–0:55 — Live livestock upload (or sensor input) → cloud escalation path → presenter explicitly says "different domain, same login, same history, same advisory format" and shows the timeline now has both entries interleaved.
- 0:55–1:00 — Close on the single timeline view, not on a disease label. The last thing judges see must be the unification, not a diagnosis.
- Include exact on-screen labels/copy the agent should hardcode into the Streamlit demo build (banner text, tab labels, timeline header) so the visual matches the script word-for-word.

**Output of Phase 3:** `unification_fix_and_demo_script.md` containing 4.1–4.4, plus any concrete code diffs Person A can make within Zone 1 + Streamlit to support it (e.g., the refactor target function signature, the timeline component sketch). If a needed change is on Person B's side (e.g., timeline query), state that explicitly as a dependency and hand-off note rather than attempting to write Zone 2/3 code.

---

## 5. Gemini API Call Specification (Document, Don't Re-decide)

Since Person A's confidence gate decides `route='cloud'`, the agent must document — precisely, for defense in Q&A — the actual Gemini call Person B's code makes when that route fires, from Person A's side of the contract outward:

- Exact model string currently called in code (open the actual client file, do not assume — report the literal string, e.g. `gemini-2.5-flash` or whatever is hardcoded).
- State the tradeoff reasoning that should justify that choice in a live Q&A: latency budget for a rural low-bandwidth 2G/3G session vs. reasoning quality needed to avoid inventing dosages/diagnoses. If the code is calling a heavier model than the connectivity story justifies, flag this as a contradiction a judge could catch ("you said 2G-friendly, but you're calling your largest model for every cloud escalation").
- Confirm whether the system prompt enforces the safety constraints from the plan (never invent diagnoses/dosages, distinguish possible vs. confirmed, say so if evidence insufficient, recommend expert consultation) — quote the actual system prompt string from the file, don't paraphrase it.
- Confirm the cloud request payload sent to Gemini matches the Section 2 contract exactly, field for field, including `retrieved_knowledge` actually being populated by RAG output and not an empty string placeholder.

Add this as a section inside `zone1_pipeline_audit.md` titled `## Cloud Escalation Contract Verification (Person A's Outbound Side)`.

---

## 6. Phase 4 — The Harsh-Judge Critique File (Second, Separate Deliverable)

Produce a second, standalone file: `harsh_judge_review.md`. Rules for this file specifically:

- Write as a skeptical SIH evaluation panel member who has seen dozens of "AI for agriculture" pitches and is tired of vague claims. No encouragement. No softening phrases like "this is a minor issue" — state severity plainly.
- For every finding from Phases 1–3, convert it into an actual question format a judge would ask live, e.g.: *"Your safety gate claims to check safety-critical conditions before allowing a local-only decision — but `get_safety_critical_conditions()` doesn't exist yet. What happens right now if a farmer's cow has a condition that should never be auto-resolved offline?"*
- Group findings under three headings: **Architecture risk**, **Implementation risk**, **Narrative/relevance risk** (this last one specifically scores against "relevance to problem statement" — call out anywhere the demo *shows* two systems instead of one, even if the backend is technically unified).
- End with a single scored table:

| Category | Score /10 | One-line justification |
|---|---|---|
| Technical depth | | |
| Working demo reliability | | |
| Relevance to problem statement (fragmentation solved, not restated) | | |
| Innovation / differentiation | | |
| Presentation readiness | | |
| **Overall** | **/10** | |

- Scores must be justified by evidence gathered in Phases 1–3, not vibes. A module marked `BROKEN` in the audit must visibly depress the "working demo reliability" score, with the specific broken module named.
- Close the file with a prioritized fix list, ranked by (judge-question likelihood × effort to fix), cheapest-and-most-visible fixes first — the unification scripting fix from Phase 3 should rank at or near the top given it is explicitly low-effort/high-signal.

---

## 7. Final Deliverables Checklist

The agent's run is only complete when all four files exist and are internally consistent with each other (no finding in the harsh review that contradicts the audit):

1. `zone1_pipeline_audit.md` — Phase 1 module-by-module audit + Phase 2 adversarial execution log + Phase 5 Gemini contract verification, all in one file.
2. `unification_fix_and_demo_script.md` — Phase 3 in full, including the verbatim timed script and concrete code/refactor targets.
3. `harsh_judge_review.md` — Phase 4 in full, ending in the scored table and prioritized fix list.
4. A short top-level `README_AUDIT_SUMMARY.md` (max ~20 lines) linking the three files above, stating in plain language: what's currently broken, what's the single highest-leverage fix before the demo, and the overall score from file 3.

Do not proceed to writing new feature code until this audit-and-critique cycle is complete and Sagnik has reviewed the findings.
