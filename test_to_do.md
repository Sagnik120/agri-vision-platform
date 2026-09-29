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
| B-fix | Follow-ups from those results: re-run crop baseline; measure the new `--routing both` | ⏳ you run these (Part B) |
| C | RAG label review, synthetic data (Gemini), Qwen fine-tuning, comparison | ⏳ next |
| D / E | Keys you need; checklist to confirm nothing is mock | reference |

## Everything that uses an API, in one place
| Command | API | How many requests |
|---|---|---|
| `generate_synthetic_data --n N ... --i-understand-this-calls-gemini` | 🔴 Gemini | **exactly N at most** (one per scenario; failures count too; stops early after 3 failures in a row) |
| `compare_backends --backend gemini ... --limit L` | 🔴 Gemini | **L** (or the whole test set, about 50, if you leave out `--limit`) |
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

### B-fix-2. Routing fix: `--routing both` ✅ code added, ⏳ you measure it (GPU box, 🟢 NO API, about 2-10 min each)
**What it does.** Today the `moe_gate` picks ONE expert per image (`top1`). Because the gate is right only ~74% (crop) / ~82% (livestock) of the time, many images reach the wrong expert. `both` runs **every expert of the domain** (2 small ONNX models, tens of ms each on CPU) and combines the answers:
- **crop:** the most confident expert wins (gate probability only breaks ties).
- **livestock:** *disease first*. If either expert reports a disease, the most confident disease answer wins; otherwise "healthy". This targets the missed lumpy-skin cases. Expect **more false alarms** (healthy animals flagged); the evaluation shows how many.

Nothing is switched on by default. Measure first (results go to separate `*_moe_both.*` files, so the top1 reports are kept):
```bash
CUDA_VISIBLE_DEVICES=0 python -u -m training.evaluate_expert --root "$PV" --domain crop --target moe --routing both
CUDA_VISIBLE_DEVICES=0 python -u -m training.evaluate_expert --root "$CATTLE" --domain livestock --target moe --routing both --class-map $CM
```
Compare `results/zone1/eval/crop_moe.md` (top1) with `crop_moe_both.md`: accuracy, macro-F1, calibration (ECE), and for livestock the confusion matrix (lumpy → healthy count, healthy → disease count). `moe_gate_routing_accuracy` = the gate alone; `winning_expert_group_accuracy` = how often the winning expert belongs to the right group. Send me the `*_both.md` files and I will add them to the report and recommend whether to adopt it.
To adopt it in the app afterwards, set `AGRIVISION_MOE_ROUTING=both` in `.env` (default is `top1`). The app caption then shows `MoE expert: <winner> (onnx)`.

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

## C1. Review the RAG labels 🟢 NO API (laptop, your time)
Same task as A4. Do it first: the citation checks in the later steps rely on the knowledge base being right.

## C2. Generate synthetic training data 🔴 USES GEMINI API
**What happens:** the script builds "scenarios" (a disease from the knowledge base + region + season + weather + optional farm history + the retrieved knowledge documents). For each scenario it sends the same prompt the app would send and asks Gemini for the advisory JSON. **Each scenario is one request.** Answers are auto-checked (format, citations, no drug doses) and saved with `synthetic=true` and `review_status=pending`.

**How you stay under your limit:**
- `--n N` is the **maximum number of new requests in this run**, so you control the exact spend.
- It **resumes**: scenarios already stored are skipped. Running `--n 15` on three different days makes 45 different scenarios, never repeats.
- It **stops itself after 3 failures in a row** (e.g. quota reached) instead of burning more requests.
- Check your remaining quota first at <https://aistudio.google.com/> (your project's usage / rate limits). Limits differ by model and account and change over time, so I do not quote numbers.

**Step 1: preview the scenarios 🟢 NO API**
```bash
python -m training.llm.generate_synthetic_data --audit-db          # how many real records exist (expect very few)
python -m training.llm.generate_synthetic_data --dry-run --n 10    # writes scenarios_dry_run.jsonl, 0 requests
```
Open `$AGRI/results/zone2/llm_data/scenarios_dry_run.jsonl` and check that the scenarios look sensible. (The dry run never touches your real data or review sheet.)

**Step 2: pilot 🔴 USES GEMINI API (15 requests)**
```bash
GEMINI_ENABLED=true python -m training.llm.generate_synthetic_data --n 15 --i-understand-this-calls-gemini
```
The key is read from `.env` in the code directory. Output: `synthetic_advisories.jsonl` and the review sheet `review_sample.csv` in `$AGRI/results/zone2/llm_data/`.

