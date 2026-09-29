# AgriVision: Test & Run Guide

## How to read this file
Every command block carries one of these tags, so you always know what it costs:

| Tag | Meaning |
|---|---|
| 🟢 **NO API** | Runs fully locally. Free. Safe to repeat. |
| 🌐 **FREE DOWNLOAD** | Downloads files (models/packages) from the internet, but uses no quota and no key. |
| 🔴 **USES GEMINI API** | Makes real Gemini requests. **Counts against your quota and may cost money.** The number of requests is stated next to the command. |
| 🟡 **USES WEATHER API** | Calls Open-Meteo (free, no key, nothing you pay for). |

Where things run: **Laptop** = your Windows machine (PowerShell). **GPU box** = the workstation (bash).
Time / RAM / disk numbers are my estimates unless a measured result is quoted.

## Status board
| Part | What | Status |
|---|---|---|
| A | Test everything that does not need fine-tuning (laptop) | ✅ you can run any time |
| B | Fine-tune the 4 vision experts + MoE gate (GPU box) | ✅ **DONE.** Results and analysis: [docs/system/evaluation_results.md](docs/system/evaluation_results.md) |
| B-fix | `--routing both` measured (crop 77% → 94.5%, livestock 84% → 89.5%); re-run crop baseline still open | ✅ routing / ⏳ baseline (Part B) |
| C | RAG label review, synthetic data (Gemini), Qwen fine-tuning, comparison | ⏳ next (each step is tagged 💻 laptop or 🖥️ GPU box) |
| G | Check the whole system in the web app (fine-tuned experts, Gemini, Qwen) | ⏳ after Part C, partly possible now |
| D / E | Keys you need; checklist to confirm nothing is mock | reference |

## Everything that uses an API, in one place
| Command | API | How many requests |
|---|---|---|
| `generate_synthetic_data --n N ... --i-understand-this-calls-gemini` | 🔴 Gemini | **N at most** (one per scenario; failures count too; paced at 4.5 s per request; stops early after 3 failures in a row). Daily cap on your plan: 500 |
| `compare_backends --backend gemini ... --limit L` | 🔴 Gemini | **L** (or the whole test set, about 50, if you leave out `--limit`); paced at 4.5 s per request |
| Streamlit with `GEMINI_ENABLED=true`, when a result goes to the cloud route | 🔴 Gemini | **1 per "Auto-Detect" click** that ends on the cloud route |
| Streamlit with `WEATHER_ENABLED=true`, cloud route | 🟡 Open-Meteo | 1 per click (cached 30 min per region) |
| Qwen model download in `finetune_qlora` / vLLM | 🌐 Hugging Face (free, no key) | one ~3 GB download |
| Everything else (tests, evaluation, RAG eval, training, dry-runs) | none | 0 |

Gemini is only called when **both** hold: `GEMINI_ENABLED=true` is set **and** (for the two scripts) you pass `--i-understand-this-calls-gemini`. Otherwise the code refuses or uses a built-in mock.

---
# PART A: What you can test now on the laptop (no fine-tuning needed)

### A0. One-time setup 🌐 FREE DOWNLOAD (pip packages)
```powershell
python -m venv venv                     # skip if ./venv exists
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt         # 10-20 min, ~3-6 GB
pip install onnxruntime                 # needed to run the fine-tuned ONNX experts
```
Create `.env` yourself from `.env.example` (I never read it). For "no mock" testing:
```
AGRIVISION_EXPERT_MODE=real     # 'auto' silently falls back to MOCK when a model fails to load; 'real' raises an error instead
GEMINI_ENABLED=false            # switch on only in step A5
WEATHER_ENABLED=false           # switch on only in step A6
```

### A1. Automated tests 🟢 NO API (about 1-2 min)
```powershell
$env:AGRIVISION_EXPERT_MODE="mock"; $env:GEMINI_ENABLED="false"; $env:HF_HUB_OFFLINE="1"
pytest tests/ -q
```
Expect **123 passed, 13 skipped** (the 13 skips are known Windows/OpenCV skips). Delete any `test_*.db` files the tests leave in the repo root.

