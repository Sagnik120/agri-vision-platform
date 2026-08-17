# AGRI-VISION PLATFORM — 8-HOUR PARALLEL IMPLEMENTATION PLAN
### Single combined instruction file for Antigravity agents — Person A + Person B

**Repo:** `https://github.com/Sagnik120/agri-vision-platform`
**Owner / Person A:** GitHub `Sagnik120` · HF `Sagnik120` · Kaggle `chandrasagnik027` — **65–75% of work**
**Contributor / Person B:** GitHub `svj31` — **remaining work**
**Time budget:** 8 hours, both people working in parallel from the same commit.
**Base state:** Zone 1 (`src/zone1_edge/`) complete, 38 passing tests, 10/10 diagnostic checks. Zone 2/3 (`src/zone2_cloud/`, `src/zone3_memory/`) scaffolded, not implemented.
**Source plan this file compresses:** `2_Prototype_Implementation_Plan.md` (the original 2-day plan). Everything below is that plan re-scoped, re-sequenced, and re-timed to fit 8 hours with two AI coding agents doing the actual typing.

> **READ THIS ENTIRE FILE BEFORE WRITING ANY CODE.** This file is the single source of truth for both agents. If you are the Person A agent, read your sections plus every "Person B" section so you know what shape of data is coming. If you are the Person B agent, read your sections plus every "Person A" section. Do not start Phase 1 work until you have read Sections 0–3 in full.

---

## 0. NON-NEGOTIABLE RULES (read first, apply for all 8 hours)

1. **Never break `main`.** `main` must be runnable and pass its existing test suite at every point in time. All new work happens on a feature branch. `main` only receives fast-forward or clean merges of already-tested code.
2. **Never train a model.** Search Hugging Face / Kaggle for an existing small/pretrained model first. If a fine-tuned checkpoint doesn't exist, use a general-purpose pretrained model and relabel/wrap it — do not run a training loop. Every model used must be logged in `docs/MODELS_USED.md` (see Section 8) with: HF/Kaggle repo id, parameter count, quantization/precision used, why it was chosen, and the exact loading code path.
3. **Additive contract changes only.** `contract.md` may only gain new optional fields in this 8-hour window. Never rename or remove an existing field — that breaks the other person's in-progress code silently.
4. **Every module gets two scripts, not one:**
   - a **unit diagnostic script** (or pytest file) that proves that module works in isolation, run immediately after writing it;
   - a **full pipeline diagnostic script** (`setup/diagnose_pipeline.py`, already exists — EXTEND it, do not replace it) that proves the *whole* pipeline still imports, runs end-to-end on mock data, and produces contract-shaped output, run immediately before every commit that touches shared interfaces.
   No commit to a shared branch happens without both scripts passing.
5. **Commit small, commit often, push often.** Target one commit per completed sub-task (roughly every 30–45 minutes), not one giant commit at the end. This is what makes merges safe — small diffs conflict less and are easy to reason about.
6. **Progress and issues are logged continuously, not at the end.** Update `docs/new_process.md` and `docs/pipeline_issues.md` after every completed task, not in a final batch (see Section 8 for exact format).
7. **If a dependency isn't ready yet, do not block — switch to an independent task.** See Section 4 (Dependency & Handshake Protocol) for exactly what to do while waiting.
8. **Correctness over completeness.** If the 8 hours run out, a smaller set of fully-working, fully-tested features beats a larger set of half-working ones. Section 9 gives the exact drop order if time runs short — follow it, do not improvise a different cut.

---

## 1. WHAT WAS DROPPED TO FIT 8 HOURS (vs. the original 2-day / 15-item plan)

