# AgriVision — Test To-Do Guide

Legend: 🟢 testable now (no fine-tuning) · 🟡 needs an API key · 🔴 only after fine-tuning.
**All time / RAM / disk figures below are my estimates, not measurements** — I never ran GPU jobs.
Treat them as planning numbers and note what you actually observe.

---
## PART A — What to test NOW (before any fine-tuning)

### A0. One-time setup (your Windows laptop, PowerShell, repo root)
```powershell
python -m venv venv                      # skip if ./venv already exists
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt          # ~3-6 GB with torch; 10-20 min
# optional (only to test ONNX sub-experts later):  pip install onnxruntime
```
Create `.env` from `.env.example` **yourself** (I never read it). For "no mock" testing set:
```
AGRIVISION_EXPERT_MODE=real     # 'auto' silently falls back to MOCK if a model fails to load; 'real' raises instead
GEMINI_ENABLED=false            # switch to true only in step A6
WEATHER_ENABLED=false           # switch to true only in step A7
HF_HUB_OFFLINE=1                # optional: prevents any accidental download
```

### A1. 🟢 Automated tests (≈2 min, offline, no API)
```powershell
$env:AGRIVISION_EXPERT_MODE="mock"; $env:GEMINI_ENABLED="false"; $env:HF_HUB_OFFLINE="1"
pytest tests/ -q
```
Expect: **119 passed, 13 skipped** (13 skips are the Windows OpenCV/app-import skips, pre-existing).
Then delete any `test_*.db` files the tests drop in the repo root.

### A2. 🟢 "What is real vs mock right now?" (≈20 s, offline, no API calls)
```powershell
$env:AGRIVISION_EXPERT_MODE="real"
python setup/check_real_components.py
```
Read the output:
| Line | Meaning |
|---|---|
| `[OK ] crop expert REAL -> hf:...crop_model` | real HuggingFace crop model loaded |
| `[OK ] livestock expert REAL -> hf:...livestock_model` | real CLIP zero-shot livestock model loaded (note: **not fine-tuned**) |
| `[MOCK] ... cannot load` | model files missing → run `setup/download_*_model.py` (needs internet, free) |
| `MoE ...: inactive` | expected until Part B is done |
| `RAG backend = faiss` | real semantic search. `lexical` = BM25 fallback (fine, also real) |
| `[MOCK] Gemini` | `GEMINI_ENABLED` is not true |

### A3. 🟢 Streamlit app, real vision + mock Gemini
```powershell
$env:AGRIVISION_EXPERT_MODE="real"
streamlit run src/app/streamlit_app.py      # opens http://localhost:8501
```
1. Sign up (any phone/PIN) → log in.
2. Sidebar: choose **Region** (e.g. Punjab) and **Season**.
3. Upload a clear crop leaf photo (e.g. `demo_data/sharp.jpg` is only a sharpness test image; use a real leaf photo) → **Auto-Detect**.
4. How to know it is real: under the result you see `🔧 Vision backend: hf:...\models_cache\crop_model`. If you see the yellow **"MOCK vision predictor in use"** warning, it is mock.
5. If the route is **local**: check a blue 🗓️ season note and that the actions text is unchanged by season.
6. If the route is **cloud** (with Gemini disabled): you get the canned "mock advisory". Caption reads `Advisory backend: gemini(MOCK-client)` — this is how you know it is *not* real Gemini.
7. **Farm History** tab: your runs are stored; a second cloud run should show history refs like `H12` in the caption.
8. Try `demo_data/blurry.jpg` → should be **rejected** with a retake message.
9. Upload a non-plant/non-animal picture → "doesn't appear to be a crop or livestock photo".

Known limit today: the current crop checkpoint knows only 13 classes (Corn/Wheat/Potato/Rice) and the livestock model is zero-shot CLIP, so accuracy will be mediocre — that is what Part B improves.