### A2. "What is real and what is mock?" 🟢 NO API (about 20 s)
```powershell
$env:AGRIVISION_EXPERT_MODE="real"
python setup/check_real_components.py
```
| Output line | Meaning |
|---|---|
| `[OK ] crop expert REAL -> hf:...crop_model` | the **old** 13-class crop checkpoint loaded (the fallback expert, not your fine-tuned ones) |
| `[OK ] livestock expert REAL` | old CLIP zero-shot model loaded |
| `MoE crop: active` | your fine-tuned gate + ONNX experts were found in `models_cache/moe/` |
| `MoE ...: inactive` | files missing: copy `models_cache/moe/` from the GPU box and install `onnxruntime` |
| `RAG backend = faiss` | semantic search (real). `lexical` = keyword search (also real, no torch) |
| `[MOCK] Gemini` | `GEMINI_ENABLED` is not true (fine until step A5) |

### A3. Run the app with real vision models 🟢 NO API
```powershell
$env:AGRIVISION_EXPERT_MODE="real"
streamlit run src/app/streamlit_app.py     # http://localhost:8501
```
Try these, in order:
1. **Sign up / log in** with any phone and PIN.
2. **Sidebar:** pick a Region (e.g. Punjab) and a Season.
3. **Upload a real leaf photo, click Auto-Detect.** Under the result you should see `🔧 Vision backend: hf:...` (old model) or, once the Part B files are copied here, `MoE expert: crop_row (onnx)`. A yellow **MOCK** warning means a fake predictor is running.
4. **Local route:** a blue 🗓️ season note appears; the diagnosis and action list do not change with season.
5. **Cloud route with Gemini off:** you get a canned "mock advisory" and the caption `Advisory backend: gemini(MOCK-client)`. That label is how you know it is not real Gemini.
6. Upload `demo_data/blurry.jpg`: rejected with a "retake photo" message. Upload a non-plant, non-animal picture: "doesn't appear to be a crop or livestock photo".
7. **Farm History** tab shows the saved runs.
8. Livestock: open **Livestock Sensors**, set temperature 40.5 / activity low / feed low, add text "गाय को बुखार है" with a cow photo. Fusion should raise concern (usually a cloud route).

### A4. Knowledge base / RAG 🟢 NO API
```powershell
python eval/kb_coverage_audit.py                                   # expect 0 RAG gaps (about 21 offline-advisory gaps are intentional)
python -m src.zone2_cloud.rag.retriever "cow with lumps on skin and fever"     # top hit should be KB-lumpy_skin_disease
python -m src.zone2_cloud.rag.build_knowledge_base                 # rebuild the search index after any KB edit (~30 s)
python eval/rag_eval.py --backend lexical
python eval/rag_eval.py --backend faiss
```
**Your task (needed before the numbers mean anything):** open `eval/rag_queries.json`. The relevance labels were written by me, not a domain expert. Correct them, set `"reviewed": true`, re-run. Also skim the 22 draft docs (`review_status: draft_needs_expert_review`) in `src/zone2_cloud/rag/knowledge_base/` and `src/zone1_edge/knowledge/seasonal_guidance.json`.

### A5. Real Gemini in the app 🔴 USES GEMINI API (1 request per cloud-route click)
Get a key at <https://aistudio.google.com/apikey> (sign in, **Create API key**). Do not enable billing unless you want to pay. In `.env`:
```
GEMINI_ENABLED=true
GEMINI_API_KEY=<your key>
GEMINI_MODEL=gemini-2.5-flash-lite
```
Restart Streamlit and trigger a cloud-route case (low confidence or a safety-critical disease). Do only **2-3 clicks**. It is real if: the caption says `Advisory backend: gemini` with no `(MOCK-client)`; the text is specific to your case (not "This is a mock advisory..."); `Cited docs: KB-...` shows IDs that exist. If you see "Error generating advisory", the key or quota is the problem (details in the terminal). Set `GEMINI_ENABLED=false` again afterwards.

### A6. Real weather 🟡 USES WEATHER API (free, no key)
`.env`: `WEATHER_ENABLED=true`, restart, set a Region, trigger a cloud case: caption `Weather context (open-meteo): ...`. Turn Wi-Fi off and repeat: the advisory must still appear, just without weather.

---
# PART B: Vision experts and MoE gate: DONE ✅

**What was done:** the four sub-experts (`crop_row`, `crop_perennial`, `livestock_lsd`, `livestock_fmd`) and both `moe_gate` files were trained on the GPU box, and baseline and after-training evaluations were produced.
**Results, tables and analysis:** [docs/system/evaluation_results.md](docs/system/evaluation_results.md).
**Short verdict:** the experts are excellent (about 97-98% crop, 94-95% livestock on their own). The gate routes only about 74% (crop) and 82% (livestock) of images correctly, which drags the end-to-end numbers to 77% and 84%. That is still far better than before for livestock (53% → 84%), but a routing fix is recommended.