The original plan had ~4.5–5.5 person-days of ADOPT-scoped work. Eight hours total (shared across 2 people, roughly 6–7 productive hours each after setup/integration/testing overhead) is roughly 1.5–2 person-days — **not everything fits.** The following items from `2_Prototype_Implementation_Plan.md` are explicitly **OUT OF SCOPE for today** and must not be attempted unless every other item in this file is done, tested, merged, and there is still time left (see Section 9's stretch order):

- Embedding-based text-evidence fusion (multilingual sentence-transformer) — the symbolic/keyword path only, today.
- Docker-Compose for Zone 2 — documented as a next step in `docs/new_process.md`, not built today.
- Bounded clarification loop — stretch only, last item in Section 9.
- Multilingual text output beyond Hindi/English — stretch only.
- Explainability Grad-CAM heatmap — top-3 + reason-string display only today (cheap); the heatmap overlay is stretch only.
- Device-tier gating logic beyond a hardcoded stub — a `get_device_tier()` function that returns a fixed value is enough today; do not build real capability probing.

Everything else below is in scope and must be completed and merged today.

---

## 2. FINAL FOLDER STRUCTURE (build this FIRST, before any feature code, exactly as shown)

Both agents must create this exact structure on `main` (or the first shared setup commit) before splitting into branches. This is the boilerplate both people build against — it prevents folder-level merge conflicts because every new file already has an agreed home.

```
agri-vision-platform/
├── contract.md                                  # UPDATED today (Section 3) — additive only
├── requirements.txt                             # UPDATED today — both people append here (see Section 4 rule on shared files)
├── .env.example                                 # UPDATED if new env vars are needed (Gemini key already present)
├── docs/
│   ├── PROGRESS.md                               # existing — do not touch today
│   ├── new_process.md                            # NEW — living progress log (Section 8)
│   ├── pipeline_issues.md                        # NEW — living issues/fix-needed log (Section 8)
│   └── MODELS_USED.md                            # NEW — model registry (Section 0, rule 2)
├── setup/
│   ├── setup_venv.sh                             # existing, untouched
│   ├── download_crop_model.py                    # existing, untouched
│   ├── download_livestock_model.py               # existing, untouched
│   └── diagnose_pipeline.py                      # EXTENDED today by both people (additive checks only, see Section 5)
├── src/
│   ├── zone1_edge/                               # PERSON A — primary owner
│   │   ├── config.py                             # MODIFIED — add get_device_tier() stub
│   │   ├── experts/
│   │   │   ├── crop_expert.py                    # untouched (existing, working)
│   │   │   └── livestock_expert.py                # untouched (existing, working)
│   │   ├── quality/                              # NEW folder
│   │   │   └── quality_check.py                  # NEW — Task A1
│   │   ├── multimodal/
│   │   │   ├── text_evidence.py                  # MODIFIED — Task A3
│   │   │   ├── sensor_expert.py                  # MODIFIED — Task A2
│   │   │   ├── fusion.py                         # MODIFIED — Task A3 consumer + Task A2 consumer
│   │   │   └── confidence_gate.py                # MODIFIED — Task A4
│   │   ├── task_router/
│   │   │   └── task_router.py                    # MODIFIED — Task A5 (adds auto_route, keeps existing manual route)
│   │   ├── explainability/                       # NEW folder
│   │   │   └── explainability.py                 # NEW — Task A6
│   │   ├── knowledge/
│   │   │   ├── local_advisories.json              # MODIFIED by Person B primarily (Task B1), Person A reads only
│   │   │   ├── local_advisory.py                  # untouched
│   │   │   └── kb_loader.py                       # NEW — written by PERSON B first (Task B0, hard blocking dependency), consumed by Person A (Task A4)
│   │   ├── demo_data/                             # existing, add fixtures if needed (blurry/dark test images — Task A1)
│   │   └── pipeline.py                            # MODIFIED — wires quality_check + auto_route + explainability into orchestration (Task A7)
│   ├── zone2_cloud/                               # PERSON B — primary owner
│   │   ├── asr/hindi_asr.py                       # existing/stub — untouched today unless already broken
│   │   ├── tts/hindi_tts.py                       # existing/stub — untouched today unless already broken
│   │   ├── gemini/
│   │   │   ├── gemini_client.py                   # MODIFIED — Task B3 (strip_pii, safety prompt), Task B4 (validator wiring)
│   │   │   └── validator.py                       # NEW — Task B4
│   │   └── rag/
│   │       ├── build_knowledge_base.py             # MODIFIED — re-run after KB expansion (Task B1)
│   │       ├── retriever.py                       # untouched unless KB schema change requires it
│   │       └── knowledge_base/                     # MODIFIED — expanded entries (Task B1)
│   ├── zone3_memory/                              # PERSON B — primary owner
│   │   ├── db/
│   │   │   ├── farm_memory.py                     # MODIFIED — Task B2 (farmer_id scoping)
│   │   │   └── auth.py                            # NEW — Task B2 (login)
│   │   └── schema/schema.sql                       # MODIFIED — Task B2 (pin column, farmer_id indices)
│   └── app/
│       └── streamlit_app.py                        # MODIFIED by BOTH — see Section 4's file-ownership rule for shared files
├── tests/
│   ├── zone1/
│   │   ├── (38 existing tests — untouched, must stay green)
│   │   ├── test_quality_check.py                  # NEW — Task A1
│   │   ├── test_sensor_expert.py                  # MODIFIED/extended — Task A2
│   │   ├── test_fusion.py                         # MODIFIED/extended — Task A3
│   │   ├── test_confidence_gate.py                # MODIFIED/extended — Task A4
│   │   ├── test_task_router.py                    # MODIFIED/extended — Task A5
│   │   └── test_explainability.py                 # NEW — Task A6
│   ├── zone2/
│   │   ├── test_rag_kb.py                         # NEW — Task B1
│   │   ├── test_validator.py                       # NEW — Task B4
│   │   └── test_gemini_client.py                   # NEW/extended — Task B3
│   └── zone3/
│       ├── test_auth.py                           # NEW — Task B2
│       └── test_memory.py                         # MODIFIED/extended — Task B2
├── eval/                                          # NEW folder — PERSON B
│   ├── gold_set.json                              # NEW — Task B5
│   └── run_eval.py                                # NEW — Task B5
└── results/
    └── (existing structure, untouched — both people write run logs here per their zone)
```

**Rule for shared files** (`streamlit_app.py`, `requirements.txt`, `contract.md`, `setup/diagnose_pipeline.py`): these are the only files both people touch. To avoid conflicts:
- `requirements.txt` and `contract.md`: edited ONLY during the Hour-0 joint setup commit (Section 3). After that, if either person needs a new line, they add it to the **bottom** of the file in their own commit and immediately push+pull — never edit an existing line the other person added.
- `streamlit_app.py`: Person A owns the Crop/Livestock/Auto-detect tab bodies and the quality/explainability widgets. Person B owns the login gate (wraps the whole app) and the language/cloud-escalation panel. **Concretely: Person A only edits inside `# === ZONE1_UI_START ===` / `# === ZONE1_UI_END ===` markers; Person B only edits inside `# === ZONE2_ZONE3_UI_START ===` / `# === ZONE2_ZONE3_UI_END ===` markers.** Both markers are added in the Hour-0 setup commit (Section 3) so this boundary exists before either person starts editing. Never edit outside your own marker block.
- `setup/diagnose_pipeline.py`: each person only **appends** a new check function and registers it in the check list at the bottom — never edit an existing check function the other person wrote.

---

## 3. HOUR 0 (0:00–0:20) — JOINT SETUP, BOTH PEOPLE TOGETHER, BEFORE SPLITTING

Do this together (or one person does it and the other reviews the diff within 5 minutes) — this is the shared foundation everything else depends on.

1. `git checkout main && git pull && git tag pre-improvement-baseline-8hr && git push --tags`
2. Run the existing suite: `AGRIVISION_EXPERT_MODE=mock pytest tests/zone1 -v` — confirm 38/38 green. If not green, STOP and fix before proceeding; do not build on a red baseline.
3. Create the new empty folders/files from Section 2's structure that don't exist yet (`src/zone1_edge/quality/`, `src/zone1_edge/explainability/`, `src/zone2_cloud/gemini/validator.py` stub, `src/zone3_memory/db/auth.py` stub, `eval/`, `docs/new_process.md`, `docs/pipeline_issues.md`, `docs/MODELS_USED.md`) with minimal placeholder content (a docstring + `pass`) so both branches start from identical file trees.
4. Add the UI ownership markers into `src/app/streamlit_app.py` (Section 2's rule) at the appropriate existing locations — Person A's tabs get `ZONE1_UI_START/END`, the login/escalation panel area gets `ZONE2_ZONE3_UI_START/END`.
5. Append the additive `contract.md` fields (exact text in Section 3.1 below).
6. Commit as **one single commit** directly to `main`: `git commit -m "chore: 8hr-sprint scaffolding — folders, UI markers, contract additions" && git push origin main`.
7. **Now create the two branches from this exact commit:**
   - Person A: `git checkout -b feature/zone1-8hr-sprint && git push -u origin feature/zone1-8hr-sprint`
   - Person B: `git checkout -b feature/zone2-zone3-8hr-sprint && git push -u origin feature/zone2-zone3-8hr-sprint`
8. Both agents confirm: `AGRIVISION_EXPERT_MODE=mock python setup/diagnose_pipeline.py --mode mock` passes on their own branch before writing any feature code.

### 3.1 Exact `contract.md` additions (paste verbatim, additive only)

```markdown
## Additive fields — 8-hour sprint (do not remove/rename existing fields)

### Image expert output — gains:
- "quality_score": float        # 0.0-1.0, from quality_check.py
- "quality_flag": "ok" | "warn" | "reject"

### Fusion output — gains:
- "threshold_used": float
- "threshold_reason": [str, ...]
- "advisory_tier": "confident" | "possible" | "refer_expert"

### Sensor output — new top-level shape (replaces old flat dict, still domain="livestock"):
{
  "domain": "livestock",
  "temperature": float,
  "activity": str,
  "feed_intake": str,
  "anomaly": bool,
  "trend": "rising" | "falling" | "stable",
  "candidates": [
    {"condition": str, "score": float, "first_aid": [str, ...]}
  ]
}

### Cloud request payload — gains:
- "farmer_id": str
- "advisory_tier": str            # passed through from fusion/confidence_gate output

### New shared function contract (hard dependency, Person B writes first):
knowledge/kb_loader.py :: get_safety_critical_conditions() -> set[str]
  Reads `is_safety_critical: bool` from knowledge base entries and returns
  the set of condition keys flagged true. Both Zone 1 (confidence_gate.py)
  and Zone 2 (gemini prompt / validator) import this — never hardcode a
  duplicate list anywhere else.
```

---

## 4. DEPENDENCY & HANDSHAKE PROTOCOL (read carefully — this prevents blocking)

### 4.1 The one hard blocking dependency

**`src/zone1_edge/knowledge/kb_loader.py::get_safety_critical_conditions() -> set[str]`** is written by **Person B**, in the **first 40 minutes**, and is required by **Person A's Task A4** (confidence gate). This is the only cross-person function-level dependency in the whole plan.

**Handshake procedure:**
1. Person B writes `kb_loader.py` with a working `get_safety_critical_conditions()` against a small seed set (5–6 conditions is enough — it does not need the full 25–40 entry KB expansion yet) within the first 40 minutes, commits, and pushes to `feature/zone2-zone3-8hr-sprint`.
2. Person B posts (in whatever channel you use — Slack/WhatsApp/a shared doc) the exact line: **"kb_loader ready — branch feature/zone2-zone3-8hr-sprint, commit <hash>"**.
3. Person A, when reaching Task A4 (should be around Hour 2), checks: has that message arrived?
   - **If yes:** `git fetch origin feature/zone2-zone3-8hr-sprint && git checkout origin/feature/zone2-zone3-8hr-sprint -- src/zone1_edge/knowledge/kb_loader.py` (cherry-pick just that one file into your own branch), then continue Task A4.
   - **If no:** do not wait idle. Reorder your own task list — skip ahead to Task A5 (task router) or Task A6 (explainability), both of which have zero dependency on Person B's work, and come back to Task A4 once the file is available. Check again after each subsequent task you complete.
4. Symmetric rule for Person A → Person B: Person A's `src/zone1_edge/multimodal/fusion.py` output shape (with the new `advisory_tier`/`threshold_reason` fields) is needed by Person B's `eval/run_eval.py` (Task B5, which needs the *whole* Zone 1 pipeline working to run end-to-end evals) and by the Streamlit cloud-escalation panel (shared file, Person B's marker block). Person A should push a **working, tested** `fusion.py` + `confidence_gate.py` by the **Hour 4 integration checkpoint** (Section 6) at the latest. If Person B reaches Task B5 before that checkpoint, Person B works on Task B1–B4 first (all independent of Zone 1) and only attempts Task B5 after Hour 4.

### 4.2 General rule when blocked

If you are ever blocked on a specific file from the other person that hasn't landed yet:
1. Do not wait passively for more than ~10 minutes.
2. Re-check your own task list for anything with zero cross-person dependency (most tasks below are marked "no dependency" — do those first if blocked).
3. If truly nothing independent remains, write the function signature and a mocked/stub return value yourself (matching the agreed contract shape exactly), write your code against the stub, and note in `docs/pipeline_issues.md` "TEMPORARY STUB: replace `kb_loader.get_safety_critical_conditions()` mock with real import once available" — then swap the real import in as soon as it lands. This keeps you moving without producing incorrect final code.

---

## 5. PERSON A — TASK LIST (Zone 1), TIME-BOXED

**Branch:** `feature/zone1-8hr-sprint`. Push after every completed + tested task (not just at the end).

### Task A1 — Capture Quality Check (0:20–1:10, 50 min) — NO DEPENDENCY
**Files:** new `src/zone1_edge/quality/quality_check.py`, new `tests/zone1/test_quality_check.py`
**Do:**
1. Add `opencv-python-headless` to the bottom of `requirements.txt`, `pip install -r requirements.txt`.
2. Implement `compute_blur_score(img: np.ndarray) -> float` (Laplacian variance on a resized max-512px grayscale copy).
3. Implement `compute_exposure_score(img: np.ndarray) -> float` (fraction of pixels in extreme luminance bins).
4. Implement `compute_quality(img: np.ndarray) -> dict` returning `{"quality_score": float, "quality_flag": "ok"|"warn"|"reject", "reasons": [str,...]}`. Start with `quality_score = 0.6*blur_norm + 0.4*exposure_norm`; `reject` if `<0.4`, `warn` if `0.4–0.6`, `ok` if `>0.6`.
5. In `demo_data/`, generate 2–3 test fixtures: take one existing sharp sample image, produce a Gaussian-blurred copy and an over/under-exposed copy programmatically (a short one-off script or inline in the test file using `cv2.GaussianBlur` / brightness scaling — do not need real new photos).
6. Write `test_quality_check.py`: sharp image → `ok`; blurred copy → `reject`; over/under-exposed copy → `reject` or `warn`. 4–6 tests.
**Diagnostic (unit):** `pytest tests/zone1/test_quality_check.py -v` — must be 100% green before moving on.
**Diagnostic (pipeline):** append a check to `setup/diagnose_pipeline.py`: `check_quality_module()` — imports `compute_quality`, runs it on a fixture image, asserts the returned dict has all three required keys with correct types. Run `python setup/diagnose_pipeline.py --mode mock` — must still fully pass.
**Commit:** `git add -A && git commit -m "feat(zone1): capture quality check module + tests" && git push`

### Task A2 — Sensor Feature/Rule Upgrade (1:10–1:55, 45 min) — NO DEPENDENCY
**Files:** modify `src/zone1_edge/multimodal/sensor_expert.py`, modify `tests/zone1/test_sensor_expert.py`
**Do:**
1. Replace the flat simulated dict with a small generator sampling temperature around 38.5°C ± noise, with an `anomaly_mode: bool` parameter for demo control.
2. Add a 2-reading trend check (`trend: "rising"|"falling"|"stable"`) — store the previous reading in a simple in-memory/session cache passed in as an argument (do not introduce global state — pass `previous_reading: dict|None` as a function argument so it stays pure/testable).
3. Implement `top_k_first_aid(sensor_reading: dict, trend: str) -> list[dict]` returning up to 3 ranked `{"condition": str, "score": float, "first_aid": [str,...]}` entries from a small hand-written mapping. First-aid text must be **generic and safe only** (isolate, shade/water, monitor, no medication without vet confirmation) — never a drug name.
4. Update the function that assembles the final sensor output dict to match the new contract shape from Section 3.1 exactly (`domain`, `temperature`, `activity`, `feed_intake`, `anomaly`, `trend`, `candidates`).
5. Update `fusion.py`'s sensor-consuming code path to read the new shape (`candidates` list instead of whatever old shape existed) — grep the codebase for every place that reads sensor output and update all call sites in the same commit, not just fusion.py, so nothing is left reading a stale shape.
**Diagnostic (unit):** extend `test_sensor_expert.py` — trend detection over 2 synthetic readings; `top_k_first_aid` returns 1–3 non-empty candidates; a keyword-denylist test asserting no first-aid string contains a drug-name-like token (simple regex/word list check).
**Diagnostic (pipeline):** append `check_sensor_module()` to `diagnose_pipeline.py` — run the full sensor→fusion path on mock data, assert the final fusion output doesn't crash on the new sensor shape.
**Commit:** `git commit -m "feat(zone1): sensor expert trend detection + top-k first aid" && git push`

### Task A3 — Text Evidence Fusion Expansion (1:55–2:35, 40 min) — NO DEPENDENCY (embedding path is OUT OF SCOPE today per Section 1 — symbolic only)
**Files:** modify `src/zone1_edge/multimodal/text_evidence.py`, modify `src/zone1_edge/multimodal/fusion.py`, modify `tests/zone1/test_fusion.py`
**Do:**
1. Expand the Hindi/English symptom keyword dictionary from its current size to at least 20–25 entries — add terms for whatever conditions exist in the current `local_advisories.json` today (do not wait on Person B's KB expansion; add terms for what's already there, and it's fine if Person B's later KB expansion adds a few conditions this dictionary doesn't cover yet — note any gap in `docs/pipeline_issues.md`).
2. Keep the existing `+0.10` (supports) / `-0.20` (conflicts) rule exactly as-is — do NOT build the embedding-similarity blend today (explicitly out of scope, Section 1). Just widen the dictionary coverage.
3. In `config.py`, add a stub `get_device_tier() -> str` returning a hardcoded `"medium"` — this is intentionally a stub today (Section 1), just needs to exist so any code that will read it later doesn't break, and so the architecture story in `docs/new_process.md` can note it's stubbed.
**Diagnostic (unit):** extend `test_fusion.py` with 3–4 new symptom-phrase test cases exercising the expanded dictionary.
**Diagnostic (pipeline):** re-run existing `diagnose_pipeline.py` fusion check (already exists) — confirm still green with the expanded dictionary.
**Commit:** `git commit -m "feat(zone1): expand text-evidence symptom dictionary" && git push`

### Task A4 — Dynamic Confidence & Safety Gate (2:35–3:35, 60 min) — **DEPENDS ON `kb_loader.py` FROM PERSON B (see Section 4.1)**
**Files:** modify `src/zone1_edge/multimodal/confidence_gate.py`, modify `tests/zone1/test_confidence_gate.py`
**Do:**
1. Check the Section 4.1 handshake — pull `kb_loader.py` if ready, else stub `get_safety_critical_conditions()` locally returning a hardcoded small set and note the stub in `docs/pipeline_issues.md`, then swap to the real import the moment it's available (do this swap before your final commit of this task if at all possible).
2. Replace the fixed scalar threshold with: `threshold = 0.75 + delta_quality + delta_agreement + delta_domain - delta_history_match`, clipped to `[0.60, 0.90]`. `delta_history_match` can be hardcoded to `0` today (Zone 3 farm-history coupling is out of scope for 8 hours) — just leave the term in the formula for documentation/future-wiring purposes.
3. Add the safety-list override: if predicted condition is in `get_safety_critical_conditions()`, force `route="cloud"` and cap `advisory_tier` at `"possible"` regardless of numeric confidence.
4. Populate `threshold_reason: [str,...]` with human-readable strings for whichever deltas fired.
5. Assign `advisory_tier` per the 3-tier ladder: confident / possible / refer_expert (exact rule as in the source plan §2.5 step 4).
**Diagnostic (unit):** extend `test_confidence_gate.py` — table-driven: safety-list override fires regardless of confidence; low quality raises threshold; high agreement lowers it; tier assignment correctness for constructed input combos. Minimum 6 test cases.
**Diagnostic (pipeline):** append `check_confidence_gate_safety_override()` to `diagnose_pipeline.py` — construct a mock high-confidence prediction for a known safety-list condition, assert it still routes to cloud.
**Commit:** `git commit -m "feat(zone1): dynamic confidence gate + safety-list override + advisory tiering" && git push`

### Task A5 — Zero-Train Dual-Backbone Task Router (3:35–4:05, 30 min) — NO DEPENDENCY
**Files:** modify `src/zone1_edge/task_router/task_router.py`, modify `tests/zone1/test_task_router.py`
**Do:**
1. Add `auto_route(img) -> dict`: run both existing crop and livestock experts' forward pass once each, compute softmax entropy for each (`entropy = -sum(p*log(p))`), pick the domain with higher max-confidence (primary signal) using entropy only as a tie-breaker/sanity note in the returned dict.
2. Keep the existing manual Crop/Livestock selection path completely untouched — `auto_route` is an additional function, called only from a new "Auto-detect" tab, never replacing the manual buttons.
3. Do not modify `crop_expert.py` or `livestock_expert.py` internals — only call their existing public inference functions.
**Diagnostic (unit):** extend `test_task_router.py` — using existing crop/livestock fixture images, assert `auto_route` picks the correct domain on at least 4 clear cases and returns both raw scores.
**Diagnostic (pipeline):** re-run `diagnose_pipeline.py` — confirm existing manual-route checks are unaffected (they must be, since this task doesn't touch that code path).
**Commit:** `git commit -m "feat(zone1): zero-train dual-backbone auto task router" && git push`

### Task A6 — Explainability (Lightweight Version Only Today) (4:05–4:45, 40 min) — NO DEPENDENCY
**Files:** new `src/zone1_edge/explainability/explainability.py`, new `tests/zone1/test_explainability.py`
**Do:**
1. Implement `format_top3(top_k: list) -> dict` — trivial passthrough/formatting of the existing `top_k` contract field for display.
2. Implement `format_reason(threshold_reason: list[str], advisory_tier: str) -> str` — joins the reason list from Task A4 into a single readable sentence.
3. **Grad-CAM heatmap is OUT OF SCOPE today** (Section 1, stretch-only — see Section 9 if time remains at the end). Do not attempt it now; leave a clearly marked `# TODO (stretch, see Section 9): grad-cam overlay` comment in the file instead.
**Diagnostic (unit):** `test_explainability.py` — assert `format_top3` and `format_reason` produce correctly structured/non-empty output on constructed inputs.
**Diagnostic (pipeline):** none needed beyond the unit test — this module has no other consumers today besides the UI.
**Commit:** `git commit -m "feat(zone1): explainability text formatting (top-3, reason string)" && git push`

### Task A7 — Wire Everything Into `pipeline.py` + Streamlit (Person A's marker block) (4:45–5:45, 60 min) — NO EXTERNAL DEPENDENCY (uses only Person A's own new modules)
**Files:** modify `src/zone1_edge/pipeline.py`, modify `src/app/streamlit_app.py` (**ONLY inside the `ZONE1_UI_START`/`END` markers**)
**Do:**
1. In `pipeline.py`, insert `quality_check.compute_quality()` as the first step; if `quality_flag == "reject"`, short-circuit and return the reject message, never call any expert.
2. Wire `auto_route` as the default path for a new "Auto-detect" flow, alongside the existing manual Crop/Livestock flows (all three remain selectable).
3. Wire the upgraded sensor/fusion/confidence_gate outputs through to the final pipeline return value, matching the Section 3.1 contract exactly.
4. In Streamlit (marker block only): add the reject/warn UX (clear message + "Retake Photo" button clearing the uploader state on reject; non-blocking banner on warn), add the Auto-detect tab, add a small explainability panel showing top-3 + reason string.
**Diagnostic (full pipeline):** `AGRIVISION_EXPERT_MODE=mock python setup/diagnose_pipeline.py --mode mock` — must be 100% green, covering every check function added by Tasks A1–A6.
**Diagnostic (full test suite):** `AGRIVISION_EXPERT_MODE=mock pytest tests/zone1 -v` — all original 38 + every new test from A1–A6 must pass, zero regressions.
**Commit:** `git commit -m "feat(zone1): wire quality/auto-route/explainability into pipeline + UI" && git push`

### Task A8 — Buffer, Integration Support, Final Re-test (5:45–8:00) — see Section 6 & 7
Use remaining time for: the Hour-6 integration checkpoint (Section 6), fixing anything found there, supporting Person B if they're blocked on Zone 1 output shapes, and the final joint re-test (Section 7). If genuinely finished early, proceed to Section 9's stretch list in order.

---

## 6. PERSON B — TASK LIST (Zone 2 + Zone 3), TIME-BOXED

**Branch:** `feature/zone2-zone3-8hr-sprint`. Push after every completed + tested task.

### Task B0 — `kb_loader.py` (0:20–1:00, 40 min) — **HARD BLOCKING DEPENDENCY FOR PERSON A, DO THIS FIRST**
**Files:** new `src/zone1_edge/knowledge/kb_loader.py`, minimal seed additions to `local_advisories.json` if needed
**Do:**
1. Add `is_safety_critical: bool` to at least 5–6 existing `local_advisories.json` entries (a correct seed set — pick genuinely notifiable/contagious conditions like FMD, lumpy skin disease if present in the current KB; if not present yet, add minimal correct entries now, expand fully in Task B1).
2. Implement `get_safety_critical_conditions() -> set[str]` reading this flag from the KB file and returning the matching condition keys.
3. **Immediately push and announce per Section 4.1's handshake procedure** — this is the single highest-priority task in the whole 8 hours for unblocking Person A.
**Diagnostic (unit):** a quick inline test (`tests/zone2/test_kb_loader.py` or fold into `test_rag_kb.py` in Task B1) — assert the returned set is non-empty and matches the seeded entries.
**Commit:** `git commit -m "feat(shared): kb_loader.get_safety_critical_conditions (unblocks Zone1 confidence gate)" && git push` — then send the handshake message from Section 4.1.

### Task B1 — Expanded RAG Knowledge Base (1:00–2:30, 90 min) — NO DEPENDENCY
**Files:** modify `src/zone2_cloud/rag/knowledge_base/*`, modify `src/zone2_cloud/rag/build_knowledge_base.py`, `src/zone1_edge/knowledge/local_advisories.json` (shared source of truth — see below), new `tests/zone2/test_rag_kb.py`
**Do:**
1. Grow the KB from its current size to 20–30 entries (scaled down from the original 25–40 target to fit 8 hours — quality and correctness over count). Source from real ICAR/state agri-extension style content — hand-curate, do not let an LLM invent facts for this file.
2. Each entry keeps the existing schema and gains `canonical_description: str` (one clean sentence — needed later even though the embedding-fusion consumer is out of scope today, this field costs nothing extra to add now and avoids a second pass later) and `is_safety_critical: bool` (Task B0's field, now filled in for the full expanded set).
3. **Important:** `local_advisories.json` (Zone 1's offline KB) and the Zone 2 RAG knowledge base should reference the same underlying condition keys/flags — if they are currently two separate files, keep them separate files but make sure `is_safety_critical` values agree between them for any condition that appears in both, since `kb_loader.py` reads from `local_advisories.json` per the contract in Section 3.1. Do not create a third, third-source-of-truth file.
4. Re-run `build_knowledge_base.py` to rebuild the FAISS/Chroma index against the expanded KB.
**Diagnostic (unit):** `test_rag_kb.py` — schema validation for every entry (required fields present, `is_safety_critical` boolean, no duplicate condition keys), plus a retrieval smoke test (a known symptom query returns the expected entry in the top-3 retrieved results).
**Diagnostic (pipeline):** manually run `retriever.py` against 2–3 sample queries, confirm sane results, log output to `results/zone2/rag_runs/` (per existing results folder convention).
**Commit:** `git commit -m "feat(zone2): expand RAG knowledge base to 20-30 entries + rebuild index" && git push`

### Task B2 — Farmer Login + Farmer-Scoped Zone 3 (2:30–3:45, 75 min) — NO DEPENDENCY
**Files:** new `src/zone3_memory/db/auth.py`, modify `src/zone3_memory/db/farm_memory.py`, modify `src/zone3_memory/schema/schema.sql`, modify `src/zone2_cloud/gemini/gemini_client.py` (add `strip_pii`), new `tests/zone3/test_auth.py`, modify `tests/zone3/test_memory.py`
**Do:**
1. Add a `pin` column to the `farm` table in `schema.sql` (plaintext for demo, comment clearly `-- DEMO ONLY: production must hash+salt`).
2. `auth.py`: a simple `login(phone: str, pin: str) -> str|None` returning `farmer_id` on success, `None` on failure; a `signup(phone: str, pin: str, name: str) -> str` creating a new farmer record. Keep it minimal — no session/token infra, Streamlit's `st.session_state` holds `farmer_id` for the rest of the session.
3. Retrofit `save_observation()` and `get_farm_history()` in `farm_memory.py` to accept and filter by `farmer_id` (`WHERE farmer_id = ?`) — mechanical change, not a rebuild.
4. Add `strip_pii(payload: dict) -> dict` in `gemini_client.py`'s request-building path — strips phone/name keys, keeps only `farmer_id` (opaque) and derived summary text.
**Diagnostic (unit):** `test_auth.py` (login/signup happy path + wrong-PIN rejection); extend `test_memory.py` (two different `farmer_id`s never see each other's history; `strip_pii` removes phone/name keys from a sample payload).
**Diagnostic (pipeline):** manually run through login → save an observation → fetch history → confirm scoping works via a short throwaway script or the extended test file itself.
**Commit:** `git commit -m "feat(zone3): farmer login, farmer-scoped memory, PII stripping" && git push`

### Task B3 — Gemini Client Hardening (3:45–4:30, 45 min) — NO DEPENDENCY (uses Task B0's `is_safety_critical` concept, already available from B0/B1)
**Files:** modify `src/zone2_cloud/gemini/gemini_client.py`
**Do:**
1. Tighten the system prompt: use image+text+sensor+farm history+retrieved KB; never invent diagnoses/dosages; distinguish possible vs. confirmed; explicitly flag safety-critical conditions (reference `get_safety_critical_conditions()`) with a stronger "recommend expert consultation" instruction; say so if evidence is insufficient; return structured JSON matching the agreed cloud-response contract.
2. Ensure the request payload includes the new `farmer_id` and `advisory_tier` fields from Section 3.1's contract addition.
3. Call `strip_pii()` (Task B2) on the payload immediately before the API call.
**Diagnostic (unit):** extend/create `test_gemini_client.py` — mock the API call, assert the constructed prompt/payload contains the required elements and does not contain raw PII keys.
**Commit:** `git commit -m "feat(zone2): harden gemini client prompt + payload (safety, PII, contract fields)" && git push`

### Task B4 — Gemini Output Validator (4:30–5:30, 60 min) — NO DEPENDENCY
**Files:** new `src/zone2_cloud/gemini/validator.py`, new `tests/zone2/test_validator.py`, modify `gemini_client.py` to call it
**Do:**
1. `validate_advisory(response_json: dict, retrieved_snippets: list[str], input_evidence: dict) -> tuple[bool, list[str]]`:
   - (a) JSON schema conformance check against the agreed cloud-response shape;
   - (b) crude grounding check — flag (don't hard-block) if a named condition/action isn't traceable to `retrieved_snippets`/`input_evidence`, log a warning and cap `advisory_tier` at `"possible"` if this fails;
   - (c) drug-name/dosage regex denylist scan (e.g., patterns like `\d+\s?(mg|ml/kg)` near a capitalized word) — hard-block on match, fall back to a safe templated response.
2. Wire into `gemini_client.py` immediately after the API call returns, before the result reaches the UI.
**Diagnostic (unit):** `test_validator.py` — one clean-pass fixture, one ungrounded-claim fixture, one drug-dosage-violation fixture, assert each check independently produces the correct bool + reason list.
**Commit:** `git commit -m "feat(zone2): gemini output validator (schema, grounding, safety denylist)" && git push`

### Task B5 — Small Offline Eval Harness (5:30–6:30, 60 min) — **DEPENDS ON PERSON A's WORKING PIPELINE (see Section 4.1's symmetric rule)** — do this AFTER the Hour-6 integration checkpoint if Zone 1 isn't ready before then
**Files:** new `eval/gold_set.json`, new `eval/run_eval.py`
**Do:**
1. Hand-write 10–15 cases (scaled down from 15–20 to fit 8 hours) — mix crop/livestock, mix clear/ambiguous, at least 2 safety-list conditions — each with expected `advisory_tier` and "must mention / must not mention" keyword lists.
2. `run_eval.py`: runs the full pipeline (Zone 1 → Zone 2) against each case, reports schema-valid %, correct-tier %, safety-list-escalation-correct %, drug-mention-violation count. Save the report to `results/zone2/eval_runs/`.
**Diagnostic:** running `run_eval.py` itself IS the diagnostic — a clean run producing a report with no crashes is the pass condition. Note the actual measured numbers in `docs/new_process.md` (Section 8) — this is a real artifact worth citing later.
**Commit:** `git commit -m "feat(eval): offline gold-set evaluation harness + first report" && git push`

### Task B6 — Streamlit Login Gate + Cloud Panel (Person B's marker block) (6:30–7:15, 45 min) — depends on Task B2 being done
**Files:** modify `src/app/streamlit_app.py` (**ONLY inside `ZONE2_ZONE3_UI_START`/`END` markers**)
**Do:**
1. Wrap the whole app behind the login screen from Task B2; store `farmer_id` in `st.session_state`.
2. Add the "Why cloud?" panel showing `threshold_reason` and `advisory_tier` (reads Person A's Task A4 output — coordinate via the shared contract shape, not by reading Person A's code directly).
3. Show the retrieved KB snippet(s) alongside the Gemini advisory output (Task B1/B4 outputs).
**Diagnostic:** manual run-through of the full Streamlit app: login → upload → see local or cloud result with the transparency panel.
**Commit:** `git commit -m "feat(app): login gate + cloud escalation transparency panel" && git push`

### Task B7 — Buffer, Integration Support, Final Re-test (7:15–8:00) — see Section 7
Support the final joint integration. If genuinely finished early, proceed to Section 9's stretch list in order (Docker-Compose is the first Zone-2-relevant stretch item).

---

## 7. INTEGRATION CHECKPOINTS (both people, mandatory, do not skip)

### Checkpoint 1 — Hour 2:30 (quick sync, 10 min)
- Confirm Task B0 (`kb_loader.py`) has landed and Person A has pulled it in for Task A4.
- Confirm no `contract.md`/`requirements.txt` conflicts have appeared (both should still match the Hour-0 baseline plus only-appended lines).

### Checkpoint 2 — Hour 4:00 (30 min, this is the important one)
1. Person A pushes their branch; Person B pushes theirs.
2. Both agents open a PR from each feature branch into `main` (do not merge yet).
3. Read each other's diff, specifically checking: does Person A's `fusion.py`/`confidence_gate.py` output exactly match the Section 3.1 contract shape Person B's code expects? Does Person B's `kb_loader.py` signature exactly match what Person A imported?
4. Fix any shape mismatches found, on each person's own branch, immediately.
5. **Do not merge into `main` yet** — this checkpoint is a verification sync, not a merge point (see Section 7.1 for the actual merge sequencing).

### Checkpoint 3 — Hour 6:00 (30 min)
1. Person A's branch should be feature-complete (Tasks A1–A7 done) by now. Person B's branch should have B0–B4 done, B5/B6 in progress.
2. Merge Person A's branch into `main` first (Section 7.1 explains why).
3. Person B rebases/merges `main` into their own branch to pick up Person A's final, tested Zone 1 code, then finishes B5 (which needs a working Zone 1 pipeline) and B6.

### 7.1 Merge sequencing (why Person A merges first)

Zone 2's eval harness (B5) and Streamlit integration (B6) need Zone 1's finished, tested output shape to run against — so the safest order is: **Person A's branch merges to `main` first** (once its own full test suite + pipeline diagnostic pass cleanly), **then Person B rebases onto the updated `main`** and finishes their remaining Zone-1-dependent work, **then Person B's branch merges to `main` last**. This is a one-way dependency (B depends on A's shapes, not the reverse) so this order minimizes conflict risk — do not merge Person B's branch before Person A's.

**Merge command sequence (Person A, at Hour 6, once A1–A7 pass cleanly):**
```
git checkout feature/zone1-8hr-sprint
AGRIVISION_EXPERT_MODE=mock pytest tests/zone1 -v            # must be 100% green
AGRIVISION_EXPERT_MODE=mock python setup/diagnose_pipeline.py --mode mock   # must be 100% green
git checkout main && git pull
git merge --no-ff feature/zone1-8hr-sprint -m "merge: zone1 8hr sprint improvements"
git push origin main
```

**Merge command sequence (Person B, after Person A's merge, near end of Hour 7):**
```
git checkout feature/zone2-zone3-8hr-sprint
git fetch origin main
git merge origin/main                     # pull in Person A's now-merged changes, resolve any conflicts (should be minimal given the marker-block/contract discipline above)
# re-run everything after resolving:
AGRIVISION_EXPERT_MODE=mock pytest tests/zone1 tests/zone2 tests/zone3 -v   # must be 100% green
AGRIVISION_EXPERT_MODE=mock python setup/diagnose_pipeline.py --mode mock  # must be 100% green
python eval/run_eval.py                    # sanity run, no crash
git checkout main
git merge --no-ff feature/zone2-zone3-8hr-sprint -m "merge: zone2/zone3 8hr sprint improvements"
git push origin main
```

### Final joint step (Hour 7:30–8:00, both together)
1. On `main`, run the full test suite one more time (`pytest tests/ -v`) and the full pipeline diagnostic — both must be green.
2. Run `eval/run_eval.py` one final time against merged `main`, save the report.
3. Manually walk through: blurry photo → reject; safety-list condition → forced cloud escalation regardless of confidence; login → save → re-login → history recall.
4. Tag: `git tag submission-8hr-final && git push --tags`.
5. Finalize `docs/new_process.md` with the end state (Section 8).

---

## 8. LIVING DOCUMENTATION — UPDATE THESE CONTINUOUSLY, NOT AT THE END

### 8.1 `docs/new_process.md` — progress log

Both agents append to this file after **every completed task** (not just at checkpoints). Use this exact structure, appending new entries under the relevant person's running log — do not rewrite earlier entries:

```markdown
# 8-Hour Sprint — Progress Log

## Overall Goal
[1-2 sentences: what this sprint is improving, copied from Section 1 of this plan]

## Status Summary (update this block at every checkpoint — Section 7)
- Hour 2:30 checkpoint: [brief status]
- Hour 4:00 checkpoint: [brief status]
- Hour 6:00 checkpoint: [brief status]
- Final (Hour 8:00): [brief status]

## Person A Log (append newest at bottom)
### Task A1 — Capture Quality Check
- Status: DONE / IN PROGRESS / BLOCKED
- Time taken: __ min (planned 50)
- Files touched: ...
- Tests: X/X passing
- Notes: [anything the other person or a future reader needs to know]

[... one block per task ...]

## Person B Log (append newest at bottom)
[same structure]

## What Was Completed (final summary, filled at Hour 8:00)
[list]

## What Was Explicitly Deferred (from Section 1 + Section 9, and why)
[list]

## Models Used
[link to docs/MODELS_USED.md]
```

### 8.2 `docs/pipeline_issues.md` — known issues / fix-needed log

Append an entry **immediately** whenever something is stubbed, temporarily hacked, discovered broken, or deferred — do not wait until the end to remember these. Format:

```markdown
# Pipeline Issues & Fix-Needed Log

## [Hour:Min] — [Person A/B] — [Task ID] — TITLE
- **What's wrong / stubbed / temporary:** ...
- **Why it was done this way under time pressure:** ...
- **What needs to happen to fix it properly:** ...
- **Severity:** blocks demo / cosmetic only / documented-scope-cut (not actually a bug)
- **Status:** OPEN / RESOLVED [+ resolution time if resolved later in the sprint]
```

### 8.3 `docs/MODELS_USED.md` — model registry (Section 0, rule 2)

```markdown
# Models Used — 8-Hour Sprint

| Model | HF/Kaggle repo id | Params | Precision/quantization | Used for | Loaded in | Why chosen |
|---|---|---|---|---|---|---|
| (existing crop model — copy from setup/download_crop_model.py) | | | | | | |
| (existing livestock model) | | | | | | |
| (any new model added today, if any) | | | | | | |
```
No new models are expected to be added today (all of today's tasks are rule-based/logic, not new-model tasks) — if an agent does end up needing a new small model for any reason, it must be logged here before being used, per Section 0 rule 2.

---

## 9. IF TIME RUNS OUT — DROP ORDER (do not improvise a different order)

If Hour 6/7/8 checkpoints reveal you're behind, drop from the **bottom** of this list first, protecting the top:

1. **Never drop:** Task A1 (quality check), Task A4 (dynamic gate + safety list), Task B0 (kb_loader), Task B2 (login + scoped memory), Task B4 (validator).
2. Drop Task B1's KB size target — 10–12 well-formed entries beats 20–30 rushed ones; never drop the validator (B4) to save time on KB size.
3. Drop Task A5 (auto-route) — fall back to manual tab selection only, which already exists and works; document as unchanged-by-design.
4. Drop Task A2's `top_k_first_aid` ranking — fall back to the original simple threshold-rule sensor output shape if truly out of time (but keep the trend detection if at all possible, it's cheap).
5. Drop Task A6 (explainability) entirely — even the lightweight version — if nothing else can be cut.
6. Drop Task B5 (eval harness) size — run against 4–5 cases instead of 10–15, better than not running it at all.
7. Drop Task B6's cloud transparency panel polish — a minimal working escalation flow without the pretty "why cloud?" panel is acceptable.
8. **Stretch items (only attempt if everything above is done, tested, and merged, with real time remaining):** in order — (a) Grad-CAM heatmap for Task A6, (b) Docker-Compose for Zone 2, (c) embedding-based text fusion, (d) multilingual text output, (e) bounded clarification loop. Do not start a stretch item with less than 30 minutes remaining — a half-finished stretch feature that breaks the pipeline is strictly worse than not attempting it, per Section 0 rule 8.

---

## 10. QUICK REFERENCE — SHARED NAMING CONVENTIONS (use exactly these, both people)

- Function names are `snake_case`, always typed with `-> dict` / `-> tuple[bool, list[str]]` etc. return annotations — no bare untyped returns on any new function.
- Every new dict-shaped output must match a shape documented in `contract.md` — if you need a new field, add it to `contract.md` in the same commit that introduces it (append-only, per Section 0 rule 3).
- Boolean flags are always `is_x` or `has_x` or `enable_x` (e.g., `is_safety_critical`, `enable_embedding_fusion`).
- Every new file starts with a one-line module docstring stating which Task ID (e.g., "Task A1") it belongs to, so a reader of `docs/new_process.md` can jump straight to the matching code.
- Test files mirror source paths 1:1 (`src/zone1_edge/quality/quality_check.py` → `tests/zone1/test_quality_check.py`) — never a different naming scheme.
- Every new pytest file must be independently runnable with `AGRIVISION_EXPERT_MODE=mock` (matching the project's existing convention) — never require a live network call or real API key to pass in CI/local test runs.