### A4. 🟢 RAG / knowledge base (offline)
```powershell
python eval/kb_coverage_audit.py                     # 0 RAG gaps expected; ~21 offline-advisory gaps are intentional
python -m src.zone2_cloud.rag.retriever "cow with lumps on skin and fever"    # top hit should be KB-lumpy_skin_disease
python -m src.zone2_cloud.rag.build_knowledge_base   # rebuild FAISS after any KB edit (~30 s, uses cached MiniLM)
python eval/rag_eval.py --backend lexical
python eval/rag_eval.py --backend faiss
```
**Your manual task:** open `eval/rag_queries.json`, correct the relevance labels using your domain knowledge, set `"reviewed": true`, re-run. Only then treat precision/recall/MRR as real. Also skim the 22 draft docs (`review_status: draft_needs_expert_review` in `src/zone2_cloud/rag/knowledge_base/`) and the notes in `src/zone1_edge/knowledge/seasonal_guidance.json`.

Optional reranker comparison (needs the cached model, ~2 GB RAM):
```powershell
$env:RAG_RERANK_MODEL="BAAI/bge-reranker-v2-m3"; python eval/rag_eval.py --backend faiss --rerank
```

### A5. 🟢 Livestock sensors + Hindi text
In the app expand **Livestock Sensors**, set temp 40.5 / activity low / feed low and add text "गाय को बुखार है" with a cow photo. Expect fusion to raise concern → usually a cloud route. (Voice input is intentionally disabled.)

### A6. 🟡 Real Gemini (costs API quota — do a few runs only)
Get the key: <https://aistudio.google.com/apikey> → sign in → **Create API key**. Free tier has rate limits; do **not** enable billing unless you want to pay. Put it in `.env`:
```
GEMINI_ENABLED=true
GEMINI_API_KEY=<your key>
GEMINI_MODEL=gemini-2.5-flash-lite
```
Restart Streamlit, upload a **low-confidence or safety-critical** case (forces cloud route). How to verify it is real:
- Caption shows `Advisory backend: gemini` **without** `(MOCK-client)`.
- Summary is case-specific, not "This is a mock advisory from MockGeminiClient."
- Caption `Cited docs: KB-...` lists IDs that really appear in the retrieved set; `Citations verified ✅`.
- If it says "Error generating advisory" the key/quota is wrong (check the terminal for the error text).
Quota is spent per cloud-route click; keep tests few.

### A7. 🟡 Real weather (free, no key)
`.env`: `WEATHER_ENABLED=true`, restart, set a Region in the sidebar, trigger a cloud case → caption `Weather context (open-meteo): ...`. Disconnect Wi-Fi and repeat → advisory must still appear, just without the weather caption. States are approximated by centroid coordinates.

### A8. 🟢 Dry-runs of Phase 4 tooling (no API)
```powershell
python -m training.llm.generate_synthetic_data --audit-db      # how many real records exist (expect: very few → synthetic needed)
python -m training.llm.generate_synthetic_data --dry-run --n 10
python -m training.llm.compare_backends --backend mock --limit 3   # needs sft_test.jsonl first, so skip until Part C
```

---
## PART B — Fine-tuning the vision experts (on the GPU workstation)