### B-fix-1. Re-run the crop baseline on the same test images 🟢 NO API (GPU box, about 5-20 min)
Why: the earlier crop baseline used 6517 images, every other report uses 5433, so they cannot be compared. This re-scores the original checkpoint on the exact same test set. (Use your normal GPU-box session setup, shown below.)
```bash
CUDA_VISIBLE_DEVICES=0 nohup python -u -m training.evaluate_expert --root "$PV" --domain crop --target baseline > $AGRI/logs/base_crop2.log 2>&1 &
```
Then send me `results/zone1/eval/crop_baseline.md` and I will update the report.

### B-fix-2. Routing fix `--routing both` ✅ DONE and measured (results in the report, section 7)
**What it does.** Today's default (`top1`) lets the `moe_gate` pick ONE expert per image; the gate is right only ~74% (crop) / ~82% (livestock) of the time. `both` runs **every expert of the domain** (2 small ONNX models, tens of ms each on CPU) and combines the answers: crop = most confident expert wins; livestock = *disease first* (if either expert reports a disease, the most confident disease answer wins).
**Measured on your test sets (same images as top1):**
| | top1 | both |
|---|---|---|
| Crop accuracy / ECE | 77.3% / 0.136 | **94.5% / 0.037** |
| Livestock accuracy / ECE | 83.6% / 0.145 | **89.5% / 0.091** |
| Lumpy skin predicted "healthy" | 34 of 181 | **6 of 181** |
| Healthy animals flagged as disease | 8.8% | 12.9% (the price of disease-first) |
**Recommendation:** use `AGRIVISION_MOE_ROUTING=both` (set it in `.env`; default stays `top1`). Details: [docs/system/evaluation_results.md](docs/system/evaluation_results.md) section 7.
To re-run: `python -u -m training.evaluate_expert --root "$PV" --domain crop --target moe --routing both` (and the livestock equivalent with `--class-map $CM`).

### Copy the trained files to the laptop (to try them in the app) 🟢 NO API
Copy from the GPU box `$AGRI/models_cache/moe/` (only `model.onnx` and `meta.json` in each expert folder, plus the two `*_moe_gate.json`; skip `best.pt`) to the laptop's `models_cache/moe/`. Then A2 should show `MoE crop: active`.

### GPU box session setup (already done; kept for reference)
Code: `/home/m25cse030/agri-vision-platform`. Everything big: `/DATA1/shrusti/agri-vision-platform` (`venv/ data/ models_cache/ results/ logs/ hf_cache/ pip_cache/ tmp/`).
```bash
export AGRI=/DATA1/shrusti/agri-vision-platform
export CODE=/home/m25cse030/agri-vision-platform
export AGRIVISION_DATA_ROOT=$AGRI        # training scripts write models_cache/ and results/ here, not into the code dir
export HF_HOME=$AGRI/hf_cache TORCH_HOME=$AGRI/hf_cache/torch
export PIP_CACHE_DIR=$AGRI/pip_cache TMPDIR=$AGRI/tmp
export CUDA_DEVICE_ORDER=PCI_BUS_ID      # CUDA_VISIBLE_DEVICES numbers match nvidia-smi
export PV="$AGRI/data/plantvillage/PlantVillage"
export CATTLE="$AGRI/data/cattle/Cows datasets"
export CM=training/configs/cattle_class_map.json
source $AGRI/venv/bin/activate
cd $CODE
```
Use `python -u` with `nohup` so logs are not buffered. Use one 24 GB card (`CUDA_VISIBLE_DEVICES=<idx>`), never the 48 GB one.

<details><summary>Part B commands (for re-running; all 🟢 NO API)</summary>