**Step 3: review by hand 🟢 NO API.** Open `review_sample.csv`. For each row read the summary and actions for agronomic or veterinary correctness and type `approved` or `rejected` in the column `review_status(approved/rejected)`. If most are rejected, tell me and we fix the prompt before spending more.

**Step 4: scale up in batches 🔴 USES GEMINI API (your choice, e.g. 50 requests per run)**
Target: **300-500 approved examples** (fewer than about 150 will not teach the model reliably). With roughly 80% approved that is about 400-600 requests in total; spread them over days if your quota is small.
```bash
GEMINI_ENABLED=true python -m training.llm.generate_synthetic_data --n 50 --i-understand-this-calls-gemini    # repeat as often as you like
```
Each run appends new rows to the same sheet; review the new rows only.

## C3. Build the training files 🟢 NO API
```bash
python -m training.llm.prepare_sft_dataset --reviewed $AGRI/results/zone2/llm_data/review_sample.csv
```
Keeps only rows you marked `approved` **and** that pass the validator and the citation check, then splits them per disease into train / val / **test** (about 80/10/10). The test part is never used for training and is what the final comparison uses. Only rows present in the reviewed sheet are used, so make sure the whole sheet is filled in.

## C4. Fine-tune Qwen (QLoRA) 🌐 FREE DOWNLOAD (base model ~3 GB from Hugging Face, no key) (GPU box)
```bash
CUDA_VISIBLE_DEVICES=0 nohup python -u -m training.llm.finetune_qlora --base Qwen/Qwen2.5-1.5B-Instruct --out $AGRI/models_cache/llm/agrivision-qwen-lora > $AGRI/logs/qlora.log 2>&1 &
tail -f $AGRI/logs/qlora.log
```
**What happens:** the 1.5 B model is loaded in 4-bit (small memory) and only tiny "LoRA adapter" layers (~70 MB) are trained on your approved examples, in the model's own chat format. Gemini is not involved.
Estimates: GPU 8-12 GB · RAM ~8 GB · disk ~3 GB base model (in `$AGRI/hf_cache`) + ~0.2 GB adapters · **20-60 min** for ~500 examples × 3 epochs.
**Healthy signs:** `eval_loss` goes down over the epochs; the best epoch is kept automatically. **If out of memory:** add `--batch 2 --grad-accum 8` or `--max-len 1536`. A Hugging Face token is only needed if downloads get rate-limited (huggingface.co/settings/tokens, new *read* token, then `huggingface-cli login`).

## C5. Serve the model 🟢 NO API (GPU box)
```bash
pip install vllm       # large install
CUDA_VISIBLE_DEVICES=0 nohup python -u -m vllm.entrypoints.openai.api_server --model Qwen/Qwen2.5-1.5B-Instruct --enable-lora --lora-modules agrivision-advisor=$AGRI/models_cache/llm/agrivision-qwen-lora --port 8000 > $AGRI/logs/vllm.log 2>&1 &
```
This starts a local web server that speaks the OpenAI chat format (no OpenAI account or key involved). To use it from the app add to `.env`: `ADVISORY_BACKEND=local_llm`, `LOCAL_LLM_URL=http://<gpu-host>:8000/v1`, `LOCAL_LLM_MODEL=agrivision-advisor`. Reach it through an SSH tunnel (`ssh -L 8000:localhost:8000 user@gpu-host`); do not expose port 8000 publicly. In the UI the caption should read `Advisory backend: local_llm`; if the server is down you will see `gemini_fallback...`.

## C6. Compare Qwen with Gemini on the held-out test set
```bash
# Qwen (only talks to your own server)                                                     🟢 NO API
ADVISORY_BACKEND=local_llm LOCAL_LLM_URL=http://localhost:8000/v1 python -m training.llm.compare_backends --backend local_llm

# Gemini                                                                                   🔴 USES GEMINI API
# --limit 20 = 20 requests; without --limit = the whole test set (about 50 requests)
GEMINI_ENABLED=true python -m training.llm.compare_backends --backend gemini --limit 20 --i-understand-this-calls-gemini

# citation score on the saved Qwen answers                                                 🟢 NO API
python eval/rag_eval.py --citations $AGRI/results/zone2/llm_compare/local_llm.jsonl
```
For a fair comparison use the same `--limit` for both (add `--limit 20` to the Qwen command too). Reports: `$AGRI/results/zone2/llm_compare/*_report.json` (schema validity, validator pass, citation correctness, farm-history citation correctness). Also read a few answers by hand: these numbers do not tell you whether the advice is agronomically or medically right. Send me the reports and I will add them to [docs/system/evaluation_results.md](docs/system/evaluation_results.md).

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