### B0. GPU workstation setup (Linux, bash)
**Code** lives in `/home/m25cse030/agri-vision-platform` (the git clone). **Everything big** (venv, datasets, checkpoints, outputs, downloads, logs) lives on the HDD under `/DATA1/shrusti/agri-vision-platform`, so your home disk stays small.
```
/home/m25cse030/agri-vision-platform/      <- CODE ONLY (git clone; you cd here and run every command from here)

/DATA1/shrusti/agri-vision-platform/         <- HDD: everything else
├── venv/           python environment (~7-9 GB)
├── data/           plantvillage/  cattle/            (datasets)
├── models_cache/   moe/<group>/ (ONNX+checkpoints), moe/*_moe_gate.json, llm/ (LoRA adapters)
├── results/        eval reports, gate reports, llm_data/, llm_compare/, rag_eval/
├── logs/           nohup logs
├── hf_cache/       Hugging Face + torch downloads (Qwen base model ~3 GB, timm backbones)
├── pip_cache/      pip download cache
└── tmp/            temp files
```
One-time setup (run these exact lines; `AGRI` = HDD, `CODE` = code dir):
```bash
export AGRI=/DATA1/shrusti/agri-vision-platform
export CODE=/home/m25cse030/agri-vision-platform
mkdir -p $AGRI/{data,models_cache,results,logs,hf_cache,pip_cache,tmp}
git clone <your-repo-url> $CODE && cd $CODE
python3 -m venv $AGRI/venv && source $AGRI/venv/bin/activate
export PIP_CACHE_DIR=$AGRI/pip_cache TMPDIR=$AGRI/tmp
pip install --upgrade pip
# torch build must match the CUDA version shown by nvidia-smi (example: CUDA 12.1):
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
pip install -r training/requirements-train.txt onnxruntime
python -c "import torch;print(torch.cuda.is_available(), torch.cuda.device_count())"
```
**Put these in `~/.bashrc` (or a file `$AGRI/env.sh` you `source` every session)** — they redirect all outputs and downloads to the HDD:
```bash
export AGRI=/DATA1/shrusti/agri-vision-platform
export CODE=/home/m25cse030/agri-vision-platform
export AGRIVISION_DATA_ROOT=$AGRI            # models_cache/, results/ (training scripts write models_cache/ + results/ here, NOT into the code dir)
export HF_HOME=$AGRI/hf_cache                # Hugging Face downloads (Qwen etc.)
export TORCH_HOME=$AGRI/hf_cache/torch       # timm/torch pretrained weights
export PIP_CACHE_DIR=$AGRI/pip_cache TMPDIR=$AGRI/tmp
export CUDA_DEVICE_ORDER=PCI_BUS_ID          # CUDA_VISIBLE_DEVICES numbering == nvidia-smi numbering
source $AGRI/venv/bin/activate
cd $CODE                                     # always run commands from the code dir (python -m training... needs it)
```
Check GPUs with `nvidia-smi -L`, then put `CUDA_VISIBLE_DEVICES=<idx of a 24 GB card>` before each command (the 48 GB card is never needed).
Verify the redirect worked: `python -c "from training.paths import MODELS,RESULTS,DATA;print(MODELS,RESULTS)"` must print `/DATA1/...`.
Always use `python -u` so `nohup` logs are not buffered; follow with `tail -f $AGRI/logs/<name>.log`, GPU with `watch -n2 nvidia-smi`, disk with `du -sh $AGRI/*`.

**Disk (estimates):** venv 7–9 GB · PlantVillage 1–3 GB · cattle dataset 0.2–2 GB · hf_cache ~3.5 GB (with Qwen) · models/results <1 GB. **≈15–20 GB on the HDD; keep 30 GB free.** Check: `df -h /DATA1`.
**HDD speed note:** training reads ~50k small images; the first epoch is slow on a spinning disk (random reads) and later epochs are faster (OS file cache; keep ≥16 GB free RAM). If a run looks I/O-bound (GPU utilisation low, `iostat -x 2` shows the HDD ~100% busy), copy the dataset to a local SSD/`/dev/shm` once and pass that path as `--root`. Checkpoints/logs/results are small and fine on the HDD.
**CPU:** vision training is data-loader bound — give it 8+ cores (`--workers 8`), RAM ≈ 8–16 GB.

### B1. Get the datasets (verify names/licences on their pages yourself)
- PlantVillage (38 classes, ImageFolder): e.g. Kaggle "plantvillage dataset" (use the **color** folder) or a Hugging Face copy. For Kaggle: <https://www.kaggle.com/settings> → **Create New Token** → save `~/.kaggle/kaggle.json` (`chmod 600`), `pip install kaggle`, `kaggle datasets download -d <owner/slug> --unzip -p $AGRI/data/plantvillage`.
- Cattle disease dataset (LSD / FMD / healthy) — the one you chose. Put it in `$AGRI/data/cattle/<class_folder>/*.jpg`, then edit `training/configs/cattle_class_map.json` so the keys match your **actual folder names**.
The class folder names for PlantVillage must match `src/zone1_edge/moe/expert_groups.py` (e.g. `Corn_(maize)___Common_rust_`). The audit tells you which folders didn't match.

### B2. Step 1 — dataset audit (CPU, <1 min)
```bash
python -m training.dataset_audit --root $AGRI/data/plantvillage --domain crop
python -m training.dataset_audit --root $AGRI/data/cattle --domain livestock --class-map training/configs/cattle_class_map.json
```
Look for: `crop_row ... OK`, `crop_perennial ... OK`, and `unmapped_folders` (fix names/class-map if not empty).
If `livestock_fmd` says **UNDER-SUPPORTED**, skip the FMD expert (see B6) — FMD stays on zero-shot + cloud.