```bash
python -m training.dataset_audit --root "$PV" --domain crop
python -m training.dataset_audit --root "$CATTLE" --domain livestock --class-map $CM
CUDA_VISIBLE_DEVICES=0 nohup python -u -m training.finetune_expert --root "$PV" --group crop_row --batch 64 --workers 8 > $AGRI/logs/ft_crop_row.log 2>&1 &
CUDA_VISIBLE_DEVICES=0 nohup python -u -m training.finetune_expert --root "$PV" --group crop_perennial --batch 64 --workers 8 > $AGRI/logs/ft_crop_perennial.log 2>&1 &
CUDA_VISIBLE_DEVICES=0 nohup python -u -m training.finetune_expert --root "$CATTLE" --group livestock_lsd --class-map $CM --batch 32 --workers 8 > $AGRI/logs/ft_lsd.log 2>&1 &
CUDA_VISIBLE_DEVICES=0 nohup python -u -m training.finetune_expert --root "$CATTLE" --group livestock_fmd --class-map $CM --batch 32 --workers 8 > $AGRI/logs/ft_fmd.log 2>&1 &
python -u -m training.train_moe_gate --root "$PV" --domain crop
python -u -m training.train_moe_gate --root "$CATTLE" --domain livestock --class-map $CM
CUDA_VISIBLE_DEVICES=0 python -u -m training.evaluate_expert --root "$PV" --domain crop --target sub:crop_row      # also sub:crop_perennial and moe
CUDA_VISIBLE_DEVICES=0 python -u -m training.evaluate_expert --root "$CATTLE" --domain livestock --target moe --class-map $CM
```
Data split rules: PlantVillage `train/` trains; its `val/` is split 50/50 per class into validation (picks the best epoch) and test (final numbers only). Cattle has no shipped split, so it gets a fixed 70/15/15.
</details>

---
# PART C: RAG review, Qwen fine-tuning, comparison

**What Part C achieves:** the cloud advisory currently comes from Gemini. Part C teaches a small open model (Qwen2.5-1.5B) to write the same kind of structured, source-cited advisory, so you can run it yourself instead of (or next to) Gemini. To teach it we need examples. We have almost no real advisories, so we ask Gemini to write some (synthetic data), **you check them by hand**, then Qwen trains on the approved ones.

## Where each step runs
| Step | Machine | Why |
|---|---|---|
| C1 review RAG labels | 💻 **Laptop** | your time, no compute |
| C2 generate synthetic data (Gemini) | 💻 **Laptop** | your `.env` with the Gemini key lives here; only needs internet |
| C2 review the sheet | 💻 **Laptop** | open the CSV in Excel |
| C3 build training files | 💻 **Laptop** | CPU only, seconds |
| C3b copy the training files | 💻 → 🖥️ | `scp` laptop → GPU box (about 1 MB) |
| C4 fine-tune Qwen | 🖥️ **GPU box** | needs the GPU |
| C5 serve Qwen | 🖥️ **GPU box** | needs the GPU; laptop reaches it through an SSH tunnel |
| C6 compare Qwen vs Gemini | 💻 **Laptop** (through the tunnel) | it needs both the Gemini key (laptop) and the Qwen server (GPU box) |

All laptop commands are **PowerShell in the repo root with the venv active**. All GPU-box commands are bash with your normal session setup (see "GPU box session setup" in Part B).

## Your Gemini limits (from your AI Studio dashboard) and the plan built on them
| Limit | Value | What it means for us |
|---|---|---|
| Requests per minute (RPM) | **15** | scripts now wait **4.5 s** between requests (`--min-interval 4.5`), so they never exceed 13/min |
| Tokens per minute (TPM) | 250 000 | one request is roughly 2-4 k tokens (estimate), i.e. about 40 k TPM at our pace: no problem |
| **Requests per day (RPD)** | **500** (you had already used **54** today) | **this is the real limit**; each Streamlit cloud click counts too |

Model: your dashboard shows "Gemini 3.5 Flash Lite". Copy the **exact model id** for the API from AI Studio (open "Get code" on that model and copy the string in `model="..."`) into `.env` as `GEMINI_MODEL=...`. I cannot verify the id, so do not guess it. The daily counter normally resets at a fixed time (I believe midnight Pacific; check your dashboard).

**Budget plan (about 415 requests for training data + 50 for the comparison, spread over 3 days, keeping a safety margin):**
| Day | What | Requests |
|---|---|---|
| Day 1 | pilot (15) → review → first batch (200) | 215 |
| Day 2 | second batch (200) | 200 |
| Day 3 | Gemini comparison on the test set (`--limit 50`) + a few app tests | ~60 |
You can go faster (the daily cap is 500) but leave at least 50 requests unused each day for app tests. Pacing: 200 requests take about 15 minutes.

## C1. Review the RAG labels 💻 LAPTOP, 🟢 NO API
Same task as A4. Do it first: the citation checks in the later steps rely on the knowledge base being right.

## C2. Generate synthetic training data 💻 LAPTOP, 🔴 USES GEMINI API
**What happens:** the script builds "scenarios" (a disease from the knowledge base + region + season + weather + optional farm history + the retrieved knowledge documents). For each scenario it sends the same prompt the app would send and asks Gemini for the advisory JSON. **Each scenario is one request.** Answers are auto-checked (format, citations, no drug doses) and saved with `synthetic=true` and `review_status=pending`.

**How you stay under your limits:**
- `--n N` is the **maximum number of new requests in this run**.
- `--min-interval 4.5` keeps you under 15 requests/minute.
- It **resumes**: scenarios already stored are skipped, so running it on another day continues where it stopped and never repeats a request.
- It **stops itself after 3 failures in a row** (for example when the daily quota is used up).
- Before each session look at the AI Studio usage page: `500 - used today` is what you have left.

In `.env` on the laptop (once): `GEMINI_MODEL=<exact id from AI Studio>` and your `GEMINI_API_KEY`.

**Step 1: preview the scenarios 🟢 NO API**
```powershell
python -m training.llm.generate_synthetic_data --audit-db          # how many real records exist (expect very few)
python -m training.llm.generate_synthetic_data --dry-run --n 10    # writes scenarios_dry_run.jsonl, 0 requests
```
Open `results\zone2\llm_data\scenarios_dry_run.jsonl` and check that the scenarios look sensible. (The dry run never touches your real data or review sheet.)

**Step 2: pilot 🔴 USES GEMINI API (15 requests, about 70 seconds)**
```powershell
$env:GEMINI_ENABLED="true"
python -m training.llm.generate_synthetic_data --n 15 --i-understand-this-calls-gemini
```
Output: `results\zone2\llm_data\synthetic_advisories.jsonl` and the review sheet `review_sample.csv`.

**Step 3: review by hand 💻 LAPTOP, 🟢 NO API.** Open `review_sample.csv` in Excel. For each row read the summary and actions for agronomic or veterinary correctness and type `approved` or `rejected` in the column `review_status(approved/rejected)`. Save as CSV (keep the same file name and columns). If most are rejected, tell me and we fix the prompt before spending more requests.

**Step 4: scale up 🔴 USES GEMINI API (200 requests per run, about 15 minutes)**
Target: **300-500 approved examples** (fewer than about 150 will not teach the model reliably). At roughly 80% approval, about 415 requests give about 330 approved.
```powershell
$env:GEMINI_ENABLED="true"
python -m training.llm.generate_synthetic_data --n 200 --i-understand-this-calls-gemini      # Day 1
python -m training.llm.generate_synthetic_data --n 200 --i-understand-this-calls-gemini      # Day 2 (continues, no repeats)
```
Each run appends new rows to the same sheet; review only the new rows. If a run stops early with "Too many consecutive failures", your daily quota is probably used up: continue tomorrow. Set `$env:GEMINI_ENABLED="false"` afterwards.

## C3. Build the training files 💻 LAPTOP, 🟢 NO API
```powershell
python -m training.llm.prepare_sft_dataset --reviewed results\zone2\llm_data\review_sample.csv
```
Keeps only rows you marked `approved` **and** that pass the validator and the citation check, then splits them per disease into train / val / **test** (about 80/10/10). The test part is never used for training and is what the final comparison uses. Only rows present in the reviewed sheet are used. It prints the number of examples per split: you want about 250+ in `train`.

### C3b. Copy the training files to the GPU box 💻 → 🖥️ 🟢 NO API
```powershell
ssh m25cse030@<gpu-host> "mkdir -p /DATA1/shrusti/agri-vision-platform/results/zone2/llm_data"
scp results\zone2\llm_data\sft_train.jsonl results\zone2\llm_data\sft_val.jsonl results\zone2\llm_data\sft_test.jsonl m25cse030@<gpu-host>:/DATA1/shrusti/agri-vision-platform/results/zone2/llm_data/
```
(The GPU box needs `git pull` first so it has the latest code.)