### B3. Step 2 — BASELINE ("before" numbers), current unmodified experts
```bash
CUDA_VISIBLE_DEVICES=0 nohup python -u -m training.evaluate_expert --root $AGRI/data/plantvillage --domain crop --target baseline > $AGRI/logs/base_crop.log 2>&1 &
CUDA_VISIBLE_DEVICES=0 nohup python -u -m training.evaluate_expert --root $AGRI/data/cattle --domain livestock --target baseline --class-map training/configs/cattle_class_map.json > $AGRI/logs/base_live.log 2>&1 &
```
Time ≈ 5–20 min each (the runtime experts run on CPU). Output: `$AGRI/results/zone1/eval/<domain>_baseline.{md,json}`. Expect low crop scores because the current checkpoint has no Tomato/Apple/etc. classes — that is a true statement about "before", not a bug.

### B4. Step 3 — fine-tune the 4 sub-experts (one at a time on one 24 GB GPU)
Defaults: `mobilenetv3_large_100`, 224 px, 3+5+5 epochs (A head-only, B top-2 blocks, C full net with layerwise-lower LRs), class-weighted loss, best checkpoint by **val macro-F1**.
```bash
export CUDA_DEVICE_ORDER=PCI_BUS_ID
CUDA_VISIBLE_DEVICES=0 nohup python -u -m training.finetune_expert --root $AGRI/data/plantvillage --group crop_row --batch 64 --workers 8 > $AGRI/logs/ft_crop_row.log 2>&1 &
# when finished:
CUDA_VISIBLE_DEVICES=0 nohup python -u -m training.finetune_expert --root $AGRI/data/plantvillage --group crop_perennial --batch 64 --workers 8 > $AGRI/logs/ft_crop_perennial.log 2>&1 &
CUDA_VISIBLE_DEVICES=0 nohup python -u -m training.finetune_expert --root $AGRI/data/cattle --group livestock_lsd --class-map training/configs/cattle_class_map.json --batch 32 --workers 8 > $AGRI/logs/ft_lsd.log 2>&1 &
CUDA_VISIBLE_DEVICES=0 nohup python -u -m training.finetune_expert --root $AGRI/data/cattle --group livestock_fmd --class-map training/configs/cattle_class_map.json --batch 32 --workers 8 > $AGRI/logs/ft_fmd.log 2>&1 &   # only if audit OK
```
Per-run estimates on one 24 GB card (AMP on):
| Expert | Images (approx) | Time | GPU mem | CPU RAM |
|---|---|---|---|---|
| crop_row (21 cls) | ~30 k | 10–30 min | 3–5 GB | 6–10 GB |
| crop_perennial (17 cls) | ~20 k | 8–20 min | 3–5 GB | 6–10 GB |
| livestock_lsd / fmd | 1–5 k | 3–10 min | 2–4 GB | 4–8 GB |
Because they use ~4 GB each, you **can** run 2–3 concurrently on the same 24 GB GPU, but the CPU loaders will then compete; sequential is safer. Never needs the 48 GB card.
The log prints one line per epoch (`stage`, `train_loss`, `val_acc`, `val_macro_f1`). Healthy signs: val macro-F1 rises in stage A then improves again in B/C; if it drops in C, lower `--lr-head` (e.g. `5e-4`) or `--top-blocks`. Exact N and LRs are meant to be tuned on val.
Outputs in `$AGRI/models_cache/moe/<group>/`: `model.onnx`, `meta.json`, `best.pt`, `training_log.csv`, `test_report.md/json`, `split_manifest.json`.
If it crashes with CUDA OOM: `--batch 32`. If dataloader errors about shared memory: `--workers 4`.

### B5. Step 4 — train the learned moe_gate (CPU, ~2–5 min)
```bash
python -u -m training.train_moe_gate --root $AGRI/data/plantvillage --domain crop
python -u -m training.train_moe_gate --root $AGRI/data/cattle --domain livestock --class-map training/configs/cattle_class_map.json
```
Prints `moe_gate test routing accuracy`. Writes `$AGRI/models_cache/moe/<domain>_moe_gate.json` (<100 KB). If routing accuracy is poor, **report it honestly** — gate features are simple colour/texture statistics and may confuse the two crop groups; the documented fallback is a gate on backbone embeddings (future change, ask me).

### B6. Step 5 — evaluate ("after") and compare with baseline
```bash
CUDA_VISIBLE_DEVICES=0 python -u -m training.evaluate_expert --root $AGRI/data/plantvillage --domain crop --target sub:crop_row
CUDA_VISIBLE_DEVICES=0 python -u -m training.evaluate_expert --root $AGRI/data/plantvillage --domain crop --target sub:crop_perennial
CUDA_VISIBLE_DEVICES=0 python -u -m training.evaluate_expert --root $AGRI/data/plantvillage --domain crop --target moe        # end-to-end + gate routing accuracy
CUDA_VISIBLE_DEVICES=0 python -u -m training.evaluate_expert --root $AGRI/data/cattle --domain livestock --target moe --class-map training/configs/cattle_class_map.json
```
(needs `onnxruntime` installed on the GPU box: `pip install onnxruntime`). Time 2–10 min each. Compare `$AGRI/results/zone1/eval/*_baseline.md` vs `*_moe.md`: accuracy, macro-F1, per-class recall, confusion matrix, ECE (calibration). Note accuracy on train data ≠ test; only the `test` split numbers count.
**If FMD is under-supported:** don't ship `livestock_fmd`; MoE for livestock stays inactive (all four ONNX files must exist), so livestock keeps the CLIP path. Say so in your report.

### B7. Step 6 — use the trained models in the app
Copy `$AGRI/models_cache/moe/` from the GPU box to the app machine's `models_cache/moe/` (`scp -r`; ~50 MB ONNX+gate — leave `best.pt` files behind), or point the app at it with `AGRIVISION_DATA_ROOT` / `AGRIVISION_MODEL_CACHE`, `pip install onnxruntime`, keep `AGRIVISION_MOE_ENABLED=auto`. Re-run `python setup/check_real_components.py` → `MoE crop: active`. In the app the caption shows `MoE expert: crop_row (onnx)`. Ensure fine-tuned outputs still route correctly (e.g. Tomato early blight should now hit the offline advisory).

---
## PART C — LLM fine-tuning (Phase 4)

### C1. 🟡 Generate synthetic data (**calls Gemini, uses quota; run from any machine with the key**)
```bash
python -m training.llm.generate_synthetic_data --audit-db
python -m training.llm.generate_synthetic_data --dry-run --n 20                      # free: inspect scenarios
GEMINI_ENABLED=true python -m training.llm.generate_synthetic_data --n 40 --i-understand-this-calls-gemini    # pilot: 40 calls
```
**Human review is mandatory:** open `$AGRI/results/zone2/llm_data/review_sample.csv`, read each row for agronomic/veterinary correctness, write `approved` or `rejected` in the `review_status(approved/rejected)` column. Fix prompts if many rejected. Then scale up (e.g. `--n 600`; ~ 600 Gemini calls — watch your quota).
```bash
python -m training.llm.prepare_sft_dataset --reviewed $AGRI/results/zone2/llm_data/review_sample.csv   # keeps only approved+valid+citation-clean, splits train/val/test
```
⚠️ Only rows that appear in the reviewed CSV are used, so for the scaled run review the **full** CSV, not just the pilot.
Aim for ≥300–500 approved examples; fewer than ~150 will underfit/hurt quality.

### C2. QLoRA training (GPU; one 24 GB card is enough)
```bash
CUDA_VISIBLE_DEVICES=0 nohup python -u -m training.llm.finetune_qlora --base Qwen/Qwen2.5-1.5B-Instruct --out $AGRI/models_cache/llm/agrivision-qwen-lora > $AGRI/logs/qlora.log 2>&1 &
```
Estimates: VRAM 8–12 GB (4-bit + gradient checkpointing, batch 4 × accum 4) · CPU RAM ~8 GB · disk ~3 GB base download (into `$AGRI/hf_cache`) + ~0.2 GB adapters (into `$AGRI/models_cache/llm`) · time 20–60 min for ~500 examples × 3 epochs. HF token is optional (Qwen 2.5 is open): only if you hit rate limits, <https://huggingface.co/settings/tokens> → new **read** token → `huggingface-cli login`.
Healthy signs: `eval_loss` decreases across epochs; best epoch is kept automatically. If OOM: `--batch 2 --grad-accum 8` or `--max-len 1536`.