## C4. Fine-tune Qwen (QLoRA) 🖥️ GPU BOX, 🌐 FREE DOWNLOAD (base model ~3 GB from Hugging Face, no key)
```bash
CUDA_VISIBLE_DEVICES=0 nohup python -u -m training.llm.finetune_qlora --base Qwen/Qwen2.5-1.5B-Instruct --out $AGRI/models_cache/llm/agrivision-qwen-lora > $AGRI/logs/qlora.log 2>&1 &
tail -f $AGRI/logs/qlora.log
```
**What happens:** the 1.5 B model is loaded in 4-bit (small memory) and only tiny "LoRA adapter" layers (~70 MB) are trained on your approved examples, in the model's own chat format. Gemini is not involved.
Estimates: GPU 8-12 GB · RAM ~8 GB · disk ~3 GB base model (in `$AGRI/hf_cache`) + ~0.2 GB adapters · **20-60 min** for ~300-500 examples × 3 epochs.
**Healthy signs:** `eval_loss` goes down over the epochs; the best epoch is kept automatically. **If out of memory:** add `--batch 2 --grad-accum 8` or `--max-len 1536`. A Hugging Face token is only needed if downloads get rate-limited (huggingface.co/settings/tokens, new *read* token, then `huggingface-cli login`).

## C5. Serve Qwen 🖥️ GPU BOX, 🟢 NO API
```bash
pip install vllm       # large install, once
CUDA_VISIBLE_DEVICES=0 nohup python -u -m vllm.entrypoints.openai.api_server --model Qwen/Qwen2.5-1.5B-Instruct --enable-lora --lora-modules agrivision-advisor=$AGRI/models_cache/llm/agrivision-qwen-lora --port 8000 > $AGRI/logs/vllm.log 2>&1 &
tail -f $AGRI/logs/vllm.log        # wait for "Application startup complete"
```
This starts a local web server that speaks the OpenAI chat format (no OpenAI account or key involved).
**Then, on the laptop, open the tunnel and leave that window open** 💻:
```powershell
ssh -L 8000:localhost:8000 m25cse030@<gpu-host>
```
Test it from the laptop in a second PowerShell window (🟢 NO API; it only talks to your GPU box):
```powershell
curl http://localhost:8000/v1/models        # should list "agrivision-advisor"
```
Do not expose port 8000 publicly.

## C6. Compare Qwen with Gemini 💻 LAPTOP (tunnel open), on the held-out test set
(`sft_test.jsonl` is already on the laptop from C3.) Use the same `--limit` for both so the comparison is fair.
```powershell
# Qwen through the tunnel (only talks to your GPU box)                                     🟢 NO API
$env:ADVISORY_BACKEND="local_llm"; $env:LOCAL_LLM_URL="http://localhost:8000/v1"; $env:LOCAL_LLM_MODEL="agrivision-advisor"
python -m training.llm.compare_backends --backend local_llm --limit 50

# Gemini                                                                                   🔴 USES GEMINI API (50 requests, about 4 minutes)
$env:GEMINI_ENABLED="true"
python -m training.llm.compare_backends --backend gemini --limit 50 --i-understand-this-calls-gemini
$env:GEMINI_ENABLED="false"

# citation score on the saved answers                                                      🟢 NO API
python eval\rag_eval.py --citations results\zone2\llm_compare\local_llm.jsonl
python eval\rag_eval.py --citations results\zone2\llm_compare\gemini.jsonl
```
Reports: `results\zone2\llm_compare\*_report.json` (schema validity, validator pass, citation correctness, farm-history citation correctness). Also read a few answers by hand: these numbers do not tell you whether the advice is agronomically or medically right. Send me the reports and I will add them to [docs/system/evaluation_results.md](docs/system/evaluation_results.md).

---
# PART D: Keys and tokens
| Token | Needed for | How to get | Cost |
|---|---|---|---|
| `GEMINI_API_KEY` | A5, C2, C6 (the Gemini steps) | <https://aistudio.google.com/apikey> | free tier with rate limits; billing optional (leave it off to cap spend) |
| Hugging Face token | only if downloads are rate-limited | huggingface.co/settings/tokens (read) | free |
| Kaggle token | only if you download more Kaggle datasets | kaggle.com/settings → Create New Token | free |
| Weather | none (Open-Meteo) | n/a | free, non-commercial |
| `LOCAL_LLM_API_KEY` | only if your Qwen server requires one | your server | n/a |

# PART E: Confirm nothing is mock
- [ ] `python setup/check_real_components.py` shows `[OK ]` for both experts, `MoE ...: active` after copying the Part B files, and `[OK ] Gemini` after A5.
- [ ] Result caption: `Vision backend: hf:<path>` (never `mock`) or `MoE expert: <group> (onnx)`; no yellow MOCK warning.
- [ ] Advisory caption: `gemini` with no `(MOCK-client)`, or `local_llm`.
- [ ] `AGRIVISION_EXPERT_MODE=real` so a missing model raises an error instead of silently mocking.

# PART F: Notes
- **Storage:** all training outputs follow `AGRIVISION_DATA_ROOT`; the app reads trained models from `$AGRIVISION_DATA_ROOT/models_cache` (or `AGRIVISION_MODEL_CACHE`). The small FAISS index and the farm database stay in the repo.
- **Training code is optimised** (mixed precision, channels-last, pinned memory, persistent workers, fast JPEG decoding). If you ever see `nan` loss, tell me.
- **Vercel:** the Streamlit UI cannot run on Vercel serverless, and the old HF/torch models exceed its limits; the new ONNX experts, numpy gate and keyword RAG are light enough. Options are in `docs/system/ai_upgrade_walkthrough.md`.

---
# PART G: Check the whole system in the web app (fine-tuned models, Qwen, Gemini)

Run this on the **💻 laptop**, after Part B files are copied and (for G6) Qwen is served and the tunnel is open. Goal: prove with your own eyes that every component in the chain is the real one, not a mock and not the old model.

### G0. Prepare 🟢 NO API
1. Files present on the laptop: `models_cache\moe\crop_row`, `crop_perennial`, `livestock_lsd`, `livestock_fmd` (each with `model.onnx` + `meta.json`) and `crop_moe_gate.json`, `livestock_moe_gate.json`. And `pip install onnxruntime`.
2. Copy about 10 test photos from the dataset on the GPU box so you know the true answer (folder name = truth): `scp` a few images from `$PV/val/Tomato___Early_blight/`, `$PV/val/Apple___Apple_scab/`, `$PV/val/Potato___healthy/`, and from `$CATTLE/lumpy`, `$CATTLE/healthy`, `$CATTLE/foot-and-mouth`. (Use images from `val/`, which the model never trained on.)
3. `.env` for the first pass (no Gemini yet):
```
AGRIVISION_EXPERT_MODE=real
AGRIVISION_MOE_ENABLED=true
AGRIVISION_MOE_ROUTING=both
ADVISORY_BACKEND=gemini
GEMINI_ENABLED=false
WEATHER_ENABLED=false
```
4. Check: `python setup/check_real_components.py`. **Pass if** it prints `MoE (routing=both) crop: active` and the same for livestock. **If `inactive`:** a file is missing in `models_cache\moe` or `onnxruntime` is not installed.

### G1. Fine-tuned crop experts are really used 🟢 NO API
`streamlit run src/app/streamlit_app.py`, log in, upload the **Tomato___Early_blight** image, click Auto-Detect. Look under the result:
- `🔧 Vision backend: ...` followed by `MoE expert: crop_row (onnx) · routing=both`. **Pass:** the words `MoE`, `onnx` and `routing=both` appear and there is no yellow MOCK warning. **Fail:** `hf:...crop_model` means the old 13-class model ran (MoE not active, go back to G0.4).
- `🔬 Each expert's answer: crop_row: Tomato___Early_blight (9x%) | crop_perennial: Apple___... (xx%)`. **Pass:** both experts listed; the right one has high confidence.
- The prediction matches the folder name. Repeat with Apple scab (winner should be `crop_perennial`) and Potato healthy. Try about 10 images; you expect most (not all) to match (measured test accuracy: 94.5%).
- Proof it is not the old model: the old model could not predict tomato or apple at all.
- Optional cross-check that the app equals the evaluation code (🟢): `python -c "from src.zone1_edge.moe import moe_expert as m, json; print(json.dumps(m.run('crop', r'C:\path\to\image.jpg', routing='both')['_moe'], indent=1))"` should show the same per-expert answers as the caption.
- Compare `top1`: set `AGRIVISION_MOE_ROUTING=top1`, restart, upload the same image: the caption shows `routing=top1` and no per-expert line. (Fewer correct answers on hard images is expected.)

### G2. Fine-tuned livestock experts 🟢 NO API
Upload a lumpy photo, a healthy cow photo and an FMD photo (Auto-Detect). Expected: the per-expert line lists `livestock_lsd` and `livestock_fmd`. With `both` the rule is disease-first: a lumpy photo should be reported as lumpy (or at least as a disease); the measured miss rate is 3.3% (6 of 181), false alarms on healthy about 13%. Safety-critical diseases go to the cloud route by design, so expect a cloud-assist message for lumpy/FMD. Note: `AGRIVISION_MOE_ENABLED=true` needs all four livestock files; if `livestock_fmd` is missing the check in G0 shows livestock `inactive`.