### C3. Serve and connect
```bash
pip install vllm          # on the GPU box (large install)
CUDA_VISIBLE_DEVICES=0 nohup python -u -m vllm.entrypoints.openai.api_server --model Qwen/Qwen2.5-1.5B-Instruct --enable-lora --lora-modules agrivision-advisor=$AGRI/models_cache/llm/agrivision-qwen-lora --port 8000 > $AGRI/logs/vllm.log 2>&1 &
```
(Or any OpenAI-compatible server.) In the app's `.env`: `ADVISORY_BACKEND=local_llm`, `LOCAL_LLM_URL=http://<gpu-host>:8000/v1`, `LOCAL_LLM_MODEL=agrivision-advisor` (use an SSH tunnel; don't expose port 8000 publicly). Verify in the UI: `Advisory backend: local_llm`. If the server is down it falls back and shows `gemini_fallback...`.

### C4. Compare vs Gemini (same held-out test set)
```bash
ADVISORY_BACKEND=local_llm LOCAL_LLM_URL=http://localhost:8000/v1 python -m training.llm.compare_backends --backend local_llm
GEMINI_ENABLED=true python -m training.llm.compare_backends --backend gemini --i-understand-this-calls-gemini   # spends quota = test-set size
python eval/rag_eval.py --citations $AGRI/results/zone2/llm_compare/local_llm.jsonl
```
Reports in `$AGRI/results/zone2/llm_compare/*_report.json`: schema-validity, validator pass, citation correctness, farm-history citation correctness. Also read a sample of the JSONL outputs by hand — these metrics don't measure medical/agronomic quality.

---
## PART D — Which extra keys/tokens do I need?
| Token | Needed for | How to get | Cost |
|---|---|---|---|
| `GEMINI_API_KEY` | real cloud advisory (A6), synthetic data (C1), Gemini comparison (C4) | <https://aistudio.google.com/apikey> | free tier rate-limited; billing optional — leave billing off to cap spend |
| Kaggle `kaggle.json` | downloading datasets from Kaggle only | kaggle.com/settings → Create New Token | free |
| HF token (optional) | avoiding rate limits / gated models | huggingface.co/settings/tokens (read) | free |
| Weather | none (Open-Meteo) | — | free, non-commercial |
| Local LLM key | only if your server requires one (`LOCAL_LLM_API_KEY`) | your server | — |

## PART E — Checklist: how to confirm "not mock"
- [ ] `python setup/check_real_components.py` shows `[OK ]` for both experts and `[OK ] Gemini` (after A6).
- [ ] UI caption `Vision backend: hf:<path>` (never `mock`), no yellow MOCK warning.
- [ ] UI caption `Advisory backend: gemini` (no `(MOCK-client)`), or `local_llm`.
- [ ] After Part B: caption `MoE expert: <group> (onnx)`.
- [ ] Set `AGRIVISION_EXPERT_MODE=real` so a missing model raises an error instead of silently mocking.

## PART F — Is the fine-tuning code optimised?
I reviewed it and it was **not** fully optimised, so I fixed it (`training/finetune_expert.py`):
- Mixed precision (AMP + GradScaler) → ~2× faster, ~half activation memory · `channels_last` + `cudnn.benchmark` · pinned memory, non-blocking transfers, persistent workers, prefetch 4 · JPEG `draft` decoding (big CPU saving on large camera photos) · workers default = min(8, CPU cores) · `set_to_none` grads · AMP during validation.
- Already efficient: frozen-backbone stage A (only head gets gradients), small edge backbone, per-group LRs, QLoRA (4-bit, gradient checkpointing, bf16/fp16 auto) for the LLM.
- Verified only by a tiny CPU smoke test (AMP paths are inactive on CPU) — first GPU run is the real test; if you see `nan` loss, tell me and I'll switch to bf16/disable the scaler.
- Storage: all outputs honour `AGRIVISION_DATA_ROOT` (`training/paths.py`); `src/` reads trained models from `$AGRIVISION_DATA_ROOT/models_cache` automatically (or `AGRIVISION_MODEL_CACHE`). The small FAISS index and farm DB stay in the repo.
- Not optimised on purpose: gate feature extraction is single-process CPU (~1–3 min); no multi-GPU (unneeded).

## PART G — Report back
Send me the tails of `$AGRI/logs/*.log` and `$AGRI/results/zone1/eval/*.md` and I'll write the before/after comparison and adjust hyperparameters.