### G3. Local advisory and season note 🟢 NO API
Use a high-confidence healthy or common-disease image (for example tomato early blight at ~99%). **Pass:** a 🟢 "Local AI Decision" box with a summary and actions, plus the blue 🗓️ note for the season/region you picked in the sidebar. The label was normalised to the knowledge base (`Tomato___Early_blight` → `tomato_early_blight`), otherwise it would have been sent to the cloud.

### G4. Cloud route with everything mocked 🟢 NO API
Upload a low-confidence or blurry-ish image, or a lumpy photo. **Pass:** "CLOUD ASSIST", then the caption `Advisory backend: gemini(MOCK-client)` and the canned mock text. That confirms the safe fallback path; the citation caption should show `KB-...` IDs and `Citations verified ✅`.

### G5. Real Gemini in the app 🔴 USES GEMINI API (1 request per cloud-route click; do at most 2-3)
1. Note your current usage on the AI Studio dashboard (for example `54 / 500`).
2. `.env`: `GEMINI_ENABLED=true`, `GEMINI_MODEL=<exact id>`, key set. Restart the app.
3. Upload the lumpy photo (cloud route). **Pass:** caption `Advisory backend: gemini` (no `(MOCK-client)`), case-specific text (region/season mentioned), `Cited docs: KB-lumpy_skin_disease ...`, `Citations verified ✅`.
4. Refresh the AI Studio dashboard: **the request counter must have gone up by exactly 1.** That is the strongest proof the call was real.
5. Run the same image again: the **History refs** line should now show `H<number>` (farm history cited).

### G6. Qwen in the app 🟢 NO API to Google (only your GPU box)
1. Confirm the vLLM server is running on the GPU box and the tunnel window is open (`curl http://localhost:8000/v1/models` in PowerShell shows `agrivision-advisor`).
2. `.env`: `ADVISORY_BACKEND=local_llm`, `LOCAL_LLM_URL=http://localhost:8000/v1`, `LOCAL_LLM_MODEL=agrivision-advisor`, and set `GEMINI_ENABLED=false` (so nothing can secretly use Gemini). Restart the app.
3. Upload the lumpy photo again (cloud route). **Pass:** caption `Advisory backend: local_llm` (exactly, no `fallback`), a structured advisory, `Cited docs: KB-...`.
4. Proof from the other side: on the GPU box `tail -n 20 $AGRI/logs/vllm.log` shows a new `POST /v1/chat/completions ... 200` line at that moment; and the AI Studio counter did **not** go up.
5. Failure test: close the tunnel window and run again. **Pass:** the app still answers, with the caption `Advisory backend: gemini_fallback(MOCK-client)` (no Gemini request is made because `GEMINI_ENABLED=false`).
6. Quality: read the advice yourself. Qwen may be worse than Gemini in wording; the comparison (C6) tells you by how much.

### G7. Weather (optional) 🟡 USES WEATHER API (free)
`WEATHER_ENABLED=true`, pick a Region, trigger a cloud case: caption `Weather context (open-meteo): ...`. Turn Wi-Fi off and retry: the advisory must still appear.

### G8. Final checklist
- [ ] `check_real_components.py`: `MoE (routing=both)` active for crop and livestock.
- [ ] Crop images: caption shows `MoE expert ... (onnx) · routing=both`, ~10 test photos mostly correct.
- [ ] Livestock images: both experts listed; lumpy photo not called healthy.
- [ ] Local route shows the season note; cloud route shows citations ✅.
- [ ] Gemini step: AI Studio counter went up by exactly 1 per click.
- [ ] Qwen step: `local_llm` caption, vLLM log shows the request, AI Studio counter unchanged, fallback works when the tunnel is closed.
- [ ] Set `.env` back to your preferred defaults (for example `GEMINI_ENABLED=false` when not testing).

**Known limitation to be aware of:** the fine-tuned crop experts only know the 38 PlantVillage classes. The old checkpoint also knew wheat and rice; with MoE active those crops are forced into a PlantVillage label (usually with a misleadingly high confidence). Keep this in mind when demoing, or tell me and I will add an "unknown crop" reject rule.
